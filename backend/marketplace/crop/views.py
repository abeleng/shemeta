import csv
from django.http import JsonResponse
from .models import KebeleCrop

import csv
from django.http import JsonResponse
from .models import Crop

def load_crop_csv_from_path(request):
    """
    Loads crop data from a hardcoded local CSV file path into the Crop model.
    """
    csv_path = r"C:\Users\HP\Downloads\crops_2.csv"  # <-- update path if needed

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            try:
                Crop.objects.create(
                    name=row.get('Crop'),
                    ndvi_peak=float(row.get('ndvi_peak', 0)),
                    ndvi_scale=float(row.get('ndvi_scale', 0)),
                    ndvi_seasonal_avg=float(row.get('ndvi_seasonal_avg', 0)),
                    ndvi_start_of_season=int(row.get('ndvi_start_of_season', 0)),
                    ndvi_end_of_season=int(row.get('ndvi_end_of_season', 0)),
                    ndvi_integral=float(row.get('ndvi_integral', 0)),
                    ndvi_threshold=float(row.get('ndvi_threshold', 0)),
                    ndvi_anomaly_avg=float(row.get('ndvi_anomaly_avg', 0)),
                    seasonal_rainfall_total_min=float(row.get('seasonal_rainfall_total_min', 0)),
                    seasonal_rainfall_total_opt=float(row.get('seasonal_rainfall_total_opt', 0)),
                    seasonal_rainfall_total_max=float(row.get('seasonal_rainfall_total_max', 0)),
                    onset_date=int(row.get('onset_date', 0)),
                    cessation_date=int(row.get('cessation_date', 0)),
                    rainy_days_count=int(row.get('rainy_days_count', 0)),
                    dry_spell_days=int(row.get('dry_spell_days', 0)),
                    onset_delay_days=int(row.get('onset_delay_days', 0)),
                    onset_threshold=float(row.get('onset_threshold', 0)),
                    rainy_day_threshold=int(row.get('rainy_day_threshold', 0)),
                    dry_spell_threshold=int(row.get('dry_spell_threshold', 0)),
                    rainfall_std_dev=float(row.get('rainfall_std_dev', 0)),
                    rainfall_skewness=float(row.get('rainfall_skewness', 0)),
                    data_quality_flag=float(row.get('data_quality_flag', 0)),
                    mean_soil_moisture=float(row.get('mean_soil_moisture', 0)),
                    dry_soil_days=int(row.get('dry_soil_days', 0)),
                    dry_threshold=float(row.get('dry_threshold', 0)),
                    soil_moisture_std=float(row.get('soil_moisture_std', 0)),
                    mean_temp_season_min=float(row.get('mean_temp_season_min', 0)),
                    mean_temp_season_max=float(row.get('mean_temp_season_max', 0)),
                    max_temp_avg=float(row.get('max_temp_avg', 0)),
                    min_temp_avg=float(row.get('min_temp_avg', 0)),
                    gdd_total=int(row.get('gdd_total', 0)),
                    gdd_base_temp=int(row.get('gdd_base_temp', 0)),
                    heatwave_days=int(row.get('heatwave_days', 0)),
                    heatwave_threshold=int(row.get('heatwave_threshold', 0)),
                )
                count += 1
            except Exception as e:
                continue  # Optionally log error
    print(f"{count} crop records loaded from {csv_path}")
    return JsonResponse({'success': True, 'message': f'{count} crop records loaded.'})


def load_kebele_crop_csv_from_path(request):
    """
    Loads kebele crop data from a hardcoded local CSV file path.
    """
    csv_path = r"C:\Users\HP\Downloads\ac.csv"  # <-- update path if needed

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            try:
                KebeleCrop.objects.create(
                    kebele=row.get('kebele'),
                    crop=row.get('crop'),
                    seasonal_rainfall_total=float(row.get('seasonal_rainfall_total', 0)),
                    onset_date=float(row.get('onset_date', 0)),
                    cessation_date=float(row.get('cessation_date', 0)),
                    rainy_days_count=float(row.get('rainy_days_count', 0)),
                    dry_spell_days=float(row.get('dry_spell_days', 0)),
                    onset_delay_days=float(row.get('onset_delay_days', 0)),
                    onset_threshold=float(row.get('onset_threshold', 0)),
                    rainy_day_threshold=float(row.get('rainy_day_threshold', 0)),
                    dry_spell_threshold=float(row.get('dry_spell_threshold', 0)),
                    rainfall_std_dev=float(row.get('rainfall_std_dev', 0)),
                    rainfall_skewness=float(row.get('rainfall_skewness', 0)),
                    mean_soil_moisture=float(row.get('mean_soil_moisture', 0)),
                    dry_soil_days=float(row.get('dry_soil_days', 0)),
                    dry_threshold=float(row.get('dry_threshold', 0)),
                    soil_moisture_std=float(row.get('soil_moisture_std', 0)),
                    mean_temp_season=float(row.get('mean_temp_season', 0)),
                    max_temp_avg=float(row.get('max_temp_avg', 0)),
                    min_temp_avg=float(row.get('min_temp_avg', 0)),
                    gdd_total=float(row.get('gdd_total', 0)),
                    gdd_base_temp=float(row.get('gdd_base_temp', 0)),
                    heatwave_days=float(row.get('heatwave_days', 0)),
                    heatwave_threshold=float(row.get('heatwave_threshold', 0)),
                    ndvi_peak=float(row.get('ndvi_peak', 0)),
                    ndvi_scale=float(row.get('ndvi_scale', 0)),
                    ndvi_seasonal_avg=float(row.get('ndvi_seasonal_avg', 0)),
                    ndvi_start_of_season=float(row.get('ndvi_start_of_season', 0)),
                    ndvi_end_of_season=float(row.get('ndvi_end_of_season', 0)),
                    ndvi_integral=float(row.get('ndvi_integral', 0)),
                    ndvi_threshold=float(row.get('ndvi_threshold', 0)),
                    ndvi_anomaly_avg=float(row.get('ndvi_anomaly_avg', 0)),
                )
                count += 1
            except Exception as e:
                continue  # Optionally log error
    print(f"{count} records loaded from {csv_path}")