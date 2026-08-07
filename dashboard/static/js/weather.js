/**
 * FarmPulse Weather Intelligence Module
 * Independent page for agricultural weather insights with Live GPS
 */

// ============================================================
// GPS LOCATION DETECTION
// ============================================================

// GPS state management
let gpsInProgress = false;

async function detectGPSLocation() {
  // Prevent multiple simultaneous GPS requests
  if (gpsInProgress) {
    console.log('[GPS] Request already in progress, ignoring click');
    return;
  }
  
  gpsInProgress = true;
  console.log('[GPS] Requesting location permission...');
  
  const gpsCard = document.getElementById('gpsCard');
  if (gpsCard) {
    gpsCard.innerHTML = buildGPSCard('detecting');
  }
  
  if (!navigator.geolocation) {
    console.error('[GPS] Geolocation not supported');
    if (gpsCard) {
      gpsCard.innerHTML = buildGPSCard('error', 'GPS not supported by your browser');
    }
    gpsInProgress = false;
    return;
  }
  
  const options = {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0
  };
  
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      console.log('[GPS] Location detected:', position.coords);
      
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const accuracy = position.coords.accuracy;
      
      if (gpsCard) {
        gpsCard.innerHTML = buildGPSCard('loading', 'Fetching location details...');
      }
      
      try {
        // Check cache first (5 minute cache)
        const cachedGeocode = getCachedGeocode(lat, lon);
        let location;
        
        if (cachedGeocode) {
          console.log('[GPS] Using cached geocode result');
          location = cachedGeocode;
        } else {
          console.log('[GPS] Fetching fresh geocode from API');
          location = await API.reverseGeocode(lat, lon);
          cacheGeocode(lat, lon, location);
        }
        
        console.log('[GPS] Location details:', location);
        
        AppState.gpsLocation = {
          lat: lat,
          lon: lon,
          accuracy: accuracy,
          village: location.village,
          town: location.town,
          city: location.town || location.district,
          district: location.district,
          state: location.state,
          country: location.country,
          timestamp: Date.now()
        };
        
        if (gpsCard) {
          gpsCard.innerHTML = buildGPSCard('success', null, AppState.gpsLocation);
        }
        
        await refreshWeatherWithGPS();
        gpsInProgress = false;
        
      } catch (error) {
        console.error('[GPS] Reverse geocoding failed:', error);
        
        AppState.gpsLocation = {
          lat: lat,
          lon: lon,
          accuracy: accuracy,
          city: 'Your Location',
          state: '',
          timestamp: Date.now()
        };
        
        if (gpsCard) {
          gpsCard.innerHTML = buildGPSCard('success', null, AppState.gpsLocation);
        }
        
        await refreshWeatherWithGPS();
        gpsInProgress = false;
      }
    },
    (error) => {
      console.error('[GPS] Location error:', error);
      
      let errorMessage = 'Location access denied';
      if (error.code === 1) {
        errorMessage = 'Location permission denied. Enable GPS in browser settings.';
      } else if (error.code === 2) {
        errorMessage = 'Location unavailable. Check device settings.';
      } else if (error.code === 3) {
        errorMessage = 'Location request timeout. Try again.';
      }
      
      if (gpsCard) {
        gpsCard.innerHTML = buildGPSCard('error', errorMessage);
      }
      gpsInProgress = false;
    },
    options
  );
}

// ============================================================
// REVERSE GEOCODING CACHE (5 minute TTL)
// ============================================================

const geocodeCache = new Map();
const GEOCODE_CACHE_TTL = 5 * 60 * 1000; // 5 minutes

function getCachedGeocode(lat, lon) {
  const key = `${lat.toFixed(4)},${lon.toFixed(4)}`;
  const cached = geocodeCache.get(key);
  
  if (!cached) return null;
  
  const age = Date.now() - cached.timestamp;
  if (age > GEOCODE_CACHE_TTL) {
    geocodeCache.delete(key);
    return null;
  }
  
  return cached.data;
}

function cacheGeocode(lat, lon, data) {
  const key = `${lat.toFixed(4)},${lon.toFixed(4)}`;
  geocodeCache.set(key, {
    data: data,
    timestamp: Date.now()
  });
  
  // Cleanup old entries
  if (geocodeCache.size > 10) {
    const firstKey = geocodeCache.keys().next().value;
    geocodeCache.delete(firstKey);
  }
}

