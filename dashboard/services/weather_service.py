"""
FarmPulse AI — Weather Service
Fetches and processes weather data from Open-Meteo API.
Converts raw API responses to frontend-friendly JSON.
"""

import logging
import requests

logger = logging.getLogger(__name__)

# State coordinates for weather lookups
STATE_COORDS = {
    'Gujarat': {'lat': 23.0, 'lon': 72.6, 'city': 'Ahmedabad'},
    'Maharashtra': {'lat': 19.1, 'lon': 72.9, 'city': 'Mumbai'},
    'Rajasthan': {'lat': 26.9, 'lon': 75.8, 'city': 'Jaipur'},
    'Madhya Pradesh': {'lat': 23.3, 'lon': 77.4, 'city': 'Bhopal'},
    'Karnataka': {'lat': 12.97, 'lon': 77.6, 'city': 'Bangalore'},
    'Andhra Pradesh': {'lat': 17.4, 'lon': 78.5, 'city': 'Hyderabad'},
    'Telangana': {'lat': 17.4, 'lon': 78.5, 'city': 'Hyderabad'},
    'Uttar Pradesh': {'lat': 26.85, 'lon': 80.95, 'city': 'Lucknow'},
}


def _weather_icon(code):
    """Convert WMO weather code to emoji icon."""
    if code == 0:
        return '☀️'  # Clear sky
    if code <= 3:
        return '⛅'  # Partly cloudy
    if code <= 48:
        return '🌫️'  # Fog
    if code <= 67:
        return '🌧️'  # Rain
    if code <= 77:
        return '🌨️'  # Snow
    if code <= 82:
        return '🌧️'  # Rain showers
    if code <= 86:
        return '🌨️'  # Snow showers
    return '⛈️'  # Thunderstorm


def _weather_description(code):
    """Convert WMO weather code to human-readable description."""
    descriptions = {
        0: 'Clear Sky',
        1: 'Mainly Clear',
        2: 'Partly Cloudy',
        3: 'Overcast',
        45: 'Foggy',
        48: 'Foggy',
        51: 'Light Drizzle',
        53: 'Moderate Drizzle',
        55: 'Dense Drizzle',
        61: 'Light Rain',
        63: 'Moderate Rain',
        65: 'Heavy Rain',
        71: 'Light Snow',
        73: 'Moderate Snow',
        75: 'Heavy Snow',
        77: 'Snow Grains',
        80: 'Light Rain Showers',
        81: 'Moderate Rain Showers',
        82: 'Violent Rain Showers',
        85: 'Light Snow Showers',
        86: 'Heavy Snow Showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with Light Hail',
        99: 'Thunderstorm with Heavy Hail',
    }
    return descriptions.get(code, 'Unknown')


def _format_time(iso_string):
    """Extract HH:MM from ISO timestamp."""
    if not iso_string or 'T' not in iso_string:
        return None
    try:
        return iso_string.split('T')[1][:5]
    except (IndexError, AttributeError):
        return None


def _format_date(iso_string):
    """Extract date from ISO timestamp."""
    if not iso_string:
        return None
    try:
        return iso_string.split('T')[0]
    except (IndexError, AttributeError):
        return None


