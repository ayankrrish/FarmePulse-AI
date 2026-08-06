# Implementation Plan: FarmPulse AI Dashboard Transformation

## Overview

This plan transforms the FarmPulse AI frontend into a farmer-friendly, production-quality interface while preserving 100% of backend functionality. Implementation uses **HTML, CSS, and JavaScript** (no React/Next.js), staying within the existing Flask + vanilla JS stack.

**Technology Stack:**
- Frontend: HTML5, CSS3, Vanilla JavaScript, Plotly.js
- Backend: Flask (UNCHANGED — no modifications to routes, services, models)
- Implementation Language: JavaScript for frontend, Python for backend (unchanged)

**Critical Constraint:** ZERO backend changes. All tasks modify only `/dashboard/templates/`, `/dashboard/static/css/`, and `/dashboard/static/js/`.

## Tasks

- [ ] 1. Phase 1: Design System Foundation
  - [ ] 1.1 Create CSS design tokens and variables
    - Define color palette (green-800, emerald, amber, rose, blue as CSS custom properties)
    - Define spacing scale (4px, 8px, 16px, 24px, 32px, 48px)
    - Define typography (Inter font family, JetBrains Mono for numbers)
    - Define border radius, shadows, and transitions
    - File: `dashboard/static/css/style.css` (first 200 lines)
    - _Requirements: 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9_

  - [ ] 1.2 Build base component styles (cards, buttons, forms, badges)
    - Implement card component (border, shadow, border-radius, padding, hover)
    - Implement button styles (btn-primary, btn-ghost with hover states)
    - Implement form input styles (text inputs, select dropdowns, focus states)
    - Implement badge/tag styles (color-coded: green, amber, rose)
    - Implement alert card styles (left-border color-coded alerts)
    - File: `dashboard/static/css/style.css` (component section)
    - _Requirements: 13.2, 13.3, 13.8, 10.6_

  - [ ] 1.3 Create stat card component styles
    - Implement stat card grid layout (auto-fit minmax(200px, 1fr))
    - Create stat card with top color bar (3px gradient)
    - Style stat label, value (28px mono font), and change indicator
    - Add staggered entrance animation (cardIn keyframe with delays)
    - File: `dashboard/static/css/style.css` (stat cards section)
    - _Requirements: 2.7, 13.3, 13.4_

  - [ ] 1.4 Test design system in isolation
    - Create sample HTML snippets for each component
    - Test color contrast ratios (WCAG AA 4.5:1 for text)
    - Verify animations are smooth (150ms-400ms transitions)
    - Test in Chrome, Firefox, Safari, Edge
    - File: Create temporary `_design_test.html` in templates folder
    - _Requirements: 13.2, 13.3, 18.5, 20.2_

- [ ] 2. Phase 2: Navigation & Layout Structure
  - [ ] 2.1 Build sidebar navigation component
    - Implement sidebar HTML structure (logo, nav items, footer)
    - Style logo section with icon and FarmPulse AI branding
    - Create nav-item styles (icon + text, hover, active states)
    - Add sidebar footer with version display
    - Files: `dashboard/templates/index.html`, `dashboard/static/css/style.css`
    - _Requirements: 9.1, 9.5, 9.6, 9.9_

  - [ ] 2.2 Implement page header with controls
    - Create sticky page header (position: sticky, top: 0, z-index: 50)
    - Add page title and subtitle (dynamic, updates on navigation)
    - Implement controls bar (crop select, state select, date picker)
    - Style select dropdowns with custom arrow indicator
    - Files: `dashboard/templates/index.html`, `dashboard/static/css/style.css`
    - _Requirements: 9.1, 9.9, 12.5, 13.6_

  - [ ] 2.3 Create page section containers and routing
    - Implement page-section divs for all 6 pages (dashboard, forecast, profit, alerts, comparison, assistant)
    - Add active class toggle logic (show/hide sections)
    - Create JavaScript navigation function (navigateTo)
    - Update page title/subtitle on navigation
    - Remove Weather page from navigation (weather embedded in Dashboard)
    - Files: `dashboard/templates/index.html`, `dashboard/static/js/app.js`
    - _Requirements: 3.8, 9.1, 9.2, 9.4, 9.9_

  - [ ] 2.4 Add mobile hamburger menu and overlay
    - Create hamburger button (hidden on desktop, visible <768px)
    - Implement sidebar transform: translateX(-100%) on mobile
    - Add dark overlay (rgba(0,0,0,0.4)) behind open sidebar
    - Add click handlers for hamburger, overlay, and nav items
    - Files: `dashboard/templates/index.html`, `dashboard/static/css/style.css`, `dashboard/static/js/app.js`
    - _Requirements: 9.8, 12.2, 12.5, 12.6_

  - [ ]* 2.5 Write integration tests for navigation
    - Test navigation between all 6 pages
    - Test page title/subtitle updates correctly
    - Test active nav-item highlighting
    - Test mobile sidebar open/close
    - Test overlay closes sidebar on click
    - _Requirements: 9.1, 9.3, 9.4, 9.8_

