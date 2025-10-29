Tourism Intelligence Dashboard
An interactive, visually-rich analytics dashboard for city-level tourism data—offering real‑time KPIs, domestic/international tourist breakdown, dynamic hotel/occupancy review, and actionable visualizations for smarter planning.

📸 Demo
<img src="image.jpg" width="65%" alt="Tourism Intelligence Dashboard - Screenshot">
📒 Table of Contents
About the Project

Key Features

Architecture & Flowcharts

Setup & Installation

Usage

Use Cases

Contributing

License

Contact

📝 About the Project
Tourism Intelligence Dashboard brings together all vital metrics—arrivals, revenue, hotel data, domestic/international split—across multiple cities, in an easy-to-use web interface. Its goal: empower cities, hotels, and agencies to make data-driven decisions and respond proactively to tourism trends.

✨ Key Features
KPI Cards: Total arrivals, revenue, average hotel occupancy

Tourist Breakdown: Domestic and International, shown numerically and as a donut chart

Hotel Data Table: Name, Stars, Rooms, Price/Night, Occupancy

Charts:

Trend chart (Arrivals, Revenue, Occupancy, Domestic/International over last 6 months)

Hotel occupancy comparison (bar chart)

Donut chart for tourist split

Dynamic Selection: Instantly updates all visuals based on city/month/year

Responsive Design: Modern UI, city-themed colors, animated, and fast

🔗 Architecture & Flowcharts
1️⃣ System Workflow
text
flowchart TD
    A[User Input (City, Month, Year)] --> B[Data Fetch/Processing]
    B --> C[KPI Calculation (Totals, Domestic/Intl, Revenue, Occupancy)]
    C --> D[Visualization (KPIs, Table, Charts, Donut)]
    D --> E[Reports/Exports, Actions, Decision Support]
2️⃣ Data Pipeline
text
flowchart LR
    Source1[Tourism Stats] --> ETL
    Source2[Hotels Data] --> ETL
    Source3[Arrivals by Type] --> ETL
    ETL --> KPIs
    ETL --> Table
    ETL --> Graphs
    ETL --> Donut
    KPIs & Table & Graphs & Donut --> Action[Decision, Reports, Exports]
⚙️ Setup & Installation
Clone this repo

bash
git clone https://github.com/your-username/tourism-intelligence-dashboard.git
cd tourism-intelligence-dashboard
Run locally

Open index.html in your browser

Or run a simple server:

bash
python3 -m http.server
(Optional: For real data/API integration, see scripts/ and extend JavaScript as required)

🚀 Usage
Select the city, month, and year at the top.

Instantly view KPIs, domestic/international stats, and the hotel occupancy/pricing table.

Analyze live graphs updating to your selections.

Use for:

Trend analysis

Statistical reporting

Visual presentations

Management decisions

🏆 Use Cases
💼 City Planners: Seasonal demand, resource allocation, event management

🏨 Hotels: Compare occupancy, optimize pricing

🏢 Government: Policy targeting, visa and campaign monitoring

📊 Business/Analytics: Report generation, export, academic research

🧑‍💼 General: Real-time, mobile-friendly data exploration

🤝 Contributing
Fork the repo

Make your feature or fix

Create a pull request

Suggestions/feature requests are welcome via Issues!
