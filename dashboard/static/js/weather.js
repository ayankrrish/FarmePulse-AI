/**
 * FarmPulse Weather Intelligence Module
 * Independent page for agricultural weather insights
 */

// ============================================================
// WEATHER PAGE LOADER
// ============================================================

async function loadWeatherPage(crop, state) {
  const el = document.getElementById('weatherBody');
  if (!el) return;

  try {
    // Fetch dashboard data for context
    const targetDate = AppState.targetDate || '';
    const dashData = await API.getDashboard(crop, state, targetDate);
    
    // Fetch weather (reuses cache if available)
    const weatherData = await fetchWeather(
      state,
      crop,
      dashData.recommendation?.primary_action,
      dashData.predicted_price
    );

    if (!weatherData || !weatherData._full) {
      throw new Error('Weather data unavailable');
    }

    // Render weather page
    renderWeatherPage(weatherData._full, dashData);
    
  } catch (error) {
    console.error('[Weather Page] Error:', error);
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

  const c = weather.current || {};
  const t = weather.today || {};
  const h = weather.hourly || {};
  const d = weather.daily || {};
  const loc = weather.location || 'Unknown Location';

  el.innerHTML = `
    <div class="weather-intelligence">
      <!-- Hero Weather Card -->
      ${buildWeatherHero(c, loc, t)}
      
      <!-- Current Weather Highlights -->
      ${buildWeatherHighlights(c, t)}
      
      <!-- Agricultural Conditions -->
      ${buildAgriculturalConditions(c)}
      
      <!-- 24 Hour Forecast -->
      ${buildHourlyForecast(h)}
      
      <!-- 7 Day Forecast -->
      ${buildDailyForecast(d)}
      
      <!-- AI Weather Advisory -->
      ${buildWeatherAdvisory(weather, dashData)}
      
      <!-- Farming Tips -->
      ${buildFarmingTips(c, t, h)}
    </div>
  `;
}

// ============================================================
// COMPONENT BUILDERS
// ============================================================

function buildWeatherHero(current, location, today) {
  const temp = current.temperature != null ? current.temperature : '--';
  const feels = current.feels_like != null ? current.feels_like : '--';
  const icon = current.weather_icon || '🌤️';
  const condition = current.weather_description || 'Unknown';
  
  return `
    <div class="wx-hero">
      <div class="wx-hero-main">
        <div class="wx-hero-icon">${icon}</div>
        <div class="wx-hero-temp">
          <div class="wx-hero-temp-value">${temp}°C</div>
          <div class="wx-hero-feels">Feels like ${feels}°C</div>
        </div>
      </div>
      <div class="wx-hero-details">
        <div class="wx-hero-condition">${condition}</div>
        <div class="wx-hero-location">📍 ${location}</div>
        <div class="wx-hero-updated">Updated just now</div>
      </div>
    </div>
  `;
}

function buildWeatherHighlights(current, today) {
  const highlights = [
    { icon: '🌡️', label: 'Temperature', value: current.temperature, unit: '°C' },
    { icon: '💧', label: 'Humidity', value: current.humidity, unit: '%' },
    { icon: '💨', label: 'Wind Speed', value: current.wind_speed, unit: ' km/h' },
    { icon: '🧭', label: 'Wind Direction', value: current.wind_direction, unit: '°' },
    { icon: '📊', label: 'Pressure', value: current.pressure, unit: ' hPa' },
    { icon: '👁️', label: 'Visibility', value: current.visibility ? (current.visibility/1000).toFixed(1) : null, unit: ' km' },
    { icon: '☁️', label: 'Cloud Cover', value: current.cloud_cover, unit: '%' },
    { icon: '🌧️', label: 'Rain Probability', value: today.precipitation_probability, unit: '%' },
    { icon: '☀️', label: 'UV Index', value: today.uv_index, unit: '/11' },
    { icon: '🌅', label: 'Sunrise', value: formatTime(today.sunrise), unit: '' },
    { icon: '🌆', label: 'Sunset', value: formatTime(today.sunset), unit: '' }
  ];

  const cards = highlights.map(h => `
    <div class="wx-highlight-card">
      <div class="wx-hl-icon">${h.icon}</div>
      <div class="wx-hl-label">${h.label}</div>
      <div class="wx-hl-value">${h.value != null ? h.value : '--'}${h.unit}</div>
    </div>
  `).join('');

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">Current Weather Highlights</h2>
      <div class="wx-highlights-grid">${cards}</div>
    </div>
  `;
}

function buildAgriculturalConditions(current) {
  const conditions = [];
  
  if (current.soil_temp != null) {
    conditions.push({ icon: '🌡️', label: 'Soil Temperature', value: `${current.soil_temp.toFixed(1)}°C` });
  }
  
  if (current.soil_moisture != null) {
    const sm = current.soil_moisture;
    const status = sm < 0.15 ? 'Dry' : sm > 0.35 ? 'Wet' : 'Optimal';
    conditions.push({ icon: '💧', label: 'Soil Moisture', value: sm.toFixed(3), status });
  }
  
  if (current.evapotranspiration != null) {
    conditions.push({ icon: '💨', label: 'Evapotranspiration', value: `${current.evapotranspiration.toFixed(2)} mm` });
  }
  
  if (current.vpd != null) {
    const vpd = current.vpd;
    const status = vpd > 2.5 ? 'High Stress' : vpd < 0.5 ? 'Low Stress' : 'Optimal';
    conditions.push({ icon: '🌿', label: 'VPD', value: `${vpd.toFixed(2)} kPa`, status });
  }

  if (conditions.length === 0) return '';

  const cards = conditions.map(c => `
    <div class="wx-agri-card">
      <div class="wx-agri-icon">${c.icon}</div>
      <div class="wx-agri-content">
        <div class="wx-agri-label">${c.label}</div>
        <div class="wx-agri-value">${c.value}</div>
        ${c.status ? `<div class="wx-agri-status">${c.status}</div>` : ''}
      </div>
    </div>
  `).join('');

  return `
    <div class="wx-section">
      <h2 class="wx-section-title">Agricultural Conditions</h2>
      <div class="wx-agri-grid">${cards}</div>
    </div>
  `;
}

function buildHourlyForecast(hourly) {
  if (!hourly || !hourly.time || hourly.time.length === 0) return '';

  const hours = Math.min(24, hourly.time.length);
  const cards = [];
  
  for (let i = 0; i < hours; i++) {
    const time = i === 0 ? 'Now' : formatTime(hourly.time[i]);
    const temp = hourly.temperature && hourly.temperature[i] != null ? hourly.temperature[i] : '--';
    const rain = hourly.precipitation_probability && hourly.precipitation_probability[i] != null ? hourly.precipitation_probability[i] : 0;
    const code = hourly.weather_code && hourly.weather_code[i] != null ? hourly.weather_code[i] : 0;
    const icon = getWeatherIcon(code);
    
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
  if (!daily || !daily.time || daily.time.length === 0) return '';

  const days = Math.min(7, daily.time.length);
  const rows = [];
  
  for (let i = 0; i < days; i++) {
    const day = i === 0 ? 'Today' : formatDayName(daily.time[i]);
    const code = daily.weather_code && daily.weather_code[i] != null ? daily.weather_code[i] : 0;
    const icon = getWeatherIcon(code);
    const maxTemp = daily.temperature_max && daily.temperature_max[i] != null ? daily.temperature_max[i] : '--';
    const minTemp = daily.temperature_min && daily.temperature_min[i] != null ? daily.temperature_min[i] : '--';
    const rain = daily.precipitation_probability && daily.precipitation_probability[i] != null ? daily.precipitation_probability[i] : 0;
    
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
// HELPER FUNCTIONS
// ============================================================

function getWeatherIcon(code) {
  if (code === 0) return '☀️';
  if (code <= 3) return '⛅';
  if (code <= 48) return '🌫️';
  if (code <= 67) return '🌧️';
  if (code <= 82) return '🌧️';
  return '⛈️';
}

function formatTime(isoString) {
  if (!isoString || typeof isoString !== 'string' || !isoString.includes('T')) return 'N/A';
  try {
    return isoString.split('T')[1].substring(0, 5);
  } catch (e) {
    return 'N/A';
  }
}

function formatDayName(dateString) {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[date.getDay()];
  } catch (e) {
    return '';
  }
}
