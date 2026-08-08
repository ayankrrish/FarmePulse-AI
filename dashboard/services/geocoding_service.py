"""
FarmPulse AI — Geocoding Service
Converts location names to coordinates for weather queries.
"""

import logging
import requests
import time

logger = logging.getLogger(__name__)

# Cache for geocoding results (location_name -> {lat, lon, display_name})
_geocode_cache = {}
_last_request_time = 0
_min_request_interval = 1.0  # Nominatim rate limit: 1 req/sec


def geocode_location(location_name, country='India'):
    """
    Convert location name to latitude/longitude coordinates.
    
    Args:
        location_name: Name of city, town, village, district, or state
        country: Country name (default: 'India')
        
    Returns:
        dict with 'lat', 'lon', 'display_name', 'city', 'state' or None if not found
    """
    global _last_request_time
    
    if not location_name or not location_name.strip():
        return None
    
    # Normalize cache key
    cache_key = f"{location_name.lower().strip()},{country.lower()}"
    
    # Check cache
    if cache_key in _geocode_cache:
        logger.info(f"Geocoding cache hit for: {location_name}")
        return _geocode_cache[cache_key]
    
    try:
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - _last_request_time
        if time_since_last_request < _min_request_interval:
            time.sleep(_min_request_interval - time_since_last_request)
        
        # Use Nominatim (OpenStreetMap) for forward geocoding
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{location_name}, {country}",
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        headers = {'User-Agent': 'FarmPulse/1.0'}
        
        _last_request_time = time.time()
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            logger.warning(f"Location not found: {location_name}")
            return None
        
        # Extract first result
        result = data[0]
        address = result.get('address', {})
        
        location_data = {
            'lat': float(result['lat']),
            'lon': float(result['lon']),
            'display_name': result.get('display_name', location_name),
            'city': (address.get('city') or 
                    address.get('town') or 
                    address.get('village') or 
                    address.get('municipality') or 
                    address.get('hamlet')),
            'state': address.get('state'),
            'district': address.get('county') or address.get('state_district'),
            'country': address.get('country')
        }
        
        # Cache the result
        _geocode_cache[cache_key] = location_data
        
        logger.info(f"Geocoded '{location_name}' to ({location_data['lat']}, {location_data['lon']})")
        return location_data
        
    except requests.Timeout:
        logger.error(f"Geocoding timeout for: {location_name}")
        return None
    except requests.RequestException as e:
        logger.error(f"Geocoding request failed for '{location_name}': {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        logger.error(f"Geocoding parsing error for '{location_name}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected geocoding error for '{location_name}': {e}")
        return None


def extract_location_from_query(query):
    """
    Extract location mentions from natural language query.
    
    Args:
        query: User's natural language question
        
    Returns:
        list of potential location names found in the query
    """
    import re
    
    # Common location patterns
    patterns = [
        r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)',
        r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    locations = []
    for pattern in patterns:
        matches = re.findall(pattern, query)
        locations.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_locations = []
    for loc in locations:
        loc_normalized = loc.strip().lower()
        if loc_normalized not in seen:
            seen.add(loc_normalized)
            unique_locations.append(loc.strip())
    
    return unique_locations
