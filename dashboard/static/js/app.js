/**
 * FarmPulse AI — Application v3.0
 * Farmer-friendly agricultural intelligence.
 * No ML jargon. No dark mode. Clean and simple.
 */

// ============================================================
// State
// ============================================================
const AppState = {
  config: {},
  currentCrop: null,
  currentState: null,
  currentPage: 'dashboard',
  dashboardData: null,
  chatMessages: [],
  mode: localStorage.getItem('farmpulse-mode') || 'farmer',
  presentationMode: false,
  analyticsData: null,
  targetDate: null,  // ADDED: Centralized forecast month state
};

// ============================================================
// State Management
// ============================================================
function saveStateToStorage() {
  try {
    localStorage.setItem('farmpulse-crop', AppState.currentCrop || '');
    localStorage.setItem('farmpulse-state', AppState.currentState || '');
    localStorage.setItem('farmpulse-targetDate', AppState.targetDate || '');
  } catch (e) {
    console.warn('Failed to save state:', e);
  }
}

function loadStateFromStorage() {
  try {
    const savedCrop = localStorage.getItem('farmpulse-crop');
    const savedState = localStorage.getItem('farmpulse-state');
    const savedDate = localStorage.getItem('farmpulse-targetDate');
    
    if (savedCrop) AppState.currentCrop = savedCrop;
    if (savedState) AppState.currentState = savedState;
    if (savedDate) AppState.targetDate = savedDate;
  } catch (e) {
    console.warn('Failed to load state:', e);
  }
}

// ============================================================
// API
// ============================================================
const API = {
  async get(endpoint, params = {}) {
    const url = new URL(endpoint, window.location.origin);
    Object.entries(params).forEach(([k, v]) => {
      if (v != null && v !== '') url.searchParams.set(k, v);
    });
    const res = await fetch(url);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    return data;
  },
  getConfig: () => API.get('/api/config'),
  getDashboard: (c, s, d) => API.get('/api/dashboard_summary', { crop: c, state: s, target_date: d }),
  getEnsemble: (c, s, d) => API.get('/api/ensemble_predict', { crop: c, state: s, target_date: d }),
  getRecommendation: (c, s) => API.get('/api/recommendation', { crop: c, state: s }),
  getMspAlert: (c, s) => API.get('/api/msp_alert', { crop: c, state: s }),
  getMarketComparison: (c) => API.get('/api/market_comparison', { crop: c }),
  getProfitEstimate: (c, s, q, cost) => API.get('/api/profit_estimate', { crop: c, state: s, quantity: q, cost }),
  getModelMetrics: () => API.get('/api/model_metrics'),
  getAnalyticsMetadata: (c) => API.get('/api/analytics_metadata', { crop: c }),
};

// ============================================================
// Navigation
// ============================================================
const PAGE_META = {
  dashboard: ['Dashboard', 'AI-powered price intelligence for Indian farmers'],
  forecast: ['Price Forecast', 'Should you sell today or wait?'],
  profit: ['Profit Estimator', 'Calculate your revenue and best selling strategy'],
  alerts: ['MSP Alerts', 'Minimum Support Price safety checks'],
  comparison: ['Market Comparison', 'Find the best mandi for your crop'],
  assistant: ['AI Assistant', 'Ask anything about prices, markets, and selling'],
  weather: ['Weather Intelligence', 'Agricultural weather insights and forecasts'],
  analytics: ['Model Analytics', 'Transparent view of the live prediction pipeline'],
  about: ['About FarmPulse AI', 'Project scope, architecture, and technology stack'],
};

function navigateTo(page) {
  AppState.currentPage = page;
  document.querySelectorAll('.nav-item').forEach(el =>
    el.classList.toggle('active', el.dataset.page === page));
  document.querySelectorAll('.page-section').forEach(el =>
    el.classList.toggle('active', el.id === `page-${page}`));
  const [title, sub] = PAGE_META[page] || ['', ''];
  const t = document.getElementById('pageTitle');
  const s = document.getElementById('pageSubtitle');
  if (t) t.textContent = title;
  if (s) s.textContent = sub;
  loadPage(page);
  closeMobile();
}

function closeMobile() {
  document.querySelector('.sidebar')?.classList.remove('open');
  document.querySelector('.sidebar-overlay')?.classList.remove('active');
}

// ============================================================
// Page Loader
// ============================================================
async function loadPage(page) {
  const crop = AppState.currentCrop;
  const state = AppState.currentState;
  if (!crop || !state) return;
  try {
    switch (page) {
      case 'dashboard': await loadDashboard(crop, state); break;
      case 'forecast': await loadForecast(crop, state); break;
      case 'profit': await loadProfit(crop, state); break;
      case 'alerts': await loadAlerts(crop, state); break;
      case 'comparison': await loadComparison(crop); break;
      case 'assistant': renderAssistant(); break;
      case 'weather': await loadWeatherPage(crop, state); break;
      case 'analytics': await loadAnalytics(crop, state); break;
      case 'about': renderAbout(); break;
    }
  } catch (err) {
    console.error('Page error:', err);
  }
}

