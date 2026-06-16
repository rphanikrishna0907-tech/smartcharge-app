
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from math import radians, sin, cos, sqrt, atan2

import pandas as pd
import streamlit as st

try:
    from streamlit_js_eval import get_geolocation
except Exception:
    get_geolocation = None


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="VoltIQ Technologies Pvt. Ltd",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# FILE STORAGE
# ==================================================
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
VEHICLES_FILE = os.path.join(DATA_DIR, "vehicles.csv")
STATIONS_FILE = os.path.join(DATA_DIR, "stations.csv")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.csv")

os.makedirs(DATA_DIR, exist_ok=True)


# ==================================================
# DEFAULT DATA
# ==================================================
KNOWN_LOCATIONS = {
    "Hyderabad": (17.3850, 78.4867),
    "Gachibowli": (17.4401, 78.3489),
    "Hitech City": (17.4504, 78.3805),
    "Madhapur": (17.4483, 78.3915),
    "Kukatpally": (17.4933, 78.3996),
    "Begumpet": (17.4435, 78.4622),
    "Durgam Cheruvu": (17.4309, 78.3894),
    "Miyapur": (17.4964, 78.3611),
    "BHEL": (17.4948, 78.3053),
    "Secunderabad": (17.4399, 78.4983),
    "Banjara Hills": (17.4126, 78.4482),
    "Kondapur": (17.4698, 78.3578),
    "Financial District": (17.4149, 78.3422),
    "Jubilee Hills": (17.4239, 78.4738),
}

DEFAULT_USERS = [
    {
        "User ID": "U-ADMIN",
        "Name": "VoltIQ Host",
        "Email": "group 1 goated",
        "Password Hash": hashlib.sha256("shahid is goat".encode()).hexdigest(),
        "Phone": "9999999999",
        "Role": "Host",
        "Preferred Area": "Hyderabad",
        "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "User ID": "U-DEMO",
        "Name": "Demo User",
        "Email": "user@demo.com",
        "Password Hash": hashlib.sha256("User@123".encode()).hexdigest(),
        "Phone": "8888888888",
        "Role": "User",
        "Preferred Area": "Gachibowli",
        "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
]

VEHICLE_COLUMNS = [
    "Vehicle ID",
    "User ID",
    "Vehicle Number",
    "EV Model",
    "Connector",
    "Battery Capacity kWh",
    "Created At",
]

RESERVATION_COLUMNS = [
    "Reservation ID",
    "User ID",
    "Driver Name",
    "Vehicle Number",
    "EV Model",
    "Mobile Number",
    "Station ID",
    "Station Name",
    "Date",
    "Time",
    "Duration",
    "Status",
    "Created At",
]

DEFAULT_STATIONS = [
    {
        "Station ID": "SC001",
        "Station Name": "Tata Power EZ Charge - Begumpet",
        "Network": "Tata Power EZ Charge",
        "City": "Hyderabad",
        "Area": "Begumpet",
        "Address": "Begumpet, Hyderabad, Telangana",
        "Charging Type": "DC Fast Charging",
        "Connector": "CCS2",
        "Total Chargers": 4,
        "Available Chargers": 2,
        "Occupied Chargers": 1,
        "Faulty Chargers": 1,
        "Queue Length": 1,
        "Price per kWh": 22,
        "Rating": 4.2,
        "Open 24x7": "No",
        "Amenities": "Parking, Service Center",
        "Latitude": 17.4435,
        "Longitude": 78.4622,
    },
    {
        "Station ID": "SC002",
        "Station Name": "Statiq EV Charging Station - Kukatpally",
        "Network": "Statiq",
        "City": "Hyderabad",
        "Area": "Kukatpally",
        "Address": "Kukatpally, Hyderabad, Telangana",
        "Charging Type": "DC Fast Charging",
        "Connector": "CCS2",
        "Total Chargers": 4,
        "Available Chargers": 1,
        "Occupied Chargers": 2,
        "Faulty Chargers": 1,
        "Queue Length": 3,
        "Price per kWh": 21,
        "Rating": 4.1,
        "Open 24x7": "Yes",
        "Amenities": "Parking, Food",
        "Latitude": 17.4933,
        "Longitude": 78.3996,
    },
    {
        "Station ID": "SC003",
        "Station Name": "ChargeZone Charging Hub - Hitech City",
        "Network": "ChargeZone",
        "City": "Hyderabad",
        "Area": "Hitech City",
        "Address": "Hitech City, Hyderabad, Telangana",
        "Charging Type": "DC Fast Charging",
        "Connector": "CCS2",
        "Total Chargers": 5,
        "Available Chargers": 2,
        "Occupied Chargers": 3,
        "Faulty Chargers": 0,
        "Queue Length": 1,
        "Price per kWh": 22,
        "Rating": 4.5,
        "Open 24x7": "Yes",
        "Amenities": "Parking, Food, Restroom, Mall",
        "Latitude": 17.4504,
        "Longitude": 78.3805,
    },
    {
        "Station ID": "SC004",
        "Station Name": "Jio-bp Pulse EV Charging - Madhapur",
        "Network": "Jio-bp",
        "City": "Hyderabad",
        "Area": "Madhapur",
        "Address": "Madhapur, Hyderabad, Telangana",
        "Charging Type": "DC Fast Charging",
        "Connector": "CCS2",
        "Total Chargers": 4,
        "Available Chargers": 0,
        "Occupied Chargers": 4,
        "Faulty Chargers": 0,
        "Queue Length": 4,
        "Price per kWh": 23,
        "Rating": 4.0,
        "Open 24x7": "Yes",
        "Amenities": "Parking, Food, Restroom",
        "Latitude": 17.4483,
        "Longitude": 78.3915,
    },
    {
        "Station ID": "SC005",
        "Station Name": "GLIDA Green Drive - Gachibowli",
        "Network": "GLIDA",
        "City": "Hyderabad",
        "Area": "Gachibowli",
        "Address": "Gachibowli, Hyderabad, Telangana",
        "Charging Type": "DC Fast Charging",
        "Connector": "CCS2",
        "Total Chargers": 6,
        "Available Chargers": 4,
        "Occupied Chargers": 2,
        "Faulty Chargers": 0,
        "Queue Length": 0,
        "Price per kWh": 20,
        "Rating": 4.4,
        "Open 24x7": "Yes",
        "Amenities": "Parking, Restroom, Food",
        "Latitude": 17.4401,
        "Longitude": 78.3489,
    },
    {
        "Station ID": "SC006",
        "Station Name": "Public EV Charging Point - Durgam Cheruvu",
        "Network": "Public EV Network",
        "City": "Hyderabad",
        "Area": "Durgam Cheruvu",
        "Address": "Durgam Cheruvu, Hyderabad, Telangana",
        "Charging Type": "AC Charging",
        "Connector": "Type 2",
        "Total Chargers": 3,
        "Available Chargers": 1,
        "Occupied Chargers": 1,
        "Faulty Chargers": 1,
        "Queue Length": 1,
        "Price per kWh": 17,
        "Rating": 3.9,
        "Open 24x7": "No",
        "Amenities": "Parking",
        "Latitude": 17.4309,
        "Longitude": 78.3894,
    },
    {
        "Station ID": "SC007",
        "Station Name": "Tata Power EZ Charge - Miyapur",
        "Network": "Tata Power EZ Charge",
        "City": "Hyderabad",
        "Area": "Miyapur",
        "Address": "Miyapur Metro Station, Hyderabad, Telangana",
        "Charging Type": "AC Charging",
        "Connector": "Type 2",
        "Total Chargers": 3,
        "Available Chargers": 1,
        "Occupied Chargers": 2,
        "Faulty Chargers": 0,
        "Queue Length": 2,
        "Price per kWh": 18,
        "Rating": 4.0,
        "Open 24x7": "No",
        "Amenities": "Parking, Metro Access",
        "Latitude": 17.4964,
        "Longitude": 78.3611,
    },
    {
        "Station ID": "SC008",
        "Station Name": "Public EV Charging Station - BHEL",
        "Network": "Public EV Network",
        "City": "Hyderabad",
        "Area": "BHEL",
        "Address": "BHEL, Hyderabad, Telangana",
        "Charging Type": "AC Charging",
        "Connector": "Type 2",
        "Total Chargers": 4,
        "Available Chargers": 2,
        "Occupied Chargers": 2,
        "Faulty Chargers": 0,
        "Queue Length": 1,
        "Price per kWh": 16,
        "Rating": 4.0,
        "Open 24x7": "No",
        "Amenities": "Parking",
        "Latitude": 17.4948,
        "Longitude": 78.3053,
    },
    {
        "Station ID": "SC009",
        "Station Name": "VoltIQ FastCharge - Financial District",
        "Network": "VoltIQ",
        "City": "Hyderabad",
        "Area": "Financial District",
        "Address": "Financial District, Hyderabad, Telangana",
        "Charging Type": "DC Fast Charging",
        "Connector": "CCS2",
        "Total Chargers": 8,
        "Available Chargers": 5,
        "Occupied Chargers": 3,
        "Faulty Chargers": 0,
        "Queue Length": 0,
        "Price per kWh": 19,
        "Rating": 4.6,
        "Open 24x7": "Yes",
        "Amenities": "Parking, Food, Restroom",
        "Latitude": 17.4149,
        "Longitude": 78.3422,
    },
    {
        "Station ID": "SC010",
        "Station Name": "VoltIQ ChargePoint - Kondapur",
        "Network": "VoltIQ",
        "City": "Hyderabad",
        "Area": "Kondapur",
        "Address": "Kondapur, Hyderabad, Telangana",
        "Charging Type": "AC Charging",
        "Connector": "Type 2",
        "Total Chargers": 4,
        "Available Chargers": 2,
        "Occupied Chargers": 2,
        "Faulty Chargers": 0,
        "Queue Length": 1,
        "Price per kWh": 17,
        "Rating": 4.2,
        "Open 24x7": "No",
        "Amenities": "Parking, Food",
        "Latitude": 17.4698,
        "Longitude": 78.3578,
    },
]


# ==================================================
# FILE HELPERS
# ==================================================
def save_df(df, file_path):
    df.to_csv(file_path, index=False)


def load_df(file_path, columns, default_data=None):
    if not os.path.exists(file_path):
        if default_data is None:
            df = pd.DataFrame(columns=columns)
        else:
            df = pd.DataFrame(default_data)
        save_df(df, file_path)
        return df

    try:
        df = pd.read_csv(file_path, dtype=str).fillna("")
    except Exception:
        if default_data is None:
            df = pd.DataFrame(columns=columns)
        else:
            df = pd.DataFrame(default_data)
        save_df(df, file_path)
        return df

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns]