- [ ] 3. Phase 3: Dashboard Page — Hero Card & Quick Insights
  - [ ] 3.1 Build hero card ("Should I Sell?") component
    - Create hero-card HTML structure with flex layout
    - Display recommendation icon and primary_action text
    - Show action_detail paragraph with explanation
    - Add risk_level and trend_direction tags
    - Display predicted price in highlighted box with color coding (green/amber/red)
    - Implement left-border color based on recommendation
    - Files: `dashboard/templates/index.html`, `dashboard/static/js/app.js` (renderDashboard function)
    - _Requirements: 2.1, 2.2, 2.3, 2.7, 2.9_

  - [ ] 3.2 Create stat cards grid for quick insights
    - Build stats-grid container (auto-fit minmax(200px, 1fr))
    - Create "Today's Mandi Price" card (green, current_price)
    - Create "Expected Market Price" card (emerald, predicted_price, change_pct)
    - Create "MSP Safety" card (color-coded by alert_level, msp, difference)
    - Create "Price Trend" card (blue, trend icon: 📈📉➡️)
    - Add staggered animation delays (0.05s, 0.1s, 0.15s, 0.2s)
    - Files: `dashboard/static/js/app.js` (renderDashboard function)
    - _Requirements: 2.3, 2.4, 2.5, 2.6, 2.7, 2.9_

  - [ ] 3.3 Fetch and render dashboard data from API
    - Call `/api/dashboard_summary` endpoint
    - Parse response JSON (crop, state, current_price, predicted_price, msp_alert, recommendation)
    - Populate hero card with recommendation data
    - Populate stat cards with metrics
    - Handle loading state (spinner) and error state
    - Files: `dashboard/static/js/app.js` (loadDashboard function, API.getDashboard)
    - _Requirements: 2.9, 2.10, 14.2, 17.1, 17.2, 17.3, 17.4_

  - [ ]* 3.4 Write unit tests for dashboard rendering
    - Test hero card renders with correct action text
    - Test stat cards display correct values
    - Test color-coding logic (green/amber/red)
    - Test loading and error states
    - _Requirements: 2.1, 2.3, 2.7, 17.1, 17.5_

- [ ] 4. Checkpoint — Ensure navigation and dashboard load correctly
  - Verify navigation between pages works smoothly
  - Verify dashboard loads with real API data
  - Verify stat cards display correctly
  - Ask user if questions arise

- [ ] 5. Phase 4: Weather Integration into Dashboard
  - [ ] 5.1 Create weather widget component HTML structure
    - Build weather-card container with gradient background
    - Create weather-top section (location, temperature, icon)
    - Add weather detail rows (humidity, wind, rain probability)
    - Add weather-advice section with farming tips
    - Files: `dashboard/static/css/style.css` (weather widget section), `dashboard/static/js/app.js`
    - _Requirements: 3.1, 3.3, 3.4, 3.9_

  - [ ] 5.2 Implement Open-Meteo weather API integration
    - Create state-to-coordinates mapping (Gujarat: {lat: 23.0, lon: 72.6, city: 'Ahmedabad'}, etc.)
    - Build fetchWeather function with Open-Meteo API URL
    - Parse weather response (temperature_2m, relative_humidity_2m, wind_speed_10m, weather_code, precipitation_probability_max)
    - Implement weatherIcon function (code → emoji mapping)
    - Implement weatherAdvice function (rain/temp thresholds → farming advice)
    - Handle API timeout (5 seconds) and errors gracefully
    - Files: `dashboard/static/js/app.js`
    - _Requirements: 3.3, 3.5, 3.6, 3.7, 17.8_

  - [ ] 5.3 Integrate weather widget into dashboard layout
    - Embed weather widget in dashboard grid (two-column: chart + weather)
    - Call fetchWeather in loadDashboard function
    - Render weather data if available, fallback message if not
    - Update dashboard layout to grid-main (2fr 1fr on desktop, 1fr on mobile)
    - Files: `dashboard/static/js/app.js` (renderDashboard function)
    - _Requirements: 3.1, 3.2, 3.6, 3.8, 3.9_

  - [ ]* 5.4 Write integration tests for weather widget
    - Test Open-Meteo API call success
    - Test weather data parsing and display
    - Test fallback message on API failure
    - Test weatherAdvice logic for different conditions
    - _Requirements: 3.3, 3.5, 3.6, 17.8_

