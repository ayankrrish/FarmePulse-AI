# Technical Design Document

## Overview

### Project Context

FarmPulse AI is a production Flask-based agricultural price intelligence platform serving Indian farmers with ML-powered market insights. This transformation modernizes the frontend into a farmer-friendly, production-quality interface while preserving 100% of backend functionality—no changes to Flask routes, services, ML models, or data pipelines.

**Transformation Scope**: Frontend ONLY (HTML, CSS, JavaScript)

**Core Value Proposition**: Transform a functional but basic UI into a polished, farmer-centric interface that hides ML complexity and surfaces actionable insights.

### Design Principles

1. **Backend Preservation**: Zero modifications to Flask routes, services (`ensemble.py`, `recommendation.py`, `msp_alerts.py`, `market_comparison.py`, `profit_calculator.py`), ML models, or data pipelines
2. **Farmer-First UX**: Eliminate ML jargon, surface actionable decisions ("Sell Today" vs "Wait"), use visual cards over tables
3. **Production Quality**: Professional appearance, smooth animations, responsive design, accessibility compliance
4. **Technology Constraints**: Stay with Flask + HTML/CSS/JS stack (no React/Next.js), use existing Plotly.js for charts
5. **Single Theme**: Premium light theme only (no dark mode toggle)

### Tech Stack (Unchanged)

- **Backend**: Flask, scikit-learn, TensorFlow/Keras, XGBoost, LSTM/GRU models, ensemble prediction
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Plotly.js
- **Data**: CSV pipeline, pandas, historical price data from CEDA Agmarknet

### Success Criteria

- Farmer can determine "Should I sell today?" within 5 seconds of page load
- Zero backend code changes (validated by git diff on `/dashboard/services/`, `/dashboard/app.py` routes)
- Mobile responsive on 480px screens
- WCAG AA accessibility compliance
- Sub-2 second page transitions
- Clear visual hierarchy on all devices

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Client)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  HTML Templates (index.html)                          │  │
│  │  • Sidebar Navigation                                 │  │
│  │  • Page Sections (Dashboard, Forecast, Profit, etc.) │  │
│  │  • Reusable Components (Cards, Charts, Forms)        │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  CSS Design System (style.css)                        │  │
│  │  • Design Tokens (colors, spacing, typography)       │  │
│  │  • Component Styles (cards, buttons, forms)          │  │
│  │  • Responsive Breakpoints (mobile, tablet, desktop)  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  JavaScript Application (app.js)                      │  │
│  │  • AppState Management                                │  │
│  │  • API Client Layer                                   │  │
│  │  • Page Renderers (Dashboard, Forecast, etc.)        │  │
│  │  • Chart Helpers (Plotly.js integration)             │  │
│  │  • Weather Integration (Open-Meteo API)              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼ AJAX/Fetch API
┌─────────────────────────────────────────────────────────────┐
│              Flask Backend (UNCHANGED)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Flask Routes (app.py)                                │  │
│  │  • /api/config                                        │  │
│  │  • /api/dashboard_summary                             │  │
│  │  • /api/ensemble_predict                              │  │
│  │  • /api/recommendation                                │  │
│  │  • /api/msp_alert                                     │  │
│  │  • /api/market_comparison                             │  │
│  │  • /api/profit_estimate                               │  │
│  │  • /api/model_metrics (optional dev mode)            │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Services Layer (Unchanged)                           │  │
│  │  • ensemble.py      - Weighted model averaging        │  │
│  │  • recommendation.py - Sell/Wait decision logic       │  │
│  │  • msp_alerts.py    - MSP safety checks               │  │
│  │  • market_comparison.py - Cross-state analysis        │  │
│  │  • profit_calculator.py - Revenue calculations        │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ML Models (Unchanged)                                │  │
│  │  • LSTM, GRU, XGBoost, Random Forest v2               │  │
│  │  • ARIMA, SARIMA (on-demand fitting)                  │  │
│  │  • Ensemble prediction with dynamic weighting         │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Data Layer (Unchanged)                               │  │
│  │  • CSV files: latest_context_all.csv, tur_context.csv│  │
│  │  • pandas DataFrames with historical price data       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Frontend Architecture

**Single-Page Application (SPA) Pattern**
- One HTML file (`index.html`) with multiple page sections
- JavaScript-based client-side routing
- All pages load on initial request, toggled via CSS classes
- No full page reloads after initial load

**State Management Pattern**
```javascript
const AppState = {
  config: {},            // Available crops/states from /api/config
  currentCrop: null,     // Selected crop (Chana/Moong/Tur)
  currentState: null,    // Selected state
  currentPage: 'dashboard', // Active page
  dashboardData: null,   // Cached dashboard data
  chatMessages: [],      // AI Assistant conversation history
};
```

**API Client Layer**
- Centralized `API` object with methods for each endpoint
- Error handling and response parsing
- Query parameter construction
- Loading state management

---

## Components and Interfaces

### 1. Design System

**Color Palette**

```css
/* Primary Green (Agricultural Theme) */
--green-800: #2E7D32;  /* Primary actions, active states */
--green-700: #388E3C;  /* Hover states */
--emerald: #059669;    /* Positive indicators, profit */
--amber: #d97706;      /* Warning, caution */
--rose: #dc2626;       /* Danger, below MSP */
--blue: #2563eb;       /* Information */

/* Backgrounds */
--bg-page: #f0f5f1;    /* Soft green tint */
--bg-card: #ffffff;    /* Pure white cards */
--bg-input: #f3f4f6;   /* Input fields */

/* Text */
--text-primary: #1a2e1a;
--text-secondary: #4a6a4a;
--text-muted: #7a9a7a;
```

**Typography**

- **Primary Font**: Inter (Google Fonts) — clean, readable sans-serif
- **Monospace Font**: JetBrains Mono — for numeric data (prices, quantities)
- **Font Sizes**: 11px (labels) → 14px (body) → 22px (page titles) → 32px (hero numbers)

**Spacing Scale**

```css
--s-xs: 4px;
--s-sm: 8px;
--s-md: 16px;
--s-lg: 24px;
--s-xl: 32px;
--s-2xl: 48px;
```

**Border Radius**

```css
--r-sm: 8px;   /* Inputs, small buttons */
--r-md: 12px;  /* Cards, buttons */
--r-lg: 16px;  /* Large cards */
--r-xl: 20px;  /* Hero cards */
--r-full: 9999px;  /* Pills, badges */
```

**Shadows**

```css
--shadow-sm: 0 1px 3px rgba(0,0,0,0.06);   /* Cards */
--shadow-md: 0 4px 6px rgba(0,0,0,0.07);   /* Hover states */
--shadow-lg: 0 10px 15px rgba(0,0,0,0.07); /* Modals */
--shadow-focus: 0 0 0 3px rgba(46,125,50,0.2); /* Focus rings */
```

### 2. Navigation Sidebar

**Structure**

