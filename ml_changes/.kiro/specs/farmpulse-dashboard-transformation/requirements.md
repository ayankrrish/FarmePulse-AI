# Requirements Document

## Introduction

FarmPulse AI is an existing Flask-based agricultural price intelligence platform for Indian farmers, featuring a complete ML pipeline with 6+ models, ensemble prediction, and real-time market analysis for pulse crops (Chana, Moong, Tur) across 8 states. The platform currently functions as a student project with basic UI/UX. This transformation will elevate it to production-quality by redesigning the frontend into a farmer-friendly, modern interface while preserving all backend functionality, APIs, ML models, and business logic.

**Core Objective**: Frontend transformation ONLY — modernize UI/UX to production standards without touching backend Flask routes, services, prediction logic, or data pipelines.

**Target Users**: Indian farmers, agricultural officers, Farm Producer Organizations (FPOs), and AgriTech startups.

## Glossary

- **Dashboard_System**: The main FarmPulse AI Flask application serving farmers
- **Frontend_Layer**: HTML templates, CSS stylesheets, JavaScript UI logic
- **Backend_Layer**: Flask routes, services, ML models, APIs, data pipeline
- **Farmer_UI**: The transformed production-quality farmer-facing interface
- **Developer_Mode**: Optional technical view showing ML engineering details
- **ML_Engineering_Details**: Technical metrics (model weights, RMSE, MAE, feature importance, model comparison)
- **Farmer_Terminology**: Simple, jargon-free language avoiding technical ML terms
- **Weather_Widget**: Embedded weather information with farming advice
- **MSP_Alert**: Minimum Support Price safety check notification
- **AI_Assistant**: ChatGPT-style conversational interface for farmer queries
- **Price_Forecast_View**: Simplified prediction display hiding ML complexity
- **Profit_Estimator**: Revenue and profit calculation interface
- **Market_Comparison_View**: Cross-state price comparison in card format
- **Navigation_Sidebar**: Left navigation menu for page switching
- **Responsive_Design**: Mobile-first adaptive layout (desktop/laptop/tablet/mobile)
- **Design_System**: Consistent visual language (colors, typography, spacing, components)
- **Production_Quality**: Professional appearance not resembling student project
- **Quick_Insights**: At-a-glance metrics on dashboard (today's price, forecast, sell/wait decision)
- **Visual_Cards**: Card-based UI components replacing table layouts
- **Action_Recommendation**: Clear sell/wait/hold advice for farmers
- **Single_Theme**: Premium light theme (dark mode removed)
- **Ensemble_Prediction**: Weighted average of multiple ML models
- **Context_Data**: Historical price data used by ML models
- **CSV_Pipeline**: Data processing from raw CSV to model-ready format

## Requirements

### Requirement 1: Architecture Preservation

**User Story:** As a developer, I want the transformation to preserve all backend functionality, so that existing ML models and APIs continue working without modification.

#### Acceptance Criteria

1. THE Backend_Layer SHALL remain unchanged (Flask routes, services, models, data pipeline)
2. THE Frontend_Layer SHALL be modified while Backend_Layer remains intact
3. THE Dashboard_System SHALL maintain all existing API endpoints
4. THE Dashboard_System SHALL preserve ensemble prediction logic
5. THE Dashboard_System SHALL maintain CSV data pipeline
6. THE Dashboard_System SHALL keep all ML model files unchanged
7. THE Dashboard_System SHALL retain existing Flask route structure
8. THE Dashboard_System SHALL preserve service layer functions (ensemble.py, recommendation.py, msp_alerts.py, market_comparison.py, profit_calculator.py)

### Requirement 2: Dashboard Redesign as Farmer Home Page

**User Story:** As a farmer, I want the dashboard to show me immediate insights, so that I can quickly decide whether to sell today.

#### Acceptance Criteria

1. WHEN Dashboard_System loads, THE Farmer_UI SHALL display Quick_Insights (today's price, expected price, sell/wait decision, MSP status, weather, trend)
2. THE Farmer_UI SHALL show Action_Recommendation prominently ("Sell Today" or "Wait for Better Price")
3. THE Farmer_UI SHALL embed Weather_Widget into dashboard (not separate page)
4. THE Farmer_UI SHALL display price history chart with 7-day forecast
5. THE Farmer_UI SHALL show MSP_Alert status with color-coded indicator
6. THE Farmer_UI SHALL present trend direction (rising/falling/stable)
7. THE Farmer_UI SHALL use Visual_Cards for all metric displays
8. THE Farmer_UI SHALL hide ML_Engineering_Details from main view
9. THE Dashboard_System SHALL fetch all data from /api/dashboard_summary endpoint
10. THE Farmer_UI SHALL display last update timestamp

### Requirement 3: Weather Integration into Dashboard

**User Story:** As a farmer, I want weather information on the dashboard, so that I can plan harvesting and transport timing.

#### Acceptance Criteria

1. THE Weather_Widget SHALL be embedded in dashboard layout (not separate page)
2. WHEN Dashboard_System loads, THE Weather_Widget SHALL fetch current weather for selected state
3. THE Weather_Widget SHALL display temperature, humidity, wind speed, rain probability
4. THE Weather_Widget SHALL provide AI farming advice based on weather conditions
5. THE Weather_Widget SHALL use Open-Meteo API for weather data
6. WHEN weather data fails to load, THE Weather_Widget SHALL display fallback message
7. THE Weather_Widget SHALL use state-to-coordinates mapping for API calls
8. THE Navigation_Sidebar SHALL remove separate Weather page link
9. THE Weather_Widget SHALL match Design_System visual style

### Requirement 4: Price Forecast Simplification

**User Story:** As a farmer, I want to see only actionable price forecasts, so that I am not confused by technical ML metrics.

#### Acceptance Criteria

1. THE Price_Forecast_View SHALL hide ML_Engineering_Details (model weights, contributions, comparison tables)
2. THE Price_Forecast_View SHALL display current price and predicted price prominently
3. THE Price_Forecast_View SHALL show AI_Assistant suggestion text ("Prices expected to rise — consider waiting")
4. THE Price_Forecast_View SHALL visualize price history and forecast on single chart
5. THE Price_Forecast_View SHALL display confidence score as percentage
6. THE Price_Forecast_View SHALL show MSP comparison
7. THE Price_Forecast_View SHALL use Farmer_Terminology ("Expected Market Price" not "Ensemble Prediction")
8. WHERE Developer_Mode is enabled, THE Price_Forecast_View SHALL reveal ML_Engineering_Details
9. THE Dashboard_System SHALL use /api/ensemble_predict endpoint
10. THE Price_Forecast_View SHALL support target date selection

### Requirement 5: Profit Estimator UI Improvement

**User Story:** As a farmer, I want an intuitive profit calculator, so that I can estimate my revenue for different selling strategies.

#### Acceptance Criteria

1. THE Profit_Estimator SHALL provide input fields for quantity (quintals) and production cost
2. WHEN user enters quantity and cost, THE Profit_Estimator SHALL calculate current revenue, predicted revenue, MSP revenue
3. THE Profit_Estimator SHALL display total cost, current profit, predicted profit IF cost is provided
4. THE Profit_Estimator SHALL show revenue difference (amount and percentage)
5. THE Profit_Estimator SHALL recommend best selling option (sell today / wait / MSP procurement)
6. THE Profit_Estimator SHALL use Visual_Cards for result display
7. THE Profit_Estimator SHALL highlight best option with visual distinction
8. THE Dashboard_System SHALL preserve /api/profit_estimate endpoint logic
9. THE Profit_Estimator SHALL support real-time recalculation on input change
10. THE Profit_Estimator SHALL use Farmer_Terminology for labels

### Requirement 6: MSP Alerts UI Modernization

**User Story:** As a farmer, I want clear MSP safety alerts, so that I know if government procurement is my best option.

#### Acceptance Criteria

1. THE MSP_Alert SHALL display status for all crops with color-coded indicators (Green/Yellow/Red)
2. THE MSP_Alert SHALL use Visual_Cards layout (not table format)
3. WHEN MSP_Alert status is Green, THE Farmer_UI SHALL display "Safe - Above MSP" message
4. WHEN MSP_Alert status is Yellow, THE Farmer_UI SHALL display "Near MSP - Monitor" message
5. WHEN MSP_Alert status is Red, THE Farmer_UI SHALL display "Below MSP - Sell through Government" message
6. THE MSP_Alert SHALL show current price, MSP, and difference for each crop
7. THE MSP_Alert SHALL display trend direction and recommendation
8. THE MSP_Alert SHALL animate card entrance with staggered timing
9. THE Dashboard_System SHALL use /api/msp_alert endpoint
10. THE MSP_Alert SHALL use icon-based visual communication

### Requirement 7: Market Comparison Visual Redesign

**User Story:** As a farmer, I want to quickly see which state offers the best price, so that I can plan where to sell my crop.

#### Acceptance Criteria

1. THE Market_Comparison_View SHALL display top 5 markets in Visual_Cards layout
2. THE Market_Comparison_View SHALL show best market summary (highest price state, price spread, overall trend)
3. THE Market_Comparison_View SHALL rank markets (#1, #2, #3...) with visual badges
4. WHEN Market_Comparison_View displays rank badges, THE Farmer_UI SHALL use gold/silver/bronze styling for top 3
5. THE Market_Comparison_View SHALL show today's price, expected price, change percentage, and trend for each market
6. THE Market_Comparison_View SHALL provide full market table below top 5 cards
7. THE Market_Comparison_View SHALL replace existing table-only layout
8. THE Dashboard_System SHALL preserve /api/market_comparison endpoint
9. THE Market_Comparison_View SHALL animate cards with staggered entrance
10. THE Market_Comparison_View SHALL use Farmer_Terminology for labels

### Requirement 8: AI Assistant Redesign

**User Story:** As a farmer, I want a ChatGPT-style assistant, so that I can ask questions in my own words and get instant answers.

#### Acceptance Criteria

1. THE AI_Assistant SHALL provide chat interface with message bubbles
2. THE AI_Assistant SHALL display quick prompt buttons ("Should I sell today?", "Which state gives best price?", "What is MSP?", "Today's weather", "Profit for 10 quintals")
3. WHEN farmer sends message, THE AI_Assistant SHALL process question and return contextual answer
4. THE AI_Assistant SHALL support questions about price forecast, MSP, market comparison, profit, weather, selling recommendation
5. THE AI_Assistant SHALL use conversational Farmer_Terminology in responses
6. THE AI_Assistant SHALL display typing indicator while processing
7. THE AI_Assistant SHALL show message timestamps
8. THE AI_Assistant SHALL differentiate user messages from AI messages visually
9. THE AI_Assistant SHALL auto-scroll to latest message
10. THE AI_Assistant SHALL include disclaimer ("AI uses real FarmPulse data. Predictions are estimates — not financial advice.")

### Requirement 9: Navigation Simplification

**User Story:** As a farmer, I want simple navigation, so that I can quickly access the features I need.

#### Acceptance Criteria

1. THE Navigation_Sidebar SHALL display menu items: Dashboard, Price Forecast, Profit Estimator, MSP Alerts, Market Comparison, AI Assistant
2. THE Navigation_Sidebar SHALL remove separate Weather page (weather embedded in Dashboard)
3. THE Navigation_Sidebar SHALL highlight active page
4. WHEN farmer clicks navigation item, THE Dashboard_System SHALL load corresponding page
5. THE Navigation_Sidebar SHALL show FarmPulse AI logo and version
6. THE Navigation_Sidebar SHALL use icon-based navigation
7. THE Navigation_Sidebar SHALL maintain consistent styling with Design_System
8. THE Navigation_Sidebar SHALL include collapsible mobile menu for small screens
9. THE Dashboard_System SHALL update page title and subtitle on navigation
10. THE Navigation_Sidebar SHALL persist across all pages

### Requirement 10: Dark Mode Removal and Single Theme

**User Story:** As a product owner, I want a single premium light theme, so that the interface is consistent and polished.

#### Acceptance Criteria

1. THE Farmer_UI SHALL use Single_Theme (light mode only)
2. THE Design_System SHALL remove dark mode toggle and styling
3. THE Farmer_UI SHALL use green color palette (primary: green-800, accent: green-700, backgrounds: soft green tints)
4. THE Farmer_UI SHALL use consistent typography (Inter font family)
5. THE Design_System SHALL define semantic colors (emerald for positive, amber for warning, rose for danger)
6. THE Design_System SHALL use consistent border radius (8px-20px range)
7. THE Design_System SHALL use consistent shadows (sm/md/lg)
8. THE Design_System SHALL define spacing scale (4px, 8px, 16px, 24px, 32px, 48px)
9. THE Design_System SHALL use JetBrains Mono for numeric data display
10. THE Farmer_UI SHALL maintain visual consistency across all pages

### Requirement 11: Farmer-Friendly Terminology

**User Story:** As a farmer, I want simple language, so that I can understand the information without technical knowledge.

#### Acceptance Criteria

1. THE Farmer_UI SHALL use "Expected Market Price" instead of "Ensemble Prediction"
2. THE Farmer_UI SHALL use "Today's Mandi Price" instead of "Current Price"
3. THE Farmer_UI SHALL use "MSP Safety" instead of "MSP Alert Level"
4. THE Farmer_UI SHALL use "Forecast Confidence" instead of "Model Agreement Score"
5. THE Farmer_UI SHALL use "Should You Sell Today?" instead of "Recommendation"
6. THE Farmer_UI SHALL use "Price Trend" instead of "Momentum Indicator"
7. THE Farmer_UI SHALL avoid ML jargon (LSTM, ensemble, RMSE, MAE, feature engineering)
8. WHERE Developer_Mode is enabled, THE Farmer_UI SHALL reveal technical terminology
9. THE Farmer_UI SHALL use action-oriented language ("Sell Today", "Wait for Better Price")
10. THE AI_Assistant SHALL use conversational Farmer_Terminology in all responses

### Requirement 12: Full Responsive Design

**User Story:** As a farmer, I want the platform to work on my mobile phone, so that I can check prices from anywhere.

#### Acceptance Criteria

1. THE Responsive_Design SHALL adapt layout for desktop (1200px+), laptop (1024px), tablet (768px), and mobile (480px)
2. WHEN viewport width is below 768px, THE Navigation_Sidebar SHALL collapse into hamburger menu
3. WHEN viewport width is below 768px, THE Dashboard_System SHALL stack Visual_Cards vertically
4. WHEN viewport width is below 768px, THE Farmer_UI SHALL adjust font sizes for readability
5. THE Responsive_Design SHALL maintain touch-friendly button sizes (minimum 44px touch target)
6. THE Responsive_Design SHALL ensure horizontal scrolling is never required
7. THE Responsive_Design SHALL adapt chart sizes for mobile screens
8. THE Responsive_Design SHALL reflow multi-column layouts to single column on mobile
9. THE Responsive_Design SHALL test across Chrome, Firefox, Safari, Edge
10. THE Responsive_Design SHALL maintain visual hierarchy on all screen sizes

### Requirement 13: Production Quality Standards

**User Story:** As a product owner, I want the platform to look professional, so that farmers and investors trust the platform.

#### Acceptance Criteria

1. THE Farmer_UI SHALL not resemble student project aesthetics
2. THE Design_System SHALL use professional color palette with proper contrast ratios (WCAG AA)
3. THE Farmer_UI SHALL use smooth transitions and animations (150ms-400ms)
4. THE Farmer_UI SHALL display loading states for async operations
5. THE Farmer_UI SHALL handle error states gracefully with user-friendly messages
6. THE Farmer_UI SHALL use consistent spacing and alignment
7. THE Farmer_UI SHALL use high-quality iconography
8. THE Farmer_UI SHALL maintain visual polish (shadows, borders, hover states)
9. THE Dashboard_System SHALL display professional branding ("FarmPulse AI — Agricultural Intelligence")
10. THE Farmer_UI SHALL perform smooth page transitions

### Requirement 14: Backend API Contract Preservation

**User Story:** As a developer, I want all existing API contracts preserved, so that future integrations continue working.

#### Acceptance Criteria

1. THE Backend_Layer SHALL maintain /api/config endpoint response format
2. THE Backend_Layer SHALL maintain /api/dashboard_summary endpoint response format
3. THE Backend_Layer SHALL maintain /api/ensemble_predict endpoint response format
4. THE Backend_Layer SHALL maintain /api/recommendation endpoint response format
5. THE Backend_Layer SHALL maintain /api/msp_alert endpoint response format
6. THE Backend_Layer SHALL maintain /api/market_comparison endpoint response format
7. THE Backend_Layer SHALL maintain /api/profit_estimate endpoint response format
8. THE Backend_Layer SHALL maintain /api/model_metrics endpoint response format
9. THE Backend_Layer SHALL preserve all query parameters for existing endpoints
10. THE Backend_Layer SHALL maintain JSON response structure for all endpoints

### Requirement 15: Developer Mode (Optional Technical View)

**User Story:** As a technical user, I want access to ML engineering details, so that I can audit model performance and contribution.

#### Acceptance Criteria

1. WHERE Developer_Mode is enabled, THE Farmer_UI SHALL reveal ML_Engineering_Details
2. WHERE Developer_Mode is enabled, THE Price_Forecast_View SHALL display model weights, individual predictions, RMSE, MAE
3. WHERE Developer_Mode is enabled, THE Dashboard_System SHALL show model comparison table
4. WHERE Developer_Mode is enabled, THE Farmer_UI SHALL display feature importance charts
5. WHERE Developer_Mode is enabled, THE Dashboard_System SHALL show ensemble contribution breakdown
6. WHERE Developer_Mode is disabled, THE Farmer_UI SHALL hide all ML_Engineering_Details
7. THE Developer_Mode SHALL be toggled via query parameter (?dev=true) or settings panel
8. THE Developer_Mode SHALL maintain separate styling from Farmer_UI
9. THE Developer_Mode SHALL display technical terminology alongside farmer-friendly labels
10. THE Developer_Mode SHALL preserve existing /api/model_metrics endpoint usage

### Requirement 16: Chart Visualization Enhancement

**User Story:** As a farmer, I want clear price charts, so that I can visually understand price trends and forecasts.

#### Acceptance Criteria

1. THE Dashboard_System SHALL use Plotly.js for interactive charts
2. THE Farmer_UI SHALL display historical price trend line (12 months minimum)
3. THE Farmer_UI SHALL display forecast price trend line with different styling
4. THE Farmer_UI SHALL show MSP reference line on price charts
5. WHEN user hovers over chart, THE Dashboard_System SHALL display price tooltip with date and value
6. THE Farmer_UI SHALL support zoom and pan interactions on charts
7. THE Farmer_UI SHALL use color-coded lines (green for historical, emerald for forecast, amber for MSP)
8. THE Farmer_UI SHALL display chart legend
9. THE Responsive_Design SHALL adapt chart height for mobile screens
10. THE Farmer_UI SHALL animate chart rendering on page load

### Requirement 17: Performance and Loading States

**User Story:** As a farmer, I want fast page loads, so that I don't waste time waiting for data.

#### Acceptance Criteria

1. WHEN page is loading, THE Farmer_UI SHALL display loading spinner with descriptive text
2. THE Dashboard_System SHALL fetch dashboard data asynchronously
3. THE Farmer_UI SHALL render static content before API responses arrive
4. WHEN API request fails, THE Farmer_UI SHALL display error message with retry option
5. THE Dashboard_System SHALL cache crop/state configuration
6. THE Farmer_UI SHALL display skeleton loaders for cards during data fetch
7. THE Dashboard_System SHALL optimize Plotly chart rendering
8. THE Farmer_UI SHALL lazy-load non-critical components
9. THE Dashboard_System SHALL minimize CSS/JS bundle size
10. THE Dashboard_System SHALL implement debouncing for input-triggered API calls

### Requirement 18: Accessibility Compliance

**User Story:** As a farmer with visual impairment, I want the platform to work with screen readers, so that I can access price information.

#### Acceptance Criteria

1. THE Farmer_UI SHALL use semantic HTML5 elements (header, nav, main, section, article)
2. THE Farmer_UI SHALL provide alt text for all icons and images
3. THE Farmer_UI SHALL use ARIA labels for interactive elements
4. THE Farmer_UI SHALL maintain keyboard navigation support (Tab, Enter, Escape)
5. THE Design_System SHALL ensure color contrast meets WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
6. THE Farmer_UI SHALL provide focus indicators for interactive elements
7. THE Farmer_UI SHALL use descriptive link text (not "click here")
8. THE Farmer_UI SHALL provide skip navigation links
9. THE Farmer_UI SHALL ensure form inputs have associated labels
10. THE Dashboard_System SHALL test with screen reader (NVDA or JAWS)

### Requirement 19: Data Freshness Indicators

**User Story:** As a farmer, I want to know when data was last updated, so that I can trust the information is current.

#### Acceptance Criteria

1. THE Farmer_UI SHALL display "Last Updated" timestamp on dashboard
2. THE Farmer_UI SHALL show data freshness indicator for price forecasts
3. THE Dashboard_System SHALL fetch latest context data on page load
4. THE Farmer_UI SHALL display data source attribution ("Source: CEDA Agmarknet")
5. THE Farmer_UI SHALL show model last training date in Developer_Mode
6. THE Farmer_UI SHALL indicate if data is stale (older than 7 days)
7. THE Dashboard_System SHALL refresh data on crop/state selection change
8. THE Farmer_UI SHALL display weather data timestamp
9. THE AI_Assistant SHALL include data freshness in responses when relevant
10. THE Dashboard_System SHALL log data fetch timestamps

### Requirement 20: Cross-Browser Compatibility

**User Story:** As a farmer, I want the platform to work on my browser, so that I don't need to install specific software.

#### Acceptance Criteria

1. THE Dashboard_System SHALL support Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
2. THE Farmer_UI SHALL render consistently across supported browsers
3. THE Dashboard_System SHALL polyfill ES6+ features if needed
4. THE Farmer_UI SHALL test CSS Grid and Flexbox layouts in all browsers
5. THE Dashboard_System SHALL handle browser-specific API differences
6. THE Farmer_UI SHALL test Plotly.js rendering in all browsers
7. THE Dashboard_System SHALL provide fallback for fetch API if unavailable
8. THE Farmer_UI SHALL test responsive breakpoints in all browsers
9. THE Dashboard_System SHALL handle localStorage browser differences
10. THE Dashboard_System SHALL document browser compatibility in README