- [ ] 6. Phase 5: Price History & Forecast Chart
  - [ ] 6.1 Create chart helper function with Plotly.js
    - Build renderPriceChart function (takes containerId, data)
    - Create historical price trace (green line, mode: 'lines+markers')
    - Create forecast price trace (emerald dashed line, mode: 'lines+markers')
    - Create MSP reference line (amber dotted horizontal line)
    - Configure layout (xaxis: 'Month', yaxis: 'Price (₹/quintal)', hovermode: 'x unified')
    - Configure responsive settings (responsive: true, displayModeBar: true)
    - Files: `dashboard/static/js/charts.js` (new file)
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 16.10_

  - [ ] 6.2 Integrate chart into dashboard page
    - Add chart-container div in dashboard HTML
    - Call renderPriceChart in renderDashboard function after DOM update
    - Pass history, forecast_path, forecast_labels, and msp from API response
    - Handle mobile responsive height (350px desktop, 250px mobile)
    - Files: `dashboard/static/js/app.js`, `dashboard/templates/index.html`
    - _Requirements: 2.4, 2.5, 16.1, 16.9_

  - [ ]* 6.3 Write unit tests for chart rendering
    - Test chart renders with historical and forecast data
    - Test MSP line displays correctly
    - Test hover tooltips show correct data
    - Test responsive behavior on mobile
    - _Requirements: 16.1, 16.2, 16.4, 16.5, 16.9_

- [ ] 7. Checkpoint — Verify complete dashboard functionality
  - Ensure all dashboard components render correctly
  - Verify weather widget displays real data
  - Verify chart shows historical and forecast lines
  - Ask user if questions arise

- [ ] 8. Phase 6: Price Forecast Page Simplification
  - [ ] 8.1 Build AI suggestion card for forecast page
    - Create rec-card HTML structure with AI icon
    - Generate plain-language suggestion text based on change_pct
    - Display prediction explanation ("Prices expected to rise by X%")
    - Hide ML engineering details (model weights, RMSE, MAE)
    - Files: `dashboard/static/js/app.js` (renderForecast function)
    - _Requirements: 4.1, 4.2, 4.3, 4.7, 11.1, 11.7_

  - [ ] 8.2 Create forecast stat cards (current, predicted, MSP, confidence)
    - Build stats-grid with 4 cards
    - Display "Today's Mandi Price" (current_price)
    - Display "Expected Market Price" (ensemble_price, change_pct)
    - Display "MSP (Safety Net)" (msp)
    - Display "Forecast Confidence" (confidence as percentage with visual meter)
    - Files: `dashboard/static/js/app.js` (renderForecast function)
    - _Requirements: 4.2, 4.4, 4.5, 4.6, 11.2, 11.4_

  - [ ] 8.3 Integrate forecast chart with history and prediction
    - Add chart-container div in forecast page HTML
    - Call renderPriceChart with ensemble forecast data
    - Display confidence_per_step if available
    - Use target_date selection from date picker
    - Files: `dashboard/static/js/app.js` (loadForecast, renderForecast functions)
    - _Requirements: 4.4, 4.9, 4.10, 14.3_

  - [ ]* 8.4 Implement optional developer mode toggle
    - Add ?dev=true query parameter detection
    - Show ML engineering details when dev mode enabled (model weights, individual predictions, RMSE, MAE)
    - Hide details in default farmer mode
    - Use sessionStorage to persist dev mode across pages
    - Files: `dashboard/static/js/app.js`
    - _Requirements: 4.8, 15.1, 15.2, 15.3, 15.6, 15.7, 15.9_

  - [ ]* 8.5 Write unit tests for forecast page
    - Test AI suggestion text generation
    - Test confidence meter display
    - Test dev mode toggle
    - Test forecast chart with multi-step predictions
    - _Requirements: 4.1, 4.4, 4.5, 15.1_

- [ ] 9. Phase 7: Profit Estimator UI Redesign
  - [ ] 9.1 Build profit input form
    - Create profit-form HTML (quantity quintals, production cost inputs)
    - Style form inputs with labels and placeholders
    - Add real-time calculation on input change (debounced 500ms)
    - Add "Calculate Profit" button (full-width, primary style)
    - Files: `dashboard/static/js/app.js` (loadProfit function)
    - _Requirements: 5.1, 5.9, 5.10, 17.10_

  - [ ] 9.2 Create profit results grid with visual cards
    - Build profit-results grid (auto-fit minmax(200px, 1fr))
    - Display "Current Revenue" card
    - Display "Predicted Revenue" card (green highlight)
    - Display "Difference" card (show amount and percentage)
    - Display "MSP Revenue" card
    - Display "Total Cost", "Current Profit", "Predicted Profit" cards if cost provided
    - Files: `dashboard/static/js/app.js` (renderProfitResults function)
    - _Requirements: 5.2, 5.3, 5.4, 5.6, 11.10_

  - [ ] 9.3 Implement "Best Option" recommendation card
    - Calculate best option logic (compare current, predicted, MSP revenue)
    - Display recommendation card with icon and action text
    - Show explanation detail ("Predicted revenue is highest...")
    - Highlight card with emerald border
    - Files: `dashboard/static/js/app.js` (renderProfitResults function)
    - _Requirements: 5.5, 5.7, 11.5_

  - [ ] 9.4 Connect profit estimator to API endpoint
    - Call `/api/profit_estimate` with crop, state, quantity, cost parameters
    - Parse response (current_revenue, predicted_revenue, msp_revenue, revenue_difference, revenue_difference_pct, total_cost, current_profit, predicted_profit)
    - Update UI on input change without page reload
    - Handle error states gracefully
    - Files: `dashboard/static/js/app.js` (calculateProfit function, API.getProfitEstimate)
    - _Requirements: 5.8, 5.9, 14.7, 17.3, 17.4_

  - [ ]* 9.5 Write unit tests for profit calculator
    - Test revenue calculations with different quantity values
    - Test profit calculations with cost provided
    - Test best option logic (sell/wait/MSP)
    - Test real-time recalculation
    - _Requirements: 5.2, 5.3, 5.5, 5.9_