```
┌───────────────────────┐
│ [Logo] FarmPulse AI   │
│ Agricultural Intel.   │
├───────────────────────┤
│ MENU                  │
│ 📊 Dashboard          │ ← Active (green background)
│ 📈 Price Forecast     │
│ 💰 Profit Estimator   │
│ 🔔 MSP Alerts         │
│ 🏪 Market Comparison  │
│ 🤖 AI Assistant       │
├───────────────────────┤
│ [FP] FarmPulse AI     │
│      v3.0·Production  │
└───────────────────────┘
```

**Behavior**
- Fixed position (left: 0, height: 100vh)
- Width: 260px on desktop
- Collapses to hamburger menu on mobile (<768px)
- Active page highlighted with green background
- Smooth transitions on hover (150ms)

**Mobile Sidebar**
- Translates off-screen: `transform: translateX(-100%)`
- Opens when hamburger clicked: `transform: translateX(0)`
- Dark overlay (`rgba(0,0,0,0.4)`) behind sidebar
- Closes on overlay click or page navigation

### 3. Page Header

**Structure**

```
┌───────────────────────────────────────────────────────────┐
│ [☰] Dashboard                      [Crop ▾] [State ▾] [Month] │
│     AI-powered price intelligence                            │
└───────────────────────────────────────────────────────────┘
```

**Components**
- **Hamburger Menu**: Hidden on desktop, visible on mobile
- **Page Title**: Dynamic, updates on navigation
- **Page Subtitle**: Contextual description of current page
- **Controls Bar**: Crop select, State select, Target date picker

**Sticky Behavior**
- `position: sticky; top: 0; z-index: 50;`
- Background: white with bottom border
- Maintains context while scrolling

### 4. Dashboard Page Components

#### Hero Card (Should I Sell?)

**Visual Hierarchy**

```
┌────────────────────────────────────────────────────────┐
│ SHOULD YOU SELL TODAY?                                 │
│                                                        │
│ ✅ Sell Today                    Expected Market Price│
│ Prices are stable. Current      ┌──────────────────┐ │
│ rates offer good returns.       │   ₹5,850         │ │
│                                  │   +2.3%          │ │
│ [Risk: LOW] [Trend: Rising]     └──────────────────┘ │
└────────────────────────────────────────────────────────┘
```

**Color Logic**
- **Green** (Sell Today): `border-left: 4px solid var(--emerald)`
- **Amber** (Wait): `border-left: 4px solid var(--amber)`
- **Red** (Risk High): `border-left: 4px solid var(--rose)`

**Data Source**: `/api/dashboard_summary`
- `recommendation.primary_action` → Action text
- `recommendation.action_detail` → Explanation
- `recommendation.risk_level` → Badge color
- `predicted_price` → Price box value

#### Quick Insights (Stat Cards Grid)

**Layout**

```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
gap: 16px;
```

**Card Types**
1. **Today's Mandi Price** (Green) — Current price from CEDA
2. **Expected Market Price** (Emerald) — Ensemble prediction
3. **MSP Safety** (Green/Amber/Red) — Alert level indicator
4. **Price Trend** (Blue) — Rising/Falling/Stable icon

**Animation**
- Staggered entrance: `animation-delay: 0.05s, 0.1s, 0.15s, 0.2s`
- Fade in + slide up: `opacity: 0 → 1, translateY(6px) → 0`

#### Weather Widget

**Visual Design**

```
┌──────────────────────────────────────┐
│ Ahmedabad, Gujarat       ☀️         │
│ 32°C                                │
│ ☀️ 45% humidity                     │
├──────────────────────────────────────┤
│ 💧 Humidity     45%                 │
│ 💨 Wind         12 km/h             │
│ 🌧️ Rain Chance  10%                 │
├──────────────────────────────────────┤
│ ☀️ Good weather for harvesting      │
│ and transport to mandi.             │
└──────────────────────────────────────┘
```

**Data Source**: Open-Meteo API
- URL: `https://api.open-meteo.com/v1/forecast`
- Parameters: `latitude`, `longitude`, `current`, `daily`
- State mapping: `{ Gujarat: {lat: 23.0, lon: 72.6}, ... }`

**Farming Advice Logic**

```javascript
if (rainProb > 70) return "Heavy rain expected. Avoid outdoor storage.";
if (rainProb > 40) return "Moderate rain possible. Plan carefully.";
if (temp > 40) return "Extreme heat. Ensure proper storage.";
if (temp > 35) return "Hot day. Good for drying harvested crop.";
return "Good weather for harvesting and transport.";
```

#### Price History & Forecast Chart

**Chart Type**: Plotly.js Line Chart

**Data Series**
1. **Historical Prices** (Green line) — Last 12 months from CSV data
2. **Forecast Prices** (Emerald dashed line) — 7-day ensemble forecast
3. **MSP Line** (Amber horizontal) — Government minimum support price

**Interactions**
- Hover tooltips with date and price
- Zoom/pan enabled
- Responsive height: 350px desktop, 250px mobile

**Data Source**: `/api/dashboard_summary`
- `history` → [{date, modal_price}]
- `forecast_path` → [price1, price2, ...]
- `forecast_labels` → ["2024-02", "2024-03", ...]
- `msp` → Single value for horizontal line

### 5. Price Forecast Page

**Simplified View (Farmer Mode)**

```
┌────────────────────────────────────────────────────────┐
│ 🤖 AI SUGGESTION                                       │
│ Based on historical patterns, Tur prices in Karnataka │
│ are expected to increase by 3.2%. Consider waiting.   │
└────────────────────────────────────────────────────────┘

[Today: ₹5,720] [Expected: ₹5,903] [MSP: ₹7,550] [Confidence: 78%]

┌────────────────────────────────────────────────────────┐
│ Historical Price & Forecast                            │
│ [Plotly Chart with history + forecast line]            │
└────────────────────────────────────────────────────────┘
```

**Hidden from Farmer Mode**
- Model weights breakdown
- Individual model predictions table
- RMSE/MAE metrics
- Feature importance charts

**Developer Mode (?dev=true)**
- Show all ML engineering details
- Model comparison table with weights
- Confidence score per model
- Contribution breakdown

**Data Source**: `/api/ensemble_predict`
- `ensemble_price` → Main prediction
- `confidence` → Percentage 0-100
- `models_used` → Array of model names
- `weights` → Object {model: weight}
- `individual_forecasts` → Object {model: [prices]}

### 6. Profit Estimator Page

**Input Form**

```
┌────────────────────────────────────────────────────────┐
│ 💰 Calculate Your Profit                              │
├────────────────────────────────────────────────────────┤
│ Quantity (Quintals)     Production Cost (₹/Quintal)   │
│ [   10    ]             [    3500      ]              │
│                                                        │
│ [Calculate Profit - Full Width Button]                │
└────────────────────────────────────────────────────────┘
```

**Results Grid**

