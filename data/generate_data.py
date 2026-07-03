"""
Indian E-Commerce Sales Data Generator
=========================================
Dataset Source Reference:
    This synthetic dataset is modeled after Indian e-commerce sales data
    publicly available on Kaggle:

    Title   : Amazon Sales Report (India) - E-Commerce Sales Dataset
    URL     : https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data
    Author  : The Devastator (Kaggle)
    License : CC0 - Public Domain

    Additional inspiration from:
    Title   : E-Commerce Data (India)
    URL     : https://www.kaggle.com/datasets/benroshan/ecommerce-data
    Author  : Ben Roshan

    The column schema, Indian state/city hierarchy, product categories,
    pricing in INR, festival-driven seasonality, and sales distributions
    are designed to mirror real Indian e-commerce retail behavior so that
    any model trained here can be applied directly to the real Kaggle data.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ── Indian Regions -> States -> Cities ────────────────────────────────────────
REGIONS = {
    "North": {
        "Uttar Pradesh":   ["Lucknow", "Kanpur", "Agra", "Varanasi", "Noida"],
        "Delhi":           ["New Delhi", "Dwarka", "Rohini", "Karol Bagh", "Lajpat Nagar"],
        "Rajasthan":       ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
        "Punjab":          ["Chandigarh", "Amritsar", "Ludhiana", "Patiala", "Jalandhar"],
    },
    "South": {
        "Karnataka":       ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belagavi"],
        "Tamil Nadu":      ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
        "Telangana":       ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
        "Kerala":          ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam"],
    },
    "West": {
        "Maharashtra":     ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
        "Gujarat":         ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
        "Goa":             ["Panaji", "Margao", "Vasco da Gama"],
    },
    "East": {
        "West Bengal":     ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
        "Odisha":          ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
        "Bihar":           ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga"],
        "Jharkhand":       ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"],
    },
    "Central": {
        "Madhya Pradesh":  ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"],
        "Chhattisgarh":    ["Raipur", "Bhilai", "Bilaspur", "Durg", "Rajnandgaon"],
    },
}

# ── Indian Product Categories ─────────────────────────────────────────────────
CATEGORIES = {
    "Electronics": [
        "Smartphones", "Laptops", "Tablets", "Earphones & Headphones",
        "Smart TVs", "Cameras", "Power Banks", "Smart Watches",
    ],
    "Clothing & Apparel": [
        "Men's Ethnic Wear", "Women's Sarees", "Kurta & Kurti",
        "Men's T-Shirts", "Women's Western Wear", "Kids Clothing",
        "Sportswear", "Innerwear & Socks",
    ],
    "Home & Kitchen": [
        "Cookware", "Furniture", "Bedsheets & Pillows", "Home Decor",
        "Kitchen Appliances", "Storage & Organisation", "Cleaning Supplies",
    ],
    "FMCG & Grocery": [
        "Packaged Foods", "Beverages", "Personal Care", "Health Supplements",
        "Baby Products", "Pet Supplies",
    ],
    "Books & Stationery": [
        "Competitive Exam Books", "Fiction & Literature", "Children Books",
        "Notebooks & Diaries", "Art & Craft Supplies",
    ],
    "Sports & Outdoors": [
        "Cricket Equipment", "Yoga & Fitness", "Cycling Accessories",
        "Trekking Gear", "Badminton Equipment",
    ],
}

PAYMENT_MODES = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking", "EMI"]
CUSTOMER_SEGMENTS = ["Individual", "Small Business", "Enterprise", "Student"]
FULFILMENT_TYPE = ["Amazon", "Merchant", "Meesho", "Flipkart"]
ORDER_STATUS = ["Delivered", "Shipped", "Cancelled", "Returned"]

# ── INR Pricing by Category ───────────────────────────────────────────────────
CATEGORY_PARAMS = {
    "Electronics":         {"price_mean": 18000, "price_std": 15000, "margin": 0.08},
    "Clothing & Apparel":  {"price_mean": 900,   "price_std": 600,   "margin": 0.22},
    "Home & Kitchen":      {"price_mean": 2500,  "price_std": 3000,  "margin": 0.14},
    "FMCG & Grocery":      {"price_mean": 350,   "price_std": 250,   "margin": 0.18},
    "Books & Stationery":  {"price_mean": 400,   "price_std": 300,   "margin": 0.20},
    "Sports & Outdoors":   {"price_mean": 1800,  "price_std": 1400,  "margin": 0.16},
}

# ── Indian Festival Seasonality (month-wise boost multipliers) ────────────────
# Key peaks: Diwali (Oct-Nov), Navratri (Sep-Oct), Holi (Mar),
#            Independence Day sale (Aug), Republic Day (Jan), End-of-year (Dec)
MONTHLY_SEASONALITY = {
    1:  0.82,   # Jan - Republic Day sale
    2:  0.76,   # Feb - Low
    3:  0.95,   # Mar - Holi
    4:  0.80,   # Apr - Low
    5:  0.85,   # May - Summer sale
    6:  0.78,   # Jun - Monsoon slowdown
    7:  0.82,   # Jul - Mid-year sale
    8:  1.05,   # Aug - Independence Day + Amazon Prime sale
    9:  1.15,   # Sep - Navratri begins, Onam
    10: 1.55,   # Oct - Navratri + Dussehra + Pre-Diwali peak
    11: 1.65,   # Nov - Diwali + Great Indian Festival
    12: 1.20,   # Dec - Christmas + Year-end sale
}


def generate_dataset(n_rows: int = 10_000, output_path: str = "data/train.csv") -> pd.DataFrame:
    """Generate a realistic Indian e-commerce sales dataset and save to CSV."""

    start = pd.Timestamp("2020-01-01")
    end   = pd.Timestamp("2023-12-31")
    all_days = pd.date_range(start, end, freq="B")  # business days only

    records = []
    order_counter = 1000

    region_names = list(REGIONS.keys())
    cat_names    = list(CATEGORIES.keys())

    # Category probability distribution
    cat_probs = [0.30, 0.25, 0.18, 0.12, 0.08, 0.07]

    for _ in range(n_rows):
        order_date  = pd.Timestamp(np.random.choice(all_days))
        month       = order_date.month
        season_mult = MONTHLY_SEASONALITY[month]

        # Category -> Sub-Category
        category   = np.random.choice(cat_names, p=cat_probs)
        sub_cat    = np.random.choice(CATEGORIES[category])

        # Region -> State -> City
        region     = np.random.choice(region_names, p=[0.28, 0.25, 0.25, 0.12, 0.10])
        state      = np.random.choice(list(REGIONS[region].keys()))
        city       = np.random.choice(REGIONS[region][state])

        segment    = np.random.choice(CUSTOMER_SEGMENTS, p=[0.55, 0.22, 0.12, 0.11])
        fulfilment = np.random.choice(FULFILMENT_TYPE,   p=[0.45, 0.25, 0.18, 0.12])
        payment    = np.random.choice(PAYMENT_MODES,     p=[0.35, 0.18, 0.17, 0.18, 0.07, 0.05])
        status     = np.random.choice(ORDER_STATUS,      p=[0.78, 0.10, 0.07, 0.05])

        # INR Pricing
        params      = CATEGORY_PARAMS[category]
        base_price  = max(50, np.random.normal(params["price_mean"], params["price_std"]))
        quantity    = np.random.randint(1, 6)
        discount    = np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50],
                                       p=[0.35, 0.12, 0.15, 0.12, 0.10, 0.08, 0.05, 0.03])

        # Cancelled/Returned orders have 0 or negative sales impact
        if status in ["Cancelled", "Returned"]:
            sales  = 0.0
            profit = 0.0
        else:
            sales  = round(base_price * quantity * (1 - discount) * season_mult
                           * np.random.uniform(0.88, 1.12), 2)
            profit_rate = params["margin"] - discount * 0.4 + np.random.uniform(-0.02, 0.02)
            profit = round(sales * profit_rate, 2)

        # GST (Indian Goods & Services Tax) — applied to electronics/appliances
        gst_rate = 0.18 if category == "Electronics" else (0.12 if category == "Home & Kitchen" else 0.05)
        gst_amt  = round(sales * gst_rate, 2)

        courier_days = np.random.randint(1, 8)
        ship_date   = order_date + pd.Timedelta(days=courier_days)

        records.append({
            "Order ID":        f"IND-{order_date.year}-{order_counter:07d}",
            "Order Date":      order_date.strftime("%Y-%m-%d"),
            "Ship Date":       ship_date.strftime("%Y-%m-%d"),
            "Fulfilment":      fulfilment,
            "Customer Segment": segment,
            "Country":         "India",
            "Region":          region,
            "State":           state,
            "City":            city,
            "Category":        category,
            "Sub-Category":    sub_cat,
            "Payment Mode":    payment,
            "Order Status":    status,
            "Quantity":        quantity,
            "Discount":        discount,
            "Sales (INR)":     sales,
            "Profit (INR)":    profit,
            "GST (INR)":       gst_amt,
        })
        order_counter += 1

    df = pd.DataFrame(records)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df = df.sort_values("Order Date").reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[OK] Indian dataset generated: {output_path}  ({len(df):,} rows)")
    print(f"     Date range: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}")
    print(f"     States covered: {df['State'].nunique()}")
    print(f"     Cities covered: {df['City'].nunique()}")
    return df


if __name__ == "__main__":
    generate_dataset()
