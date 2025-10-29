import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient
import matplotlib.pyplot as plt

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["tourism_intelligence"]

def initialize_database():
    db = get_db()
    if db.destinations.count_documents({}) > 0:
        return

    cities = [
        {"destination_id": "D001", "name": "Delhi", "country": "India", "attractions": ["Red Fort", "Qutub Minar", "India Gate"], "rating": 4.6, "popular_season": "Winter", "coordinates": {"lat": 28.6139, "lon": 77.2090}},
        {"destination_id": "D002", "name": "Mumbai", "country": "India", "attractions": ["Gateway of India", "Marine Drive", "Elephanta Caves"], "rating": 4.7, "popular_season": "Winter", "coordinates": {"lat": 19.0760, "lon": 72.8777}},
        {"destination_id": "D003", "name": "Bangalore", "country": "India", "attractions": ["Lalbagh", "Vidhana Soudha", "Bangalore Palace"], "rating": 4.5, "popular_season": "Winter", "coordinates": {"lat": 12.9716, "lon": 77.5946}},
        {"destination_id": "D004", "name": "Kolkata", "country": "India", "attractions": ["Victoria Memorial", "Howrah Bridge", "Dakshineswar Temple"], "rating": 4.4, "popular_season": "Winter", "coordinates": {"lat": 22.5726, "lon": 88.3639}}
    ]
    db.destinations.insert_many(cities)

    months = []
    arrivals = []
    revenue = []
    np.random.seed(42)
    base_date = datetime.now() - timedelta(days=330)
    for m in range(12):
        date = base_date + timedelta(days=30*m)
        months.append(date.strftime('%b'))
        # DELHI - spikes in summer/winter, random dips
        d = int(45000 + 25000*(np.sin(m/2) + 1) + 8000*np.random.randn())
        r = int(18e6 + m*1.5e6 + 1e6*np.random.randn())
        arrivals.append({"destination":"Delhi","date":date,"arrivals":max(d,1000),"month":date.month,"year":date.year})
        revenue.append({"destination":"Delhi","date":date,"revenue":max(r,10e5),"month":date.month,"year":date.year})
        # MUMBAI - saw-tooth, random spikes, festive bursts
        d = int(60000 + ((m%3)*20000) + np.random.choice([0,40000],p=[0.7,0.3]))
        r = int(20e6 + ((m%4)*3e6) + np.random.choice([0,7e6],p=[0.8,0.2]))
        arrivals.append({"destination":"Mumbai","date":date,"arrivals":max(d,1500),"month":date.month,"year":date.year})
        revenue.append({"destination":"Mumbai","date":date,"revenue":max(r,12e6),"month":date.month,"year":date.year})
        # BANGALORE - climb then sudden drops, tech events impact
        d = int(35000 + m*6000 + (np.random.choice([-20000,0,20000],p=[0.1,0.7,0.2])))
        r = int(15e6 + m*2e6 + np.random.choice([-5e6,0,6e6],p=[0.1,0.6,0.3]))
        arrivals.append({"destination":"Bangalore","date":date,"arrivals":max(d,900),"month":date.month,"year":date.year})
        revenue.append({"destination":"Bangalore","date":date,"revenue":max(r,5e6),"month":date.month,"year":date.year})
        # KOLKATA - steady, then festival burst, rainfall dip
        festival = 85000 if m==9 else 0
        rainfall = -40000 if m==6 else 0
        d = int(42000 + 17000*np.cos(m) + 7000*np.random.randn() + festival + rainfall)
        r = int(12e6 + m*1.1e6 + 1.2e6*np.random.randn() + festival*120 + rainfall*80)
        arrivals.append({"destination":"Kolkata","date":date,"arrivals":max(d,1000),"month":date.month,"year":date.year})
        revenue.append({"destination":"Kolkata","date":date,"revenue":max(r,4e6),"month":date.month,"year":date.year})

    db.tourist_arrivals.insert_many(arrivals)
    db.revenue.insert_many(revenue)

    hotels = [
        {"hotel_id": "H001","name": "The Delhi Grand","destination": "Delhi","star_rating": 5,"total_rooms": 250,"available_rooms": 28,"price_per_night": 5500,"occupancy_rate": 82},
        {"hotel_id": "H002","name": "Mumbai Palace","destination": "Mumbai","star_rating": 5,"total_rooms": 220,"available_rooms": 44,"price_per_night": 6500,"occupancy_rate": 80},
        {"hotel_id": "H003","name": "Bangalore Residency","destination": "Bangalore","star_rating": 4,"total_rooms": 180,"available_rooms": 36,"price_per_night": 4300,"occupancy_rate": 75},
        {"hotel_id": "H004","name": "Kolkata Heritage","destination": "Kolkata","star_rating": 4,"total_rooms": 200,"available_rooms": 40,"price_per_night": 4900,"occupancy_rate": 77}
    ]
    db.hotels.insert_many(hotels)

    # Extra: Simulate some bookings for hotel revenue calculation
    bookings = []
    for h in hotels:
        for m in range(12):
            n = np.random.randint(20,60)
            bookings.append({
                "booking_id": f"B_{h['hotel_id']}_{m}",
                "destination": h['destination'],
                "hotel_id": h['hotel_id'],
                "nights": n,
                "guests": np.random.randint(1,4),
                "total_amount": h['price_per_night'] * n
            })
    db.bookings.insert_many(bookings)