def load_users():
    return load_df(USERS_FILE, list(DEFAULT_USERS[0].keys()), DEFAULT_USERS)


def save_users(df):
    save_df(df, USERS_FILE)


def load_vehicles():
    return load_df(VEHICLES_FILE, VEHICLE_COLUMNS)


def save_vehicles(df):
    save_df(df, VEHICLES_FILE)


def load_stations():
    return load_df(STATIONS_FILE, list(DEFAULT_STATIONS[0].keys()), DEFAULT_STATIONS)


def save_stations(df):
    save_df(df, STATIONS_FILE)


def load_reservations():
    return load_df(RESERVATIONS_FILE, RESERVATION_COLUMNS)


def save_reservations(df):
    save_df(df, RESERVATIONS_FILE)


def reload_all_data():
    st.session_state.users = load_users()
    st.session_state.vehicles = load_vehicles()
    st.session_state.stations = load_stations()
    st.session_state.reservations = load_reservations()


# ==================================================
# GENERAL HELPERS
# ==================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


APP_TIMEZONE = ZoneInfo("Asia/Kolkata")


def now_ist():
    return datetime.now(APP_TIMEZONE)


def today_ist():
    return now_ist().date()


def round_up_to_next_30_minutes(dt):
    dt = dt.replace(second=0, microsecond=0)

    if dt.minute == 0:
        return dt

    if dt.minute <= 30:
        return dt.replace(minute=30)

    return dt.replace(minute=0) + timedelta(hours=1)


def get_time_options_for_date(date_text):
    selected_date = datetime.strptime(date_text, "%Y-%m-%d").date()

    opening_hour = 6
    closing_hour = 23

    start_time = datetime.combine(selected_date, datetime.min.time(), tzinfo=APP_TIMEZONE)
    start_time = start_time.replace(hour=opening_hour, minute=0)

    if selected_date == today_ist():
        next_valid_time = round_up_to_next_30_minutes(now_ist() + timedelta(minutes=15))
        if next_valid_time > start_time:
            start_time = next_valid_time

    end_time = datetime.combine(selected_date, datetime.min.time(), tzinfo=APP_TIMEZONE)
    end_time = end_time.replace(hour=closing_hour, minute=0)

    options = []
    current = start_time

    while current <= end_time:
        options.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)

    return options


def get_booking_date_options(days=8):
    options = []

    for i in range(days):
        day = today_ist() + timedelta(days=i)
        day_text = day.strftime("%Y-%m-%d")

        if get_time_options_for_date(day_text):
            options.append(day_text)

    return options


def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(radius * c, 2)


def get_maps_link(latitude, longitude):
    return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"


def calculate_wait_time(queue_length, charging_type):
    queue_length = int(float(queue_length or 0))
    if charging_type == "DC Fast Charging":
        return queue_length * 30
    if charging_type == "AC Charging":
        return queue_length * 55
    return queue_length * 45


def health_status(total, faulty):
    total = int(float(total or 0))
    faulty = int(float(faulty or 0))
    if total <= 0:
        return "Invalid"
    ratio = faulty / total
    if ratio == 0:
        return "Excellent"
    if ratio <= 0.20:
        return "Good"
    if ratio <= 0.40:
        return "Average"
    return "Poor"