// ============================================================
// Weather Helpers (for Dashboard integration)
// ============================================================
const STATE_COORDS = {
  'Gujarat': { lat: 23.0, lon: 72.6, city: 'Ahmedabad' },
  'Maharashtra': { lat: 19.1, lon: 72.9, city: 'Mumbai' },
  'Rajasthan': { lat: 26.9, lon: 75.8, city: 'Jaipur' },
  'Madhya Pradesh': { lat: 23.3, lon: 77.4, city: 'Bhopal' },
  'Karnataka': { lat: 12.97, lon: 77.6, city: 'Bangalore' },
  'Andhra Pradesh': { lat: 17.4, lon: 78.5, city: 'Hyderabad' },
  'Telangana': { lat: 17.4, lon: 78.5, city: 'Hyderabad' },
  'Uttar Pradesh': { lat: 26.85, lon: 80.95, city: 'Lucknow' },
};

function weatherIcon(code) {
  if (code <= 1) return '☀️';
  if (code <= 3) return '⛅';
  if (code <= 48) return '🌫️';
  if (code <= 67) return '🌧️';
  if (code <= 82) return '🌧️';
  return '⛈️';
}

function weatherAdvice(rainProb, temp) {
  if (rainProb > 70) return '🌧️ Heavy rain expected. Avoid outdoor storage. Mandi arrivals may drop — prices could rise.';
  if (rainProb > 40) return '🌦️ Moderate rain possible. Plan harvest timing carefully.';
  if (temp > 40) return '🌡️ Extreme heat. Ensure proper storage. Transport during cooler hours.';
  if (temp > 35) return '☀️ Hot day. Good for drying harvested crop.';
  return '☀️ Good weather for harvesting and transport to mandi.';
}

