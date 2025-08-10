from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import LandDetail, CropRequirement
from .gee import get_kebele_id_from_location_string
from .models import Kebele
import pandas as pd
from crop.models import Crop, KebeleCrop
from .matcher import CropEnvMatcherForKebele, Weights
import random

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user and return JWT tokens."""
    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role')
    phone_number = request.data.get('phone_number', '')
    language = request.data.get('language', '')
    if not username or not password or not role:
        return Response({'success': False, 'message': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'success': False, 'message': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(
        username=username,
        password=password,
        role=role,
        phone_number=phone_number,
        language=language
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'success': True,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user_id': user.id,
        'role': user.role
    }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Blacklist refresh token to logout."""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_land_detail_view(request):
    """Add land detail for authenticated user, assign to a random kebele."""
    user = request.user
    data = request.data
    region = data.get('region')
    location = data.get('location')
    plot_size = data.get('plotSize')
    soil_type = data.get('soilType')
    irrigation_available = data.get('irrigationAvailable', False)

    if not (region and location and plot_size and soil_type):
        return Response({'success': False, 'message': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve all kebeles and assign one randomly
    kebeles = list(Kebele.objects.all())
    kebele_instance = random.choice(kebeles) if kebeles else None

    LandDetail.objects.create(
        user=user,
        region=region,
        location=location,
        plot_size=float(plot_size),
        soil_type=soil_type,
        irrigation_available=bool(irrigation_available),
        kebele_id=kebele_instance
    )
    return Response({'success': True, 'message': 'Land detail saved successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_recommendations(request):
    """
    Loads crop and kebele crop data from the database,
    runs matcher2.py logic, and returns recommended crops for the user's kebele.
    Expects kebele_id as a query param (?kebele_id=xxxx).
    """
    kebele_id = request.query_params.get('kebele_id')
    if not kebele_id:
        return Response({'success': False, 'message': 'Missing kebele_id.'}, status=400)

    # Get all KebeleCrop entries for this kebele
    area_instances = []
    for kc in KebeleCrop.objects.filter(kebele=kebele_id):
        area_dict = {
            "crop": kc.crop.name if hasattr(kc.crop, "name") else str(kc.crop),  # <-- FIX HERE
            "ndvi_peak": kc.ndvi_peak,
            "ndvi_scale": kc.ndvi_scale,
            "ndvi_seasonal_avg": kc.ndvi_seasonal_avg,
            "ndvi_start_of_season": kc.ndvi_start_of_season,
            "ndvi_end_of_season": kc.ndvi_end_of_season,
            "ndvi_integral": kc.ndvi_integral,
            "ndvi_threshold": kc.ndvi_threshold,
            "ndvi_anomaly_avg": kc.ndvi_anomaly_avg,
            "seasonal_rainfall_total": kc.seasonal_rainfall_total,
            "onset_date": kc.onset_date,
            "cessation_date": kc.cessation_date,
            "rainy_days_count": kc.rainy_days_count,
            "dry_spell_days": kc.dry_spell_days,
            "onset_delay_days": kc.onset_delay_days,
            "onset_threshold": kc.onset_threshold,
            "rainy_day_threshold": kc.rainy_day_threshold,
            "dry_spell_threshold": kc.dry_spell_threshold,
            "rainfall_std_dev": kc.rainfall_std_dev,
            "rainfall_skewness": kc.rainfall_skewness,
            "data_quality_flag": getattr(kc, "data_quality_flag", 1.0),
            "mean_soil_moisture": kc.mean_soil_moisture,
            "dry_soil_days": kc.dry_soil_days,
            "dry_threshold": kc.dry_threshold,
            "soil_moisture_std": kc.soil_moisture_std,
            "mean_temp_season": kc.mean_temp_season,
            "max_temp_avg": kc.max_temp_avg,
            "min_temp_avg": kc.min_temp_avg,
            "gdd_total": kc.gdd_total,
            "gdd_base_temp": kc.gdd_base_temp,
            "heatwave_days": kc.heatwave_days,
            "heatwave_threshold": kc.heatwave_threshold,
        }
        area_instances.append(area_dict)

    # Get all crops as DataFrame
    crop_qs = Crop.objects.all()
    crop_df = pd.DataFrame([{
        "crop": c.name,
        "ndvi_peak": c.ndvi_peak,
        "ndvi_scale": c.ndvi_scale,
        "ndvi_seasonal_avg": c.ndvi_seasonal_avg,
        "ndvi_start_of_season": c.ndvi_start_of_season,
        "ndvi_end_of_season": c.ndvi_end_of_season,
        "ndvi_integral": c.ndvi_integral,
        "ndvi_threshold": c.ndvi_threshold,
        "ndvi_anomaly_avg": c.ndvi_anomaly_avg,
        "seasonal_rainfall_total_min": c.seasonal_rainfall_total_min,
        "seasonal_rainfall_total_opt": getattr(c, "seasonal_rainfall_total_opt", 0),
        "seasonal_rainfall_total_max": getattr(c, "seasonal_rainfall_total_max", 0),
        "onset_date": getattr(c, "onset_date", 0),
        "cessation_date": getattr(c, "cessation_date", 0),
        "rainy_days_count": getattr(c, "rainy_days_count", 0),
        "dry_spell_days": getattr(c, "dry_spell_days", 0),
        "onset_delay_days": getattr(c, "onset_delay_days", 0),
        "onset_threshold": getattr(c, "onset_threshold", 0),
        "rainy_day_threshold": getattr(c, "rainy_day_threshold", 0),
        "dry_spell_threshold": getattr(c, "dry_spell_threshold", 0),
        "rainfall_std_dev": getattr(c, "rainfall_std_dev", 0),
        "rainfall_skewness": getattr(c, "rainfall_skewness", 0),
        "data_quality_flag": getattr(c, "data_quality_flag", 1.0),
        "mean_soil_moisture": getattr(c, "mean_soil_moisture", 0),
        "dry_soil_days": getattr(c, "dry_soil_days", 0),
        "dry_threshold": getattr(c, "dry_threshold", 0),
        "soil_moisture_std": getattr(c, "soil_moisture_std", 0),
        "mean_temp_season_min": getattr(c, "mean_temp_season_min", 0),
        "mean_temp_season_max": getattr(c, "mean_temp_season_max", 0),
        "max_temp_avg": getattr(c, "max_temp_avg", 0),
        "min_temp_avg": getattr(c, "min_temp_avg", 0),
        "gdd_total": getattr(c, "gdd_total", 0),
        "gdd_base_temp": getattr(c, "gdd_base_temp", 0),
        "heatwave_days": getattr(c, "heatwave_days", 0),
        "heatwave_threshold": getattr(c, "heatwave_threshold", 0),
    } for c in crop_qs])

    # Run matcher
    matcher = CropEnvMatcherForKebele().fit(crop_df)
    results_df = matcher.query_kebele(area_instances, max_distance=100.0, return_all=False)
    results = results_df.to_dict(orient="records")

    return Response({"success": True, "data": results}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def farmer_home_view(request):
    """
    Returns recommendations, land details, and matches for the authenticated farmer.
    For each match, includes crop requirement info from the exporter.
    """
    user = request.user
    # Get all land details for this farmer
    land_details = LandDetail.objects.filter(user=user)
    land_details_data = []
    kebele_ids = set()
    for land in land_details:
        land_details_data.append({
            "region": land.region,
            "location": land.location,
            "plot_size": land.plot_size,
            "soil_type": land.soil_type,
            "irrigation_available": land.irrigation_available,
            "kebele_id": land.kebele_id.kebele_id if land.kebele_id else None,
        })
        if land.kebele_id:
            kebele_ids.add(land.kebele_id.kebele_id)

    # Get recommendations for all kebeles associated with the farmer
    recommendations = {}
    for kebele_id in kebele_ids:
        area_instances = []
        for kc in KebeleCrop.objects.filter(kebele=kebele_id):
            area_dict = {
                "crop": kc.crop.name if hasattr(kc.crop, "name") else str(kc.crop),
                "ndvi_peak": kc.ndvi_peak,
                "ndvi_scale": kc.ndvi_scale,
                "ndvi_seasonal_avg": kc.ndvi_seasonal_avg,
                "ndvi_start_of_season": kc.ndvi_start_of_season,
                "ndvi_end_of_season": kc.ndvi_end_of_season,
                "ndvi_integral": kc.ndvi_integral,
                "ndvi_threshold": kc.ndvi_threshold,
                "ndvi_anomaly_avg": kc.ndvi_anomaly_avg,
                "seasonal_rainfall_total": kc.seasonal_rainfall_total,
                "onset_date": kc.onset_date,
                "cessation_date": kc.cessation_date,
                "rainy_days_count": kc.rainy_days_count,
                "dry_spell_days": kc.dry_spell_days,
                "onset_delay_days": kc.onset_delay_days,
                "onset_threshold": kc.onset_threshold,
                "rainy_day_threshold": kc.rainy_day_threshold,
                "dry_spell_threshold": kc.dry_spell_threshold,
                "rainfall_std_dev": kc.rainfall_std_dev,
                "rainfall_skewness": kc.rainfall_skewness,
                "data_quality_flag": getattr(kc, "data_quality_flag", 1.0),
                "mean_soil_moisture": kc.mean_soil_moisture,
                "dry_soil_days": kc.dry_soil_days,
                "dry_threshold": kc.dry_threshold,
                "soil_moisture_std": kc.soil_moisture_std,
                "mean_temp_season": kc.mean_temp_season,
                "max_temp_avg": kc.max_temp_avg,
                "min_temp_avg": kc.min_temp_avg,
                "gdd_total": kc.gdd_total,
                "gdd_base_temp": kc.gdd_base_temp,
                "heatwave_days": kc.heatwave_days,
                "heatwave_threshold": kc.heatwave_threshold,
            }
            area_instances.append(area_dict)

        crop_qs = Crop.objects.all()
        crop_df = pd.DataFrame([{
            "crop": c.name,
            "ndvi_peak": c.ndvi_peak,
            "ndvi_scale": c.ndvi_scale,
            "ndvi_seasonal_avg": c.ndvi_seasonal_avg,
            "ndvi_start_of_season": c.ndvi_start_of_season,
            "ndvi_end_of_season": c.ndvi_end_of_season,
            "ndvi_integral": c.ndvi_integral,
            "ndvi_threshold": c.ndvi_threshold,
            "ndvi_anomaly_avg": c.ndvi_anomaly_avg,
            "seasonal_rainfall_total_min": getattr(c, "seasonal_rainfall_total_min", 0),
            "seasonal_rainfall_total_opt": getattr(c, "seasonal_rainfall_total_opt", 0),
            "seasonal_rainfall_total_max": getattr(c, "seasonal_rainfall_total_max", 0),
            "onset_date": getattr(c, "onset_date", 0),
            "cessation_date": getattr(c, "cessation_date", 0),
            "rainy_days_count": getattr(c, "rainy_days_count", 0),
            "dry_spell_days": getattr(c, "dry_spell_days", 0),
            "onset_delay_days": getattr(c, "onset_delay_days", 0),
            "onset_threshold": getattr(c, "onset_threshold", 0),
            "rainy_day_threshold": getattr(c, "rainy_day_threshold", 0),
            "dry_spell_threshold": getattr(c, "dry_spell_threshold", 0),
            "rainfall_std_dev": getattr(c, "rainfall_std_dev", 0),
            "rainfall_skewness": getattr(c, "rainfall_skewness", 0),
            "data_quality_flag": getattr(c, "data_quality_flag", 1.0),
            "mean_soil_moisture": getattr(c, "mean_soil_moisture", 0),
            "dry_soil_days": getattr(c, "dry_soil_days", 0),
            "dry_threshold": getattr(c, "dry_threshold", 0),
            "soil_moisture_std": getattr(c, "soil_moisture_std", 0),
            "mean_temp_season_min": getattr(c, "mean_temp_season_min", 0),
            "mean_temp_season_max": getattr(c, "mean_temp_season_max", 0),
            "max_temp_avg": getattr(c, "max_temp_avg", 0),
            "min_temp_avg": getattr(c, "min_temp_avg", 0),
            "gdd_total": getattr(c, "gdd_total", 0),
            "gdd_base_temp": getattr(c, "gdd_base_temp", 0),
            "heatwave_days": getattr(c, "heatwave_days", 0),
            "heatwave_threshold": getattr(c, "heatwave_threshold", 0),
        } for c in crop_qs])

        # Run matcher
        matcher = CropEnvMatcherForKebele().fit(crop_df)
        results_df = matcher.query_kebele(area_instances, max_distance=17.0, return_all=False)
        rows = results_df.to_dict(orient="records")
        if rows and "distance" in results_df.columns:
            recommendations[kebele_id] = results_df.sort_values("distance").reset_index(drop=True).to_dict(orient="records")
        else:
            recommendations[kebele_id] = rows

    # Get matches for this farmer
    from .models import FarmerExporterMatch
    matches_qs = FarmerExporterMatch.objects.filter(farmer=user)
    matches = []
    for match in matches_qs:
        req = match.crop_requirement
        matches.append({
            "match_id": match.id,
            "crop_name": match.crop_name,
            "exporter": match.exporter.username,
            "status": match.status,
            "matched_on": match.matched_on,
            "requirement": {
                "id": req.id,
                "crop_name": req.crop_name,
                "quantity": req.quantity,
                "price_per_kg": req.price_per_kg,
                "harvest_date": req.harvest_date,
                "region": req.region,
                "quality_requirements": req.quality_requirements,
                "additional_notes": req.additional_notes,
                "created_at": req.created_at,
            }
        })

    return Response({
        "success": True,
        "land_details": land_details_data,
        "recommendations": recommendations,
        "matches": matches
    }, status=200)


def test_add_kebeles(request):
    """
    Adds kebeles with the given kebele_ids to the Kebele model.
    """
    kebele_ids = [
        "00d1fc6c-c0b0-4e5d-a9f4-498eb254071c",
        "7c4a7c99-436a-4ad3-93eb-75a098246cc0",
        "95d4ef76-ac56-4dd8-8bfe-40ddcdeea9d0",
        "faf8cfe8-bff7-4a86-9c28-7fa9308e8f12",
        "bb1c8df1-c824-40a3-a507-0dff5c7c7655",
        "becb019b-936a-49c4-9ada-c0733b012fc1",
        "53198744-8400-4537-a1ec-dfe798eca102",
        "5bef4450-17ac-4f1c-ae40-b25eb2091a30",
        "6f3ada95-32d9-4c51-9423-fbafd8d0edaf",
        "41613c5a-b1c3-4c83-b989-b2dbde340ca2",
    ]
    created = []
    for kebele_id in kebele_ids:
        kebele, was_created = Kebele.objects.get_or_create(kebele_id=kebele_id)
        if was_created:
            created.append(kebele_id)
    return Response({
        "success": True,
        "created": created,
        "total": len(kebele_ids)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_crop_requirement(request):
    """
    Receives crop requirement data from frontend, saves it,
    finds matching farmers for the crop, creates FarmerExporterMatch objects,
    and returns the matched farmers (with crop name only).
    """
    user = request.user
    data = request.data
    crop_name = data.get('cropName')
    quantity = data.get('quantity')
    price_per_kg = data.get('pricePerKg')
    harvest_date = data.get('harvestDate')
    region = data.get('region')
    quality_requirements = data.get('qualityRequirements', '')
    additional_notes = data.get('additionalNotes', '')

    if not all([crop_name, quantity, price_per_kg, harvest_date, region]):
        return Response({'success': False, 'message': 'Missing required fields.'}, status=400)

    try:
        # Save the crop requirement
        requirement = CropRequirement.objects.create(
            crop_name=crop_name,
            quantity=float(quantity),
            price_per_kg=float(price_per_kg),
            harvest_date=harvest_date,
            region=region,
            quality_requirements=quality_requirements,
            additional_notes=additional_notes
        )

        # Find matching farmers with land that can grow this crop
        matched_farmers = []
        farmer_users = set()
        for land in LandDetail.objects.filter(region=region):
            # You can add more logic here for soil, irrigation, etc.
            farmer = land.user
            # Check if farmer already matched for this requirement
            if farmer.id not in farmer_users:
                matched_farmers.append({
                    "farmer_id": farmer.id,
                    "farmer_username": farmer.username,
                    "crop_name": crop_name
                })
                farmer_users.add(farmer.id)
                # Create FarmerExporterMatch object
                FarmerExporterMatch.objects.create(
                    farmer=farmer,
                    exporter=user,
                    crop_requirement=requirement,
                    land_detail=land,
                    crop_name=crop_name,
                    status='pending'
                )

        return Response({
            'success': True,
            'message': 'Crop requirement posted successfully.',
            'matched_farmers': matched_farmers
        }, status=201)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=400)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CropRequirement, FarmerExporterMatch

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exporter_home_view(request):
    """
    Returns the exporter's crop requirements and matches.
    """
    user = request.user

    # Get requirements posted by this exporter
    requirements = CropRequirement.objects.filter(created_at__isnull=False, region__isnull=False)  # You may want to filter by exporter if you add a ForeignKey

    # Get matches where this user is the exporter
    matches = FarmerExporterMatch.objects.filter(exporter=user)

    requirements_data = [
        {
            "id": req.id,
            "crop_name": req.crop_name,
            "quantity": req.quantity,
            "price_per_kg": req.price_per_kg,
            "harvest_date": req.harvest_date,
            "region": req.region,
            "quality_requirements": req.quality_requirements,
            "additional_notes": req.additional_notes,
            "created_at": req.created_at,
        }
        for req in requirements
    ]

    matches_data = [
        {
            "id": match.id,
            "crop_name": match.crop_name,
            "farmer": match.farmer.username,
            "land_detail": str(match.land_detail) if match.land_detail else None,
            "matched_on": match.matched_on,
            "status": match.status,
        }
        for match in matches
    ]

    return Response({
        "success": True,
        "requirements": requirements_data,
        "matches": matches_data,
    })