def availability_status(available):
    available = int(float(available or 0))
    if available >= 3:
        return "Good Availability"
    if available >= 1:
        return "Limited Availability"
    return "Currently Full"


def extract_location(location_data):
    if not location_data:
        return None, None
    if isinstance(location_data, dict):
        if "coords" in location_data:
            coords = location_data["coords"]
            return coords.get("latitude"), coords.get("longitude")
        if "latitude" in location_data and "longitude" in location_data:
            return location_data.get("latitude"), location_data.get("longitude")
    return None, None


def prepare_station_data(stations):
    df = stations.copy()
    df = df.drop_duplicates(subset=["Station ID", "Station Name"], keep="first")

    numeric_columns = [
        "Total Chargers",
        "Available Chargers",
        "Occupied Chargers",
        "Faulty Chargers",
        "Queue Length",
        "Price per kWh",
        "Rating",
        "Latitude",
        "Longitude",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Estimated Wait Time"] = df.apply(
        lambda row: calculate_wait_time(row["Queue Length"], row["Charging Type"]),
        axis=1,
    )

    df["Health Status"] = df.apply(
        lambda row: health_status(row["Total Chargers"], row["Faulty Chargers"]),
        axis=1,
    )

    df["Availability Status"] = df["Available Chargers"].apply(availability_status)

    df["Maps Link"] = df.apply(
        lambda row: get_maps_link(row["Latitude"], row["Longitude"]),
        axis=1,
    )

    if st.session_state.user_latitude is not None and st.session_state.user_longitude is not None:
        user_lat = float(st.session_state.user_latitude)
        user_lon = float(st.session_state.user_longitude)

        df["User Distance km"] = df.apply(
            lambda row: distance_km(
                user_lat,
                user_lon,
                float(row["Latitude"]),
                float(row["Longitude"]),
            ),
            axis=1,
        )
    else:
        df["User Distance km"] = pd.NA

    return df


def get_closest_station(dataframe):
    if dataframe is None or dataframe.empty:
        return None
    if "Available Chargers" not in dataframe.columns:
        return None

    available_df = dataframe[dataframe["Available Chargers"] > 0].copy()
    if available_df.empty:
        return None

    if "User Distance km" in available_df.columns:
        distance_df = available_df[pd.notna(available_df["User Distance km"])].copy()
        if not distance_df.empty:
            distance_df = distance_df.sort_values(
                by=["User Distance km", "Estimated Wait Time", "Price per kWh", "Rating"],
                ascending=[True, True, True, False],
            )
            if not distance_df.empty:
                return distance_df.iloc[0]

    fallback_df = available_df.sort_values(
        by=["Estimated Wait Time", "Price per kWh", "Rating"],
        ascending=[True, True, False],
    )
    if fallback_df.empty:
        return None

    return fallback_df.iloc[0]


def get_filtered_stations(stations_df):
    filtered = stations_df.copy()

    if st.session_state.selected_city != "All":
        filtered = filtered[filtered["City"] == st.session_state.selected_city]

    if st.session_state.selected_area != "All":
        filtered = filtered[filtered["Area"] == st.session_state.selected_area]

    if st.session_state.selected_network != "All":
        filtered = filtered[filtered["Network"] == st.session_state.selected_network]

    if st.session_state.selected_charging_type != "All":
        filtered = filtered[filtered["Charging Type"] == st.session_state.selected_charging_type]

    if st.session_state.selected_connector != "All":
        filtered = filtered[filtered["Connector"] == st.session_state.selected_connector]

    if st.session_state.availability_filter == "Available Now":
        filtered = filtered[filtered["Available Chargers"] > 0]
    elif st.session_state.availability_filter == "Currently Full":
        filtered = filtered[filtered["Available Chargers"] == 0]
    elif st.session_state.availability_filter == "Low Queue Only":
        filtered = filtered[filtered["Queue Length"] <= 2]

    if st.session_state.open_filter == "Open 24x7 Only":
        filtered = filtered[filtered["Open 24x7"] == "Yes"]

    if st.session_state.amenity_filter != "All":
        filtered = filtered[
            filtered["Amenities"].str.contains(st.session_state.amenity_filter, case=False, na=False)
        ]

    filtered = filtered[filtered["Price per kWh"] <= st.session_state.max_price]
    filtered = filtered[filtered["Rating"] >= st.session_state.minimum_rating]

    if st.session_state.user_latitude is not None and st.session_state.user_longitude is not None:
        filtered = filtered[filtered["User Distance km"] <= st.session_state.max_distance]

    search_text = st.session_state.search_keyword.strip()
    if search_text:
        filtered = filtered[
            filtered["Station Name"].str.contains(search_text, case=False, na=False)
            | filtered["Area"].str.contains(search_text, case=False, na=False)
            | filtered["Network"].str.contains(search_text, case=False, na=False)
            | filtered["Connector"].str.contains(search_text, case=False, na=False)
        ]

    return filtered


def sidebar_selectbox(label, options, key):
    if not options:
        options = ["All"]
    if key not in st.session_state or st.session_state[key] not in options:
        st.session_state[key] = options[0]
    return st.sidebar.selectbox(label, options, key=key)


def user_name_from_id(user_id, users_df):
    row = users_df[users_df["User ID"] == user_id]
    if row.empty:
        return "Unknown User"
    return row.iloc[0]["Name"]