async function fetchWeather(state) {
  const c = STATE_COORDS[state] || { lat: 20.6, lon: 79.0, city: state };
  try {
    const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${c.lat}&longitude=${c.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=precipitation_probability_max&timezone=Asia/Kolkata&forecast_days=1`);
    const w = await res.json();
    return {
      temp: Math.round(w.current.temperature_2m),
      humidity: w.current.relative_humidity_2m,
      wind: Math.round(w.current.wind_speed_10m),
      icon: weatherIcon(w.current.weather_code),
      rainProb: w.daily?.precipitation_probability_max?.[0] || 0,
      city: c.city,
    };
  } catch (e) {
    return null;
  }
}

// ============================================================
// DASHBOARD
// ============================================================
async function loadDashboard(crop, state) {
  // Use centralized state for target_date (same as forecast)
  const targetDate = AppState.targetDate || '';
  const [data, weather] = await Promise.all([
    API.getDashboard(crop, state, targetDate),
    fetchWeather(state),
  ]);
  AppState.dashboardData = data;
  renderDashboard(data, weather);
}

function renderDashboard(d, w) {
  const el = document.getElementById('dashboardBody');
  if (!el) return;

  const chg = d.change_pct >= 0 ? 'positive' : 'negative';
  const sign = d.change_pct >= 0 ? '+' : '';
  const alertLvl = d.msp_alert.alert_level;

  // Hero color
  const act = (d.recommendation.primary_action || '').toLowerCase();
  const isSell = act.includes('sell') && !act.includes('wait');
  const isWait = act.includes('wait') || act.includes('hold');
  const heroType = isSell ? 'green' : isWait ? 'amber' : 'green';
  const colorClass = isSell ? 'color-green' : isWait ? 'color-amber' : 'color-green';
  const bgClass = isSell ? 'bg-green' : isWait ? 'bg-amber' : 'bg-green';

  // Weather HTML
  let weatherHtml = '';
  if (w) {
    const advice = weatherAdvice(w.rainProb, w.temp);
    weatherHtml = `
      <div class="weather-card">
        <div class="weather-top">
          <div>
            <div class="weather-location">${w.city}, ${d.state}</div>
            <div class="weather-temp">${w.temp}°C</div>
            <div class="weather-condition">${w.icon} ${w.humidity}% humidity</div>
          </div>
          <div class="weather-icon-big">${w.icon}</div>
        </div>
        <div class="weather-divider"></div>
        <div class="weather-detail-row"><span>💧 Humidity</span><span>${w.humidity}%</span></div>
        <div class="weather-detail-row"><span>💨 Wind</span><span>${w.wind} km/h</span></div>
        <div class="weather-detail-row"><span>🌧️ Rain Chance</span><span>${w.rainProb}%</span></div>
        <div class="weather-advice">${advice}</div>
      </div>
    `;
  }

  el.innerHTML = `
    <!-- Hero: Should I Sell? -->
    <div class="hero-card border-${heroType}">
      <div class="hero-layout">
        <div class="hero-content">
          <div class="hero-eyebrow">Should You Sell Today?</div>
          <div class="hero-action">
            <span class="hero-action-icon">${d.recommendation.action_icon}</span>
            <span class="hero-action-text ${colorClass}">${d.recommendation.primary_action}</span>
          </div>
          <p class="hero-detail">${d.recommendation.action_detail}</p>
          <div class="tags-row">
            <span class="tag ${d.recommendation.risk_level === 'low' ? 'green' : d.recommendation.risk_level === 'high' ? 'rose' : 'amber'}">Risk: ${d.recommendation.risk_level.toUpperCase()}</span>
            <span class="tag">Trend: ${d.recommendation.trend_direction}</span>
            ${d.recommendation.season_note ? '<span class="tag amber">🌾 Seasonal</span>' : ''}
          </div>
          ${d.recommendation.season_note ? `<p class="hero-detail" style="margin-top:12px;font-size:13px;color:var(--amber)">🌾 ${d.recommendation.season_note}</p>` : ''}
        </div>
        <div class="hero-price-box ${bgClass}">
          <div class="hero-price-label">Expected Market Price</div>
          <div class="hero-price-value ${colorClass}">₹${d.predicted_price.toLocaleString('en-IN')}</div>
          <div class="stat-change ${chg}" style="margin-top:8px">${sign}${d.change_pct}%</div>
        </div>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-grid">
      <div class="stat-card green">
        <div class="stat-label">Today's Mandi Price</div>
        <div class="stat-value">₹${d.current_price.toLocaleString('en-IN')}</div>
        <div class="stat-meta">${d.crop} · ${d.state}</div>
      </div>
      <div class="stat-card emerald">
        <div class="stat-label">Expected Market Price</div>
        <div class="stat-value">₹${d.predicted_price.toLocaleString('en-IN')}</div>
        <div class="stat-change ${chg}">${sign}${d.change_pct}%</div>
      </div>
      <div class="stat-card ${alertLvl === 'green' ? 'emerald' : alertLvl === 'yellow' ? 'amber' : 'rose'}">
        <div class="stat-label">MSP Safety</div>
        <div class="stat-value" style="font-size:16px">${d.msp_alert.icon} ${d.msp_alert.message}</div>
        <div class="stat-meta">MSP: ₹${d.msp.toLocaleString('en-IN')}</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-label">Price Trend</div>
        <div class="stat-value" style="font-size:20px;text-transform:capitalize">${d.trend === 'rising' ? '📈' : d.trend === 'falling' ? '📉' : '➡️'} ${d.trend}</div>
      </div>
    </div>

    <!-- Two Column: Chart + Weather -->
    <div class="grid-main">
      <div>
        <div class="chart-container">
          <div class="card-header">
            <div class="card-title">Price History & Forecast</div>
          </div>
          <div class="chart-wrapper" id="dashboardChart"></div>
        </div>
      </div>
      <div>
        ${weatherHtml || '<div class="card"><p style="color:var(--text-muted);text-align:center;padding:var(--s-xl)">🌤️ Weather data unavailable</p></div>'}
      </div>
    </div>
  `;

  setTimeout(() => renderPriceChart('dashboardChart', d), 100);
}

// ============================================================
// PRICE FORECAST (Decision Support — No ML Details)
// ============================================================
async function loadForecast(crop, state) {
  // Use centralized state instead of reading from DOM
  const targetDate = AppState.targetDate || '';
  const data = await API.getEnsemble(crop, state, targetDate);
  renderForecast(data);
}

function renderForecast(d) {
  const el = document.getElementById('forecastBody');
  if (!el) return;

  const chg = d.change_pct >= 0 ? 'positive' : 'negative';
  const sign = d.change_pct >= 0 ? '+' : '';

  // AI suggestion text
  const trendWord = d.change_pct >= 0 ? 'increase' : 'decrease';
  const suggestion = d.change_pct >= 3
    ? 'Prices are expected to rise. Consider waiting for a better price before selling.'
    : d.change_pct <= -3
      ? 'Prices are expected to fall. Selling soon may be a good idea.'
      : 'Prices are relatively stable. Sell based on your immediate needs.';

  el.innerHTML = `
    <!-- AI Suggestion -->
    <div class="rec-card">
      <div class="rec-action">🤖 <span>AI Suggestion</span></div>
      <p class="rec-detail">Based on historical patterns and market analysis, ${d.crop} prices in ${d.state} are expected to ${trendWord} by ${Math.abs(d.change_pct)}% in the coming months. ${suggestion}</p>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card green">
        <div class="stat-label">Today's Mandi Price</div>
        <div class="stat-value">₹${d.current_price.toLocaleString('en-IN')}</div>
      </div>
      <div class="stat-card emerald">
        <div class="stat-label">Expected Market Price</div>
        <div class="stat-value">₹${d.ensemble_price.toLocaleString('en-IN')}</div>
        <div class="stat-change ${chg}">${sign}${d.change_pct}%</div>
      </div>
      <div class="stat-card amber">
        <div class="stat-label">MSP (Safety Net)</div>
        <div class="stat-value">₹${d.msp.toLocaleString('en-IN')}</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-label">Forecast Confidence</div>
        <div class="stat-value">${d.confidence}%</div>
        <div class="confidence-meter" style="margin-top:8px">
          <div class="confidence-bar"><div class="confidence-fill ${d.confidence >= 70 ? 'high' : d.confidence >= 40 ? 'medium' : 'low'}" style="width:${d.confidence}%"></div></div>
        </div>
      </div>
    </div>

    <!-- Chart -->
    <div class="chart-container">
      <div class="card-header">
        <div class="card-title">Historical Price & Forecast</div>
      </div>
      <div class="chart-wrapper" id="forecastChart"></div>
    </div>
  `;

  setTimeout(() => renderPriceChart('forecastChart', {
    history: d.history,
    forecast_path: d.ensemble_path,
    forecast_labels: d.forecast_labels,
    msp: d.msp,
  }), 100);
}

// ============================================================
// PROFIT ESTIMATOR
// ============================================================
// Debounce helper for real-time calculation
let profitDebounceTimer = null;
function debouncedCalculateProfit() {
  clearTimeout(profitDebounceTimer);
  profitDebounceTimer = setTimeout(() => calculateProfit(), 500);
}

async function loadProfit(crop, state) {
  const el = document.getElementById('profitBody');
  if (!el) return;

  el.innerHTML = `
    <div class="card" style="margin-bottom:var(--s-xl)">
      <div class="card-header">
        <div class="card-title">Calculate Your Profit</div>
        <span class="card-icon">💰</span>
      </div>
      <div class="profit-form" style="margin-bottom:0">
        <div class="form-group">
          <label>Quantity (Quintals)</label>
          <input type="number" id="profitQuantity" value="10" min="1" step="1">
        </div>
        <div class="form-group">
          <label>Production Cost (₹/Quintal)</label>
          <input type="number" id="profitCost" placeholder="e.g. 3500" min="0" step="100">
        </div>
      </div>
      <button class="btn btn-primary" onclick="calculateProfit()" style="margin-top:var(--s-md);width:100%">Calculate Profit</button>
    </div>
    <div id="profitResults"></div>
  `;

  // Add real-time calculation on input change (debounced 500ms)
  const qtyInput = document.getElementById('profitQuantity');
  const costInput = document.getElementById('profitCost');
  if (qtyInput) qtyInput.addEventListener('input', debouncedCalculateProfit);
  if (costInput) costInput.addEventListener('input', debouncedCalculateProfit);

  await calculateProfit();
}

async function calculateProfit() {
  const crop = AppState.currentCrop;
  const state = AppState.currentState;
  const qty = document.getElementById('profitQuantity')?.value || 10;
  const cost = document.getElementById('profitCost')?.value || '';
  try {
    const d = await API.getProfitEstimate(crop, state, qty, cost || null);
    renderProfitResults(d);
  } catch (e) { console.error(e); }
}

function renderProfitResults(d) {
  const el = document.getElementById('profitResults');
  if (!el) return;

  const diffSign = d.revenue_difference >= 0 ? '+' : '';
  const diffCls = d.revenue_difference >= 0 ? 'positive' : 'negative';

  // Determine best option
  const cur = d.current_revenue || 0;
  const pred = d.predicted_revenue || 0;
  const msp = d.msp_revenue || 0;
  let bestLabel, bestIcon, bestDetail;
  if (pred >= cur && pred >= msp) {
    bestLabel = 'Wait for Better Price';
    bestIcon = '⏳';
    bestDetail = `Predicted revenue (₹${pred.toLocaleString('en-IN')}) is highest. Waiting could increase your earnings.`;
  } else if (cur >= msp) {
    bestLabel = 'Sell at Mandi Today';
    bestIcon = '✅';
    bestDetail = `Current mandi price gives the best return (₹${cur.toLocaleString('en-IN')}).`;
  } else {
    bestLabel = 'Sell Through MSP';
    bestIcon = '🏛️';
    bestDetail = `MSP guarantees ₹${msp.toLocaleString('en-IN')}. Government procurement is your safest option.`;
  }

  let profitHtml = '';
  if (d.total_cost !== undefined) {
    profitHtml = `
      <div class="profit-card">
        <div class="profit-value" style="color:var(--rose)">₹${d.total_cost.toLocaleString('en-IN')}</div>
        <div class="profit-label">Total Cost</div>
      </div>
      <div class="profit-card">
        <div class="profit-value" style="color:${d.current_profit >= 0 ? 'var(--emerald)' : 'var(--rose)'}">₹${d.current_profit.toLocaleString('en-IN')}</div>
        <div class="profit-label">Current Profit</div>
      </div>
      <div class="profit-card">
        <div class="profit-value" style="color:${d.predicted_profit >= 0 ? 'var(--emerald)' : 'var(--rose)'}">₹${d.predicted_profit.toLocaleString('en-IN')}</div>
        <div class="profit-label">Predicted Profit</div>
      </div>
    `;
  }

  el.innerHTML = `
    <div class="profit-results">
      <div class="profit-card">
        <div class="profit-value">₹${d.current_revenue.toLocaleString('en-IN')}</div>
        <div class="profit-label">Current Revenue</div>
      </div>
      <div class="profit-card">
        <div class="profit-value" style="color:var(--emerald)">₹${d.predicted_revenue.toLocaleString('en-IN')}</div>
        <div class="profit-label">Predicted Revenue</div>
      </div>
      <div class="profit-card">
        <div class="profit-value ${diffCls}" style="color:${d.revenue_difference >= 0 ? 'var(--emerald)' : 'var(--rose)'}">
          ${diffSign}₹${Math.abs(d.revenue_difference).toLocaleString('en-IN')}
        </div>
        <div class="profit-label">Difference (${diffSign}${d.revenue_difference_pct.toFixed(1)}%)</div>
      </div>
      <div class="profit-card">
        <div class="profit-value">₹${d.msp_revenue.toLocaleString('en-IN')}</div>
        <div class="profit-label">MSP Revenue</div>
      </div>
      ${profitHtml}
    </div>

    ${d.profit_recommendation ? `
      <div class="rec-card" style="margin-top:var(--s-lg)">
        <div class="rec-action">💡 <span>${d.profit_recommendation}</span></div>
      </div>
    ` : ''}

    <div class="best-option">
      <div class="best-option-label">Current Best Option</div>
      <div class="best-option-value">${bestIcon} ${bestLabel}</div>
      <div class="best-option-detail">${bestDetail}</div>
    </div>
  `;
}

// ============================================================
// MSP ALERTS
// ============================================================
async function loadAlerts(crop, state) {
  const el = document.getElementById('alertsBody');
  if (!el) return;

  const crops = Object.keys(AppState.config);
  const alerts = [];
  for (const c of crops) {
    const states = AppState.config[c];
    if (states?.length > 0) {
      try {
        const s = states.includes(state) ? state : states[0];
        alerts.push(await API.getMspAlert(c, s));
      } catch (e) { console.warn(`Alert skip: ${c}`); }
    }
  }
  renderAlerts(alerts);
}

function renderAlerts(alerts) {
  const el = document.getElementById('alertsBody');
  if (!el) return;

  const borderColor = (lvl) =>
    lvl === 'green' ? 'var(--emerald)' : lvl === 'yellow' ? 'var(--amber)' : 'var(--rose)';

  el.innerHTML = `
    <div class="stats-grid">
      ${alerts.map((a, i) => `
        <div class="card" style="animation-delay:${i * 0.08}s;border-left:4px solid ${borderColor(a.alert_level)}">
          <div class="card-header">
            <div class="card-title">${a.crop} — ${a.state}</div>
            <span style="font-size:24px">${a.icon}</span>
          </div>
          <div class="alert-badge ${a.alert_level}" style="margin-bottom:var(--s-md)">${a.message}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--s-md);margin-bottom:var(--s-md)">
            <div>
              <div class="stat-label">Current Price</div>
              <div style="font-family:var(--font-mono);font-size:18px;font-weight:600">₹${(a.current_price || a.predicted_price).toLocaleString('en-IN')}</div>
            </div>
            <div>
              <div class="stat-label">MSP</div>
              <div style="font-family:var(--font-mono);font-size:18px;font-weight:600">₹${a.msp.toLocaleString('en-IN')}</div>
            </div>
          </div>
          <div style="font-size:13px;color:var(--text-secondary);margin-bottom:var(--s-sm)">
            <strong>Difference:</strong> ₹${a.difference.toLocaleString('en-IN')}
            ${a.trend ? ` · <strong>Trend:</strong> ${a.trend}` : ''}
          </div>
          <div class="rec-detail">${a.recommendation}</div>
        </div>
      `).join('')}
    </div>
  `;
}

// ============================================================
// MARKET COMPARISON (Card-based Top 5)
// ============================================================
async function loadComparison(crop) {
  const data = await API.getMarketComparison(crop);
  renderComparison(data);
}

function renderComparison(d) {
  const el = document.getElementById('comparisonBody');
  if (!el) return;

  const top5 = (d.markets || []).slice(0, 5);
  const rankClass = (r) => r === 1 ? 'gold' : r === 2 ? 'silver' : r === 3 ? 'bronze' : 'normal';

  // Extract worst market (lowest price)
  const worstMarket = (d.markets || []).length > 0 ? d.markets[d.markets.length - 1] : null;
  if (worstMarket && !d.worst_market) {
    d.worst_market = worstMarket;
  }

  // Helper function for AI recommendation
  function generateMarketRecommendation(d) {
    if (!d.best_market || !d.markets || d.markets.length === 0) {
      return 'Select a crop to see market recommendations.';
    }
    
    const best = d.best_market;
    const spread = d.price_spread || 0;
    const trend = d.overall_trend || 'stable';
    
    // Recommendation logic
    if (spread > 500) {
      // Significant price difference between markets
      return `✔ Sell in ${best.state} — Prices are ₹${spread.toLocaleString('en-IN')} higher than other markets. Transport costs may be worth it for this premium.`;
    } else if (trend === 'rising' && best.change_pct > 3) {
      // Best market is rising strongly
      return `⏳ Consider waiting in ${best.state} — Prices are expected to rise by ${Math.abs(best.change_pct).toFixed(1)}% in the coming weeks. Holding may increase your profit.`;
    } else if (spread <= 200) {
      // Markets are similar
      return `✔ Sell locally — All markets have similar prices (within ₹${spread.toLocaleString('en-IN')}). Selling at your nearest mandi will save transport costs.`;
    } else {
      // General best market recommendation
      return `✔ Sell in ${best.state} — This market offers the best expected price of ₹${best.predicted_price.toLocaleString('en-IN')}/quintal for ${d.crop}.`;
    }
  }

  el.innerHTML = `
    <!-- Summary -->
    <div class="stats-grid" style="margin-bottom:var(--s-xl)">
      <div class="stat-card emerald">
        <div class="stat-label">Best Market</div>
        <div class="stat-value" style="font-size:20px">${d.best_market?.state || 'N/A'}</div>
        <div class="stat-meta">₹${d.best_market?.predicted_price?.toLocaleString('en-IN') || 0}/quintal</div>
      </div>
      <div class="stat-card rose">
        <div class="stat-label">Lowest Market</div>
        <div class="stat-value" style="font-size:20px">${d.worst_market?.state || 'N/A'}</div>
        <div class="stat-meta">₹${d.worst_market?.predicted_price?.toLocaleString('en-IN') || 0}/quintal</div>
      </div>
      <div class="stat-card amber">
        <div class="stat-label">Price Spread</div>
        <div class="stat-value">₹${d.price_spread?.toLocaleString('en-IN') || 0}</div>
        <div class="stat-meta">${d.num_markets} markets compared</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-label">Overall Trend</div>
        <div class="stat-value" style="font-size:20px;text-transform:capitalize">
          ${d.overall_trend === 'rising' ? '📈' : d.overall_trend === 'falling' ? '📉' : '➡️'} ${d.overall_trend || 'stable'}
        </div>
      </div>
    </div>

    <!-- AI Recommendation -->
    <div class="rec-card" style="margin-bottom:var(--s-xl)">
      <div class="rec-action">🎯 <span>AI Recommendation</span></div>
      <p class="rec-detail">${generateMarketRecommendation(d)}</p>
    </div>

    <!-- Top 5 Markets -->
    <div class="card-header" style="margin-bottom:var(--s-md)">
      <div class="card-title">Top 5 Markets for ${d.crop}</div>
    </div>
    <div class="market-cards">
      ${top5.map((m, i) => {
        const chgSign = m.change_pct >= 0 ? '+' : '';
        const chgCls = m.change_pct >= 0 ? 'positive' : 'negative';
        return `
          <div class="market-card" style="animation-delay:${i * 0.05}s">
            <div class="market-rank ${rankClass(m.rank)}">#${m.rank}</div>
            <div class="market-state">${m.state}</div>
            <div class="market-price">₹${m.predicted_price.toLocaleString('en-IN')}</div>
            <div style="margin-top:var(--s-md)">
              <div class="market-detail-row">
                <span>Today's Price</span>
                <span style="font-family:var(--font-mono)">₹${m.current_price.toLocaleString('en-IN')}</span>
              </div>
              <div class="market-detail-row">
                <span>Expected Change</span>
                <span class="stat-change ${chgCls}" style="font-size:12px;margin:0">${chgSign}${m.change_pct.toFixed(1)}%</span>
              </div>
              <div class="market-detail-row">
                <span>Trend</span>
                <span style="text-transform:capitalize">${m.trend === 'rising' ? '📈' : m.trend === 'falling' ? '📉' : '➡️'} ${m.trend}</span>
              </div>
            </div>
          </div>
        `;
      }).join('')}
    </div>

    <!-- Full Table -->
    ${(d.markets || []).length > 5 ? `
      <div class="card" style="margin-top:var(--s-xl)">
        <div class="card-header"><div class="card-title">All Markets</div></div>
        <table class="comparison-table">
          <thead><tr><th>Rank</th><th>State</th><th>Today's Price</th><th>Expected Price</th><th>Change</th></tr></thead>
          <tbody>
            ${(d.markets || []).map(m => `
              <tr>
                <td><span class="rank-badge rank-${m.rank}">${m.rank}</span></td>
                <td style="font-family:var(--font-sans);font-weight:500">${m.state}</td>
                <td>₹${m.current_price.toLocaleString('en-IN')}</td>
                <td>₹${m.predicted_price.toLocaleString('en-IN')}</td>
                <td><span class="stat-change ${m.change_pct >= 0 ? 'positive' : 'negative'}" style="font-size:12px">${m.change_pct >= 0 ? '+' : ''}${m.change_pct.toFixed(1)}%</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    ` : ''}
  `;
}

// ============================================================
// AI ASSISTANT (ChatGPT-style)
// ============================================================
function renderAssistant() {
  const el = document.getElementById('assistantBody');
  if (!el) return;

  if (AppState.chatMessages.length === 0) {
    AppState.chatMessages.push({
      sender: 'ai',
      text: `Namaste! 🙏 I'm your FarmPulse AI Assistant.\n\nI can help you with:\n• Market price predictions and forecasts\n• Selling recommendations based on MSP and trends\n• Profit calculations and market comparisons\n• General farming questions and best practices\n\nSelect a crop and state, then ask me anything!`,
      time: new Date(),
    });
  }

  const suggestions = [
    { icon: '💰', text: 'Should I sell my crop now?' },
    { icon: '📊', text: 'Why is the predicted price changing?' },
    { icon: '🏛️', text: `What is the MSP for ${AppState.currentCrop || 'this crop'}?` },
    { icon: '💵', text: 'How much profit can I expect?' },
    { icon: '🌍', text: 'Which state has the best market price?' },
    { icon: '📈', text: 'Explain today\'s forecast' },
  ];

  el.innerHTML = `
    <div class="chat-container">
      <div class="chat-messages" id="chatMessages">
        ${AppState.chatMessages.map(m => chatBubbleHtml(m)).join('')}
      </div>

      ${AppState.chatMessages.length <= 1 ? `
        <div class="chat-suggestions">
          <div class="chat-suggestions-label">Quick questions:</div>
          <div class="chat-suggestions-grid">
            ${suggestions.map(s => `
              <button class="chat-suggestion-btn" onclick="askAI('${s.text}')">
                <span style="font-size:18px">${s.icon}</span>
                <span>${s.text}</span>
              </button>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <div class="chat-input-area">
        <div class="chat-input-wrapper">
          <textarea class="chat-input" id="chatInput" rows="1" placeholder="Ask about prices, markets, farming, or anything..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendChat()}"></textarea>
          <button class="btn btn-primary" onclick="sendChat()">Send</button>
          ${AppState.chatMessages.length > 1 ? `<button class="btn btn-secondary" onclick="clearChat()" style="margin-left: 8px;">Clear</button>` : ''}
        </div>
        <div class="chat-disclaimer">AI uses real FarmPulse data. Predictions are estimates — not financial advice.</div>
      </div>
    </div>
  `;
  scrollChat();
}

function chatBubbleHtml(msg) {
  const isAI = msg.sender === 'ai';
  const time = msg.time ? new Date(msg.time).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : '';
  const text = msg.text.replace(/\n/g, '<br>');

  return `
    <div class="chat-msg ${isAI ? '' : 'user'}">
      <div class="chat-msg-inner">
        <div class="chat-avatar ${isAI ? 'ai' : 'user-av'}">${isAI ? '✨' : '👤'}</div>
        <div>
          <div class="chat-bubble ${isAI ? 'ai-bubble' : 'user-bubble'}">${text}</div>
          <div class="chat-time">${time}</div>
        </div>
      </div>
    </div>
  `;
}

function scrollChat() {
  setTimeout(() => {
    const el = document.getElementById('chatMessages');
    if (el) el.scrollTop = el.scrollHeight;
  }, 50);
}

async function askAI(question) {
  const input = document.getElementById('chatInput');
  if (input) input.value = question;
  await sendChat();
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const q = input?.value?.trim();
  if (!q) return;

  AppState.chatMessages.push({ sender: 'user', text: q, time: new Date() });
  input.value = '';
  renderAssistant();

  // Typing indicator
  const msgs = document.getElementById('chatMessages');
  if (msgs) {
    msgs.insertAdjacentHTML('beforeend', `
      <div id="typingInd" class="chat-msg">
        <div class="chat-msg-inner">
          <div class="chat-avatar ai">✨</div>
          <div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>
        </div>
      </div>
    `);
    scrollChat();
  }

  const answer = await processQuestion(q);
  document.getElementById('typingInd')?.remove();
  AppState.chatMessages.push({ sender: 'ai', text: answer, time: new Date() });
  renderAssistant();
}

async function clearChat() {
  if (!confirm('Clear conversation history?')) return;
  
  // Clear local messages
  AppState.chatMessages = [];
  
  // Clear server-side session
  try {
    await fetch('/api/ai_assistant/clear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': AppState.sessionId || 'default'
      },
      body: JSON.stringify({
        session_id: AppState.sessionId || 'default'
      })
    });
  } catch (e) {
    console.warn('Failed to clear server session:', e);
  }
  
  // Reset session ID
  delete AppState.sessionId;
  
  // Re-render with fresh greeting
  renderAssistant();
}

async function processQuestion(q) {
  const crop = AppState.currentCrop;
  const state = AppState.currentState;

  // Check if crop and state are selected
  if (!crop || !state) {
    return `❌ Please select a crop and state first to get personalized advice.`;
  }

  try {
    // Call the AI Assistant API
    const response = await fetch('/api/ai_assistant', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': AppState.sessionId || 'default'
      },
      body: JSON.stringify({
        question: q,
        crop: crop,
        state: state,
        target_date: AppState.targetDate || null
      })
    });

    const data = await response.json();

    if (!response.ok) {
      // Check if AI is not configured
      if (response.status === 503 && data.configured === false) {
        return `⚠️ AI Assistant is not configured.\n\nThe GROQ_API_KEY environment variable needs to be set.\n\nIn the meantime, try using the Dashboard, Price Forecast, or other modules for predictions.`;
      }
      
      // Handle other errors
      throw new Error(data.error || 'Failed to get AI response');
    }

    // Store session ID for conversation continuity
    if (data.session_id) {
      AppState.sessionId = data.session_id;
    }

    return data.response;

  } catch (e) {
    console.error('AI Assistant error:', e);
    return `❌ Sorry, I couldn't process your question.\n\nError: ${e.message}\n\nPlease try again or use the Dashboard for predictions.`;
  }
}

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
  try {
    AppState.config = await API.getConfig();
    
    // Load saved state from localStorage
    loadStateFromStorage();
    
    const cropSelect = document.getElementById('cropSelect');
    const stateSelect = document.getElementById('stateSelect');
    const targetDateInput = document.getElementById('targetDate');

    Object.keys(AppState.config).forEach(crop => {
      const opt = document.createElement('option');
      opt.value = crop;
      opt.textContent = crop;
      cropSelect.appendChild(opt);
    });

    // Restore saved crop if it exists in config, otherwise use first option
    if (AppState.currentCrop && AppState.config[AppState.currentCrop]) {
      cropSelect.value = AppState.currentCrop;
    } else {
      AppState.currentCrop = cropSelect.value;
    }
    
    updateStates();
    
    // Restore saved state if it exists in config, otherwise use first option
    if (AppState.currentState && AppState.config[AppState.currentCrop]?.includes(AppState.currentState)) {
      stateSelect.value = AppState.currentState;
    } else {
      AppState.currentState = stateSelect.value;
    }
    
    // Restore saved targetDate to input field
    if (AppState.targetDate && targetDateInput) {
      targetDateInput.value = AppState.targetDate;
    }

    cropSelect.addEventListener('change', () => {
      AppState.currentCrop = cropSelect.value;
      updateStates();
      saveStateToStorage();
      loadPage(AppState.currentPage);
    });

    stateSelect.addEventListener('change', () => {
      AppState.currentState = stateSelect.value;
      saveStateToStorage();
      loadPage(AppState.currentPage);
    });

    targetDateInput?.addEventListener('change', () => {
      AppState.targetDate = targetDateInput.value;
      saveStateToStorage();
      loadPage(AppState.currentPage);
    });

    document.querySelectorAll('.nav-item[data-page]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo(el.dataset.page);
      });
    });

    document.querySelector('.menu-toggle')?.addEventListener('click', () => {
      document.querySelector('.sidebar')?.classList.toggle('open');
      document.querySelector('.sidebar-overlay')?.classList.toggle('active');
    });
    document.querySelector('.sidebar-overlay')?.addEventListener('click', closeMobile);

    navigateTo('dashboard');
    initAcademicUi();
  } catch (err) {
    console.error('Init failed:', err);
  }
});

function updateStates() {
  const crop = AppState.currentCrop;
  const sel = document.getElementById('stateSelect');
  const states = AppState.config[crop] || [];
  sel.innerHTML = '';
  states.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s;
    opt.textContent = s;
    sel.appendChild(opt);
  });
  AppState.currentState = sel.value;
}
