from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def get_coordinates(address):
    """
    Get coordinates (latitude, longitude) for a given address using Nominatim.
    Includes caching to avoid repeated API calls for the same address.
    """
    # Check cache first
    cache_key = f'geocode_{address}'
    coords = cache.get(cache_key)
    if coords:
        return coords

    try:
        # Initialize the geocoder
        geolocator = Nominatim(user_agent="food_donation_app")
        
        # Get location
        location = geolocator.geocode(address)
        
        if location:
            coords = (location.latitude, location.longitude)
            # Cache the result for 24 hours
            cache.set(cache_key, coords, 60 * 60 * 24)
            return coords
        return None
    except Exception as e:
        logger.error(f"Geocoding error for address {address}: {str(e)}")
        return None

def calculate_distance(coord1, coord2):
    """
    Calculate distance between two coordinates in miles.
    coord1 and coord2 should be tuples of (latitude, longitude)
    """
    try:
        if not all(isinstance(x, (int, float)) for x in coord1 + coord2):
            return None
        # Use geodesic distance calculation for accuracy
        return round(geodesic(coord1, coord2).miles, 2)
    except:
        return None

def get_nearby_addresses(center_coords, addresses, radius_miles=5.0):
    """
    Filter addresses within radius_miles of center_coords.
    Returns list of addresses and their distances.
    """
    if not center_coords:
        return []
    
    try:
        radius_miles = float(radius_miles)
    except (TypeError, ValueError):
        radius_miles = 5.0
    
    nearby = []
    for addr_info in addresses:
        try:
            addr_coords = (float(addr_info.get('latitude')), float(addr_info.get('longitude')))
            if None not in addr_coords:
                distance = calculate_distance(center_coords, addr_coords)
                if distance is not None and distance <= radius_miles:
                    nearby.append({
                        'address': addr_info.get('address'),
                        'distance': distance,
                        'organization': addr_info.get('organization'),
                        'donations': addr_info.get('donations', [])
                    })
        except (TypeError, ValueError):
            continue
    
    # Sort by distance
    return sorted(nearby, key=lambda x: x['distance'])