/**
 * FarmPulse AI — Chart Configuration (Plotly.js)
 * Light theme · Farmer-friendly · Clean
 */

const ChartTheme = {
  bg: 'rgba(0,0,0,0)',
  grid: 'rgba(0,0,0,0.05)',
  text: '#7a9a7a',
  font: "'Inter', sans-serif",
  mono: "'JetBrains Mono', monospace",
  hover: { bg: '#ffffff', border: 'rgba(0,0,0,0.1)', text: '#1a2e1a' },
  colors: {
    green: '#2E7D32',
    emerald: '#059669',
    amber: '#d97706',
    rose: '#dc2626',
    blue: '#2563eb',
  },
};

function baseLayout() {
  return {
    paper_bgcolor: ChartTheme.bg,
    plot_bgcolor: ChartTheme.bg,
    font: { family: ChartTheme.font, color: ChartTheme.text, size: 12 },
    margin: { l: 55, r: 20, t: 20, b: 40 },
    xaxis: {
      gridcolor: ChartTheme.grid,
      linecolor: ChartTheme.grid,
      tickfont: { family: ChartTheme.mono, size: 11 },
    },
    yaxis: {
      gridcolor: ChartTheme.grid,
      linecolor: ChartTheme.grid,
      tickfont: { family: ChartTheme.mono, size: 11 },
      tickprefix: '₹',
    },
    legend: {
      bgcolor: 'rgba(0,0,0,0)',
      font: { size: 11, color: ChartTheme.text },
      orientation: 'h',
      y: -0.15,
    },
    hovermode: 'x unified',
    hoverlabel: {
      bgcolor: ChartTheme.hover.bg,
      bordercolor: ChartTheme.hover.border,
      font: { family: ChartTheme.mono, size: 12, color: ChartTheme.hover.text },
    },
  };
}

const plotlyConfig = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
  displaylogo: false,
  responsive: true,
};

/**
 * Main price history + forecast chart.
 */
function renderPriceChart(containerId, data) {
  const el = document.getElementById(containerId);
  if (!el) return;

  const hDates = data.history.map(h => h.date);
  const hPrices = data.history.map(h => h.modal_price);

  const history = {
    x: hDates, y: hPrices,
    type: 'scatter', mode: 'lines',
    name: 'Historical Price',
    line: { color: ChartTheme.colors.green, width: 2, shape: 'spline' },
    fill: 'tozeroy',
    fillcolor: 'rgba(46, 125, 50, 0.06)',
    hovertemplate: '₹%{y:,.0f}<extra>Historical</extra>',
  };

  const fDates = [hDates[hDates.length - 1], ...data.forecast_labels];
  const fPrices = [hPrices[hPrices.length - 1], ...data.forecast_path];

  const forecast = {
    x: fDates, y: fPrices,
    type: 'scatter', mode: 'lines+markers',
    name: 'Forecast',
    line: { color: ChartTheme.colors.emerald, width: 2, dash: 'dot', shape: 'spline' },
    marker: { size: 5, color: ChartTheme.colors.emerald },
    hovertemplate: '₹%{y:,.0f}<extra>Forecast</extra>',
  };

  const allDates = [...hDates, ...data.forecast_labels];
  const msp = {
    x: allDates, y: allDates.map(() => data.msp),
    type: 'scatter', mode: 'lines',
    name: `MSP (₹${data.msp.toLocaleString('en-IN')})`,
    line: { color: ChartTheme.colors.rose, width: 1.5, dash: 'dash' },
    hovertemplate: '₹%{y:,.0f}<extra>MSP</extra>',
  };

  const maVals = [];
  for (let i = 0; i < hPrices.length; i++) {
    if (i < 2) { maVals.push(null); continue; }
    maVals.push((hPrices[i] + hPrices[i-1] + hPrices[i-2]) / 3);
  }

  const ma = {
    x: hDates, y: maVals,
    type: 'scatter', mode: 'lines',
    name: '3M Moving Avg',
    line: { color: ChartTheme.colors.amber, width: 1.5, shape: 'spline' },
    opacity: 0.7,
    hovertemplate: '₹%{y:,.0f}<extra>3M Avg</extra>',
  };

  Plotly.newPlot(el, [history, forecast, msp, ma], { ...baseLayout(), showlegend: true }, plotlyConfig);
}