async function refreshWeatherWithGPS() {
  if (!AppState.gpsLocation) {
    console.warn('[GPS] No GPS location available');
    return;
  }
  
  const el = document.getElementById('weatherBody');
  if (!el) return;
  
  try {
    console.log('[Weather GPS] Fetching for:', AppState.gpsLocation.lat, AppState.gpsLocation.lon);
    
    const crop = AppState.currentCrop;
    const state = AppState.currentState;
    const targetDate = AppState.targetDate || '';
    
    const dashData = await API.getDashboard(crop, state, targetDate);
    
    const weatherData = await API.getWeather(
      null,
      crop,
      dashData?.recommendation?.primary_action,
      dashData?.predicted_price,
      AppState.gpsLocation.lat,
      AppState.gpsLocation.lon
    );

    if (!weatherData || !weatherData.current) {
      throw new Error('Weather data unavailable for GPS location');
    }

    if (AppState.gpsLocation.city) {
      weatherData.location.city = AppState.gpsLocation.city;
      weatherData.location.state = AppState.gpsLocation.state || '';
    }

    AppState.weather = weatherData;
    console.log('[Weather GPS] Weather stored');

    renderWeatherPage(weatherData, dashData);
    
  } catch (error) {
    console.error('[Weather GPS] Error:', error);
    const gpsCard = document.getElementById('gpsCard');
    if (gpsCard) {
      gpsCard.innerHTML = buildGPSCard('error', 'Failed to fetch weather. Using previous data.');
    }
    // Keep existing weather display - don't clear the page
  }
}

function buildGPSCard(status = 'idle', errorMessage = null, location = null) {
  // Don't allow clicks if GPS is in progress
  const clickHandler = status === 'detecting' || status === 'loading' 
    ? '' 
    : 'onclick="detectGPSLocation()"';
  
  if (status === 'idle') {
    return `
      <div class="wx-gps-banner" ${clickHandler}>
        <div class="wx-gps-banner-icon">📍</div>
        <div class="wx-gps-banner-content">
          <div class="wx-gps-banner-title">Use Live GPS Location</div>
          <div class="wx-gps-banner-subtitle">Tap to detect precise weather for your location</div>
        </div>
        <div class="wx-gps-banner-action">
          <span class="wx-gps-banner-btn">Enable GPS</span>
        </div>
      </div>
    `;
  }
  
  if (status === 'detecting') {
    return `
      <div class="wx-gps-banner wx-gps-banner-loading">
        <div class="wx-gps-banner-icon wx-gps-pulse">📡</div>
        <div class="wx-gps-banner-content">
          <div class="wx-gps-banner-title">Detecting Your Location</div>
          <div class="wx-gps-banner-subtitle">Getting GPS coordinates from your device...</div>
        </div>
      </div>
    `;
  }
  
  if (status === 'loading') {
    return `
      <div class="wx-gps-banner wx-gps-banner-loading">
        <div class="wx-gps-banner-icon wx-gps-pulse">🌐</div>
        <div class="wx-gps-banner-content">
          <div class="wx-gps-banner-title">Loading Weather Data</div>
          <div class="wx-gps-banner-subtitle">${errorMessage || 'Fetching live weather for your location...'}</div>
        </div>
      </div>
    `;
  }
  
  if (status === 'error') {
    return `
      <div class="wx-gps-banner wx-gps-banner-error" ${clickHandler}>
        <div class="wx-gps-banner-icon">⚠️</div>
        <div class="wx-gps-banner-content">
          <div class="wx-gps-banner-title">GPS Unavailable</div>
          <div class="wx-gps-banner-subtitle">${errorMessage}</div>
        </div>
        <div class="wx-gps-banner-action">
          <span class="wx-gps-banner-btn">Retry</span>
        </div>
      </div>
    `;
  }
  
  if (status === 'success' && location) {
    const cityDisplay = location.city || location.town || location.district || 'Your Location';
    const stateDisplay = location.state || '';
    const latDisplay = Math.abs(location.lat).toFixed(4);
    const lonDisplay = Math.abs(location.lon).toFixed(4);
    const latDir = location.lat >= 0 ? 'N' : 'S';
    const lonDir = location.lon >= 0 ? 'E' : 'W';
    
    const timeAgo = location.timestamp ? getTimeAgo(location.timestamp) : 'Just now';
    
    return `
      <div class="wx-gps-banner wx-gps-banner-active">
        <div class="wx-gps-banner-live">
          <span class="wx-gps-live-dot"></span>
          <span class="wx-gps-live-text">Live</span>
        </div>
        <div class="wx-gps-banner-content">
          <div class="wx-gps-banner-title">📍 ${cityDisplay}${stateDisplay ? ', ' + stateDisplay : ''}</div>
          <div class="wx-gps-banner-meta">
            <span>GPS Accuracy: ±${Math.round(location.accuracy || 0)}m</span>
            <span class="wx-gps-separator">•</span>
            <span>${latDisplay}° ${latDir}, ${lonDisplay}° ${lonDir}</span>
            <span class="wx-gps-separator">•</span>
            <span>Updated: ${timeAgo}</span>
          </div>
        </div>
        <div class="wx-gps-banner-action" onclick="event.stopPropagation(); detectGPSLocation();">
          <span class="wx-gps-banner-refresh" title="Refresh location">🔄</span>
        </div>
      </div>
    `;
  }
  
  return buildGPSCard('idle');
}

