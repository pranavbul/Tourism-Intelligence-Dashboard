
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import time

# -----------------------------
# Configuration
# -----------------------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "TourismDB"
COLLECTION_NAME = "TourismStats"

st.set_page_config(page_title="Tourism Intelligence Dashboard", layout="wide")

# -----------------------------
# Mock data (same dataset & logic)
# -----------------------------
mock_hotels = {
    "Delhi": [["The Delhi Grand", 5, 282, 5500, 82],
              ["Royal Residency", 4, 140, 3500, 75]],
    "Mumbai": [["Mumbai Palace", 5, 442, 6500, 80],
               ["Marine View", 4, 201, 4800, 70]],
    "Bangalore": [["Bangalore Residency", 4, 361, 4300, 75],
                  ["Palace Inn", 3, 180, 2800, 67]],
    "Kolkata": [["Kolkata Heritage", 4, 402, 4900, 77],
                ["Sunshine Hotel", 3, 122, 2100, 64]]
}

mock_KPIs = {
    "Delhi":     {"arr": 243400, "rev": 12200000, "occ": 80, "domestic": 182500, "international": 60900},
    "Mumbai":    {"arr": 254100, "rev": 12570000, "occ": 78, "domestic": 189000, "international": 65100},
    "Bangalore": {"arr": 186400, "rev": 8300000,  "occ": 74, "domestic": 155300, "international": 31100},
    "Kolkata":   {"arr": 201800, "rev": 9650000,  "occ": 76, "domestic": 161600, "international": 40200}
}

mock_trends = {
    "Delhi": {
        "months": [5, 6, 7, 8, 9, 10],
        "arrivals": [135000, 156000, 183000, 205000, 222000, 243400],
        "domestic": [110000, 128000, 146000, 168200, 171000, 182500],
        "international": [25000, 28000, 37000, 36800, 51000, 60900],
        "revenue": [6500000, 7500000, 8900000, 9800000, 11200000, 12200000],
        "occupancy": [67, 71, 76, 78, 81, 80]
    },
    "Mumbai": {
        "months": [5, 6, 7, 8, 9, 10],
        "arrivals": [141000, 168000, 191000, 225000, 238000, 254100],
        "domestic": [116600, 142800, 152800, 176000, 179300, 189000],
        "international": [24400, 25200, 38200, 49000, 58700, 65100],
        "revenue": [7100000, 7950000, 9620000, 11000000, 11800000, 12570000],
        "occupancy": [65, 72, 74, 75, 77, 78]
    },
    "Bangalore": {
        "months": [5, 6, 7, 8, 9, 10],
        "arrivals": [93000, 111000, 141000, 155000, 174000, 186400],
        "domestic": [76000, 94900, 122400, 129700, 143100, 155300],
        "international": [17000, 16100, 18600, 25300, 30900, 31100],
        "revenue": [4250000, 5080000, 6830000, 7580000, 8120000, 8300000],
        "occupancy": [62, 69, 71, 72, 73, 74]
    },
    "Kolkata": {
        "months": [5, 6, 7, 8, 9, 10],
        "arrivals": [105000, 121000, 153000, 172000, 188000, 201800],
        "domestic": [84000, 97500, 127300, 137400, 145100, 161600],
        "international": [21000, 23500, 25700, 34600, 42900, 40200],
        "revenue": [5040000, 6350000, 7500000, 8620000, 9410000, 9650000],
        "occupancy": [61, 64, 69, 70, 73, 76]
    }
}

attractions = {
    "Delhi": ["Red Fort", "Qutub Minar", "India Gate", "Lotus Temple", "Humayun's Tomb",
              "Akshardham Temple", "Jama Masjid", "Rashtrapati Bhavan", "National Museum", "Lodhi Gardens"],
    "Mumbai": ["Gateway of India", "Marine Drive", "Elephanta Caves", "Chhatrapati Shivaji Terminus", "Haji Ali Dargah"],
    "Bangalore": ["Lalbagh", "Cubbon Park", "Bangalore Palace", "Vidhana Soudha", "UB City"],
    "Kolkata": ["Victoria Memorial", "Howrah Bridge", "Dakshineswar Kali Temple", "Indian Museum", "Prinsep Ghat"]
}

