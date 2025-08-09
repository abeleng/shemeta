import ee
import pandas as pd
import numpy as np
from scipy.stats import gamma # For SPI calculation

# Initialize Earth Engine (ensure you've authenticated first)
ee.Initialize()

# Load FAO GAUL administrative boundaries (Level 1 for Regions)
# This provides more accurate geometries than hardcoded rectangles.
# The GAUL dataset is 'FAO/GAUL_SIMPLIFIED_500m/2015/level1' [13, 14]
ethiopia_admin_boundaries = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level1")

# Function to get geometry for a region by its name from GEE
def get_region_geometry_ee(region_name):
    """
    Fetches the Earth Engine geometry for a given Ethiopian region.
    Uses FAO GAUL administrative boundaries.
    """
    # Map common names to GAUL ADM1_NAME if they differ
    gaul_name_map = {
        "Oromia": "Oromiya", # Common variant in GAUL
        "Amhara": "Amhara",
        "Tigray": "Tigray",
        "Somali": "Somali",
        "Afar": "Afar",
        "SNNP": "Southern Nations, Nationalities, and Peoples'" # Full name for SNNP [15]
    }
    
    target_gaul_name = gaul_name_map.get(region_name, region_name)
    
    region_feature = ethiopia_admin_boundaries.filter(ee.Filter.eq('ADM1_NAME', target_gaul_name)).first()

    if region_feature.getInfo(): # Check if the feature actually exists
        return region_feature.geometry()
    else:
        print(f"Warning: Could not find exact GEE geometry for region: {region_name} ({target_gaul_name}). Using a fallback approximate bounding box.")
        # Fallback to approximate bounding box if GEE feature not found (rough estimates)
        if region_name == "Oromia": return ee.Geometry.Rectangle([33.0, 3.0, 48.0, 15.0])
        if region_name == "Amhara": return ee.Geometry.Rectangle([35.0, 8.0, 40.0, 14.0])
        if region_name == "Tigray": return ee.Geometry.Rectangle([36.0, 12.0, 40.0, 15.0])
        if region_name == "Somali": return ee.Geometry.Rectangle([40.0, 3.0, 48.0, 10.0])
        if region_name == "Afar": return ee.Geometry.Rectangle([39.0, 9.0, 42.0, 14.0])
        if region_name == "SNNP": return ee.Geometry.Rectangle([34.0, 4.0, 39.0, 9.0])
        return None