function getTimeAgo(timestamp) {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);
  if (seconds < 60) return 'Just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  return 'Earlier today';
}

// ============================================================
// WEATHER PAGE LOADER
// ============================================================

async function loadWeatherPage(crop, state) {
  const el = document.getElementById('weatherBody');
  if (!el) return;

  try {
    console.log('[Weather] Loading page for', crop, state);
    
    // Fetch dashboard data for context
    const targetDate = AppState.targetDate || '';
    const dashData = await API.getDashboard(crop, state, targetDate);
    
    console.log('[Weather] Dashboard data received');
    
    // Check if we have cached complete weather
    if (AppState.weather && AppState.weather.current) {
      console.log('[Weather] Using cached weather from AppState');
      renderWeatherPage(AppState.weather, dashData);
      return;
    }
    
    // Fetch complete weather from backend
    console.log('[Weather] Fetching complete weather from /api/weather');
    const weatherData = await API.getWeather(
      state,
      crop,
      dashData.recommendation?.primary_action,
      dashData.predicted_price
    );

    if (!weatherData || !weatherData.current) {
      throw new Error('Weather data unavailable');
    }

    // Store in AppState for reuse
    AppState.weather = weatherData;
    console.log('[Weather] Weather stored in AppState:', weatherData);

    // Render
    renderWeatherPage(weatherData, dashData);
    
  } catch (error) {
    console.error('[Weather] Error:', error);
    el.innerHTML = `
      <div class="weather-error">
        <div class="weather-error-icon">🌤️</div>
        <h3>Weather data currently unavailable</h3>
        <p>Please check your connection and try again.</p>
        <button onclick="loadWeatherPage('${crop}', '${state}')" class="btn btn-primary">
          Retry
        </button>
      </div>
    `;
  }
}

// ============================================================
// WEATHER PAGE RENDERER
// ============================================================

function renderWeatherPage(weather, dashData) {
  const el = document.getElementById('weatherBody');
  if (!el) return;

  console.log('[Weather] Rendering with data:', weather);

  const current = weather.current || {};
  const hourly = weather.hourly || [];
  const daily = weather.daily || [];
  const today = weather.today || {};
  const location = weather.location || { city: 'Unknown', state: '' };
  const agriculture = weather.agriculture || {};

  el.innerHTML = `
    <div class="weather-intelligence">
      <!-- GPS Status Banner -->
      <div id="gpsCard" class="wx-gps-banner-wrapper">
        ${AppState.gpsLocation ? buildGPSCard('success', null, AppState.gpsLocation) : buildGPSCard('idle')}
      </div>
      
      <!-- Hero Weather Card -->
      ${buildWeatherHero(current, location, today)}
      
      <!-- Current Weather Highlights -->
      ${buildWeatherHighlights(current, today)}
      
      <!-- Agricultural Conditions -->
      ${buildAgriculturalConditions(agriculture)}
      
      <!-- 24 Hour Forecast -->
      ${buildHourlyForecast(hourly)}
      
      <!-- 7 Day Forecast -->
      ${buildDailyForecast(daily)}
      
      <!-- AI Weather Advisory -->
      ${buildWeatherAdvisory(weather, dashData)}
      
      <!-- Farming Tips -->
      ${buildFarmingTips(current, today, hourly)}
    </div>
  `;
}

