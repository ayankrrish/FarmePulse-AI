/** FarmPulse AI academic-mode UI. Uses only read-only project APIs and artifacts. */
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
}

function hasNumericValue(value) {
  return value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value));
}

function formatPrice(value) {
  if (!hasNumericValue(value)) return 'Not provided';
  const amount = Number(value);
  const prefix = amount < 0 ? '-₹' : '₹';
  return `${prefix}${Math.abs(amount).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
}

function formatArtifactDate(value) {
  if (!value) return 'Not provided';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Not provided'
    : date.toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
}

function notProvided() {
  return '<span class="not-available">Not provided by recorded project artifacts</span>';
}

function setMode(mode) {
  AppState.mode = mode === 'academic' ? 'academic' : 'farmer';
  localStorage.setItem('farmpulse-mode', AppState.mode);
  const academic = AppState.mode === 'academic';
  document.body.classList.toggle('academic-mode', academic);
  document.querySelector('.academic-nav')?.toggleAttribute('hidden', !academic);
  document.querySelectorAll('.mode-option').forEach(button => {
    const selected = button.dataset.mode === AppState.mode;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-pressed', String(selected));
  });

  const presentation = document.getElementById('presentationToggle');
  if (presentation) presentation.hidden = !academic;
  if (!academic && AppState.presentationMode) togglePresentationMode(false);
  if (!academic && ['analytics', 'about'].includes(AppState.currentPage)) navigateTo('dashboard');
}

function togglePresentationMode(forceValue) {
  AppState.presentationMode = typeof forceValue === 'boolean' ? forceValue : !AppState.presentationMode;
  document.body.classList.toggle('presentation-mode', AppState.presentationMode);
  const button = document.getElementById('presentationToggle');
  button?.setAttribute('aria-pressed', String(AppState.presentationMode));
  if (button) button.textContent = AppState.presentationMode ? 'Exit presentation' : 'Presentation';
  window.setTimeout(() => window.dispatchEvent(new Event('resize')), 250);
}

function initAcademicUi() {
  document.querySelectorAll('.mode-option').forEach(button => button.addEventListener('click', () => setMode(button.dataset.mode)));
  document.getElementById('presentationToggle')?.addEventListener('click', () => togglePresentationMode());
  setMode(AppState.mode);
}

async function loadAnalytics(crop, state) {
  const el = document.getElementById('analyticsBody');
  if (!el || AppState.mode !== 'academic') return;
  el.innerHTML = '<div class="loading-overlay" role="status"><div class="spinner"></div><span>Loading recorded model data...</span></div>';
  const targetDate = document.getElementById('targetDate')?.value || '';
  const startedAt = performance.now();
  const [forecast, metrics, metadata] = await Promise.all([
    API.getEnsemble(crop, state, targetDate),
    API.getModelMetrics(),
    API.getAnalyticsMetadata(crop),
  ]);
  metadata.request_time_ms = Math.round(performance.now() - startedAt);
  AppState.analyticsData = { forecast, metrics, metadata };
  renderAnalytics(forecast, metrics, metadata);
}

function renderFeatureImportance(metadata) {
  const sources = metadata?.feature_importance || [];
  if (!sources.length) {
    return '<p class="empty-state">Feature importance is not available from the saved model artifacts for this crop.</p>';
  }

  return `<div class="importance-sources">${sources.map(source => `
    <section class="importance-source">
      <h4>${escapeHtml(source.model)}</h4>
      <div class="table-scroll"><table class="comparison-table importance-table"><thead><tr><th>Feature</th><th>Importance</th></tr></thead>
      <tbody>${(source.features || []).map(item => `<tr><td>${escapeHtml(item.feature)}</td><td>${hasNumericValue(item.importance) ? `${(Number(item.importance) * 100).toFixed(2)}%` : 'Not provided'}</td></tr>`).join('')}</tbody></table></div>
    </section>`).join('')}</div>`;
}

function renderAnalytics(forecast, metrics, metadata = {}) {
  const el = document.getElementById('analyticsBody');
  if (!el) return;

  const requestedModels = ['Random Forest', 'XGBoost', 'LSTM', 'GRU', 'ARIMA', 'SARIMA', 'Prophet'];
  const returnedModels = Object.keys(forecast.individual_predictions || {});
  const additionalModels = returnedModels.filter(name => !requestedModels.includes(name));
  const models = [...requestedModels, ...additionalModels];
  
  // Helper function to get model status message
  const getStatusMessage = (name) => {
    const status = forecast.model_status?.[name];
    if (!status) return 'No status info';
    
    // Handle success with fallback info (e.g., "success (fallback: ARIMA(1,1,1))")
    if (status.startsWith('success (fallback:')) {
      const fallbackModel = status.match(/fallback: ([^)]+)\)/)?.[1] || 'simplified config';
      return `Working (using ${fallbackModel})`;
    }
    
    // Handle success with config info (e.g., "success (SARIMA(1,1,1)(1,1,0,12))")
    if (status.startsWith('success (') && !status.includes('fallback')) {
      const configName = status.match(/success \(([^)]+)\)/)?.[1] || '';
      return configName ? `Working (${configName})` : 'Working';
    }
    
    const statusMessages = {
      'success': 'Working',
      'model_not_found': 'Model not trained',
      'model_load_failed': 'Model incompatible (Keras version)',
      'environment_missing': 'Package not installed',
      'convergence_failed': 'Failed to converge',
      'error: ModuleNotFoundError': 'Package not installed',
      'error: ImportError': 'Package not installed',
    };
    
    // Check for exact match
    if (statusMessages[status]) return statusMessages[status];
    
    // Check for error prefix
    if (status.startsWith('error:')) {
      const errorType = status.replace('error: ', '');
      return `Error: ${errorType}`;
    }
    
    return status;
  };
  
  const rows = [...models, 'Ensemble'].map(name => {
    const ensemble = name === 'Ensemble';
    const prediction = ensemble ? forecast.ensemble_price : forecast.individual_predictions?.[name];
    const weight = ensemble ? 1 : forecast.weights?.[name];
    const contribution = hasNumericValue(prediction) && hasNumericValue(weight) ? Number(prediction) * Number(weight) : null;
    const deviation = hasNumericValue(prediction) && hasNumericValue(forecast.ensemble_price) ? Number(prediction) - Number(forecast.ensemble_price) : null;
    const statusMsg = ensemble ? 'Working' : getStatusMessage(name);
    return { name, prediction, weight, contribution, deviation, confidence: ensemble ? forecast.confidence : null, status: statusMsg };
  });
  const metricRows = Object.entries(metrics.models || {}).map(([name, byCrop]) => ({ name, values: byCrop[forecast.crop] || {} }));
  const horizon = `${forecast.steps_ahead} month${forecast.steps_ahead === 1 ? '' : 's'} (${escapeHtml(forecast.target_month)})`;
  const used = (forecast.models_used || []).map(escapeHtml).join(', ') || 'Not provided';
  const evaluation = metadata.evaluation || {};
  const holdout = hasNumericValue(evaluation.holdout_months)
    ? `${evaluation.holdout_months}-month holdout per eligible state`
    : notProvided();

  el.innerHTML = `
    <div class="academic-hero"><div><div class="hero-eyebrow">Academic view</div><h2>How FarmPulse AI generated this forecast</h2><p>Every numeric value below comes from a live project API, a stored result file, or a saved model artifact. Missing metadata is marked explicitly.</p></div><div class="academic-chip">${escapeHtml(forecast.crop)} &middot; ${escapeHtml(forecast.state)}</div></div>
    <div class="stats-grid academic-stats">
      <div class="stat-card emerald"><div class="stat-label">Current prediction</div><div class="stat-value">${formatPrice(forecast.ensemble_price)}</div><div class="stat-meta">Weighted ensemble</div></div>
      <div class="stat-card blue"><div class="stat-label">Confidence</div><div class="stat-value">${hasNumericValue(forecast.confidence) ? `${escapeHtml(forecast.confidence)}%` : 'Not provided'}</div><div class="stat-meta">Agreement across live outputs</div></div>
      <div class="stat-card green"><div class="stat-label">Models used</div><div class="stat-value">${escapeHtml((forecast.models_used || []).length)}</div><div class="stat-meta">${used}</div></div>
      <div class="stat-card amber"><div class="stat-label">Forecast horizon</div><div class="stat-value stat-value-small">${horizon}</div><div class="stat-meta">API response time: ${metadata.request_time_ms ?? 'Not provided'} ms</div></div>
    </div>
    <div class="analytics-grid">
      <div class="chart-container"><div class="card-header"><div><div class="card-title">Model Comparison</div><p class="card-note">Live forecast price for every requested model and any returned baseline. Unavailable models are not substituted.</p></div></div><div class="chart-wrapper academic-chart" id="modelComparisonChart" aria-label="Bar chart comparing live model forecasts"></div></div>
      <div class="chart-container"><div class="card-header"><div><div class="card-title">Model Contribution</div><p class="card-note">Actual ensemble weights returned by the prediction API.</p></div></div><div class="chart-wrapper academic-chart" id="modelContributionChart" aria-label="Pie chart of ensemble model weights"></div></div>
    </div>
    <div class="chart-container"><div class="card-header"><div><div class="card-title">Multi-Model Forecast Paths</div><p class="card-note">Historical price data and live forecast paths. Use Plotly controls to inspect, zoom, and compare.</p></div></div><div class="chart-wrapper academic-chart wide" id="forecastPathsChart" aria-label="Line chart with historical prices, individual model forecasts, and ensemble forecast"></div></div>
    <div class="card analytics-card"><div class="card-header"><div class="card-title">Ensemble Pipeline</div><p class="card-note">Live models for this request: ${used}</p></div><div class="pipeline"><div>Dataset</div><i aria-hidden="true">&darr;</i><div>Cleaning</div><i aria-hidden="true">&darr;</i><div>Feature Engineering</div><i aria-hidden="true">&darr;</i><div class="pipeline-models">${requestedModels.map(name => `<span class="${forecast.models_used?.includes(name) ? 'pipeline-live' : 'pipeline-catalog'}">${escapeHtml(name)}</span>`).join('')}</div><i aria-hidden="true">&darr;</i><div class="pipeline-accent">Weighted Ensemble</div><i aria-hidden="true">&darr;</i><div>Final Prediction</div><i aria-hidden="true">&darr;</i><div>Farmer Recommendation</div></div></div>
    <div class="card analytics-card"><div class="card-header"><div><div class="card-title">Performance Metrics</div><p class="card-note">Recorded per-crop evaluation values. MAPE and validation-row counts were not persisted in the current result artifacts.</p></div></div><div class="metrics-meta"><span>MAPE: ${notProvided()}</span><span>Validation dataset size: ${notProvided()}</span><span>Evaluation: ${holdout}</span><span>Latest model artifact: ${escapeHtml(formatArtifactDate(metadata.latest_model_artifact_modified))}</span><span>Forecast horizon: ${horizon}</span></div><div class="table-scroll"><table class="comparison-table"><thead><tr><th>Model</th><th>RMSE</th><th>MAE</th><th>R&sup2;</th></tr></thead><tbody>${metricRows.length ? metricRows.map(row => `<tr><td class="table-model">${escapeHtml(row.name)}</td><td>${row.values.RMSE ?? 'Not provided'}</td><td>${row.values.MAE ?? 'Not provided'}</td><td>${row.values.R2 ?? 'Not provided'}</td></tr>`).join('') : `<tr><td colspan="4">${notProvided()}</td></tr>`}</tbody></table></div></div>
    <div class="card analytics-card"><div class="card-header"><div><div class="card-title">Prediction Summary</div><p class="card-note">Status shows why a model prediction is unavailable. Contribution equals live prediction multiplied by its live ensemble weight.</p></div></div><div class="table-scroll"><table class="comparison-table prediction-table"><thead><tr><th>Model</th><th>Prediction</th><th>Weight</th><th>Contribution</th><th>Deviation</th><th>Status</th></tr></thead><tbody>${rows.map(row => `<tr class="${row.name === 'Ensemble' ? 'ensemble-row' : ''}"><td class="table-model">${escapeHtml(row.name)}</td><td>${formatPrice(row.prediction)}</td><td>${hasNumericValue(row.weight) ? `${(Number(row.weight) * 100).toFixed(2)}%` : 'Not provided'}</td><td>${formatPrice(row.contribution)}</td><td>${hasNumericValue(row.deviation) ? formatPrice(row.deviation) : 'Not provided'}</td><td><span class="status-badge status-${row.status === 'Working' ? 'success' : 'error'}">${escapeHtml(row.status)}</span></td></tr>`).join('')}</tbody></table></div></div>
    <div class="analytics-grid"><div class="card analytics-card"><div class="card-header"><div class="card-title">Feature Importance</div><p class="card-note">Values are read directly from saved tree-model artifacts; no cross-model aggregation is calculated.</p></div>${renderFeatureImportance(metadata)}</div><div class="card analytics-card"><div class="card-header"><div class="card-title">Technology Stack</div></div><dl class="stack-list"><dt>Backend</dt><dd>Flask (Python)</dd><dt>Machine learning</dt><dd>TensorFlow/Keras, scikit-learn, XGBoost, statsmodels, Prophet</dd><dt>Visualization</dt><dd>Plotly.js</dd><dt>Data tooling</dt><dd>Pandas and NumPy</dd></dl></div></div>
    <div class="card analytics-card"><div class="card-header"><div class="card-title">Project Architecture</div></div><div class="architecture-flow"><span>User interface</span><i aria-hidden="true">&rarr;</i><span>Flask APIs</span><i aria-hidden="true">&rarr;</i><span>Prediction services</span><i aria-hidden="true">&rarr;</i><span>Models and artifacts</span><i aria-hidden="true">&rarr;</i><span>Weighted ensemble</span><i aria-hidden="true">&rarr;</i><span>Farmer recommendation</span></div></div>`;
  requestAnimationFrame(() => renderAcademicCharts(forecast, rows));
}

function renderAbout() {
  const el = document.getElementById('aboutBody');
  if (!el) return;
  const cards = [
    ['Problem Statement', 'Pulse-crop producers need clear price signals, MSP context, market comparisons, and forecast-informed selling support.'],
    ['Objectives', 'Provide price forecasts, profit estimates, MSP alerts, market comparison, a farmer-facing assistant, and transparent academic analysis.'],
    ['Dataset', 'The documented project pipeline uses CEDA Agmarknet and data.gov.in market data. Processed price-context datasets support Chana, Moong, and Tur across eight states.'],
    ['Machine Learning Models', 'The project records Random Forest, XGBoost, LSTM, GRU, ARIMA, SARIMA, and Prophet evaluation artifacts. The live ensemble includes only models that return a forecast for the selected request.'],
    ['Technologies', 'Flask, TensorFlow/Keras, scikit-learn, XGBoost, statsmodels, Prophet, Plotly.js, Pandas, NumPy, HTML, CSS, and vanilla JavaScript.'],
    ['Architecture', 'Historical data flows through cleaning and feature engineering into model training and recorded evaluation artifacts. Flask serves prediction APIs to the interactive dashboard.'],
    ['Evaluation', 'Training documentation records a 12-month holdout for eligible state series. The UI presents only metrics that were persisted in the supplied result files.'],
    ['Future Scope', 'Persist MAPE and validation-row counts, capture training provenance, add a supported Prophet inference path, and resolve model-runtime version compatibility before deployment.'],
  ];
  el.innerHTML = `<div class="academic-hero"><div><div class="hero-eyebrow">About FarmPulse AI</div><h2>A transparent agricultural price-intelligence project</h2><p>FarmPulse AI combines documented market data, multiple forecasting approaches, and farmer-oriented recommendations for pulse crops.</p></div></div><div class="about-grid">${cards.map(([title, text]) => `<article class="card analytics-card"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(text)}</p></article>`).join('')}</div>`;
}