# Define a dictionary to store regional and crop-specific information
# This is based on detailed research from the provided snippets.
ethiopia_regions_data = {
    "Oromia": {
        "geometry": get_region_geometry_ee("Oromia"),
        "crops": {
            "Maize": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10, # June to October [4, 9, 10]
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 6}, # June (Zone-1 Afar, proxy for lowland Oromia) [16]
                        {"name": "Flowering/Tasseling", "start_day": 15, "end_day": 31, "month": 8} # Approx. 2 months after June planting
                    ],
                    "harvest_month_start": 9, "harvest_month_end": 12 # September to December [5, 17]
                },
                "Belg_season": { # 22% of total maize area cultivated in Belg [5]
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Teff": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Wheat": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Haricot Bean": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            }
        }
    },
    "Amhara": {
        "geometry": get_region_geometry_ee("Amhara"),
        "crops": {
            "Teff": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Wheat": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Barley": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Chickpea": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            }
        }
    },
    "Tigray": {
        "geometry": get_region_geometry_ee("Tigray"),
        "crops": {
            "Teff": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":
                        {"name": "Planting", "start_day": 1, "end_day": 7, "month": 7} # Mid-July (Central Kola Tembien) [16],
                    "harvest_month_start": 10, "harvest_month_end": 2 # October to February [5, 18]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Wheat": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 10, "harvest_month_end": 2 # October to February [5, 18]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Barley": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 21, "month": 6} # 1st-3rd week of June (Ganta Afeshum) [16],
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                },
                "Belg_season": {
                    "start_month": 3, "end_month": 6,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 3} # March-April sowing [7],
                    "harvest_month_start": 5, "harvest_month_end": 6 # May-June harvest [7]
                }
            },
            "Sorghum": {
                "Meher_season": {
                    "start_month": 6, "end_month": 10,
                    "critical_phases":,
                    "harvest_month_start": 9, "harvest_month_end": 2 # September to February [5]
                }
            }
        }
    },
    "Somali": {
        "geometry": get_region_geometry_ee("Somali"),
        "crops": {
            "Maize": {
                "Gu_season": { # Main long rainy season in Somalia [19]
                    "start_month": 4, "end_month": 8,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 4} # Early April [19],
                    "harvest_month_start": 7, "harvest_month_end": 8 # July/August [19]
                },
                "Deyr_season": { # Shorter rainy season in Somalia [19]
                    "start_month": 10, "end_month": 2,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 10} # Early October [19],
                    "harvest_month_start": 1, "harvest_month_end": 2 # January/February [19, 20]
                }
            },
            "Sorghum": {
                "Gu_season": {
                    "start_month": 4, "end_month": 8,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 4} # Early April [19],
                    "harvest_month_start": 7, "harvest_month_end": 8 # July/August [19]
                },
                "Deyr_season": {
                    "start_month": 10, "end_month": 2,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 10} # Early October [19],
                    "harvest_month_start": 1, "harvest_month_end": 2 # January/February [19, 20]
                }
            },
            "Sesame": {
                "Deyr_season": { # Specific mention of October planting for Godey, Afder in Somali region [16]
                    "start_month": 10, "end_month": 2,
                    "critical_phases":,
                    "harvest_month_start": 1, "harvest_month_end": 2 # Inferred, similar to other Deyr crops
                }
            }
        }
    },
    "Afar": {
        "geometry": get_region_geometry_ee("Afar"),
        "crops": {
            "Maize": {
                "Karma_season": { # Main rainy season (July-September) [21]
                    "start_month": 7, "end_month": 9,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 6}, # June (Zone-1, Zone-3) [16]
                        {"name": "Planting", "start_day": 1, "end_day": 31, "month": 7} # July (Zone-2) [16],
                    "harvest_month_start": 9, "harvest_month_end": 10 # Mid-September to Early October (inferred from planting)
                },
                "Sugum_season": { # Short rainy season (February-March) [21]
                    "start_month": 2, "end_month": 3,
                    "critical_phases":,
                    "harvest_month_start": 4, "harvest_month_end": 5 # Inferred
                }
            },
            "Wheat": {
                "Karma_season": {
                    "start_month": 7, "end_month": 9,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 6} # June (Zone-1) [16],
                    "harvest_month_start": 9, "harvest_month_end": 10 # Mid-September to Early October (inferred)
                },
                "Deyr_season": { # Mid-October planting for Zone-3 [16] - this might be a specific local season
                    "start_month": 10, "end_month": 12,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 15, "end_day": 31, "month": 10} # Mid-October (Zone-3) [16],
                    "harvest_month_start": 1, "harvest_month_end": 2 # Inferred
                }
            },
            "Sorghum": {
                "Karma_season": {
                    "start_month": 7, "end_month": 9,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 15, "month": 10} # Early - Mid October (Zone-1) [16],
                    "harvest_month_start": 12, "harvest_month_end": 1 # Inferred
                }
            },
            "Teff": {
                "Karma_season": {
                    "start_month": 7, "end_month": 9,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 6} # June (Zone-3) [16],
                    "harvest_month_start": 9, "harvest_month_end": 10 # Inferred
                }
            }
        }
    },
    "SNNP": { # Southern Nations, Nationalities, and Peoples' Region
        "geometry": get_region_geometry_ee("SNNP"),
        "crops": {
            "Maize": { # Common cereal in Ethiopia [3]
                "Belg_season": {
                    "start_month": 2, "end_month": 5, # Feb-March sowing, May-July harvest [7]
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 2} # Feb-March [7],
                    "harvest_month_start": 5, "harvest_month_end": 7 # May-July [7]
                }
            },
            "Teff": { # Common cereal in Ethiopia [3]
                "Belg_season": {
                    "start_month": 2, "end_month": 5,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 2} # Feb-March [7],
                    "harvest_month_start": 5, "harvest_month_end": 7 # May-July [7]
                }
            },
            "Wheat": { # Common cereal in Ethiopia [3]
                "Belg_season": {
                    "start_month": 2, "end_month": 5,
                    "critical_phases": [
                        {"name": "Planting", "start_day": 1, "end_day": 30, "month": 2} # Feb-March [7],
                    "harvest_month_start": 5, "harvest_month_end": 7 # May-July [7]
                }
            }
            # Note: SNNP also has specific "Ganna" (March-June) and "Bona" (July-December) seasons in Bale Highlands [8]
            # This data structure can be expanded to include these specific sub-regional seasons if needed.
        }
    }
}