// ============================================================
// COMPONENT BUILDERS
// ============================================================

function buildWeatherHero(current, location, today) {
  const temp = current.temperature != null ? Math.round(current.temperature) : '--';
  const feels = current.feels_like != null ? Math.round(current.feels_like) : '--';
  const icon = current.weather_icon || '🌤️';
  const condition = current.weather_description || 'Unknown';
  const humidity = current.humidity != null ? current.humidity : '--';
  const wind = current.wind_speed != null ? current.wind_speed : '--';
  const rainProb = today.precipitation_probability != null ? today.precipitation_probability : 0;
  
  const locationStr = typeof location === 'string' 
    ? location 
    : `${location.city || 'Unknown'}, ${location.state || ''}`;
  
  const gpsActive = AppState.gpsLocation != null;
  const gpsAccuracy = gpsActive ? Math.round(AppState.gpsLocation.accuracy) : null;
  
  return `
    <div class="wx-hero">
      <div class="wx-hero-main">
        <div class="wx-hero-icon-large">${icon}</div>
        <div class="wx-hero-temp-large">
          <div class="wx-hero-temp-value" data-temp="${temp}">${temp}°</div>
          <div class="wx-hero-condition">${condition}</div>
        </div>
      </div>
      
      <div class="wx-hero-location-info">
        <div class="wx-hero-location">
          <span class="wx-location-icon">📍</span>
          <span>${locationStr}</span>
        </div>
        ${gpsActive ? `
          <div class="wx-hero-gps-badge">
            <span class="wx-gps-badge-dot"></span>
            <span>GPS Active${gpsAccuracy ? ` • ±${gpsAccuracy}m` : ''}</span>
          </div>
        ` : ''}
        <div class="wx-hero-updated">Updated just now</div>
      </div>
      
      <div class="wx-hero-chips">
        <div class="wx-chip">
          <span class="wx-chip-icon">🌡️</span>
          <span class="wx-chip-label">Feels like</span>
          <span class="wx-chip-value">${feels}°C</span>
        </div>
        <div class="wx-chip">
          <span class="wx-chip-icon">💧</span>
          <span class="wx-chip-label">Humidity</span>
          <span class="wx-chip-value">${humidity}%</span>
        </div>
        <div class="wx-chip">
          <span class="wx-chip-icon">💨</span>
          <span class="wx-chip-label">Wind</span>
          <span class="wx-chip-value">${wind} km/h</span>
        </div>
        <div class="wx-chip ${rainProb > 50 ? 'wx-chip-warning' : ''}">
          <span class="wx-chip-icon">🌧️</span>
          <span class="wx-chip-label">Rain</span>
          <span class="wx-chip-value">${rainProb}%</span>
        </div>
      </div>
    </div>
  `;
}