```
┌───────────────┬───────────────┬───────────────┬───────────────┐
│ Current       │ Predicted     │ Difference    │ MSP           │
│ Revenue       │ Revenue       │               │ Revenue       │
│ ₹57,200       │ ₹59,030       │ +₹1,830       │ ₹75,500       │
│               │               │ (+3.2%)       │               │
└───────────────┴───────────────┴───────────────┴───────────────┘

┌───────────────┬───────────────┬───────────────┐
│ Total Cost    │ Current Profit│ Predicted     │
│               │               │ Profit        │
│ ₹35,000       │ ₹22,200       │ ₹24,030       │
└───────────────┴───────────────┴───────────────┘

┌────────────────────────────────────────────────────────┐
│ CURRENT BEST OPTION                                    │
│ ✅ Wait for Better Price                               │
│ Predicted revenue (₹59,030) is highest. Waiting could │
│ increase your earnings.                                │
└────────────────────────────────────────────────────────┘
```

**Best Option Logic**

```javascript
if (predicted >= current && predicted >= msp) {
  return { action: "Wait for Better Price", icon: "⏳" };
} else if (current >= msp) {
  return { action: "Sell at Mandi Today", icon: "✅" };
} else {
  return { action: "Sell Through MSP", icon: "🏛️" };
}
```

**Data Source**: `/api/profit_estimate?crop=X&state=Y&quantity=Z&cost=W`
- `current_revenue`, `predicted_revenue`, `msp_revenue`
- `revenue_difference`, `revenue_difference_pct`
- `total_cost`, `current_profit`, `predicted_profit` (if cost provided)

### 7. MSP Alerts Page

**Card-Based Layout**

```
┌────────────────┬────────────────┬────────────────┐
│ Chana          │ Moong          │ Tur            │
│ Gujarat        │ Rajasthan      │ Maharashtra    │
│ ✅ Safe        │ ⚠️ Near MSP    │ ❌ Below MSP   │
│ ₹5,850         │ ₹8,620         │ ₹7,120         │
│ MSP: ₹5,650    │ MSP: ₹8,682    │ MSP: ₹7,550    │
│ +₹200 above    │ -₹62 below     │ -₹430 below    │
│                │                │                │
│ You're well    │ Monitor prices │ Consider govt  │
│ above MSP.     │ closely.       │ procurement.   │
└────────────────┴────────────────┴────────────────┘
```

**Color-Coded Borders**
- Green: `border-left: 4px solid var(--emerald)` — Safe (>5% above MSP)
- Amber: `border-left: 4px solid var(--amber)` — Near MSP (±5%)
- Red: `border-left: 4px solid var(--rose)` — Below MSP

**Data Source**: `/api/msp_alert` for each crop/state combination
- Iterate through all crops in `CONFIG`
- Fetch alert for each crop's first available state
- `alert_level` → "green"/"yellow"/"red"
- `message`, `recommendation`, `icon`

### 8. Market Comparison Page

**Top 5 Markets (Card Grid)**

```
┌─────────────────────────────────────────────────────────┐
│ [Best Market: Karnataka ₹5,903] [Spread: ₹450] [Rising]│
└─────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ #1 🥇        │ #2 🥈        │ #3 🥉        │ #4           │ #5           │
│ Karnataka    │ Maharashtra  │ Gujarat      │ Rajasthan    │ MP           │
│ ₹5,903       │ ₹5,820       │ ₹5,750       │ ₹5,680       │ ₹5,453       │
│ Today: 5,720 │ Today: 5,700 │ Today: 5,620 │ Today: 5,550 │ Today: 5,320 │
│ +3.2%        │ +2.1%        │ +2.3%        │ +2.3%        │ +2.5%        │
│ 📈 Rising    │ 📈 Rising    │ ➡️ Stable    │ 📈 Rising    │ 📉 Falling   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

**Rank Badge Styling**
- #1: Gold background (`#FEF3C7`), brown text
- #2: Silver background (`#E5E7EB`), gray text
- #3: Bronze background (`#FED7AA`), orange text
- Others: Light gray

**Full Table (Below Cards)**
- Sortable table with all markets
- Columns: Rank, State, Today's Price, Expected Price, Change %
- Hover highlight on rows

**Data Source**: `/api/market_comparison?crop=X`
- `markets` → Array of {state, current_price, predicted_price, change_pct, trend, rank}
- `best_market` → {state, predicted_price}
- `price_spread` → max - min
- `overall_trend` → "rising"/"falling"/"stable"

### 9. AI Assistant Page

**ChatGPT-Style Interface**

```
┌────────────────────────────────────────────────────────┐
│ [Chat Messages - Scrollable]                           │
│                                                        │
│ ✨ AI: Namaste! I can help with:                      │
│      • Should you sell today?                         │
│      • Which mandi gives best price?                  │
│      • MSP information                                │
│                                                        │
│ 👤 You: Should I sell my Tur today?                   │
│                                                        │
│ ✨ AI: ⏳ Wait for Better Price                        │
│      Tur prices in Karnataka are expected to rise...  │
│                                                        │
├────────────────────────────────────────────────────────┤
│ Quick Questions:                                       │
│ [💰 Should I sell?] [📊 Best state?] [🏛️ MSP?]       │
│ [💵 Profit?] [🌤️ Weather?]                            │
├────────────────────────────────────────────────────────┤
│ [Message input...]                      [Send Button] │
│ AI uses real FarmPulse data. Not financial advice.    │
└────────────────────────────────────────────────────────┘
```

**Message Types**
1. AI Messages: White bubble, left-aligned, AI avatar (✨)
2. User Messages: Green bubble, right-aligned, user avatar (👤)

**Quick Prompts**
- "Should I sell today?" → Calls `/api/recommendation`
- "Which state gives best price?" → Calls `/api/market_comparison`
- "What is MSP for Tur?" → Calls `/api/msp_alert`
- "Profit for 10 quintals" → Calls `/api/profit_estimate`
- "Today's weather" → Calls Open-Meteo API

**Question Processing Logic**

```javascript
if (question.includes("sell") || question.includes("should i")) {
  // Recommendation endpoint
} else if (question.includes("msp")) {
  // MSP alert endpoint
} else if (question.includes("best") || question.includes("which state")) {
  // Market comparison endpoint
} else if (question.includes("profit")) {
  // Profit estimate endpoint
} else if (question.includes("weather")) {
  // Weather API
} else if (question.includes("price") || question.includes("forecast")) {
  // Dashboard summary endpoint
}
```

**Features**
- Typing indicator (three bouncing dots) while processing
- Auto-scroll to latest message
- Message timestamps
- Disclaimer: "AI uses real FarmPulse data. Predictions are estimates — not financial advice."

---

## Data Models

### AppState Object

```typescript
interface AppState {
  config: {
    [crop: string]: string[];  // { "Chana": ["Gujarat", "Rajasthan", ...] }
  };
  currentCrop: string | null;
  currentState: string | null;
  currentPage: 'dashboard' | 'forecast' | 'profit' | 'alerts' | 'comparison' | 'assistant';
  dashboardData: DashboardData | null;
  chatMessages: ChatMessage[];
}
```

### API Response Schemas

**Dashboard Summary**