# Function to get crop critical phases for a region, crop, and season
def get_crop_critical_phases(region_name, crop_name, season_name):
    return ethiopia_regions_data.get(region_name, {}).get("crops", {}).get(crop_name, {}).get(season_name, {}).get("critical_phases",)

# Function to get crop season dates for a region, crop, and season
def get_crop_season_dates(region_name, crop_name, season_name):
    season_info = ethiopia_regions_data.get(region_name, {}).get("crops", {}).get(crop_name, {}).get(season_name, {})
    return {
        "start_month": season_info.get("start_month"),
        "end_month": season_info.get("end_month"),
        "harvest_month_start": season_info.get("harvest_month_start"),
        "harvest_month_end": season_info.get("harvest_month_end")
    }

# Example usage:
region_name = "Oromia"
crop_name = "Maize"
season_name = "Meher_season"

geometry = get_region_geometry_ee(region_name)
critical_phases = get_crop_critical_phases(region_name, crop_name, season_name)
season_dates = get_crop_season_dates(region_name, crop_name, season_name)

print(f"Geometry for {region_name}: {geometry}")
print(f"Critical phases for {crop_name} in {region_name} ({season_name}): {critical_phases}")
print(f"Season dates for {crop_name} in {region_name} ({season_name}): {season_dates}")

# Example for another region/crop
region_name_2 = "Tigray"
crop_name_2 = "Teff"
season_name_2 = "Meher_season"

geometry_2 = get_region_geometry_ee(region_name_2)
critical_phases_2 = get_crop_critical_phases(region_name_2, crop_name_2, season_name_2)
season_dates_2 = get_crop_season_dates(region_name_2, crop_name_2, season_name_2)

print(f"\nGeometry for {region_name_2}: {geometry_2}")
print(f"Critical phases for {crop_name_2} in {region_name_2} ({season_name_2}): {critical_phases_2}")
print(f"Season dates for {crop_name_2} in {region_name_2} ({season_name_2}): {season_dates_2}")

# Example for Somali's specific seasons
region_name_3 = "Somali"
crop_name_3 = "Maize"
season_name_3_gu = "Gu_season"
season_name_3_deyr = "Deyr_season"

geometry_3 = get_region_geometry_ee(region_name_3)
critical_phases_3_gu = get_crop_critical_phases(region_name_3, crop_name_3, season_name_3_gu)
season_dates_3_gu = get_crop_season_dates(region_name_3, crop_name_3, season_name_3_gu)

critical_phases_3_deyr = get_crop_critical_phases(region_name_3, crop_name_3, season_name_3_deyr)
season_dates_3_deyr = get_crop_season_dates(region_name_3, crop_name_3, season_name_3_deyr)

print(f"\nGeometry for {region_name_3}: {geometry_3}")
print(f"Critical phases for {crop_name_3} in {region_name_3} (Gu season): {critical_phases_3_gu}")
print(f"Season dates for {crop_name_3} in {region_name_3} (Gu season): {season_dates_3_gu}")
print(f"Critical phases for {crop_name_3} in {region_name_3} (Deyr season): {critical_phases_3_deyr}")
print(f"Season dates for {crop_name_3} in {region_name_3} (Deyr season): {season_dates_3_deyr}")