months_names = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# -----------------------------
# MongoDB: insert fresh data each run
# -----------------------------
def seed_mongodb():
    """
    Connect to local MongoDB and insert the mock data.
    This function will remove existing documents in the collection,
    then insert one document per city containing kpi, hotels, trends.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        # try to trigger server selection to detect connection errors early
        client.server_info()
    except Exception as e:
        st.error(f"Error connecting to MongoDB at {MONGO_URI}: {e}")
        return False

    db = client[DB_NAME]
    coll = db[COLLECTION_NAME]

    # Clear previous data to avoid duplicates (you requested fresh insert each run)
    coll.delete_many({})

    docs = []
    now = datetime.utcnow()
    for city in mock_KPIs.keys():
        doc = {
            "city": city,
            "kpi": mock_KPIs[city],
            "hotels": mock_hotels.get(city, []),
            "trends": mock_trends.get(city, {}),
            "attractions": attractions.get(city, []),
            "inserted_at": now
        }
        docs.append(doc)

    if docs:
        coll.insert_many(docs)

    # small delay to ensure write propagation (usually unnecessary but safe)
    time.sleep(0.1)
    return True

# Seed DB now (insert fresh data each run)
seed_ok = seed_mongodb()

# -----------------------------
# Helper: fetch data from MongoDB
# -----------------------------
def fetch_from_mongo():
    """
    Returns a dict keyed by city with the stored structure.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client[DB_NAME]
        coll = db[COLLECTION_NAME]
        rows = list(coll.find({}, {"_id": 0}))
        data = {}
        for r in rows:
            city = r.get("city")
            data[city] = {
                "kpi": r.get("kpi", {}),
                "hotels": r.get("hotels", []),
                "trends": r.get("trends", {}),
                "attractions": r.get("attractions", [])
            }
        return data
    except Exception as e:
        st.error(f"Error reading from MongoDB: {e}")
        return {}

# Load data (fallback to local mocks if mongo failed)
mongo_data = fetch_from_mongo()
if not mongo_data:
    # fallback - build from mocks
    mongo_data = {}
    for c in mock_KPIs.keys():
        mongo_data[c] = {
            "kpi": mock_KPIs[c],
            "hotels": mock_hotels.get(c, []),
            "trends": mock_trends.get(c, {}),
            "attractions": attractions.get(c, [])
        }