```typescript
interface DashboardSummary {
  crop: string;
  state: string;
  current_price: number;
  predicted_price: number;
  predicted_7d: number;
  change_pct: number;
  trend: 'rising' | 'falling' | 'stable';
  method_used: string;
  msp: number;
  msp_alert: MspAlert;
  recommendation: Recommendation;
  forecast_path: number[];
  forecast_labels: string[];
  history: { date: string; modal_price: number }[];
  last_updated: string;
  confidence: number;
  models_used: string[];
  weights: { [model: string]: number };
}
```

**Ensemble Prediction**

```typescript
interface EnsemblePrediction {
  crop: string;
  state: string;
  current_price: number;
  ensemble_price: number;
  change_pct: number;
  confidence: number;  // 0-100
  models_used: string[];
  weights: { [model: string]: number };
  individual_predictions: { [model: string]: number };
  msp: number;
  below_msp: boolean;
  ensemble_path: number[];
  confidence_per_step: number[];
  individual_forecasts: { [model: string]: number[] };
  forecast_labels: string[];
  history: { date: string; modal_price: number }[];
}
```

**Recommendation**

```typescript
interface Recommendation {
  primary_action: string;  // "Sell Today" | "Wait for Better Price"
  action_icon: string;     // "✅" | "⏳"
  action_detail: string;   // Explanation paragraph
  risk_level: 'low' | 'medium' | 'high';
  trend_direction: 'rising' | 'falling' | 'stable';
  volatility_level: 'low' | 'medium' | 'high';
  season_note?: string;    // Optional harvest/sowing season context
}
```

**MSP Alert**

```typescript
interface MspAlert {
  crop: string;
  state: string;
  current_price: number;
  predicted_price: number;
  msp: number;
  difference: number;  // predicted - msp
  alert_level: 'green' | 'yellow' | 'red';
  message: string;     // "Safe - Above MSP"
  icon: string;        // "✅" | "⚠️" | "❌"
  recommendation: string;
  trend?: string;
}
```

**Market Comparison**

```typescript
interface MarketComparison {
  crop: string;
  markets: {
    state: string;
    rank: number;
    current_price: number;
    predicted_price: number;
    change_pct: number;
    trend: 'rising' | 'falling' | 'stable';
  }[];
  best_market: {
    state: string;
    predicted_price: number;
  };
  price_spread: number;
  num_markets: number;
  overall_trend: 'rising' | 'falling' | 'stable';
}
```

**Profit Estimate**

```typescript
interface ProfitEstimate {
  crop: string;
  state: string;
  quantity: number;
  current_revenue: number;
  predicted_revenue: number;
  msp_revenue: number;
  revenue_difference: number;
  revenue_difference_pct: number;
  total_cost?: number;
  current_profit?: number;
  predicted_profit?: number;
  profit_recommendation?: string;
  models_used: string[];
  ensemble_confidence: number;
}
```

---

## Error Handling

### API Error States

**Network Errors**

```javascript
try {
  const data = await API.getDashboard(crop, state);
} catch (error) {
  showError("Unable to load dashboard data. Please check your connection.");
}
```

**Empty Data States**

```javascript
if (!state_rows || state_rows.empty) {
  return {
    error: "No data found for this crop/state combination",
    message: "Please select a different state or check back later."
  };
}
```

**Invalid Input States**

```javascript
if (steps < 1) {
  return {
    error: "Please choose a future month",
    message: `Latest known data is ${last_date.strftime('%Y-%m')}`
  };
}
```

### UI Error Handling

**Loading States**

```html
<div class="loading-overlay">
  <div class="spinner"></div>
  <span>Loading dashboard...</span>
</div>
```

**Error Cards**

```html
<div class="card error-card">
  <div class="error-icon">⚠️</div>
  <div class="error-title">Unable to Load Data</div>
  <div class="error-message">Please check your connection and try again.</div>
  <button class="btn btn-primary" onclick="retry()">Retry</button>
</div>
```

**Graceful Degradation**
- Weather API fails → Show "Weather data unavailable" message
- Model prediction fails → Fall back to naive baseline
- Chart fails to render → Show data in table format

---

## Testing Strategy

### Unit Tests

**Component Rendering Tests**
- Dashboard cards render with correct data
- Chart displays with proper data series
- Weather widget shows correct city/temperature
- MSP alert cards show correct color coding

**State Management Tests**
- AppState updates on crop/state selection
- Navigation updates currentPage correctly
- Chat messages append to array properly

**API Client Tests**
- GET requests construct correct query parameters
- Error responses are caught and handled
- JSON parsing works for all endpoints

**Utility Function Tests**
- `weatherIcon()` returns correct emoji for weather code
- `weatherAdvice()` returns correct advice for conditions
- `_compute_steps()` calculates months correctly

### Integration Tests

**API Integration Tests**
- `/api/config` returns valid crop/state mapping
- `/api/dashboard_summary` returns complete dashboard data
- `/api/ensemble_predict` includes all required fields
- Weather API returns valid forecast data

**Page Load Tests**
- Dashboard loads and displays all components
- Price Forecast shows chart and recommendation
- Profit Estimator calculates correctly on input change
- AI Assistant processes questions and returns answers

### E2E Tests (Manual)

**User Flows**
1. Select crop → Select state → View dashboard → See "Should I Sell?" decision
2. Navigate to Profit Estimator → Enter quantity → See revenue calculation
3. Navigate to Market Comparison → See top 5 states ranked
4. Open AI Assistant → Ask question → Receive contextual answer
5. Resize browser to mobile → Sidebar collapses → Hamburger menu works

**Cross-Browser Tests**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Accessibility Tests

**Keyboard Navigation**
- Tab through all interactive elements
- Enter key activates buttons and links
- Escape key closes mobile sidebar

**Screen Reader Tests**
- All images have alt text
- Form inputs have associated labels
- ARIA labels on interactive elements

**Color Contrast Tests**
- WCAG AA compliance (4.5:1 for text)
- Color is not sole indicator (icons + text)

### Performance Tests

**Load Time Targets**
- Initial HTML load: <1s
- Dashboard data fetch: <1s
- Page transition: <200ms
- Chart render: <500ms

**Bundle Size Targets**
- CSS: <50KB gzipped
- JavaScript: <100KB gzipped
- No external dependencies except Plotly.js (already in use)

---

## Implementation Strategy

### Phase 1: Design System Foundation (Week 1)

**Goal**: Establish reusable design tokens and component styles

**Tasks**
1. Create CSS design tokens (colors, spacing, typography, shadows)
2. Build base component styles (cards, buttons, forms, badges)
3. Implement responsive grid system
4. Test design system in isolation (Storybook-style HTML snippets)

**Deliverables**
- `style.css` with complete design system
- Sample HTML components for visual review

**Success Criteria**
- All color tokens meet WCAG AA contrast
- Components render consistently across browsers
- Responsive breakpoints work on all screen sizes

### Phase 2: Navigation & Layout (Week 1)

**Goal**: Implement sidebar navigation and page structure

**Tasks**
1. Build sidebar with logo, navigation links, footer
2. Implement page header with controls
3. Create page section containers
4. Add mobile hamburger menu and overlay
5. Implement client-side routing

**Deliverables**
- Working navigation between all 6 pages
- Mobile-responsive sidebar
- Page title/subtitle updates on navigation