function buildWeatherHighlights(current, today) {
  const highlights = [
    { 
      icon: '🌡️', 
      label: 'Temperature', 
      value: current.temperature, 
      unit: '°C',
      context: getTemperatureContext(current.temperature)
    },
    { 
      icon: '💧', 
      label: 'Humidity', 
      value: current.humidity, 
      unit: '%',
      context: getHumidityContext(current.humidity)
    },
    { 
      icon: '💨', 
      label: 'Wind Speed', 
      value: current.wind_speed, 
      unit: ' km/h',
      context: getWindContext(current.wind_speed)
    },
    { 
      icon: '🧭', 
      label: 'Wind Direction', 
      value: current.wind_direction, 
      unit: '°',
      context: null
    },
    { 
      icon: '📊', 
      label: 'Pressure', 
      value: current.pressure, 
      unit: ' hPa',
      context: null
    },
    { 
      icon: '☁️', 
      label: 'Cloud Cover', 
      value: current.cloud_cover, 
      unit: '%',
      context: null
    },
    { 
      icon: '🌧️', 
      label: 'Rain Probability', 
      value: today.precipitation_probability, 
      unit: '%',
      context: getRainContext(today.precipitation_probability)
    },
    { 
      icon: '☀️', 
      label: 'UV Index', 
      value: current.uv_index, 
      unit: '/11',
      context: getUVContext(current.uv_index)
    },
    { 
      icon: '🌅', 
      label: 'Sunrise', 
      value: today.sunrise, 
      unit: '',
      context: null
    },
    { 
      icon: '🌆', 
      label: 'Sunset', 
      value: today.sunset, 
      unit: '',
      context: null
    }
  ];

  const cards = highlights.map(h => {
    if (h.value == null) return '';
    const displayValue = typeof h.value === 'number' ? h.value : h.value;
    return `
      <div class="wx-highlight-card">
        <div class="wx-highlight-icon">${h.icon}</div>
        <div class="wx-highlight-content">
          <div class="wx-highlight-label">${h.label}</div>
          <div class="wx-highlight-value">${displayValue}${h.unit}</div>
          ${h.context ? `<div class="wx-highlight-context">${h.context}</div>` : ''}
        </div>
      </div>
    `;
  }).filter(Boolean).join('');

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">Current Conditions</h2>
      <div class="wx-highlights-grid">${cards}</div>
    </div>
  `;
}

function getTemperatureContext(temp) {
  if (temp == null) return null;
  if (temp > 40) return 'Extreme heat. Avoid spraying. Ensure shade for livestock.';
  if (temp > 35) return 'Hot day. Good for drying crops. Irrigate early morning.';
  if (temp > 30) return 'Warm conditions. Monitor crop water stress.';
  if (temp < 15) return 'Cool weather. Risk of cold stress for sensitive crops.';
  if (temp < 10) return 'Cold conditions. Protect young plants from frost.';
  return 'Comfortable temperature for most field activities.';
}

function getHumidityContext(humidity) {
  if (humidity == null) return null;
  if (humidity > 85) return 'High humidity increases fungal disease risk.';
  if (humidity > 70) return 'Moderate humidity. Monitor for disease symptoms.';
  if (humidity < 40) return 'Low humidity. Increase irrigation frequency.';
  return 'Optimal humidity for most crops.';
}

function getWindContext(wind) {
  if (wind == null) return null;
  if (wind > 30) return 'Strong winds. Avoid spraying. Secure loose structures.';
  if (wind > 20) return 'Moderate winds. Spraying not recommended.';
  if (wind > 10) return 'Light winds. Good for drying and air circulation.';
  return 'Calm conditions. Ideal for spraying operations.';
}

function getRainContext(rainProb) {
  if (rainProb == null) return null;
  if (rainProb > 70) return 'High rain probability. Delay spraying and harvesting.';
  if (rainProb > 40) return 'Possible rain. Plan field work accordingly.';
  if (rainProb > 20) return 'Low rain chance. Safe for most field activities.';
  return 'No rain expected. Good for harvesting and spraying.';
}

function getUVContext(uv) {
  if (uv == null) return null;
  if (uv > 10) return 'Extreme UV. Protect skin during outdoor work.';
  if (uv > 7) return 'High UV. Use sun protection for extended field work.';
  if (uv > 5) return 'Moderate UV. Take breaks in shade during peak hours.';
  return 'Low UV. Safe for extended outdoor activities.';
}

function buildAgriculturalConditions(agriculture) {
  const conditions = [];
  
  if (agriculture.soil_temperature != null) {
    const soilTemp = agriculture.soil_temperature;
    let status = 'optimal';
    let statusText = 'Optimal';
    let context = 'Good for seed germination.';
    
    if (soilTemp < 10) {
      status = 'low';
      statusText = 'Too Cold';
      context = 'Seed germination may be delayed.';
    } else if (soilTemp > 35) {
      status = 'high';
      statusText = 'Too Hot';
      context = 'Risk of root stress. Increase irrigation.';
    }
    
    conditions.push({ 
      icon: '🌡️', 
      label: 'Soil Temperature', 
      value: `${soilTemp.toFixed(1)}°C`,
      status,
      statusText,
      context
    });
  }
  
  if (agriculture.soil_moisture != null) {
    const sm = agriculture.soil_moisture;
    let status = 'optimal';
    let statusText = 'Optimal';
    let context = 'Good soil moisture for most crops.';
    
    if (sm < 0.15) {
      status = 'low';
      statusText = 'Dry';
      context = 'Irrigation required soon.';
    } else if (sm > 0.35) {
      status = 'high';
      statusText = 'Wet';
      context = 'Risk of waterlogging. Improve drainage.';
    }
    
    conditions.push({ 
      icon: '💧', 
      label: 'Soil Moisture', 
      value: (sm * 100).toFixed(1) + '%',
      status,
      statusText,
      context
    });
  }
  
  if (agriculture.evapotranspiration != null) {
    const et = agriculture.evapotranspiration;
    let context = 'Normal water loss from soil and plants.';
    
    if (et > 6) {
      context = 'High water loss. Monitor irrigation closely.';
    } else if (et < 2) {
      context = 'Low evaporation. Reduce irrigation frequency.';
    }
    
    conditions.push({ 
      icon: '💨', 
      label: 'Evapotranspiration', 
      value: `${et.toFixed(2)} mm`,
      status: 'neutral',
      statusText: null,
      context
    });
  }
  
  if (agriculture.vapour_pressure_deficit != null) {
    const vpd = agriculture.vapour_pressure_deficit;
    let status = 'optimal';
    let statusText = 'Optimal';
    let context = 'Good conditions for plant growth.';
    
    if (vpd > 2.5) {
      status = 'high';
      statusText = 'High Stress';
      context = 'Plants losing water rapidly. Increase humidity.';
    } else if (vpd < 0.5) {
      status = 'low';
      statusText = 'Low Stress';
      context = 'Slow transpiration. Risk of disease.';
    }
    
    conditions.push({ 
      icon: '🌿', 
      label: 'VPD', 
      value: `${vpd.toFixed(2)} kPa`,
      status,
      statusText,
      context
    });
  }

  if (conditions.length === 0) return '';

  const cards = conditions.map(c => `
    <div class="wx-agri-card">
      <div class="wx-agri-header">
        <div class="wx-agri-icon">${c.icon}</div>
        ${c.statusText ? `<span class="wx-agri-badge wx-agri-badge-${c.status}">${c.statusText}</span>` : ''}
      </div>
      <div class="wx-agri-content">
        <div class="wx-agri-label">${c.label}</div>
        <div class="wx-agri-value">${c.value}</div>
        <div class="wx-agri-context">${c.context}</div>
      </div>
    </div>
  `).join('');

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">Agricultural Metrics</h2>
      <div class="wx-agri-grid">${cards}</div>
    </div>
  `;
}