/** Charts used only by the academic view. */
function renderAcademicCharts(forecast, rows) {
  const colors = ['#2E7D32', '#2563eb', '#7c3aed', '#d97706', '#dc2626', '#0f766e', '#64748b', '#059669'];
  const comparison = document.getElementById('modelComparisonChart');
  if (comparison) {
    const missing = rows.filter(row => !Number.isFinite(Number(row.prediction))).map(row => row.name);
    Plotly.newPlot(comparison, [{
      type: 'bar', x: rows.map(row => row.name), y: rows.map(row => Number.isFinite(Number(row.prediction)) ? Number(row.prediction) : null),
      marker: { color: rows.map((_, index) => colors[index % colors.length]), borderRadius: 7 },
      hovertemplate: '%{x}<br>Forecast: ?%{y:,.2f}<extra></extra>',
    }], {
      ...baseLayout(), margin: { l: 65, r: 20, t: 25, b: 80 }, showlegend: false,
      yaxis: { ...baseLayout().yaxis, title: 'Forecast price (?/quintal)' },
      annotations: missing.length ? [{ text: `No live forecast returned for: ${missing.join(', ')}`, xref: 'paper', yref: 'paper', x: 0, y: 1.12, showarrow: false, font: { size: 11, color: ChartTheme.text } }] : [],
    }, plotlyConfig);
  }

  const contribution = document.getElementById('modelContributionChart');
  const weighted = Object.entries(forecast.weights || {}).filter(([, weight]) => Number.isFinite(Number(weight)) && Number(weight) > 0);
  if (contribution) {
    if (weighted.length) {
      Plotly.newPlot(contribution, [{
        type: 'pie', labels: weighted.map(([name]) => name), values: weighted.map(([, weight]) => Number(weight)),
        hole: 0.58, textinfo: 'label+percent', textposition: 'outside',
        marker: { colors: colors, line: { color: '#ffffff', width: 2 } },
        hovertemplate: '%{label}<br>Weight: %{percent}<extra></extra>',
      }], { ...baseLayout(), margin: { l: 20, r: 20, t: 20, b: 20 }, showlegend: false }, plotlyConfig);
    } else {
      contribution.innerHTML = '<p class="empty-state">Ensemble weights are not available for this prediction.</p>';
    }
  }

  const paths = document.getElementById('forecastPathsChart');
  if (paths) {
    const history = forecast.history || [];
    const traces = [{
      x: history.map(point => point.date), y: history.map(point => point.modal_price), type: 'scatter', mode: 'lines', name: 'Historical prices',
      line: { color: ChartTheme.colors.green, width: 2.5 }, hovertemplate: '?%{y:,.0f}<extra>Historical</extra>',
    }];
    Object.entries(forecast.individual_forecasts || {}).forEach(([name, values], index) => {
      traces.push({ x: forecast.forecast_labels, y: values, type: 'scatter', mode: 'lines+markers', name,
        line: { color: colors[index % colors.length], width: 1.8, dash: 'dot' }, marker: { size: 4 }, hovertemplate: '?%{y:,.0f}<extra>' + name + '</extra>' });
    });
    traces.push({ x: forecast.forecast_labels, y: forecast.ensemble_path, type: 'scatter', mode: 'lines+markers', name: 'Ensemble',
      line: { color: '#111827', width: 3 }, marker: { size: 5 }, hovertemplate: '?%{y:,.0f}<extra>Ensemble</extra>' });
    Plotly.newPlot(paths, traces, { ...baseLayout(), margin: { l: 65, r: 20, t: 25, b: 65 }, showlegend: true,
      yaxis: { ...baseLayout().yaxis, title: 'Price (?/quintal)' }, legend: { ...baseLayout().legend, orientation: 'h', y: -0.25 }, hovermode: 'x unified' }, plotlyConfig);
  }
}