**Success Criteria**
- Navigation highlights active page
- Mobile sidebar opens/closes smoothly
- No full page reloads on navigation

### Phase 3: Dashboard Page (Week 2)

**Goal**: Redesign dashboard as farmer home page with weather

**Tasks**
1. Build hero card ("Should I Sell?") with action recommendation
2. Create stat cards grid (Today's Price, Forecast, MSP, Trend)
3. Integrate Open-Meteo weather widget
4. Implement price history + forecast chart with Plotly.js
5. Connect to `/api/dashboard_summary` endpoint

**Deliverables**
- Complete dashboard with all components
- Weather integration working
- Chart displays historical + forecast data

**Success Criteria**
- Dashboard loads in <2 seconds
- Weather data fetches and displays correctly
- Chart is interactive (hover, zoom, pan)
- All data from API renders correctly

### Phase 4: Price Forecast Simplification (Week 2)

**Goal**: Hide ML complexity, show actionable insights

**Tasks**
1. Build AI suggestion card with plain language
2. Display current/predicted/MSP prices in stat cards
3. Show confidence meter (0-100%)
4. Implement chart with history + forecast
5. Hide model comparison table (keep for dev mode)

**Deliverables**
- Simplified forecast page for farmers
- Optional dev mode toggle (?dev=true)

**Success Criteria**
- No ML jargon visible (LSTM, ensemble, RMSE hidden)
- Confidence displayed as percentage with visual meter
- Farmer can understand recommendation without technical knowledge

### Phase 5: Profit Estimator Redesign (Week 3)

**Goal**: Intuitive calculator with visual results

**Tasks**
1. Build input form (quantity, cost)
2. Create profit results grid (revenue cards)
3. Implement "Best Option" recommendation card
4. Add real-time calculation on input change
5. Connect to `/api/profit_estimate` endpoint

**Deliverables**
- Working profit calculator
- Visual comparison of revenue options
- Clear recommendation of best selling strategy

**Success Criteria**
- Calculation updates without page reload
- Results display in card format (no tables)
- Best option highlighted visually

### Phase 6: MSP Alerts Card Layout (Week 3)

**Goal**: Replace table with color-coded cards

**Tasks**
1. Build card grid layout
2. Implement color-coded left border (green/amber/red)
3. Display alert badge with icon
4. Show current price, MSP, difference
5. Fetch alerts for all crops via `/api/msp_alert`

**Deliverables**
- Grid of MSP alert cards for all crops
- Staggered entrance animation

**Success Criteria**
- Cards visually differentiate alert levels
- All data displays correctly
- Animation is smooth (no jank)

### Phase 7: Market Comparison Visual Redesign (Week 4)

**Goal**: Top 5 card grid + full table

**Tasks**
1. Build top 5 markets card grid
2. Implement rank badges (gold/silver/bronze)
3. Add summary stat cards (best market, spread, trend)
4. Create full market table below cards
5. Connect to `/api/market_comparison` endpoint

**Deliverables**
- Card-based top 5 markets
- Full sortable table for all markets

**Success Criteria**
- Top 3 ranks have special badge styling
- Summary stats display correctly
- Table is readable and sortable

### Phase 8: AI Assistant ChatGPT Interface (Week 4)

**Goal**: Conversational interface with quick prompts

**Tasks**
1. Build chat message container with scroll
2. Implement message bubbles (user vs AI)
3. Add quick prompt buttons
4. Create message input with send button
5. Implement question processing logic
6. Connect to appropriate API endpoints based on question

**Deliverables**
- Working chat interface
- Quick prompts that trigger API calls
- Contextual responses to user questions

**Success Criteria**
- Messages display in correct order
- Quick prompts populate input and send
- Typing indicator shows while processing
- Responses are contextual and accurate

### Phase 9: Responsive Design Implementation (Week 5)

**Goal**: Mobile-first responsive breakpoints

**Tasks**
1. Implement mobile sidebar (hamburger menu)
2. Stack cards vertically on mobile
3. Adjust font sizes for small screens
4. Reflow chart dimensions
5. Test on 480px, 768px, 1024px, 1200px+ screens

**Deliverables**
- Fully responsive layout across all breakpoints
- Mobile-optimized touch targets (44px minimum)

**Success Criteria**
- No horizontal scrolling on any screen size
- All interactive elements are touch-friendly
- Charts are readable on mobile

### Phase 10: Accessibility Implementation (Week 5)

**Goal**: WCAG AA compliance

**Tasks**
1. Add semantic HTML5 elements
2. Provide ARIA labels for interactive elements
3. Ensure keyboard navigation works
4. Test color contrast ratios
5. Add skip navigation links
6. Test with screen reader (NVDA)

**Deliverables**
- WCAG AA compliant interface
- Keyboard navigation working

**Success Criteria**
- All interactive elements reachable via keyboard
- Color contrast meets 4.5:1 ratio
- Screen reader announces all content correctly

### Phase 11: Loading States & Error Handling (Week 6)

**Goal**: Graceful degradation and error recovery

**Tasks**
1. Add loading spinners for async operations
2. Implement error cards for API failures
3. Add retry buttons
4. Show fallback messages for missing data
5. Handle weather API failures gracefully

**Deliverables**
- Loading states for all async operations
- User-friendly error messages

**Success Criteria**
- No blank screens during loading
- Errors display helpful messages
- Users can retry failed operations

### Phase 12: Polish & Performance Optimization (Week 6)

**Goal**: Production-ready quality

**Tasks**
1. Add smooth animations (card entrances, page transitions)
2. Optimize CSS (remove unused styles)
3. Minify JavaScript
4. Test cross-browser compatibility
5. Optimize Plotly chart rendering
6. Add data freshness indicators

**Deliverables**
- Polished UI with smooth transitions
- Optimized bundle sizes
- Cross-browser tested

**Success Criteria**
- Page transitions <200ms
- Initial load <2s
- No visual bugs in any browser

---

## Deployment & Rollback Plan

### Deployment Strategy

**Incremental Rollout**
1. Deploy to staging environment
2. Test all pages and API integrations
3. Review with stakeholders
4. Deploy to production during low-traffic window
5. Monitor error rates and user feedback

**Rollback Criteria**
- Critical bug affecting >50% of users
- API integration broken
- Performance regression >2x slower
- Accessibility regression (keyboard navigation broken)

**Rollback Process**
1. Git revert frontend changes
2. Redeploy previous version
3. Verify rollback successful
4. Post-mortem to identify issue

### Monitoring

**Key Metrics**
- Page load time (target: <2s)
- API response time (target: <1s)
- Error rate (target: <1%)
- User engagement (pages per session, time on site)

**Alerts**
- Error rate >5% → Notify team
- API latency >3s → Notify team
- Weather API failures → Log warning (non-critical)

---

## Developer Mode Architecture

### Toggle Mechanism

**URL Parameter**
- `?dev=true` → Enable developer mode
- Stored in `sessionStorage` for persistence across pages

**State Management**

```javascript
const isDeveloperMode = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const devParam = urlParams.get('dev');
  return devParam === 'true' || sessionStorage.getItem('devMode') === 'true';
};
```

### ML Engineering Details

**Price Forecast Page (Developer Mode)**

```
┌────────────────────────────────────────────────────────┐
│ MODEL COMPARISON                                       │
├────────────────┬─────────┬────────┬────────┬──────────┤
│ Model          │ Pred.   │ Weight │ RMSE   │ MAE      │
├────────────────┼─────────┼────────┼────────┼──────────┤
│ LSTM           │ ₹5,903  │ 0.35   │ 142.3  │ 98.7     │
│ Random Forest  │ ₹5,885  │ 0.30   │ 158.9  │ 112.4    │
│ XGBoost        │ ₹5,920  │ 0.20   │ 165.3  │ 118.6    │
│ ARIMA          │ ₹5,850  │ 0.10   │ 189.4  │ 145.2    │
│ Naive Trend    │ ₹5,780  │ 0.05   │ 245.7  │ 189.3    │
└────────────────┴─────────┴────────┴────────┴──────────┘

Ensemble Prediction: ₹5,896 (weighted average)
Confidence: 78% (based on model agreement)
```

**Data Source**: `/api/model_metrics`
- Returns RMSE, MAE, R² for each model per crop
- Developer mode displays this alongside predictions

### Feature Flag Implementation

**CSS Toggle**

```css
.dev-only {
  display: none;
}

body.developer-mode .dev-only {
  display: block;
}
```

**JavaScript Toggle**

```javascript
if (isDeveloperMode()) {
  document.body.classList.add('developer-mode');
  renderModelMetrics(data.weights, data.individual_predictions);
}
```

---

## Accessibility Implementation

### Semantic HTML

```html
<header class="page-header">
  <nav class="sidebar" aria-label="Main navigation">
    <a href="#" class="nav-item" aria-current="page">Dashboard</a>
  </nav>
</header>

<main class="main-content">
  <section id="page-dashboard" aria-labelledby="dashboard-title">
    <h1 id="dashboard-title" class="page-title">Dashboard</h1>
  </section>
</main>
```

### ARIA Labels

```html
<button class="menu-toggle" aria-label="Open menu" aria-expanded="false">
  ☰
</button>

<select id="cropSelect" aria-label="Select crop">
  <option>Chana</option>
</select>

<div role="status" aria-live="polite" class="loading-overlay">
  Loading dashboard...
</div>
```

### Keyboard Navigation

**Tab Order**
1. Skip to content link
2. Sidebar navigation links
3. Page header controls (crop, state, date)
4. Main content interactive elements
5. Chat input (on AI Assistant page)

**Keyboard Shortcuts**
- `Tab` → Move to next interactive element
- `Shift+Tab` → Move to previous element
- `Enter` → Activate button/link
- `Escape` → Close mobile sidebar
- `Arrow keys` → Navigate select dropdowns

### Focus Indicators

```css
*:focus {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
}

button:focus, a:focus, input:focus, select:focus {
  box-shadow: var(--shadow-focus);
}
```

### Screen Reader Announcements

```html
<div role="alert" aria-live="assertive" class="sr-only">
  Dashboard data updated successfully
</div>

<div role="status" aria-live="polite" aria-atomic="true">
  <span class="sr-only">Expected market price: </span>
  <span class="stat-value">₹5,850</span>
</div>
```

---

## Chart Visualization Strategy

### Plotly.js Configuration

**Chart Type**: Line chart with multiple traces

**Trace Configuration**

```javascript
const traces = [
  {
    x: history.map(d => d.date),
    y: history.map(d => d.modal_price),
    type: 'scatter',
    mode: 'lines',
    name: 'Historical Price',
    line: { color: '#2E7D32', width: 2 },
  },
  {
    x: forecast_labels,
    y: forecast_path,
    type: 'scatter',
    mode: 'lines',
    name: 'Forecast',
    line: { color: '#059669', width: 2, dash: 'dash' },
  },
  {
    x: [...history.map(d => d.date), ...forecast_labels],
    y: Array(history.length + forecast_labels.length).fill(msp),
    type: 'scatter',
    mode: 'lines',
    name: 'MSP (Safety Net)',
    line: { color: '#d97706', width: 1, dash: 'dot' },
  },
];
```

**Layout Configuration**

```javascript
const layout = {
  title: '',
  xaxis: {
    title: 'Month',
    showgrid: true,
    gridcolor: '#f3f4f6',
  },
  yaxis: {
    title: 'Price (₹/quintal)',
    showgrid: true,
    gridcolor: '#f3f4f6',
  },
  hovermode: 'x unified',
  showlegend: true,
  legend: { orientation: 'h', y: -0.2 },
  margin: { l: 60, r: 40, t: 20, b: 60 },
  font: { family: 'Inter, sans-serif', size: 12 },
  plot_bgcolor: '#ffffff',
  paper_bgcolor: '#ffffff',
};
```

**Config Options**

```javascript
const config = {
  responsive: true,
  displayModeBar: true,
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
  displaylogo: false,
};

Plotly.newPlot('chartDiv', traces, layout, config);
```

### Chart Helper Function

```javascript
function renderPriceChart(containerId, data) {
  const { history, forecast_path, forecast_labels, msp } = data;
  
  const traces = [
    // Historical trace
    {
      x: history.map(d => d.date),
      y: history.map(d => d.modal_price),
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Actual Price',
      marker: { size: 4, color: '#2E7D32' },
      line: { color: '#2E7D32', width: 2 },
      hovertemplate: '<b>%{x}</b><br>₹%{y:.2f}/quintal<extra></extra>',
    },
  ];

  // Add forecast trace if available
  if (forecast_path && forecast_labels) {
    // Connect last historical point to first forecast point
    const lastDate = history[history.length - 1].date;
    const lastPrice = history[history.length - 1].modal_price;
    
    traces.push({
      x: [lastDate, ...forecast_labels],
      y: [lastPrice, ...forecast_path],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Forecast',
      marker: { size: 4, color: '#059669' },
      line: { color: '#059669', width: 2, dash: 'dash' },
      hovertemplate: '<b>%{x}</b><br>₹%{y:.2f}/quintal (forecast)<extra></extra>',
    });
  }

  // Add MSP reference line
  if (msp) {
    const allDates = [
      ...history.map(d => d.date),
      ...(forecast_labels || []),
    ];
    traces.push({
      x: allDates,
      y: Array(allDates.length).fill(msp),
      type: 'scatter',
      mode: 'lines',
      name: 'MSP',
      line: { color: '#d97706', width: 1.5, dash: 'dot' },
      hovertemplate: '<b>MSP</b><br>₹%{y:.2f}/quintal<extra></extra>',
    });
  }

  const layout = {
    xaxis: {
      title: 'Month',
      showgrid: true,
      gridcolor: 'rgba(0,0,0,0.05)',
      linecolor: 'rgba(0,0,0,0.1)',
    },
    yaxis: {
      title: 'Price (₹/quintal)',
      showgrid: true,
      gridcolor: 'rgba(0,0,0,0.05)',
      linecolor: 'rgba(0,0,0,0.1)',
    },
    hovermode: 'x unified',
    showlegend: true,
    legend: {
      orientation: 'h',
      x: 0,
      y: -0.15,
      bgcolor: 'rgba(255,255,255,0.8)',
      bordercolor: 'rgba(0,0,0,0.1)',
      borderwidth: 1,
    },
    margin: { l: 60, r: 20, t: 20, b: 60 },
    font: { family: 'Inter, sans-serif', size: 12, color: '#1a2e1a' },
    plot_bgcolor: '#ffffff',
    paper_bgcolor: '#ffffff',
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
    displaylogo: false,
  };

  Plotly.newPlot(containerId, traces, layout, config);
}
```

### Chart Interactions

**Hover Tooltips**
- Unified hover mode shows all traces at once
- Custom templates with rupee symbol and "quintal" unit
- Date formatted as "YYYY-MM"

**Zoom & Pan**
- Enabled by default via Plotly modebar
- Double-click to reset zoom
- Drag to pan along X/Y axis

**Responsive Behavior**
- `responsive: true` in config
- Chart redraws on window resize
- Mobile: Reduce margins, adjust font sizes

```javascript
window.addEventListener('resize', () => {
  Plotly.relayout(containerId, {
    'xaxis.title': window.innerWidth < 768 ? '' : 'Month',
    'margin.l': window.innerWidth < 768 ? 40 : 60,
  });
});
```

---

## Responsive Design Details

### Breakpoints

```css
/* Mobile First */
@media (max-width: 480px) {
  /* Single column layouts */
  .stats-grid { grid-template-columns: 1fr; }
  .hero-layout { flex-direction: column; }
}

@media (max-width: 768px) {
  /* Tablet - 2 columns where possible */
  .sidebar { transform: translateX(-100%); }
  .main-content { margin-left: 0; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 1024px) {
  /* Small laptop - adjust grid columns */
  .grid-main { grid-template-columns: 1fr; }
}

@media (min-width: 1200px) {
  /* Desktop - full layout */
  .stats-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
}
```

### Mobile Adaptations

**Sidebar Navigation**

```css
@media (max-width: 768px) {
  .sidebar {
    width: 280px;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 99;
  }

  .sidebar-overlay.active {
    display: block;
  }

  .menu-toggle {
    display: block;
  }
}
```

**Stat Cards**

```css
@media (max-width: 768px) {
  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 20px;  /* Down from 28px */
  }

  .stat-label {
    font-size: 11px;
  }
}
```

**Hero Card**

```css
@media (max-width: 768px) {
  .hero-layout {
    flex-direction: column;
  }

  .hero-price-box {
    width: 100%;
    text-align: left;
  }

  .hero-action-text {
    font-size: 20px;  /* Down from 24px */
  }
}
```

**Charts**

```css
@media (max-width: 768px) {
  .chart-wrapper {
    min-height: 250px;  /* Down from 350px */
  }
}

@media (max-width: 480px) {
  .chart-wrapper {
    min-height: 220px;
  }
}
```

### Touch-Friendly Interactions

**Minimum Touch Target Sizes**

```css
/* All interactive elements must be at least 44x44px */
.btn {
  min-height: 44px;
  padding: 11px 22px;
}

.nav-item {
  min-height: 44px;
  padding: 11px 16px;
}

.chat-suggestion-btn {
  min-height: 48px;
  padding: 16px;
}
```

**Tap Highlights**

```css
* {
  -webkit-tap-highlight-color: rgba(46, 125, 50, 0.2);
}

a, button {
  touch-action: manipulation;  /* Disable double-tap zoom */
}
```

---

## Performance Optimization

### CSS Optimization

**Minimize Reflows**

```css
/* Use transforms for animations instead of layout properties */
@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**GPU Acceleration**

```css
.card {
  will-change: transform;  /* Hint to browser for GPU acceleration */
}

.sidebar {
  transform: translateZ(0);  /* Force GPU rendering */
}
```

**Critical CSS**
- Inline design tokens in `<head>`
- Load component styles after page render
- Use `preconnect` for Google Fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

### JavaScript Optimization

**Debouncing**

```javascript
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Apply to input-triggered API calls
const debouncedCalculate = debounce(calculateProfit, 500);
document.getElementById('profitQuantity').addEventListener('input', debouncedCalculate);
```

**Lazy Loading**

```javascript
// Load chart library only when needed
async function loadChart() {
  if (!window.Plotly) {
    await loadScript('https://cdn.plot.ly/plotly-2.27.0.min.js');
  }
  renderPriceChart(containerId, data);
}
```

**API Response Caching**

```javascript
const cache = new Map();

async function fetchWithCache(endpoint, params) {
  const key = `${endpoint}?${new URLSearchParams(params)}`;
  if (cache.has(key)) {
    return cache.get(key);
  }
  const data = await API.get(endpoint, params);
  cache.set(key, data);
  return data;
}
```

### Bundle Size Reduction

**Remove Unused CSS**
- Audit CSS with PurgeCSS or manual review
- Remove dark mode styles
- Remove unused design tokens

**Minification**
- Minify CSS with cssnano
- Minify JS with Terser
- Enable gzip compression on server

**Target Sizes**
- `style.css`: <30KB minified + gzipped
- `app.js`: <50KB minified + gzipped
- `charts.js`: <15KB minified + gzipped

---

## Security Considerations

### Input Validation

**Query Parameters**
- Validate crop/state against CONFIG object
- Sanitize target_date format (YYYY-MM)
- Validate quantity/cost as positive numbers

```javascript
function validateCropState(crop, state) {
  if (!crop || !CONFIG[crop]) {
    throw new Error(`Invalid crop: ${crop}`);
  }
  if (!state || !CONFIG[crop].includes(state)) {
    throw new Error(`Invalid state: ${state} for crop ${crop}`);
  }
}
```

**Form Inputs**

```javascript
function validateNumber(value, min = 0, max = Infinity) {
  const num = parseFloat(value);
  if (isNaN(num) || num < min || num > max) {
    throw new Error(`Invalid number: must be between ${min} and ${max}`);
  }
  return num;
}
```

### XSS Prevention

**Escaping User Input**

```javascript
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Use when rendering chat messages
chatBubbleHtml.textContent = escapeHtml(message.text);
```

**Content Security Policy**

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' https://cdn.plot.ly; 
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
               font-src 'self' https://fonts.gstatic.com;
               connect-src 'self' https://api.open-meteo.com;">
```

### API Security

**Rate Limiting** (Backend responsibility - no frontend changes)
- Existing Flask rate limiting preserved

**CORS Configuration** (Backend responsibility - no frontend changes)
- Existing CORS policy preserved

### Third-Party API Security

**Open-Meteo Weather API**
- No authentication required (public API)
- HTTPS only
- Timeout after 5 seconds
- Fallback to "Weather unavailable" on failure

```javascript
async function fetchWeather(state) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  
  try {
    const res = await fetch(weatherUrl, { signal: controller.signal });
    const data = await res.json();
    return parseWeatherData(data);
  } catch (error) {
    console.warn('Weather fetch failed:', error);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}
```

---

## Browser Compatibility

### Supported Browsers

- **Chrome**: 90+ (April 2021)
- **Firefox**: 88+ (April 2021)
- **Safari**: 14+ (September 2020)
- **Edge**: 90+ (April 2021)

### Feature Support

**ES6+ Features Used**
- `async/await` ✅ Supported in all target browsers
- Arrow functions ✅ Supported
- Template literals ✅ Supported
- Destructuring ✅ Supported
- Spread operator ✅ Supported
- `fetch()` API ✅ Supported

**CSS Features Used**
- CSS Grid ✅ Supported (IE 11 requires `-ms-` prefix, but IE 11 not target)
- Flexbox ✅ Supported
- CSS Custom Properties (variables) ✅ Supported
- `calc()` ✅ Supported

### Polyfills (Not Required)

Given our target browser versions, no polyfills are needed. All ES6+ features and CSS capabilities are natively supported.

### Testing Strategy

**Cross-Browser Testing**
1. Chrome (Windows, macOS, Linux)
2. Firefox (Windows, macOS, Linux)
3. Safari (macOS, iOS)
4. Edge (Windows)

**Device Testing**
1. Desktop (1920x1080, 1366x768)
2. Laptop (1440x900, 1280x800)
3. Tablet (iPad 768x1024)
4. Mobile (iPhone 375x667, Android 360x640)

---

## Migration & Rollout Strategy

### Pre-Deployment Checklist

**Code Review**
- [ ] No backend code changes (validate with `git diff`)
- [ ] All API endpoints return expected response format
- [ ] Design tokens meet WCAG AA contrast requirements
- [ ] All images have alt text
- [ ] Form inputs have associated labels

**Testing**
- [ ] All pages load without errors
- [ ] Navigation works on all devices
- [ ] Charts render correctly with real data
- [ ] Weather integration functional
- [ ] AI Assistant processes questions correctly
- [ ] Mobile sidebar opens/closes smoothly
- [ ] Keyboard navigation works
- [ ] Screen reader announces content

**Performance**
- [ ] Initial page load <2 seconds
- [ ] Dashboard data fetch <1 second
- [ ] Page transitions <200ms
- [ ] CSS bundle <30KB gzipped
- [ ] JS bundle <50KB gzipped

### Deployment Steps

1. **Backup Current Frontend**
   ```bash
   cp -r dashboard/templates dashboard/templates.backup
   cp -r dashboard/static dashboard/static.backup
   ```

2. **Deploy New Frontend Files**
   ```bash
   cp new_templates/* dashboard/templates/
   cp new_static/* dashboard/static/
   ```

3. **Restart Flask Server**
   ```bash
   # Stop existing process
   pkill -f "python app.py"
   
   # Start new process
   cd dashboard
   python app.py
   ```

4. **Smoke Test**
   - Visit http://localhost:5000
   - Test all 6 pages
   - Verify API calls succeed
   - Check browser console for errors

5. **Monitor for 24 Hours**
   - Watch error logs
   - Check user feedback
   - Monitor performance metrics

### Rollback Plan

**Trigger Conditions**
- Critical bug affecting >50% users
- API integration broken
- Performance degradation >2x
- Accessibility regression

**Rollback Steps**
1. Stop Flask server
2. Restore backup files
   ```bash
   rm -rf dashboard/templates
   rm -rf dashboard/static
   cp -r dashboard/templates.backup dashboard/templates
   cp -r dashboard/static.backup dashboard/static
   ```
3. Restart Flask server
4. Verify rollback successful
5. Conduct post-mortem

---

## Maintenance & Future Enhancements

### Maintenance Tasks

**Weekly**
- Review error logs
- Check API response times
- Monitor user feedback

**Monthly**
- Update dependencies (Plotly.js)
- Review and optimize CSS/JS bundles
- Test cross-browser compatibility

**Quarterly**
- Accessibility audit
- Performance optimization review
- User experience improvements

### Future Enhancement Ideas

**Phase 2 Features** (Post-Launch)
1. **Export Functionality**
   - Download price charts as PNG
   - Export profit calculations as PDF
   - CSV export of historical data

2. **Personalization**
   - Save favorite crop/state combinations
   - Set price alerts via email/SMS
   - Customize dashboard layout

3. **Advanced Analytics**
   - Multi-crop comparison on single chart
   - Historical forecast accuracy visualization
   - Seasonal pattern analysis

4. **Offline Support**
   - Service worker for offline functionality
   - Cache historical data locally
   - Show last-known data when offline

5. **Multi-Language Support**
   - Hindi translation
   - Regional language options (Gujarati, Marathi, Kannada)

6. **Mobile App**
   - Progressive Web App (PWA)
   - Push notifications for price alerts
   - Add to Home Screen prompt

---

## Documentation Requirements

### User Documentation

**Farmer Guide** (To Be Created)
- How to navigate the dashboard
- Understanding "Should I Sell?" recommendations
- Using the Profit Estimator
- Interpreting MSP alerts
- Asking questions to AI Assistant

**FAQ Section** (To Be Created)
- What is MSP?
- How are predictions calculated?
- Why do prices change?
- What is ensemble prediction?
- How accurate are forecasts?

### Developer Documentation

**README.md Updates**
- Frontend architecture overview
- Design system documentation
- Component usage examples
- API integration guide
- Deployment instructions

**Code Comments**
- JSDoc comments for all functions
- CSS section headers
- Inline comments for complex logic

**API Documentation** (Existing - Preserve)
- Endpoint descriptions
- Request/response formats
- Error codes

---

## Success Metrics

### Launch Metrics (Week 1)

**Adoption**
- 80% of users access dashboard within first week
- Average 3+ pages viewed per session
- <5% bounce rate

**Performance**
- Page load time <2s for 95th percentile
- API response time <1s for 95th percentile
- Zero critical errors

**User Satisfaction**
- Positive feedback from 5+ farmers
- No major usability complaints
- Successful completion of profit calculation

### Long-Term Metrics (Month 1-3)

**Engagement**
- 50% increase in time spent on platform
- 30% increase in pages per session
- 20% increase in return visits

**Feature Usage**
- 60% of users try AI Assistant
- 80% of users view Market Comparison
- 40% of users calculate profit

**Quality**
- Maintain <1% error rate
- Maintain <2s page load time
- Zero accessibility violations

---

## Conclusion

This technical design document outlines a comprehensive frontend transformation strategy for FarmPulse AI. The design preserves 100% of backend functionality while modernizing the UI into a farmer-friendly, production-quality interface.

**Key Achievements**:
- Zero backend changes (validated by design constraints)
- Farmer-centric UX (actionable insights, no ML jargon)
- Production-quality design system
- Full responsive design (mobile-first)
- WCAG AA accessibility compliance
- Performance-optimized (sub-2s loads)

**Implementation Timeline**: 6 weeks across 12 phases

**Risk Mitigation**: Incremental rollout, comprehensive testing, rollback plan

This design is ready for implementation and provides a solid foundation for transforming FarmPulse AI into a polished, professional agricultural intelligence platform.

