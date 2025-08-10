import re
import ee

# Initialize Earth Engine
ee.Initialize(project="medacolleges")

# Load kebele boundaries
admin_boundaries = ee.FeatureCollection('projects/medacolleges/assets/Ethiopia_AdminBoundaries-shp')

def get_kebele_id_from_location_string(location_str):
    """
    Takes a string like "Addis Ababa, Ethiopia (9.0079, 38.7678)"
    and returns the kebele GlobalID (or None if not found).
    """
    match = re.search(r'\(([-+]?\d*\.\d+|\d+),\s*([-+]?\d*\.\d+|\d+)\)', location_str)
    if not match:
        return None
    lat = float(match.group(1))
    lon = float(match.group(2))
    point = ee.Geometry.Point([lon, lat])
    feature = admin_boundaries.filterBounds(point).first()
    if feature is None:
        return None
    info = feature.toDictionary().getInfo()
    return info.get('GlobalID')