# -----------------------------
# Styling (inject CSS similar to your UI)
# -----------------------------
st.markdown("""
<style>
/* container tweaks */
section.main > div.block-container { padding-top: 1rem; }

/* header */
.dashboard-title { font-size: 30px; font-weight:700; color:#4059d1; }

/* cards */
.kpi-card, .info-card, .table-card {
    background: #fff;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}

/* purple update button */
button.stButton>button {
    background: linear-gradient(90deg,#7b3fb9,#b35ad6);
    color: white;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 700;
    border: none;
}

/* input controls */
div[role="listbox"], input[type="number"] {
    padding: 8px;
    border-radius: 6px;
}

/* small spacing */
.stButton button { margin-top: 22px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Layout & Controls
# -----------------------------
st.markdown(f"<div style='display:flex;align-items:center;gap:12px'><span style='font-size:30px'>🌍</span><div class='dashboard-title'>Tourism Intelligence Dashboard</div></div>", unsafe_allow_html=True)
st.write("")

# Controls in a form similar to your HTML
with st.form("controls_form"):
    c1, c2, c3, c4 = st.columns([4,1,1,1])
    with c1:
        city_choice = st.selectbox("Choose Destination:", options=list(mongo_data.keys()))
    with c2:
        month_choice = st.number_input("Month:", min_value=1, max_value=12, value=10, step=1, format="%d")
    with c3:
        year_choice = st.number_input("Year:", min_value=2022, max_value=2100, value=2025, step=1, format="%d")
    with c4:
        submitted = st.form_submit_button("UPDATE")

# maintain session state so UI doesn't flicker
if "selected" not in st.session_state:
    st.session_state.selected = (city_choice, month_choice, year_choice)

if submitted:
    st.session_state.selected = (city_choice, month_choice, year_choice)

city_sel, month_sel, year_sel = st.session_state.selected

# -----------------------------
# Main Content (two-column)
# -----------------------------
left_col, right_col = st.columns([1, 1.6], gap="large")

with left_col:
    # KPI card
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    kpi = mongo_data[city_sel]["kpi"]
    st.markdown(f"*Total Arrivals:* <span style='color:#133b8a;font-weight:700'>{kpi.get('arr', 0):,}</span>", unsafe_allow_html=True)
    st.markdown(f"*Total Revenue:* <span style='color:#133b8a;font-weight:700'>₹{kpi.get('rev', 0):,}</span>", unsafe_allow_html=True)
    st.markdown(f"*Avg. Hotel Occupancy:* <span style='color:#133b8a;font-weight:700'>{kpi.get('occ', 0)}%</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    # Attractions / info card
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.markdown(f"*Top Attractions in {city_sel}*")
    at_list = mongo_data[city_sel].get("attractions", [])
    if at_list:
        cols = st.columns(2)
        for i, a in enumerate(at_list):
            with cols[i % 2]:
                st.write(f"• {a}")
    else:
        st.write("No attractions data.")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    tabs = st.tabs(["Hotels & Pricing", "Revenue"])
    with tabs[0]:
        st.markdown("<div class='table-card'>", unsafe_allow_html=True)
        st.write(f"*Hotels in {city_sel}*")
        hotels = mongo_data[city_sel].get("hotels", [])
        df_hotels = pd.DataFrame(hotels, columns=["Name", "Stars", "Rooms", "Price/Night (₹)", "Occupancy (%)"])
        st.table(df_hotels)
        st.markdown("</div>", unsafe_allow_html=True)
    with tabs[1]:
        st.markdown("<div class='table-card'>", unsafe_allow_html=True)
        st.write("*Revenue Breakdown*")
        df_rev = pd.DataFrame({
            "Type": ["Domestic", "International"],
            "Tourists": [kpi.get("domestic", 0), kpi.get("international", 0)],
            "Revenue (₹)": [int(kpi.get("rev", 0) * 0.75), int(kpi.get("rev", 0) * 0.25)]
        })
        st.table(df_rev)
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Charts: Donut, KPI trends, Hotel occupancy
# -----------------------------
st.write("")  # spacing
chart_col1, chart_col2 = st.columns([1, 1])

with chart_col1:
    st.subheader("Tourist Mix")
    dom = kpi.get("domestic", 0)
    intl = kpi.get("international", 0)
    fig1, ax1 = plt.subplots(figsize=(4,4))
    ax1.pie([dom, intl], labels=["Domestic", "International"], autopct='%1.1f%%', startangle=140,
            colors=["#22b573", "#f44336"], wedgeprops={'linewidth': 0.5, 'edgecolor': 'white'})
    centre_circle = plt.Circle((0, 0), 0.65, fc='white')
    fig1.gca().add_artist(centre_circle)
    ax1.axis('equal')
    st.pyplot(fig1)

with chart_col2:
    st.subheader("KPI Trends - Last 6 Months")
    trend = mongo_data[city_sel].get("trends", {})
    if trend:
        months = [months_names[m - 1] for m in trend.get("months", [])]
        x = np.arange(len(months))
        fig2, ax2 = plt.subplots(figsize=(8, 3.5))
        ax2.bar(x, trend.get("arrivals", []), alpha=0.6, label="Arrivals", color="#2CEEF2")
        ax2.plot(x, trend.get("domestic", []), marker='o', label="Domestic", color="#22b573")
        ax2.plot(x, trend.get("international", []), marker='o', label="International", color="#f44336")
        ax2.set_xticks(x)
        ax2.set_xticklabels(months, rotation=30, ha='right')
        ax2.set_ylabel("Number")
        ax2.legend()
        st.pyplot(fig2)
    else:
        st.info("No trend data available for this city.")

# Hotel occupancy horizontal bar
st.write("")
st.subheader("Hotel Occupancy Comparison")
hotels_list = mongo_data[city_sel].get("hotels", [])
if hotels_list:
    hot_names = [h[0] for h in hotels_list]
    hot_occ = [h[4] for h in hotels_list]
    fig3, ax3 = plt.subplots(figsize=(8, 2.5))
    bars = ax3.barh(hot_names, hot_occ, color='#f7a541', edgecolor='#278AEA')
    ax3.set_xlim(0, 100)
    for i, v in enumerate(hot_occ):
        ax3.text(v + 1, i, f"{v}%", va='center')
    st.pyplot(fig3)
else:
    st.write("No hotels data to display.")

# Footer: selected month/year
st.markdown(f"*Data for:* {months_names[month_sel - 1]}, {year_sel}")

# show MongoDB seed status and connection
if seed_ok:
    st.success(f"Data inserted into MongoDB: {DB_NAME}.{COLLECTION_NAME} (fresh insert each run).")
else:
    st.warning("MongoDB seed failed — using in-memory mock data for the UI.")