function buildHourlyForecast(hourly) {
  if (!hourly || hourly.length === 0) return '';

  const hours = Math.min(24, hourly.length);
  const cards = [];
  
  for (let i = 0; i < hours; i++) {
    const h = hourly[i];
    const time = i === 0 ? 'Now' : h.time || '--';
    const temp = h.temperature != null ? h.temperature : '--';
    const rain = h.precipitation_probability != null ? h.precipitation_probability : 0;
    const icon = h.weather_icon || '🌤️';
    
    cards.push(`
      <div class="wx-hourly-card ${i === 0 ? 'wx-hourly-now' : ''}">
        <div class="wx-hourly-time">${time}</div>
        <div class="wx-hourly-icon">${icon}</div>
        <div class="wx-hourly-temp">${temp}°</div>
        <div class="wx-hourly-rain">💧 ${rain}%</div>
      </div>
    `);
  }

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">24 Hour Forecast</h2>
      <div class="wx-hourly-scroll">${cards.join('')}</div>
    </div>
  `;
}

function buildDailyForecast(daily) {
  if (!daily || daily.length === 0) return '';

  const days = Math.min(7, daily.length);
  const rows = [];
  
  for (let i = 0; i < days; i++) {
    const d = daily[i];
    const day = i === 0 ? 'Today' : d.day_name || 'Day';
    const icon = d.weather_icon || '🌤️';
    const maxTemp = d.temp_max != null ? d.temp_max : '--';
    const minTemp = d.temp_min != null ? d.temp_min : '--';
    const rain = d.precipitation_probability != null ? d.precipitation_probability : 0;
    const wind = d.wind_speed != null ? d.wind_speed : 0;
    
    rows.push(`
      <div class="wx-daily-row">
        <div class="wx-daily-day">${day}</div>
        <div class="wx-daily-icon">${icon}</div>
        <div class="wx-daily-temps">
          <span class="wx-daily-max">${maxTemp}°</span>
          <span class="wx-daily-min">${minTemp}°</span>
        </div>
        <div class="wx-daily-rain">💧 ${rain}%</div>
      </div>
    `);
  }

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">7 Day Forecast</h2>
      <div class="wx-daily-forecast">${rows.join('')}</div>
    </div>
  `;
}