- [ ] 10. Checkpoint — Verify forecast and profit pages functional
  - Test forecast page shows AI suggestion and confidence
  - Test profit calculator calculates correctly
  - Test best option recommendation displays
  - Ask user if questions arise

- [ ] 11. Phase 8: MSP Alerts Card Layout
  - [ ] 11.1 Build MSP alert card component
    - Create card grid layout (auto-fit minmax(220px, 1fr))
    - Display crop name and state in card header
    - Show alert icon and status badge (green/yellow/red)
    - Display current price, MSP, and difference
    - Show trend and recommendation text
    - Add left-border color coding (4px solid emerald/amber/rose)
    - Files: `dashboard/static/js/app.js` (renderAlerts function)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.10_

  - [ ] 11.2 Fetch MSP alerts for all crops
    - Loop through all crops in CONFIG
    - Call `/api/msp_alert` for each crop/state combination
    - Collect alert data (alert_level, message, icon, recommendation, current_price, predicted_price, msp, difference, trend)
    - Handle missing states gracefully
    - Files: `dashboard/static/js/app.js` (loadAlerts function)
    - _Requirements: 6.6, 6.9, 14.5_

  - [ ] 11.3 Add staggered entrance animations for alert cards
    - Apply animation-delay to each card (0.08s increments)
    - Use cardIn keyframe (opacity: 0→1, translateY(6px)→0)
    - Ensure smooth 400ms animation duration
    - Files: `dashboard/static/css/style.css`, `dashboard/static/js/app.js`
    - _Requirements: 6.8, 13.3_

  - [ ]* 11.4 Write unit tests for MSP alerts
    - Test alert level color coding (green/amber/red)
    - Test icon display (✅⚠️❌)
    - Test message and recommendation text
    - Test animation timing
    - _Requirements: 6.1, 6.2, 6.3, 6.8_