def get_weather(state=None, lat=None, lon=None, crop=None, action=None, predicted_price=None):
    """
    Fetch complete weather data for a location and convert to frontend-friendly format.
    
    Args:
        state: State name (optional, used for coordinate lookup if lat/lon not provided)
        lat: Latitude (optional, preferred over state)
        lon: Longitude (optional, preferred over state)
        crop: Crop name (optional, for advisory context)
        action: Recommendation action (optional, for advisory context)
        predicted_price: Predicted price (optional, for advisory context)
        
    Returns:
        dict: Weather data in frontend-friendly format, or None if fetch fails
        
    Raises:
        requests.RequestException: If API request fails
        ValueError: If neither state nor lat/lon provided
    """
    # Determine coordinates
    if lat is not None and lon is not None:
        # Use provided coordinates
        coords = {'lat': lat, 'lon': lon, 'city': None}
        location_source = 'gps'
        logger.info(f"Fetching weather for GPS coordinates: {lat}, {lon}")
    elif state:
        # Use state lookup
        coords = STATE_COORDS.get(state)
        if not coords:
            logger.warning(f"Unknown state: {state}, using default coordinates")
            coords = {'lat': 20.6, 'lon': 79.0, 'city': state}
        location_source = 'state'
        logger.info(f"Fetching weather for {state} ({coords['city']})")
    else:
        raise ValueError("Either state or lat/lon must be provided")
    
    # Build Open-Meteo API URL
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coords['lat']}&longitude={coords['lon']}&"
        f"current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,rain,weather_code,cloud_cover,pressure_msl,"
        f"wind_speed_10m,wind_direction_10m,uv_index,"
        f"soil_temperature_0_to_7cm,soil_moisture_0_to_7cm,"
        f"et0_fao_evapotranspiration,vapour_pressure_deficit&"
        f"hourly=temperature_2m,precipitation_probability,weather_code&"
        f"daily=weather_code,temperature_2m_max,temperature_2m_min,"
        f"sunrise,sunset,precipitation_probability_max,wind_speed_10m_max&"
        f"timezone=Asia/Kolkata&forecast_days=7"
    )
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract data
        current_raw = data.get('current', {})
        hourly_raw = data.get('hourly', {})
        daily_raw = data.get('daily', {})
        
        # Build frontend-friendly response
        result = {
            'location': {
                'city': coords.get('city', 'Unknown'),
                'state': state if location_source == 'state' else None,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'source': location_source,  # 'gps' or 'state'
            },
            'current': {
                # Basic weather
                'temperature': round(current_raw.get('temperature_2m', 0)),
                'feels_like': round(current_raw.get('apparent_temperature', 0)),
                'humidity': current_raw.get('relative_humidity_2m', 0),
                'weather_code': current_raw.get('weather_code', 0),
                'weather_icon': _weather_icon(current_raw.get('weather_code', 0)),
                'weather_description': _weather_description(current_raw.get('weather_code', 0)),
                
                # Wind
                'wind_speed': round(current_raw.get('wind_speed_10m', 0)),
                'wind_direction': current_raw.get('wind_direction_10m', 0),
                
                # Atmospheric
                'pressure': round(current_raw.get('pressure_msl', 0)),
                'cloud_cover': current_raw.get('cloud_cover', 0),
                'uv_index': round(current_raw.get('uv_index', 0)),
                
                # Precipitation
                'precipitation': current_raw.get('precipitation', 0),
                'rain': current_raw.get('rain', 0),
            },
            'agriculture': {
                'soil_temperature': current_raw.get('soil_temperature_0_to_7cm'),
                'soil_moisture': current_raw.get('soil_moisture_0_to_7cm'),
                'evapotranspiration': current_raw.get('et0_fao_evapotranspiration'),
                'vapour_pressure_deficit': current_raw.get('vapour_pressure_deficit'),
            },
            'today': {
                'precipitation_probability': daily_raw.get('precipitation_probability_max', [0])[0] if daily_raw.get('precipitation_probability_max') else 0,
                'temp_max': round(daily_raw.get('temperature_2m_max', [0])[0]) if daily_raw.get('temperature_2m_max') else 0,
                'temp_min': round(daily_raw.get('temperature_2m_min', [0])[0]) if daily_raw.get('temperature_2m_min') else 0,
                'sunrise': _format_time(daily_raw.get('sunrise', [''])[0]) if daily_raw.get('sunrise') else None,
                'sunset': _format_time(daily_raw.get('sunset', [''])[0]) if daily_raw.get('sunset') else None,
            },
            'hourly': [],
            'daily': [],
            'context': {
                'crop': crop or '',
                'action': action or '',
                'predicted_price': predicted_price or '',
            },
            'timestamp': current_raw.get('time', ''),
        }
        
        # Process hourly forecast (next 24 hours)
        hourly_times = hourly_raw.get('time', [])
        hourly_temps = hourly_raw.get('temperature_2m', [])
        hourly_precip = hourly_raw.get('precipitation_probability', [])
        hourly_codes = hourly_raw.get('weather_code', [])
        
        for i in range(min(24, len(hourly_times))):
            result['hourly'].append({
                'time': _format_time(hourly_times[i]),
                'temperature': round(hourly_temps[i]) if i < len(hourly_temps) else 0,
                'precipitation_probability': hourly_precip[i] if i < len(hourly_precip) else 0,
                'weather_code': hourly_codes[i] if i < len(hourly_codes) else 0,
                'weather_icon': _weather_icon(hourly_codes[i] if i < len(hourly_codes) else 0),
            })
        
        # Process daily forecast (7 days)
        daily_times = daily_raw.get('time', [])
        daily_codes = daily_raw.get('weather_code', [])
        daily_temp_max = daily_raw.get('temperature_2m_max', [])
        daily_temp_min = daily_raw.get('temperature_2m_min', [])
        daily_precip = daily_raw.get('precipitation_probability_max', [])
        daily_wind = daily_raw.get('wind_speed_10m_max', [])
        
        for i in range(min(7, len(daily_times))):
            result['daily'].append({
                'date': _format_date(daily_times[i]),
                'day_name': _get_day_name(daily_times[i]),
                'weather_code': daily_codes[i] if i < len(daily_codes) else 0,
                'weather_icon': _weather_icon(daily_codes[i] if i < len(daily_codes) else 0),
                'temp_max': round(daily_temp_max[i]) if i < len(daily_temp_max) else 0,
                'temp_min': round(daily_temp_min[i]) if i < len(daily_temp_min) else 0,
                'precipitation_probability': daily_precip[i] if i < len(daily_precip) else 0,
                'wind_speed': round(daily_wind[i]) if i < len(daily_wind) else 0,
            })
        
        logger.info(f"Weather fetched successfully for {state}")
        return result
        
    except requests.Timeout:
        logger.error(f"Weather API timeout for {state}")
        raise
    except requests.RequestException as e:
        logger.error(f"Weather API request failed for {state}: {e}")
        raise
    except Exception as e:
        logger.error(f"Weather processing error for {state}: {e}")
        raise


def _get_day_name(iso_date):
    """Get short day name from ISO date string."""
    if not iso_date:
        return ''
    try:
        from datetime import datetime
        date = datetime.fromisoformat(iso_date.split('T')[0])
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return days[date.weekday()]
    except (ValueError, IndexError, AttributeError):
        return ''


def get_compact_weather(state):
    """
    Get compact weather data for Dashboard weather card.
    
    Args:
        state: State name
        
    Returns:
        dict: Compact weather data with temp, humidity, wind, icon, rainProb, city
        or None if fetch fails
    """
    try:
        full_weather = get_weather(state)
        if not full_weather:
            return None
        
        current = full_weather['current']
        today = full_weather['today']
        location = full_weather['location']
        
        return {
            'temp': current['temperature'],
            'humidity': current['humidity'],
            'wind': current['wind_speed'],
            'icon': current['weather_icon'],
            'rainProb': today['precipitation_probability'],
            'city': location['city'],
        }
    except Exception as e:
        logger.warning(f"Compact weather fetch failed for {state}: {e}")
        return None