function buildWeatherAdvisory(weather, dashData) {
  const advisory = weather.advisory || generateSimpleAdvisory(weather, dashData);

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">AI Weather Advisory</h2>
      <div class="wx-advisory">${advisory}</div>
    </div>
  `;
}

function generateSimpleAdvisory(weather, dashData) {
  const c = weather.current || {};
  const t = weather.today || {};
  const temp = c.temperature || 0;
  const rain = t.precipitation_probability || 0;
  const humidity = c.humidity || 0;
  
  let summary = 'Weather conditions monitored.';
  let impact = 'Normal farming operations.';
  let recommendation = 'Continue as planned.';
  let risks = 'No major risks.';
  let action = 'Monitor forecasts daily.';
  
  if (rain > 70) {
    summary = 'Heavy rain expected.';
    impact = 'Field work may be affected.';
    recommendation = 'Delay spraying and harvesting.';
    risks = 'Waterlogging possible.';
    action = 'Secure equipment and crops.';
  } else if (temp > 35) {
    summary = 'Hot weather conditions.';
    impact = 'Heat stress on crops.';
    recommendation = 'Increase irrigation.';
    risks = 'Reduced yields possible.';
    action = 'Monitor soil moisture closely.';
  } else if (humidity > 85 && temp > 20) {
    summary = 'High humidity conditions.';
    impact = 'Fungal disease risk elevated.';
    recommendation = 'Monitor crops for disease.';
    risks = 'Fungal infections likely.';
    action = 'Apply preventive treatments.';
  }
  
  return `
    <div class="wx-adv-section"><strong>Summary:</strong> ${summary}</div>
    <div class="wx-adv-section"><strong>Impact:</strong> ${impact}</div>
    <div class="wx-adv-section"><strong>Recommendation:</strong> ${recommendation}</div>
    <div class="wx-adv-section"><strong>Risks:</strong> ${risks}</div>
    <div class="wx-adv-section"><strong>Action:</strong> ${action}</div>
  `;
}

function buildFarmingTips(current, today, hourly) {
  const temp = current.temperature || 0;
  const rain = today.precipitation_probability || 0;
  const humidity = current.humidity || 0;
  const wind = current.wind_speed || 0;
  
  const tips = [];
  
  if (rain > 60) {
    tips.push({ icon: '☂️', text: 'Carry rain protection' });
    tips.push({ icon: '🚜', text: 'Avoid field operations' });
  } else if (rain > 30) {
    tips.push({ icon: '⚠️', text: 'Monitor rain forecasts' });
  }
  
  if (wind > 20 || rain > 40) {
    tips.push({ icon: '🚫', text: 'Delay spraying operations' });
  }
  
  if (temp > 35) {
    tips.push({ icon: '💧', text: 'Increase irrigation' });
    tips.push({ icon: '🐄', text: 'Provide shade for livestock' });
  }
  
  if (humidity > 80 && temp > 20 && temp < 35) {
    tips.push({ icon: '🍄', text: 'Monitor for fungal disease' });
  }
  
  if (rain < 20 && temp < 32 && wind < 15) {
    tips.push({ icon: '✅', text: 'Good conditions for harvest' });
    tips.push({ icon: '🌾', text: 'Ideal for spraying' });
  }
  
  // Check for evening rain
  if (hourly && hourly.time && hourly.time.length > 12) {
    const eveningHours = hourly.precipitation_probability ? hourly.precipitation_probability.slice(12, 18) : [];
    const eveningRain = eveningHours.length > 0 ? Math.max(...eveningHours) : 0;
    if (eveningRain > 50) {
      tips.push({ icon: '⏰', text: 'Harvest before evening' });
    }
  }
  
  if (tips.length === 0) {
    tips.push({ icon: '🌤️', text: 'Favorable weather conditions' });
    tips.push({ icon: '📋', text: 'Plan regular farm activities' });
  }

  const tipCards = tips.map(tip => `
    <div class="wx-tip-card">
      <span class="wx-tip-icon">${tip.icon}</span>
      <span class="wx-tip-text">${tip.text}</span>
    </div>
  `).join('');

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">Farming Tips</h2>
      <div class="wx-tips-grid">${tipCards}</div>
    </div>
  `;
}

// ============================================================