- [ ] 12. Phase 9: Market Comparison Visual Redesign
  - [ ] 12.1 Build market comparison summary cards
    - Create stats-grid with 3 summary cards
    - Display "Best Market" card (state name, predicted price)
    - Display "Price Spread" card (max - min, number of markets)
    - Display "Overall Trend" card (rising/falling/stable with icon)
    - Files: `dashboard/static/js/app.js` (renderComparison function)
    - _Requirements: 7.2, 7.10_

  - [ ] 12.2 Create top 5 markets card grid
    - Build market-cards grid (auto-fit minmax(220px, 1fr))
    - Display rank badge (#1 gold, #2 silver, #3 bronze, others gray)
    - Show state name, predicted price, today's price, change percentage, trend icon
    - Add market-detail-row for each metric
    - Apply staggered entrance animations (0.05s increments)
    - Files: `dashboard/static/js/app.js` (renderComparison function)
    - _Requirements: 7.1, 7.3, 7.4, 7.5, 7.9, 7.10_

  - [ ] 12.3 Add full market comparison table
    - Create comparison-table HTML (thead with column headers, tbody with market rows)
    - Display rank, state, today's price, expected price, change percentage
    - Add hover highlight on table rows
    - Show table only if more than 5 markets available
    - Files: `dashboard/static/js/app.js` (renderComparison function)
    - _Requirements: 7.6, 7.7_

  - [ ] 12.4 Connect to market comparison API endpoint
    - Call `/api/market_comparison` with crop parameter
    - Parse response (markets array, best_market, price_spread, num_markets, overall_trend)
    - Sort markets by rank
    - Handle empty markets array
    - Files: `dashboard/static/js/app.js` (loadComparison function, API.getMarketComparison)
    - _Requirements: 7.8, 14.6_

  - [ ]* 12.5 Write unit tests for market comparison
    - Test rank badge styling (gold/silver/bronze)
    - Test top 5 cards display
    - Test full table rendering
    - Test trend icon display
    - _Requirements: 7.1, 7.3, 7.4, 7.5_

- [ ] 13. Checkpoint — Verify alerts and comparison pages work
  - Test MSP alerts show color-coded cards
  - Test market comparison shows top 5 markets
  - Test rank badges display correctly
  - Ask user if questions arise

- [ ] 14. Phase 10: AI Assistant ChatGPT Interface
  - [ ] 14.1 Build chat message container and bubbles
    - Create chat-container HTML (messages area, input area)
    - Implement chat-msg structure (avatar, bubble, timestamp)
    - Style AI messages (left-aligned, white bubble)
    - Style user messages (right-aligned, green bubble)
    - Add chat-avatar styling (AI: ✨, User: 👤)
    - Files: `dashboard/templates/index.html`, `dashboard/static/css/style.css`
    - _Requirements: 8.1, 8.7, 8.8_

  - [ ] 14.2 Create quick prompt buttons
    - Build chat-suggestions-grid (2 columns on desktop, 1 on mobile)
    - Add 5 quick prompt buttons ("Should I sell today?", "Which state gives best price?", "What is MSP?", "Profit for 10 quintals", "Today's weather")
    - Style buttons with icon + text
    - Add click handlers to populate input and send message
    - Files: `dashboard/static/js/app.js` (renderAssistant function)
    - _Requirements: 8.2, 8.3_

  - [ ] 14.3 Implement message input and send functionality
    - Create chat-input textarea with send button
    - Add Enter key handler (send on Enter, Shift+Enter for newline)
    - Implement sendChat function (append user message, call API, append AI response)
    - Add typing indicator (three bouncing dots) while processing
    - Auto-scroll to latest message
    - Files: `dashboard/static/js/app.js` (sendChat, scrollChat functions)
    - _Requirements: 8.3, 8.6, 8.9_

  - [ ] 14.4 Implement question processing logic
    - Create processQuestion function with keyword detection
    - Handle "sell" questions → call `/api/recommendation`
    - Handle "msp" questions → call `/api/msp_alert`
    - Handle "best state" questions → call `/api/market_comparison`
    - Handle "profit" questions → call `/api/profit_estimate`
    - Handle "price/forecast" questions → call `/api/dashboard_summary`
    - Handle "weather" questions → call fetchWeather function
    - Return contextual responses in plain language
    - Files: `dashboard/static/js/app.js` (processQuestion function)
    - _Requirements: 8.3, 8.4, 8.5, 11.5_

  - [ ] 14.5 Add disclaimer and message timestamps
    - Display disclaimer text below input ("AI uses real FarmPulse data. Predictions are estimates — not financial advice.")
    - Show message timestamps (HH:MM format)
    - Add chat-time styling
    - Files: `dashboard/static/js/app.js` (chatBubbleHtml function)
    - _Requirements: 8.7, 8.10_

  - [ ]* 14.6 Write integration tests for AI assistant
    - Test quick prompt buttons populate input
    - Test question processing logic (keyword detection)
    - Test API calls for different question types
    - Test typing indicator display
    - Test auto-scroll functionality
    - _Requirements: 8.2, 8.3, 8.4, 8.6, 8.9_

- [ ] 15. Phase 11: Responsive Design Implementation
  - [ ] 15.1 Implement mobile breakpoints (<768px)
    - Add @media (max-width: 768px) styles
    - Sidebar: transform: translateX(-100%), width: 280px
    - Sidebar overlay: display when sidebar open
    - Menu toggle: display: block (hamburger button)
    - Stats-grid: grid-template-columns: 1fr 1fr (2 columns)
    - Main content: margin-left: 0
    - Files: `dashboard/static/css/style.css`
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.8_

  - [ ] 15.2 Adjust layouts for tablet breakpoints (<1024px)
    - Add @media (max-width: 1024px) styles
    - Grid-2: grid-template-columns: 1fr (single column)
    - Grid-3: grid-template-columns: 1fr 1fr (2 columns)
    - Grid-main: grid-template-columns: 1fr (single column)
    - Market-cards: grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))
    - Files: `dashboard/static/css/style.css`
    - _Requirements: 12.1, 12.8_

  - [ ] 15.3 Optimize for mobile screens (<480px)
    - Add @media (max-width: 480px) styles
    - Stats-grid: grid-template-columns: 1fr (single column)
    - Stat-value: font-size: 20px (down from 28px)
    - Page-title: font-size: 20px
    - Hero-layout: flex-direction: column
    - Chart-wrapper: min-height: 220px
    - Market-cards: grid-template-columns: 1fr
    - Files: `dashboard/static/css/style.css`
    - _Requirements: 12.1, 12.3, 12.4, 12.7, 12.8_

  - [ ] 15.4 Ensure touch-friendly interaction sizes
    - Set minimum touch target sizes (44px × 44px)
    - Button min-height: 44px
    - Nav-item min-height: 44px
    - Chat-suggestion-btn min-height: 48px
    - Add -webkit-tap-highlight-color styling
    - Add touch-action: manipulation to buttons
    - Files: `dashboard/static/css/style.css`
    - _Requirements: 12.5, 12.9_

  - [ ]* 15.5 Test responsive design across devices
    - Test on desktop (1920×1080, 1366×768)
    - Test on tablet (768×1024)
    - Test on mobile (375×667, 360×640)
    - Verify no horizontal scrolling on any screen size
    - Verify all interactive elements are touch-friendly
    - _Requirements: 12.1, 12.6, 12.9, 12.10_