def card_metric(label, value, help_text=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# SESSION STATE INIT
# ==================================================
if "users" not in st.session_state:
    reload_all_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "user_latitude" not in st.session_state:
    st.session_state.user_latitude = None

if "user_longitude" not in st.session_state:
    st.session_state.user_longitude = None

if "location_requested" not in st.session_state:
    st.session_state.location_requested = False


# ==================================================
# CSS
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(20,184,166,0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(99,102,241,0.18), transparent 30%),
            linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%);
    }

    .main-title {
        font-size: 46px;
        font-weight: 900;
        background: linear-gradient(90deg, #0F766E, #2563EB, #9333EA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #475569;
        margin-top: 0;
        font-weight: 500;
    }

    .glass-box {
        padding: 24px;
        border-radius: 24px;
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        margin-bottom: 20px;
    }

    .hero-box {
        padding: 28px;
        border-radius: 28px;
        background: linear-gradient(135deg, #CCFBF1, #DBEAFE, #F3E8FF);
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 20px 45px rgba(37, 99, 235, 0.12);
        margin-bottom: 22px;
        color: #0F172A;
    }

    .hero-title {
        font-size: 30px;
        font-weight: 900;
        margin-bottom: 8px;
        color: #0F172A;
    }

    .hero-text {
        font-size: 16px;
        color: #334155;
        line-height: 1.6;
    }

    .metric-card {
        padding: 20px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(239,246,255,0.95));
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        min-height: 118px;
    }

    .metric-label {
        color: #64748B;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .metric-value {
        color: #0F172A;
        font-size: 30px;
        font-weight: 900;
        margin-top: 6px;
    }

    .metric-help {
        color: #64748B;
        font-size: 12px;
        margin-top: 4px;
    }

    .station-card {
        padding: 22px;
        border-radius: 24px;
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
        margin-bottom: 18px;
    }

    .badge-green {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #DCFCE7;
        color: #166534;
        font-weight: 800;
        font-size: 12px;
        margin-right: 8px;
    }

    .badge-blue {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #DBEAFE;
        color: #1D4ED8;
        font-weight: 800;
        font-size: 12px;
        margin-right: 8px;
    }

    .badge-orange {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #FFEDD5;
        color: #C2410C;
        font-weight: 800;
        font-size: 12px;
        margin-right: 8px;
    }

    .company-box {
        padding: 24px;
        border-radius: 24px;
        background: linear-gradient(135deg, #F0FDFA, #EFF6FF, #FAF5FF);
        border: 1px solid rgba(148,163,184,0.4);
        color: #0F172A;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC, #E0F2FE);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# LOGIN PAGE
# ==================================================
def show_login_page():
    st.markdown('<p class="main-title">⚡ VoltIQ Technologies Pvt. Ltd</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Smart EV Charging Availability, Reservation and Queue Management System</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">Charge faster. Wait less. Drive smarter.</div>
            <div class="hero-text">
                Find nearby charging stations, check live availability, view queue length,
                reserve charging slots, save EV details, and let hosts manage everything from one dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(["🔐 Login", "✨ Create Account"])

    with login_tab:
        with st.container(border=True):
            st.subheader("Login to VoltIQ")

            email = st.text_input("Login ID / Email")
            password = st.text_input("Password", type="password")

            if st.button("Login", type="primary", use_container_width=True):
                users = load_users()
                email_clean = email.strip().lower()

                matched = users[
                    (users["Email"].str.lower() == email_clean)
                    & (users["Password Hash"] == hash_password(password))
                ]

                if matched.empty:
                    st.error("Invalid login ID or password.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user = matched.iloc[0].to_dict()
                    reload_all_data()
                    st.success("Login successful.")
                    st.rerun()

            st.info("User Demo: user@demo.com / User@123")
            st.caption("Host Login: group 1 goated / shahid is goat")

    with signup_tab:
        with st.container(border=True):
            st.subheader("Create New User Account")

            name = st.text_input("Full Name")
            signup_email = st.text_input("Email / Login ID")
            phone = st.text_input("Mobile Number")
            preferred_area = st.selectbox("Preferred Area", list(KNOWN_LOCATIONS.keys()))
            signup_password = st.text_input("Create Password", type="password")

            if st.button("Create Account", use_container_width=True):
                users = load_users()

                if not name.strip() or not signup_email.strip() or not phone.strip() or not signup_password:
                    st.error("Please fill all fields.")
                elif not phone.isdigit() or len(phone) != 10:
                    st.error("Please enter a valid 10-digit mobile number.")
                elif signup_email.strip().lower() in users["Email"].str.lower().tolist():
                    st.error("This login ID is already registered.")
                else:
                    new_user = {
                        "User ID": "U-" + str(uuid.uuid4())[:8].upper(),
                        "Name": name.strip(),
                        "Email": signup_email.strip().lower(),
                        "Password Hash": hash_password(signup_password),
                        "Phone": phone.strip(),
                        "Role": "User",
                        "Preferred Area": preferred_area,
                        "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
                    save_users(users)
                    reload_all_data()
                    st.success("Account created successfully. Host can now see this user in the dashboard.")


if not st.session_state.logged_in:
    show_login_page()
    st.stop()


# ==================================================
# REFRESH DATA FOR EVERY RUN
# ==================================================
reload_all_data()

user = st.session_state.user
user_id = user["User ID"]
is_host = user["Role"] == "Host"


# ==================================================
# HEADER
# ==================================================
top_col1, top_col2 = st.columns([3, 1])

with top_col1:
    st.markdown('<p class="main-title">⚡ VoltIQ Technologies Pvt. Ltd</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Live EV Charging Platform for Users and Station Hosts</p>',
        unsafe_allow_html=True,
    )

with top_col2:
    with st.popover("👤 Profile"):
        st.write(f"**Name:** {user['Name']}")
        st.write(f"**Login ID:** {user['Email']}")
        st.write(f"**Role:** {user['Role']}")
        if st.button("🔄 Refresh Data"):
            reload_all_data()
            st.rerun()
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.user_latitude = None
            st.session_state.user_longitude = None
            st.session_state.location_requested = False
            st.rerun()


# ==================================================
# HOST DASHBOARD
# ==================================================
if is_host:
    users_df = load_users()
    vehicles_df = load_vehicles()
    stations_raw = load_stations()
    reservations_df = load_reservations()
    stations_df = prepare_station_data(stations_raw)

    active_count = len(reservations_df[reservations_df["Status"].isin(["Confirmed", "Queued"])])
    confirmed_count = len(reservations_df[reservations_df["Status"] == "Confirmed"])
    queued_count = len(reservations_df[reservations_df["Status"] == "Queued"])

    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">🛠️ Host Control Center</div>
            <div class="hero-text">
                Monitor users, vehicles, reservations, queue load, charger status and station health from one place.
                User registrations and reservations are now saved in shared CSV files, so the host dashboard can cross-check them.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Refresh Latest User & Reservation Data", type="primary"):
        reload_all_data()
        st.rerun()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        card_metric("Registered Users", len(users_df[users_df["Role"] == "User"]), "visible to host")
    with c2:
        card_metric("Saved Vehicles", len(vehicles_df), "all user vehicles")
    with c3:
        card_metric("Total Reservations", len(reservations_df), "all bookings")
    with c4:
        card_metric("Active Bookings", active_count, "confirmed + queued")
    with c5:
        card_metric("Available Chargers", int(stations_df["Available Chargers"].sum()), "live capacity")

    st.markdown("### 📈 Host Quick Analytics")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if not reservations_df.empty:
            status_chart = reservations_df["Status"].value_counts().reset_index()
            status_chart.columns = ["Status", "Count"]
            st.bar_chart(status_chart.set_index("Status"))
        else:
            st.info("No reservation chart yet.")

    with chart_col2:
        station_chart = stations_df[["Station Name", "Available Chargers", "Occupied Chargers", "Queue Length"]].copy()
        station_chart = station_chart.set_index("Station Name")
        st.bar_chart(station_chart)

    host_tab1, host_tab2, host_tab3, host_tab4, host_tab5 = st.tabs(
        [
            "📋 Reservations",
            "👥 Users",
            "🚗 Vehicles",
            "⚙️ Station Management",
            "➕ Add Station",
        ]
    )

    with host_tab1:
        st.subheader("📋 Reservation Cross-Check")

        if reservations_df.empty:
            st.info("No reservations yet.")
        else:
            merged = reservations_df.merge(
                users_df[["User ID", "Name", "Email", "Phone"]],
                on="User ID",
                how="left",
                suffixes=("", " User"),
            )

            search_res = st.text_input("Search reservation, vehicle, user or station")
            display_res = merged.copy()

            if search_res.strip():
                s = search_res.strip()
                display_res = display_res[
                    display_res["Reservation ID"].str.contains(s, case=False, na=False)
                    | display_res["Driver Name"].str.contains(s, case=False, na=False)
                    | display_res["Vehicle Number"].str.contains(s, case=False, na=False)
                    | display_res["Station Name"].str.contains(s, case=False, na=False)
                    | display_res["Name"].str.contains(s, case=False, na=False)
                    | display_res["Email"].str.contains(s, case=False, na=False)
                ]

            st.dataframe(display_res, use_container_width=True, hide_index=True)

            active_res = reservations_df[reservations_df["Status"].isin(["Confirmed", "Queued"])]

            if not active_res.empty:
                st.markdown("### Complete Reservation")
                selected_res = st.selectbox(
                    "Select active reservation",
                    active_res["Reservation ID"].tolist(),
                )

                if st.button("✅ Mark Selected Reservation as Completed"):
                    reservations_df = load_reservations()
                    stations_raw = load_stations()

                    res_rows = reservations_df[reservations_df["Reservation ID"] == selected_res]

                    if res_rows.empty:
                        st.error("Reservation not found.")
                    else:
                        res_index = res_rows.index[0]
                        station_id = reservations_df.loc[res_index, "Station ID"]
                        old_status = reservations_df.loc[res_index, "Status"]

                        station_rows = stations_raw[stations_raw["Station ID"] == station_id]

                        if station_rows.empty:
                            st.error("Station not found.")
                        else:
                            station_index = station_rows.index[0]

                            occupied = int(float(stations_raw.loc[station_index, "Occupied Chargers"]))
                            available = int(float(stations_raw.loc[station_index, "Available Chargers"]))
                            queue = int(float(stations_raw.loc[station_index, "Queue Length"]))

                            if old_status == "Confirmed":
                                stations_raw.loc[station_index, "Occupied Chargers"] = max(0, occupied - 1)
                                stations_raw.loc[station_index, "Available Chargers"] = available + 1

                            if old_status == "Queued":
                                stations_raw.loc[station_index, "Queue Length"] = max(0, queue - 1)

                            reservations_df.loc[res_index, "Status"] = "Completed"

                            save_reservations(reservations_df)
                            save_stations(stations_raw)
                            reload_all_data()

                            st.success("Reservation completed and station status updated.")
                            st.rerun()

    with host_tab2:
        st.subheader("👥 Registered Users")

        user_search = st.text_input("Search users")
        users_display = users_df.drop(columns=["Password Hash"], errors="ignore")

        if user_search.strip():
            s = user_search.strip()
            users_display = users_display[
                users_display["Name"].str.contains(s, case=False, na=False)
                | users_display["Email"].str.contains(s, case=False, na=False)
                | users_display["Phone"].str.contains(s, case=False, na=False)
                | users_display["Preferred Area"].str.contains(s, case=False, na=False)
            ]

        st.dataframe(users_display, use_container_width=True, hide_index=True)

    with host_tab3:
        st.subheader("🚗 Saved Vehicles by Users")

        if vehicles_df.empty:
            st.info("No vehicles saved yet.")
        else:
            vehicle_display = vehicles_df.merge(
                users_df[["User ID", "Name", "Email", "Phone"]],
                on="User ID",
                how="left",
            )
            st.dataframe(vehicle_display, use_container_width=True, hide_index=True)

    with host_tab4:
        st.subheader("⚙️ Station Management")

        if stations_raw.empty:
            st.warning("No stations available.")
        else:
            station_choice = st.selectbox(
                "Select station to update",
                stations_raw["Station Name"].tolist(),
            )

            station_rows = stations_raw[stations_raw["Station Name"] == station_choice]

            if station_rows.empty:
                st.error("Selected station not found.")
            else:
                station_index = station_rows.index[0]
                selected = stations_raw.loc[station_index]

                st.markdown(
                    f"""
                    <div class="station-card">
                        <span class="badge-green">{selected['Network']}</span>
                        <span class="badge-blue">{selected['Charging Type']}</span>
                        <span class="badge-orange">{selected['Area']}</span>
                        <h3>{selected['Station Name']}</h3>
                        <p>{selected['Address']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form("host_station_edit_form"):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        available = st.number_input(
                            "Available Chargers",
                            min_value=0,
                            value=int(float(selected["Available Chargers"])),
                        )
                        queue = st.number_input(
                            "Queue Length",
                            min_value=0,
                            value=int(float(selected["Queue Length"])),
                        )
                    with ec2:
                        occupied = st.number_input(
                            "Occupied Chargers",
                            min_value=0,
                            value=int(float(selected["Occupied Chargers"])),
                        )
                        price = st.number_input(
                            "Price per kWh",
                            min_value=1,
                            value=int(float(selected["Price per kWh"])),
                        )
                    with ec3:
                        faulty = st.number_input(
                            "Faulty Chargers",
                            min_value=0,
                            value=int(float(selected["Faulty Chargers"])),
                        )
                        rating = st.number_input(
                            "Rating",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(selected["Rating"]),
                            step=0.1,
                        )

                    update_station = st.form_submit_button("Update Station", use_container_width=True)

                if update_station:
                    total = int(float(selected["Total Chargers"]))

                    if available + occupied + faulty != total:
                        st.error("Available + Occupied + Faulty must equal Total Chargers.")
                    else:
                        stations_raw.loc[station_index, "Available Chargers"] = available
                        stations_raw.loc[station_index, "Occupied Chargers"] = occupied
                        stations_raw.loc[station_index, "Faulty Chargers"] = faulty
                        stations_raw.loc[station_index, "Queue Length"] = queue
                        stations_raw.loc[station_index, "Price per kWh"] = price
                        stations_raw.loc[station_index, "Rating"] = rating

                        save_stations(stations_raw)
                        reload_all_data()

                        st.success("Station updated successfully. Users will see this updated status.")
                        st.rerun()

            st.markdown("### Station Database")
            st.dataframe(stations_raw, use_container_width=True, hide_index=True)

    with host_tab5:
        st.subheader("➕ Add New Charging Station")

        with st.form("add_station_form"):
            a1, a2 = st.columns(2)

            with a1:
                name = st.text_input("Station Name")
                network = st.text_input("Network", value="VoltIQ")
                city = st.text_input("City", value="Hyderabad")
                area = st.text_input("Area")
                address = st.text_input("Address")
                charging_type = st.selectbox("Charging Type", ["DC Fast Charging", "AC Charging"])
                connector = st.selectbox("Connector", ["CCS2", "Type 2", "CHAdeMO"])

            with a2:
                total = st.number_input("Total Chargers", min_value=1, value=4)
                available = st.number_input("Available Chargers", min_value=0, value=2)
                occupied = st.number_input("Occupied Chargers", min_value=0, value=2)
                faulty = st.number_input("Faulty Chargers", min_value=0, value=0)
                queue = st.number_input("Queue Length", min_value=0, value=0)
                price = st.number_input("Price per kWh", min_value=1, value=20)
                rating = st.number_input("Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.1)

            open_24 = st.selectbox("Open 24x7", ["Yes", "No"])
            amenities = st.text_input("Amenities", value="Parking, Food")
            latitude = st.number_input("Latitude", value=17.3850, format="%.6f")
            longitude = st.number_input("Longitude", value=78.4867, format="%.6f")

            add_station = st.form_submit_button("Add Station", use_container_width=True)

        if add_station:
            stations_raw = load_stations()

            if not name.strip() or not area.strip() or not address.strip():
                st.error("Station name, area and address are required.")
            elif available + occupied + faulty != total:
                st.error("Available + Occupied + Faulty must equal Total Chargers.")
            elif name.strip().lower() in stations_raw["Station Name"].str.lower().tolist():
                st.error("This station already exists.")
            else:
                new_station = {
                    "Station ID": "SC-" + str(uuid.uuid4())[:8].upper(),
                    "Station Name": name.strip(),
                    "Network": network.strip(),
                    "City": city.strip(),
                    "Area": area.strip(),
                    "Address": address.strip(),
                    "Charging Type": charging_type,
                    "Connector": connector,
                    "Total Chargers": total,
                    "Available Chargers": available,
                    "Occupied Chargers": occupied,
                    "Faulty Chargers": faulty,
                    "Queue Length": queue,
                    "Price per kWh": price,
                    "Rating": rating,
                    "Open 24x7": open_24,
                    "Amenities": amenities.strip(),
                    "Latitude": latitude,
                    "Longitude": longitude,
                }

                stations_raw = pd.concat([stations_raw, pd.DataFrame([new_station])], ignore_index=True)
                save_stations(stations_raw)
                reload_all_data()

                st.success("New station added successfully.")
                st.rerun()

    st.stop()


# ==================================================
# USER DASHBOARD
# ==================================================
users_df = load_users()
vehicles_df = load_vehicles()
stations_raw = load_stations()
reservations_df = load_reservations()

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">🚗 User Charging Dashboard</div>
        <div class="hero-text">
            Search stations, find the closest available charger, reserve a slot, and save your EV details.
            Your reservations will immediately appear in the Host Dashboard after refresh.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# LOCATION
st.markdown("## 📍 Location Settings")

location_enabled = (
    st.session_state.user_latitude is not None
    and st.session_state.user_longitude is not None
)

if location_enabled:
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success("Location is enabled. Closest station recommendation is active.")
            st.caption(
                f"Current location: "
                f"{round(float(st.session_state.user_latitude), 5)}, "
                f"{round(float(st.session_state.user_longitude), 5)}"
            )
        with col2:
            if st.button("Change Location"):
                st.session_state.user_latitude = None
                st.session_state.user_longitude = None
                st.session_state.location_requested = False
                st.rerun()
else:
    with st.container(border=True):
        st.write("Allow browser location or select your area manually.")

        loc_col1, loc_col2 = st.columns(2)

        with loc_col1:
            if st.button("Allow Browser Location", type="primary"):
                st.session_state.location_requested = True

            if st.session_state.location_requested:
                if get_geolocation is None:
                    st.warning("Browser location package unavailable. Use manual area selection.")
                else:
                    location_data = get_geolocation()
                    latitude, longitude = extract_location(location_data)

                    if latitude is not None and longitude is not None:
                        st.session_state.user_latitude = float(latitude)
                        st.session_state.user_longitude = float(longitude)
                        st.session_state.location_requested = False
                        st.rerun()
                    else:
                        st.info("Waiting for browser location. You may also use manual area selection.")

        with loc_col2:
            selected_manual_area = st.selectbox("Select Your Area", list(KNOWN_LOCATIONS.keys()))

            if st.button("Use Selected Area"):
                lat, lon = KNOWN_LOCATIONS[selected_manual_area]
                st.session_state.user_latitude = lat
                st.session_state.user_longitude = lon
                st.success(f"Location set to {selected_manual_area}.")
                st.rerun()


# FILTERS
stations_df = prepare_station_data(stations_raw)

st.sidebar.header("🔎 Smart Filters")

city_options = ["All"] + sorted(stations_df["City"].dropna().unique().tolist())
sidebar_selectbox("City", city_options, "selected_city")

city_df = stations_df.copy()
if st.session_state.selected_city != "All":
    city_df = city_df[city_df["City"] == st.session_state.selected_city]

area_options = ["All"] + sorted(city_df["Area"].dropna().unique().tolist())
sidebar_selectbox("Area", area_options, "selected_area")

area_df = city_df.copy()
if st.session_state.selected_area != "All":
    area_df = area_df[area_df["Area"] == st.session_state.selected_area]

network_options = ["All"] + sorted(area_df["Network"].dropna().unique().tolist())
sidebar_selectbox("Charging Network", network_options, "selected_network")

network_df = area_df.copy()
if st.session_state.selected_network != "All":
    network_df = network_df[network_df["Network"] == st.session_state.selected_network]

charging_options = ["All"] + sorted(network_df["Charging Type"].dropna().unique().tolist())
sidebar_selectbox("Charging Speed", charging_options, "selected_charging_type")

type_df = network_df.copy()
if st.session_state.selected_charging_type != "All":
    type_df = type_df[type_df["Charging Type"] == st.session_state.selected_charging_type]

connector_options = ["All"] + sorted(type_df["Connector"].dropna().unique().tolist())
sidebar_selectbox("Connector Type", connector_options, "selected_connector")

st.sidebar.selectbox("Availability", ["All", "Available Now", "Currently Full", "Low Queue Only"], key="availability_filter")
st.sidebar.selectbox("Operating Hours", ["All", "Open 24x7 Only"], key="open_filter")
st.sidebar.selectbox("Amenity", ["All", "Parking", "Food", "Restroom", "Mall", "Service Center", "Metro Access"], key="amenity_filter")
st.sidebar.slider("Maximum Price per kWh", 10, 30, 25, key="max_price")
st.sidebar.slider("Minimum Rating", 3.5, 5.0, 3.8, 0.1, key="minimum_rating")

if location_enabled:
    st.sidebar.slider("Maximum Distance from You", 1, 50, 15, key="max_distance")
else:
    st.session_state.max_distance = 50
    st.sidebar.caption("Set location to enable distance filter.")

st.sidebar.text_input("Search Station / Area / Network", placeholder="Example: Tata, Madhapur, CCS2", key="search_keyword")

filtered_df = get_filtered_stations(stations_df)


# USER METRICS
st.markdown("## 📊 Live Charging Overview")

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    card_metric("Stations Found", len(filtered_df), "after filters")
with m2:
    card_metric("Available Chargers", int(filtered_df["Available Chargers"].sum()) if not filtered_df.empty else 0, "ready now")
with m3:
    card_metric("Occupied Chargers", int(filtered_df["Occupied Chargers"].sum()) if not filtered_df.empty else 0, "currently busy")
with m4:
    card_metric("Vehicles in Queue", int(filtered_df["Queue Length"].sum()) if not filtered_df.empty else 0, "waiting")
with m5:
    avg_price = "₹0" if filtered_df.empty else f"₹{round(filtered_df['Price per kWh'].mean(), 2)}"
    card_metric("Avg Price/kWh", avg_price, "filtered average")

st.divider()


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🔍 Find Charger",
        "📍 Station Details",
        "🧾 Reserve Slot",
        "🚗 My Vehicles",
        "👤 My Profile",
        "🏢 Company Details",
    ]
)

with tab1:
    st.markdown("## 🔍 Closest Available Charging Station")
    closest_station = get_closest_station(filtered_df)

    if closest_station is None:
        st.warning("No available charging station found. Please change filters or location.")
    else:
        st.markdown(
            f"""
            <div class="station-card">
                <span class="badge-green">{closest_station['Availability Status']}</span>
                <span class="badge-blue">{closest_station['Charging Type']}</span>
                <span class="badge-orange">{closest_station['Connector']}</span>
                <h2>{closest_station['Station Name']}</h2>
                <p><b>Network:</b> {closest_station['Network']}</p>
                <p><b>Address:</b> {closest_station['Address']}</p>
                <p><b>Amenities:</b> {closest_station['Amenities']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            card_metric("Available", int(closest_station["Available Chargers"]), "chargers")
        with c2:
            card_metric("Queue", int(closest_station["Queue Length"]), "vehicles")
        with c3:
            card_metric("Wait Time", f"{int(closest_station['Estimated Wait Time'])} min", "estimated")
        with c4:
            distance_value = "Set location"
            if pd.notna(closest_station["User Distance km"]):
                distance_value = f"{round(closest_station['User Distance km'], 2)} km"
            card_metric("Distance", distance_value, "from you")

        st.link_button("📍 Open Exact Location in Google Maps", closest_station["Maps Link"])

with tab2:
    st.markdown("## 📍 Charging Station Details")

    if filtered_df.empty:
        st.warning("No station data available.")
    else:
        display_df = filtered_df.copy()
        if location_enabled and "User Distance km" in display_df.columns:
            display_df = display_df.sort_values("User Distance km", na_position="last")

        for _, row in display_df.iterrows():
            st.markdown(
                f"""
                <div class="station-card">
                    <span class="badge-green">{row['Availability Status']}</span>
                    <span class="badge-blue">{row['Charging Type']}</span>
                    <span class="badge-orange">{row['Health Status']} Health</span>
                    <h3>{row['Station Name']}</h3>
                    <p><b>Network:</b> {row['Network']} | <b>Area:</b> {row['Area']} | <b>Connector:</b> {row['Connector']}</p>
                    <p><b>Address:</b> {row['Address']}</p>
                    <p><b>Amenities:</b> {row['Amenities']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Available", int(row["Available Chargers"]))
            c2.metric("Occupied", int(row["Occupied Chargers"]))
            c3.metric("Faulty", int(row["Faulty Chargers"]))
            c4.metric("Queue", int(row["Queue Length"]))
            c5.metric("Price", f"₹{row['Price per kWh']}/kWh")

            if int(row["Total Chargers"]) > 0:
                st.progress(float(row["Available Chargers"]) / float(row["Total Chargers"]))

            st.link_button("Navigate in Google Maps", row["Maps Link"])

with tab3:
    st.markdown("## 🧾 Reserve a Charging Slot")

    reservation_df = filtered_df.copy()

    if reservation_df.empty:
        st.warning("No stations available for reservation.")
    else:
        if location_enabled:
            reservation_df = reservation_df.sort_values("User Distance km", na_position="last")

        station_names = reservation_df["Station Name"].dropna().tolist()
        selected_station_name = st.selectbox("Select Charging Station", station_names)

        selected_station_df = stations_df[stations_df["Station Name"] == selected_station_name]

        if selected_station_df.empty:
            st.error("Selected station data not found. Please refresh the app.")
        else:
            selected_station = selected_station_df.iloc[0]
            user_vehicles = load_vehicles()
            user_vehicles = user_vehicles[user_vehicles["User ID"] == user_id]

            st.info(
                f"{int(selected_station['Available Chargers'])} chargers available | "
                f"{int(selected_station['Queue Length'])} vehicles in queue | "
                f"Estimated wait: {int(selected_station['Estimated Wait Time'])} minutes"
            )

            with st.form("reservation_form"):
                if user_vehicles.empty:
                    st.warning("No saved vehicle found. Add one in My Vehicles tab or enter manually.")
                    vehicle_number = st.text_input("Vehicle Number")
                    ev_model = st.text_input("EV Model")
                else:
                    vehicle_choice = st.selectbox("Select Saved Vehicle", user_vehicles["Vehicle Number"].tolist())
                    selected_vehicle = user_vehicles[user_vehicles["Vehicle Number"] == vehicle_choice].iloc[0]
                    vehicle_number = selected_vehicle["Vehicle Number"]
                    ev_model = selected_vehicle["EV Model"]
                    st.write(f"**EV Model:** {ev_model}")

                driver_name = st.text_input("Driver Name", value=user["Name"])
                mobile_number = st.text_input("Mobile Number", value=str(user["Phone"]))
                date_options = get_booking_date_options()

                if not date_options:
                    st.error("No booking slots are available right now. Please try again tomorrow.")
                    st.stop()

                if (
                    "booking_date_select" not in st.session_state
                    or st.session_state.booking_date_select not in date_options
                ):
                    st.session_state.booking_date_select = date_options[0]

                reservation_date = st.selectbox(
                    "Charging Date",
                    date_options,
                    key="booking_date_select",
                )

                time_options = get_time_options_for_date(reservation_date)

                if not time_options:
                    st.error("No time slots are available for this date. Please choose another date.")
                    st.stop()

                if (
                    "booking_time_select" not in st.session_state
                    or st.session_state.booking_time_select not in time_options
                ):
                    st.session_state.booking_time_select = time_options[0]

                reservation_time = st.selectbox(
                    "Preferred Time",
                    time_options,
                    key="booking_time_select",
                )

                duration = st.selectbox(
                    "Charging Duration",
                    ["30 minutes", "1 hour", "1.5 hours", "2 hours"],
                    key="booking_duration_select",
                )
                accept_terms = st.checkbox("I agree that my booking may be moved to queue if the charger becomes unavailable.")

                submit_reservation = st.form_submit_button("Confirm Reservation", use_container_width=True)

            if submit_reservation:
                reservations_df = load_reservations()
                stations_raw = load_stations()

                vehicle_number = vehicle_number.strip().upper()
                ev_model = ev_model.strip()
                mobile_number = str(mobile_number).strip()

                active_duplicate = reservations_df[
                    (reservations_df["Vehicle Number"] == vehicle_number)
                    & (reservations_df["Status"].isin(["Confirmed", "Queued"]))
                ]

                if not vehicle_number or not ev_model or not mobile_number:
                    st.error("Please provide vehicle and mobile details.")
                elif not mobile_number.isdigit() or len(mobile_number) != 10:
                    st.error("Please enter a valid 10-digit mobile number.")
                elif not accept_terms:
                    st.error("Please accept the reservation condition.")
                elif not active_duplicate.empty:
                    st.warning("This vehicle already has an active reservation or queue entry.")
                else:
                    station_id = selected_station["Station ID"]
                    station_rows = stations_raw[stations_raw["Station ID"] == station_id]

                    if station_rows.empty:
                        st.error("Station not found. Please refresh the app.")
                    else:
                        station_index = station_rows.index[0]
                        available = int(float(stations_raw.loc[station_index, "Available Chargers"]))

                        if available > 0:
                            stations_raw.loc[station_index, "Available Chargers"] = available - 1
                            stations_raw.loc[station_index, "Occupied Chargers"] = int(float(stations_raw.loc[station_index, "Occupied Chargers"])) + 1
                            status = "Confirmed"
                        else:
                            stations_raw.loc[station_index, "Queue Length"] = int(float(stations_raw.loc[station_index, "Queue Length"])) + 1
                            status = "Queued"

                        new_reservation = {
                            "Reservation ID": "VQ-" + datetime.now().strftime("%Y%m%d%H%M%S"),
                            "User ID": user_id,
                            "Driver Name": driver_name.strip(),
                            "Vehicle Number": vehicle_number,
                            "EV Model": ev_model,
                            "Mobile Number": mobile_number,
                            "Station ID": station_id,
                            "Station Name": selected_station["Station Name"],
                            "Date": str(reservation_date),
                            "Time": str(reservation_time),
                            "Duration": duration,
                            "Status": status,
                            "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }

                        reservations_df = pd.concat([reservations_df, pd.DataFrame([new_reservation])], ignore_index=True)

                        save_reservations(reservations_df)
                        save_stations(stations_raw)
                        reload_all_data()

                        st.success(f"Reservation {status.lower()} successfully. Host can now view it in Host Dashboard.")
                        st.rerun()

    st.markdown("### My Reservations")
    my_res = load_reservations()
    my_res = my_res[my_res["User ID"] == user_id]

    if my_res.empty:
        st.info("You have not made any reservations yet.")
    else:
        st.dataframe(my_res, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("## 🚗 My Saved Vehicles")

    vehicles_df = load_vehicles()
    my_vehicles = vehicles_df[vehicles_df["User ID"] == user_id]

    if my_vehicles.empty:
        st.info("No vehicles saved yet.")
    else:
        st.dataframe(my_vehicles, use_container_width=True, hide_index=True)

    st.markdown("### Add New Vehicle")

    with st.form("vehicle_form"):
        vehicle_number_input = st.text_input("Vehicle Number")
        ev_model_input = st.text_input("EV Model")
        connector_input = st.selectbox("Connector Type", ["CCS2", "Type 2", "CHAdeMO"])
        battery_input = st.number_input("Battery Capacity kWh", min_value=10, max_value=150, value=40)
        add_vehicle = st.form_submit_button("Save Vehicle", use_container_width=True)

    if add_vehicle:
        vehicles_df = load_vehicles()
        vehicle_number_clean = vehicle_number_input.strip().upper()

        duplicate_vehicle = vehicles_df[
            (vehicles_df["User ID"] == user_id)
            & (vehicles_df["Vehicle Number"] == vehicle_number_clean)
        ]

        if not vehicle_number_clean or not ev_model_input.strip():
            st.error("Vehicle number and EV model are required.")
        elif not duplicate_vehicle.empty:
            st.error("This vehicle is already saved in your profile.")
        else:
            new_vehicle = {
                "Vehicle ID": "VH-" + str(uuid.uuid4())[:8].upper(),
                "User ID": user_id,
                "Vehicle Number": vehicle_number_clean,
                "EV Model": ev_model_input.strip(),
                "Connector": connector_input,
                "Battery Capacity kWh": battery_input,
                "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            vehicles_df = pd.concat([vehicles_df, pd.DataFrame([new_vehicle])], ignore_index=True)
            save_vehicles(vehicles_df)
            reload_all_data()

            st.success("Vehicle saved successfully. Host can now view it.")
            st.rerun()

with tab5:
    st.markdown("## 👤 My Profile")

    with st.form("profile_form"):
        new_name = st.text_input("Name", value=user["Name"])
        new_phone = st.text_input("Phone", value=str(user["Phone"]))

        area_list = list(KNOWN_LOCATIONS.keys())
        current_area = user["Preferred Area"] if user["Preferred Area"] in area_list else "Hyderabad"
        new_area = st.selectbox("Preferred Area", area_list, index=area_list.index(current_area))

        update_profile = st.form_submit_button("Update Profile", use_container_width=True)

    if update_profile:
        users_df = load_users()

        if not new_name.strip() or not new_phone.strip():
            st.error("Name and phone are required.")
        elif not new_phone.isdigit() or len(new_phone) != 10:
            st.error("Please enter a valid 10-digit mobile number.")
        else:
            user_rows = users_df[users_df["User ID"] == user_id]

            if user_rows.empty:
                st.error("User not found. Please login again.")
            else:
                user_index = user_rows.index[0]
                users_df.loc[user_index, "Name"] = new_name.strip()
                users_df.loc[user_index, "Phone"] = new_phone.strip()
                users_df.loc[user_index, "Preferred Area"] = new_area
                save_users(users_df)

                st.session_state.user = users_df.loc[user_index].to_dict()
                reload_all_data()

                st.success("Profile updated successfully.")
                st.rerun()

with tab6:
    st.markdown("## 🏢 Company Details")

    st.markdown(
        """
        <div class="company-box">
            <h3>VoltIQ Technologies Pvt. Ltd</h3>
            <p>
            <b>VoltIQ Technologies Pvt. Ltd</b> is a smart EV charging support platform
            designed to make electric vehicle charging more convenient, reliable and user-friendly.
            </p>
            <p>
            Our platform helps EV users find nearby charging stations, check charger availability,
            view queue length, estimate waiting time, reserve charging slots, save vehicle details,
            and navigate to charging stations using Google Maps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Our Services")
        st.write("✅ EV charging station discovery")
        st.write("✅ Closest available charger recommendation")
        st.write("✅ Charging slot reservation")
        st.write("✅ Queue management")
        st.write("✅ Vehicle profile management")

    with c2:
        st.markdown("### Contact")
        st.write("**Company Name:** VoltIQ Technologies Pvt. Ltd")
        st.write("**Email:** support@voltiq.com")
        st.write("**Phone:** +91 98765 43210")
        st.write("**Location:** Hyderabad, Telangana, India")
        st.write("**Working Hours:** 9:00 AM to 6:00 PM")

    st.markdown("### Mission")
    st.write("To reduce EV charging delays and make electric vehicle usage more comfortable, predictable and stress-free.")

    st.markdown("### Vision")
    st.write("To support the growth of electric mobility through a smart, connected and user-focused charging experience.")

    st.success("Powering smarter journeys, one charge at a time.")