def df_from_coll(coll):
    db = get_db()
    data = list(db[coll].find({}, {"_id": 0}))
    return pd.DataFrame(data) if data else pd.DataFrame()

def show_kpis():
    arrivals = df_from_coll("tourist_arrivals")
    revenue = df_from_coll("revenue")
    hotels = df_from_coll("hotels")
    print("\n==== Tourism KPIs ====")
    print(f"Total Arrivals: {arrivals['arrivals'].sum():,.0f}")
    print(f"Total Revenue: ₹{revenue['revenue'].sum():,.0f}")
    print(f"Avg Occupancy (%): {hotels['occupancy_rate'].mean():.1f}")

def arrivals_trend():
    arrivals = df_from_coll("tourist_arrivals")
    if arrivals.empty:
        print("No data.")
        return
    arrivals['month'] = arrivals['date'].dt.month
    plt.figure(figsize=(10,6))
    for city in arrivals['destination'].unique():
        citydata = arrivals[arrivals['destination']==city]
        plt.plot(citydata['date'], citydata['arrivals'], label=city, marker='o')
    plt.title("Monthly Tourist Arrivals (Crazy Patterns!)")
    plt.xlabel("Month")
    plt.ylabel("Arrivals")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def revenue_trend():
    revenue = df_from_coll("revenue")
    if revenue.empty:
        print("No data.")
        return
    plt.figure(figsize=(10,6))
    for city in revenue['destination'].unique():
        citydata = revenue[revenue['destination']==city]
        plt.plot(citydata['date'], citydata['revenue'], label=city, marker='x')
    plt.title("Monthly Revenue (Crazy Patterns!)")
    plt.xlabel("Month")
    plt.ylabel("Revenue (₹)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def hotels_stats():
    hotels = df_from_coll("hotels")
    if hotels.empty:
        print("No data.")
        return
    print("\n-- Hotels Data --")
    print(hotels[['name','destination','star_rating','occupancy_rate','price_per_night']].to_string(index=False))

def revenue_by_destination():
    revenue = df_from_coll("revenue")
    print("\n--- Total Revenue by Destination ---")
    g = revenue.groupby("destination")["revenue"].sum()
    for dest, val in g.items():
        print(f"{dest}: ₹{val:,.0f}")

def revenue_by_hotel():
    bookings = df_from_coll("bookings")
    hotels = df_from_coll("hotels")
    print("\n--- Revenue by Hotel ---")
    # Sum revenue grouped by hotel_id (handles missing hotels safely)
    if bookings.empty or hotels.empty:
        print("No hotel or booking data available.")
        return
    hotel_revenue = bookings.groupby("hotel_id")["total_amount"].sum().to_dict()
    for i, row in hotels.iterrows():
        revenue = hotel_revenue.get(row["hotel_id"], 0)
        print(f"{row['name']} ({row['destination']}): ₹{revenue:,.0f}")


def main():
    initialize_database()
    print("==== Tourism Intelligence (Delhi, Mumbai, Bangalore, Kolkata) ====")
    while True:
        print("""
Menu:
1. Show KPIs
2. Arrivals trend chart
3. Revenue trend chart
4. Show hotels data
5. Exit
6. Show revenue by destination/hotel
""")
        c = input("Enter your choice: ").strip()
        if c == '1':
            show_kpis()
        elif c == '2':
            arrivals_trend()
        elif c == '3':
            revenue_trend()
        elif c == '4':
            hotels_stats()
        elif c == '5':
            print("Goodbye!")
            break
        elif c == '6':
            print("a) Revenue by destination")
            print("b) Revenue by hotel")
            subc = input("Choose [a/b]: ").strip().lower()
            if subc == 'a':
                revenue_by_destination()
            elif subc == 'b':
                revenue_by_hotel()
            else:
                print("Invalid subchoice.")
        else:
            print("Invalid.")

if __name__ == "__main__":
    main()