- [ ] 16. Phase 12: Accessibility Implementation
  - [ ] 16.1 Add semantic HTML5 elements
    - Use <header>, <nav>, <main>, <section>, <article> tags
    - Add aria-label to navigation ("Main navigation")
    - Add aria-current="page" to active nav item
    - Add role="status" aria-live="polite" to loading overlays
    - Files: `dashboard/templates/index.html`
    - _Requirements: 18.1, 18.3_

  - [ ] 16.2 Provide alt text and ARIA labels
    - Add aria-label to all interactive elements (buttons, inputs, selects)
    - Add alt text to logo icon
    - Add aria-expanded to hamburger menu button
    - Add descriptive link text (avoid "click here")
    - Files: `dashboard/templates/index.html`
    - _Requirements: 18.2, 18.3, 18.7_

  - [ ] 16.3 Ensure keyboard navigation support
    - Test Tab key navigation through all interactive elements
    - Ensure Enter key activates buttons and links
    - Ensure Escape key closes mobile sidebar
    - Add skip navigation link
    - Verify focus indicators are visible (3px outline, outline-offset: 2px)
    - Files: `dashboard/templates/index.html`, `dashboard/static/css/style.css`, `dashboard/static/js/app.js`
    - _Requirements: 18.4, 18.6, 18.8_

  - [ ] 16.4 Verify color contrast ratios
    - Check text-primary (#1a2e1a) on bg-page (#f0f5f1) — ensure 4.5:1 minimum
    - Check text-secondary (#4a6a4a) on bg-card (#ffffff) — ensure 4.5:1 minimum
    - Check button text on green-800 background — ensure 4.5:1 minimum
    - Use WebAIM contrast checker or browser DevTools
    - Files: `dashboard/static/css/style.css`
    - _Requirements: 13.2, 18.5_

  - [ ] 16.5 Add form input labels and accessibility attributes
    - Ensure all form inputs have associated <label> elements
    - Add autocomplete="off" where appropriate
    - Add required and aria-required attributes as needed
    - Files: `dashboard/templates/index.html`
    - _Requirements: 18.9_

  - [ ]* 16.6 Test with screen reader (NVDA or JAWS)
    - Install NVDA or JAWS
    - Navigate through all pages with screen reader
    - Verify all content is announced correctly
    - Verify form inputs are properly labeled
    - _Requirements: 18.1, 18.2, 18.3, 18.9, 18.10_

- [ ] 17. Checkpoint — Test responsive and accessibility compliance
  - Test mobile sidebar on <768px screens
  - Test touch targets on mobile devices
  - Test keyboard navigation (Tab, Enter, Escape)
  - Test color contrast ratios (WCAG AA 4.5:1)
  - Ask user if questions arise

- [ ] 18. Phase 13: Loading States & Error Handling
  - [ ] 18.1 Add loading spinners for async operations
    - Create loading-overlay HTML (spinner + descriptive text)
    - Add spinner CSS (rotating border animation)
    - Display loading state in each page section on load
    - Remove loading overlay once data fetched
    - Files: `dashboard/templates/index.html`, `dashboard/static/css/style.css`, `dashboard/static/js/app.js`
    - _Requirements: 17.1, 17.2, 17.7_

  - [ ] 18.2 Implement error cards for API failures
    - Create error-card HTML structure
    - Display error icon (⚠️), title, and message
    - Add retry button
    - Style error card with rose color scheme
    - Files: `dashboard/static/js/app.js` (error handling in API calls)
    - _Requirements: 17.4, 17.5_

  - [ ] 18.3 Add graceful degradation for missing data
    - Weather API fails → show "Weather data unavailable" message
    - Empty state data → show "No data found" message
    - Missing forecast → fall back to current price display
    - Handle null/undefined values in all render functions
    - Files: `dashboard/static/js/app.js`
    - _Requirements: 3.6, 17.3, 17.4_

  - [ ]* 18.4 Write error handling tests
    - Test network error handling
    - Test empty data state handling
    - Test API timeout handling
    - Test retry button functionality
    - _Requirements: 17.3, 17.4, 17.5_

- [ ] 19. Phase 14: Data Freshness Indicators
  - [ ] 19.1 Display "Last Updated" timestamps
    - Add last-updated display on dashboard (format: "Last Updated: YYYY-MM-DD")
    - Show data source attribution ("Source: CEDA Agmarknet")
    - Display weather data timestamp
    - Add data freshness indicator for stale data (older than 7 days)
    - Files: `dashboard/static/js/app.js` (renderDashboard, renderForecast functions)
    - _Requirements: 19.1, 19.2, 19.4, 19.6, 19.8_

  - [ ] 19.2 Add refresh on crop/state selection
    - Trigger data fetch when crop select changes
    - Trigger data fetch when state select changes
    - Display loading state during refresh
    - Files: `dashboard/static/js/app.js` (event listeners for selects)
    - _Requirements: 19.3, 19.7_

  - [ ]* 19.3 Log data fetch timestamps
    - Add console.log for data fetch events
    - Log timestamp on successful API responses
    - Log timestamp on API errors
    - Files: `dashboard/static/js/app.js`
    - _Requirements: 19.9, 19.10_

- [ ] 20. Phase 15: Polish & Performance Optimization
  - [ ] 20.1 Add smooth animations and transitions
    - Card entrance animation (cardIn keyframe: opacity 0→1, translateY 6px→0, 400ms ease)
    - Page transition animation (pageIn keyframe: opacity 0→1, translateY 10px→0, 300ms ease)
    - Button hover transitions (150ms ease)
    - Sidebar slide transition (250ms ease)
    - Hover lift effect on cards (translateY -2px, shadow-md, 250ms ease)
    - Files: `dashboard/static/css/style.css`
    - _Requirements: 13.3, 13.10_

  - [ ] 20.2 Optimize CSS and JavaScript bundles
    - Remove unused CSS styles
    - Minify CSS with cssnano
    - Minify JavaScript with Terser
    - Verify CSS bundle <30KB gzipped
    - Verify JS bundle <50KB gzipped
    - Files: Build process or manual minification
    - _Requirements: 17.8, 17.9_

  - [ ] 20.3 Optimize Plotly chart rendering
    - Use Plotly.newPlot with config {responsive: true}
    - Minimize layout reflows during chart updates
    - Use requestAnimationFrame for chart rendering
    - Add chart loading skeleton
    - Files: `dashboard/static/js/charts.js`
    - _Requirements: 17.7, 17.8_

  - [ ] 20.4 Test cross-browser compatibility
    - Test in Chrome 90+ (Windows, macOS, Linux)
    - Test in Firefox 88+ (Windows, macOS, Linux)
    - Test in Safari 14+ (macOS, iOS)
    - Test in Edge 90+ (Windows)
    - Verify CSS Grid, Flexbox, and fetch API work in all browsers
    - Files: Manual testing
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6_

  - [ ]* 20.5 Performance testing
    - Measure initial page load time (target: <2s)
    - Measure dashboard data fetch time (target: <1s)
    - Measure page transition time (target: <200ms)
    - Measure chart render time (target: <500ms)
    - Use Chrome DevTools Performance tab
    - Files: Manual testing
    - _Requirements: 17.1, 17.2, 17.7, 17.8_

- [ ] 21. Final Checkpoint — Complete System Testing
  - Test all 6 pages load correctly with real API data
  - Test mobile responsiveness on multiple devices
  - Test keyboard navigation and accessibility
  - Test cross-browser compatibility
  - Verify ZERO backend changes (git diff on app.py, services/)
  - Ask user if final issues need addressing

- [ ] 22. Deployment Preparation
  - [ ] 22.1 Create backup of current frontend
    - Copy dashboard/templates to dashboard/templates.backup
    - Copy dashboard/static to dashboard/static.backup
    - Document backup location
    - _Requirements: Deployment safety_

  - [ ] 22.2 Update README with frontend transformation notes
    - Document new design system
    - Document component structure
    - Document API integration points
    - Add browser compatibility notes
    - Files: `README.md`
    - _Requirements: Documentation_

  - [ ]* 22.3 Create deployment checklist
    - List pre-deployment verification steps
    - List rollback procedures
    - List monitoring steps
    - Document error handling procedures
    - Files: `docs/DEPLOYMENT.md` (new file)
    - _Requirements: Deployment safety_


## Notes

### Implementation Guidelines

1. **Frontend-Only Transformation**
   - All tasks modify ONLY frontend files: `/dashboard/templates/`, `/dashboard/static/css/`, `/dashboard/static/js/`
   - Backend files (`app.py`, `services/`, `models/`) remain UNTOUCHED
   - Verify with `git diff` before committing

2. **Technology Stack**
   - HTML5, CSS3, Vanilla JavaScript (no frameworks)
   - Plotly.js for charts (already included)
   - Open-Meteo API for weather data
   - Flask backend APIs (unchanged)

3. **Testing Strategy**
   - Tasks marked with `*` are optional test tasks
   - Optional tasks can be skipped for faster MVP
   - Each checkpoint validates core functionality before proceeding

4. **Responsive Breakpoints**
   - Mobile: <480px (single column)
   - Tablet: <768px (2 columns, collapsed sidebar)
   - Laptop: <1024px (adjusted grids)
   - Desktop: ≥1200px (full layout)

5. **Accessibility Requirements**
   - WCAG AA compliance (4.5:1 contrast ratio)
   - Keyboard navigation (Tab, Enter, Escape)
   - Screen reader support (semantic HTML, ARIA labels)
   - Touch-friendly targets (44px minimum)

6. **Performance Targets**
   - Initial page load: <2 seconds
   - API response time: <1 second
   - Page transitions: <200ms
   - Chart rendering: <500ms
   - CSS bundle: <30KB gzipped
   - JS bundle: <50KB gzipped

7. **Color Coding System**
   - **Green/Emerald**: Positive indicators (above MSP, profit, safe)
   - **Amber**: Caution indicators (near MSP, wait decision)
   - **Rose**: Danger indicators (below MSP, falling prices)
   - **Blue**: Informational (trend, confidence)

8. **Farmer-Friendly Terminology**
   - Use "Today's Mandi Price" NOT "Current Price"
   - Use "Expected Market Price" NOT "Ensemble Prediction"
   - Use "MSP Safety" NOT "MSP Alert Level"
   - Use "Forecast Confidence" NOT "Model Agreement Score"
   - Avoid ML jargon: LSTM, ensemble, RMSE, MAE, feature engineering

9. **API Endpoints (Unchanged)**
   - `/api/config` — Crop/state configuration
   - `/api/dashboard_summary` — Dashboard data
   - `/api/ensemble_predict` — Price forecast
   - `/api/recommendation` — Sell/wait decision
   - `/api/msp_alert` — MSP safety check
   - `/api/market_comparison` — Cross-state comparison
   - `/api/profit_estimate` — Revenue calculation
   - `/api/model_metrics` — ML metrics (dev mode only)

10. **Critical Constraints**
    - NO modifications to `/dashboard/app.py` routes
    - NO modifications to `/dashboard/services/` files
    - NO modifications to `/models/` or `/data/` directories
    - Backend API contracts MUST remain unchanged
    - All existing API response formats preserved

### Requirements Coverage

- **Requirement 1 (Architecture Preservation)**: Tasks verify zero backend changes
- **Requirement 2 (Dashboard Redesign)**: Tasks 3.1-3.3, 5.1-5.3, 6.1-6.2
- **Requirement 3 (Weather Integration)**: Tasks 5.1-5.3
- **Requirement 4 (Forecast Simplification)**: Tasks 8.1-8.3
- **Requirement 5 (Profit Estimator)**: Tasks 9.1-9.4
- **Requirement 6 (MSP Alerts)**: Tasks 11.1-11.3
- **Requirement 7 (Market Comparison)**: Tasks 12.1-12.4
- **Requirement 8 (AI Assistant)**: Tasks 14.1-14.5
- **Requirement 9 (Navigation)**: Tasks 2.1-2.4
- **Requirement 10 (Single Theme)**: Task 1.1
- **Requirement 11 (Terminology)**: All render functions
- **Requirement 12 (Responsive)**: Tasks 15.1-15.4
- **Requirement 13 (Production Quality)**: Tasks 1.1-1.4, 13.1-13.10, 20.1
- **Requirement 14 (API Preservation)**: All API calls unchanged
- **Requirement 15 (Developer Mode)**: Task 8.4
- **Requirement 16 (Charts)**: Tasks 6.1-6.2
- **Requirement 17 (Performance)**: Tasks 18.1-18.3, 20.2-20.5
- **Requirement 18 (Accessibility)**: Tasks 16.1-16.6
- **Requirement 19 (Data Freshness)**: Tasks 19.1-19.2
- **Requirement 20 (Cross-Browser)**: Task 20.4


## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1.1", "1.2", "1.3"]
    },
    {
      "id": 1,
      "tasks": ["1.4", "2.1", "2.2"]
    },
    {
      "id": 2,
      "tasks": ["2.3", "2.4", "2.5"]
    },
    {
      "id": 3,
      "tasks": ["3.1", "3.2", "5.1"]
    },
    {
      "id": 4,
      "tasks": ["3.3", "3.4", "5.2"]
    },
    {
      "id": 5,
      "tasks": ["5.3", "5.4", "6.1"]
    },
    {
      "id": 6,
      "tasks": ["6.2", "6.3"]
    },
    {
      "id": 7,
      "tasks": ["8.1", "8.2", "8.3"]
    },
    {
      "id": 8,
      "tasks": ["8.4", "8.5", "9.1", "9.2"]
    },
    {
      "id": 9,
      "tasks": ["9.3", "9.4", "9.5"]
    },
    {
      "id": 10,
      "tasks": ["11.1", "11.2", "12.1"]
    },
    {
      "id": 11,
      "tasks": ["11.3", "11.4", "12.2", "12.3"]
    },
    {
      "id": 12,
      "tasks": ["12.4", "12.5", "14.1", "14.2"]
    },
    {
      "id": 13,
      "tasks": ["14.3", "14.4", "14.5"]
    },
    {
      "id": 14,
      "tasks": ["14.6", "15.1", "15.2", "15.3"]
    },
    {
      "id": 15,
      "tasks": ["15.4", "15.5", "16.1", "16.2"]
    },
    {
      "id": 16,
      "tasks": ["16.3", "16.4", "16.5"]
    },
    {
      "id": 17,
      "tasks": ["16.6", "18.1", "18.2", "18.3"]
    },
    {
      "id": 18,
      "tasks": ["18.4", "19.1", "19.2", "19.3"]
    },
    {
      "id": 19,
      "tasks": ["20.1", "20.2", "20.3"]
    },
    {
      "id": 20,
      "tasks": ["20.4", "20.5"]
    },
    {
      "id": 21,
      "tasks": ["22.1", "22.2", "22.3"]
    }
  ]
}
```
