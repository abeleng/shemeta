from django.contrib.auth.models import AbstractUser
from django.db import models

# contract farming moa

class User(AbstractUser):
    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('EXPORTER', 'Exporter'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

class Certification(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    farm_name = models.CharField(max_length=100)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='farmer_location')
    farm_size_ha = models.FloatField()
    available_area_ha = models.FloatField()
    certifications = models.ManyToManyField(Certification, blank=True)
    machinery_equipment = models.JSONField(blank=True, null=True)
    irrigation_access = models.BooleanField(default=False)
    input_costs = models.JSONField(blank=True, null=True)
    willing_to_try_new_crops = models.BooleanField(default=False)

class ExporterProfile(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('EXPORTER', 'Exporter'),
        ('WHOLESALER', 'Wholesaler'),
        ('PROCESSOR', 'Processor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='exporter_location')
    delivery_locations = models.ManyToManyField(Location, blank=True, related_name='exporter_delivery_locations')
    certifications_required = models.ManyToManyField(Certification, blank=True)
    payment_terms = models.TextField(blank=True, null=True)

class Kebele(models.Model):
    kebele_id = models.CharField(max_length=100)

class LandDetail(models.Model):
    SOIL_TYPE_CHOICES = [
        ('vertisol', 'Vertisol (Black Cotton Soil)'),
        ('cambisol', 'Cambisol (Brown Soil)'),
        ('luvisol', 'Luvisol (Red Soil)'),
        ('nitisol', 'Nitisol (Red Clay)'),
        ('andosol', 'Andosol (Volcanic Soil)'),
        ('fluvisol', 'Fluvisol (Alluvial Soil)'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='land_details')
    region = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    plot_size = models.FloatField(help_text="Size in hectares")
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPE_CHOICES)
    irrigation_available = models.BooleanField(default=False)
    kebele_id = models.ForeignKey(Kebele, on_delete=models.CASCADE, related_name='land_details', null=True, blank=True)
    def __str__(self):
        return f"{self.region} - {self.location} ({self.plot_size} ha)"
    
class CropRequirement(models.Model):
    CROP_CHOICES = [
        ('sorghum', 'Sorghum'),
        ('rice', 'Rice'),
        ('bean', 'Bean'),
        ('lentil', 'Lentil'),
        ('safflower', 'Safflower'),
        ('sesame', 'Sesame'),
        ('soybean', 'Soybean'),
        ('carrot', 'Carrot'),
        ('garlic', 'Garlic'),
        ('onion', 'Onion'),
        ('tomato', 'Tomato'),
        ('mandarin', 'Mandarin'),
        ('mango', 'Mango'),
        ('coffee', 'Coffee'),
        ('avocado', 'Avocado'),
        ('banana', 'Banana'),
    ]
    crop_name = models.CharField(max_length=30, choices=CROP_CHOICES)
    quantity = models.FloatField(help_text="Quantity required in tons")
    price_per_kg = models.FloatField(help_text="Price per kg in ETB")
    harvest_date = models.DateField()
    region = models.CharField(max_length=50)
    quality_requirements = models.TextField(blank=True)
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_name} ({self.quantity} tons) for {self.region}"

class FarmerExporterMatch(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_matches')
    exporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exporter_matches')
    crop_requirement = models.ForeignKey(CropRequirement, on_delete=models.CASCADE, related_name='matches')
    land_detail = models.ForeignKey(LandDetail, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches')
    crop_name = models.CharField(max_length=30)
    matched_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # e.g. pending, accepted, rejected

    def __str__(self):
        return f"Match: {self.crop_name} | Farmer: {self.farmer.username} | Exporter: {self.exporter.username}"