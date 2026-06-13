import os
import uuid
import hashlib
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

import pandas as pd
import streamlit as st

try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="VoltIQ Technologies Pvt. Ltd",
    page_icon="⚡",
    layout="wide"
)


# ==================================================
# DATA FILES
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
}

USER_COLUMNS = [
    "User ID",
    "Name",
    "Email",
    "Password Hash",
    "Phone",
    "Role",
    "Preferred Area",
    "Created At"
]

VEHICLE_COLUMNS = [
    "Vehicle ID",
    "User ID",
    "Vehicle Number",
    "EV Model",
    "Connector",
    "Battery Capacity kWh",
    "Created At"
]

STATION_COLUMNS = [
    "Station ID",
    "Station Name",
    "Network",
    "City",
    "Area",
    "Address",
    "Charging Type",
    "Connector",
    "Total Chargers",
    "Available Chargers",
    "Occupied Chargers",
    "Faulty Chargers",
    "Queue Length",
    "Price per kWh",
    "Rating",
    "Open 24x7",
    "Amenities",
    "Latitude",
    "Longitude"
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
    "Created At"
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
        "Longitude": 78.4622
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
        "Longitude": 78.3996
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
        "Longitude": 78.3805
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
        "Longitude": 78.3915
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
        "Longitude": 78.3489
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
        "Longitude": 78.3894
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
        "Longitude": 78.3611
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
        "Longitude": 78.3053
    }
]


# ==================================================
# BASIC FUNCTIONS
# ==================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def read_csv(file_path, columns):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)

    df = pd.read_csv(file_path)

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns]


def save_csv(df, file_path):
    df.to_csv(file_path, index=False)


def initialize_data():
    if not os.path.exists(USERS_FILE):
        default_users = pd.DataFrame([
            {
                "User ID": "U-ADMIN",
                "Name": "VoltIQ Host",
                "Email": "host@voltiq.com",
                "Password Hash": hash_password("Host@123"),
                "Phone": "9999999999",
                "Role": "Host",
                "Preferred Area": "Hyderabad",
                "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "User ID": "U-DEMO",
                "Name": "Demo User",
                "Email": "user@demo.com",
                "Password Hash": hash_password("User@123"),
                "Phone": "8888888888",
                "Role": "User",
                "Preferred Area": "Gachibowli",
                "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ])
        save_csv(default_users, USERS_FILE)

    if not os.path.exists(VEHICLES_FILE):
        save_csv(pd.DataFrame(columns=VEHICLE_COLUMNS), VEHICLES_FILE)

    if not os.path.exists(STATIONS_FILE):
        save_csv(pd.DataFrame(DEFAULT_STATIONS), STATIONS_FILE)

    if not os.path.exists(RESERVATIONS_FILE):
        save_csv(pd.DataFrame(columns=RESERVATION_COLUMNS), RESERVATIONS_FILE)


def to_int(value):
    try:
        return int(float(value))
    except Exception:
        return 0


def to_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


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
    queue_length = to_int(queue_length)

    if charging_type == "DC Fast Charging":
        average_time = 30
    elif charging_type == "AC Charging":
        average_time = 55
    else:
        average_time = 45

    return queue_length * average_time


def get_health_status(total, faulty):
    total = to_int(total)
    faulty = to_int(faulty)

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


def get_availability_status(available):
    available = to_int(available)

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


def prepare_station_data(stations_df):
    df = stations_df.copy()
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
        "Longitude"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Estimated Wait Time"] = df.apply(
        lambda row: calculate_wait_time(row["Queue Length"], row["Charging Type"]),
        axis=1
    )

    df["Health Status"] = df.apply(
        lambda row: get_health_status(row["Total Chargers"], row["Faulty Chargers"]),
        axis=1
    )

    df["Availability Status"] = df["Available Chargers"].apply(get_availability_status)

    df["Maps Link"] = df.apply(
        lambda row: get_maps_link(row["Latitude"], row["Longitude"]),
        axis=1
    )

    if st.session_state.user_latitude is not None and st.session_state.user_longitude is not None:
        user_lat = float(st.session_state.user_latitude)
        user_lon = float(st.session_state.user_longitude)

        df["User Distance km"] = df.apply(
            lambda row: distance_km(
                user_lat,
                user_lon,
                float(row["Latitude"]),
                float(row["Longitude"])
            ),
            axis=1
        )
    else:
        df["User Distance km"] = None

    return df


def get_closest_station(df):
    available_df = df[df["Available Chargers"] > 0].copy()

    if available_df.empty:
        return None

    if "User Distance km" in available_df.columns:
        available_df = available_df[pd.notna(available_df["User Distance km"])]

        if not available_df.empty:
            available_df = available_df.sort_values(
                by=["User Distance km", "Estimated Wait Time", "Price per kWh", "Rating"],
                ascending=[True, True, True, False]
            )
            return available_df.iloc[0]

    available_df = available_df.sort_values(
        by=["Estimated Wait Time", "Price per kWh", "Rating"],
        ascending=[True, True, False]
    )

    return available_df.iloc[0]


# ==================================================
# SESSION STATE
# ==================================================
initialize_data()

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
    .main-title {
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(90deg, #0F766E, #2563EB, #9333EA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #475569;
        margin-top: 0px;
    }

    .hero-box {
        padding: 22px;
        border-radius: 18px;
        background: linear-gradient(135deg, #ECFEFF, #EFF6FF, #F5F3FF);
        border: 1px solid #CBD5E1;
        margin-bottom: 18px;
    }

    .company-box {
        padding: 22px;
        border-radius: 18px;
        background: linear-gradient(135deg, #F0FDFA, #EFF6FF, #FAF5FF);
        border: 1px solid #CBD5E1;
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# LOGIN PAGE
# ==================================================
def show_login_page():
    st.markdown('<p class="main-title">⚡ VoltIQ Technologies Pvt. Ltd</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Smart EV Charging Availability and Queue Management System</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-box">
        Find nearby EV charging stations, view queue length, reserve charging slots,
        save your vehicles, and navigate using Google Maps.
        </div>
        """,
        unsafe_allow_html=True
    )

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        st.subheader("Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            users_df = read_csv(USERS_FILE, USER_COLUMNS)
            email_clean = email.strip().lower()

            matched = users_df[
                (users_df["Email"].str.lower() == email_clean)
                & (users_df["Password Hash"] == hash_password(password))
            ]

            if matched.empty:
                st.error("Invalid email or password.")
            else:
                st.session_state.logged_in = True
                st.session_state.user = matched.iloc[0].to_dict()
                st.success("Login successful.")
                st.rerun()

        st.info("Demo User: user@demo.com / User@123")

    with signup_tab:
        st.subheader("Create New User Account")

        name = st.text_input("Full Name")
        signup_email = st.text_input("Email Address")
        phone = st.text_input("Mobile Number")
        preferred_area = st.selectbox("Preferred Area", list(KNOWN_LOCATIONS.keys()))
        signup_password = st.text_input("Create Password", type="password")

        if st.button("Create Account"):
            users_df = read_csv(USERS_FILE, USER_COLUMNS)

            if not name.strip() or not signup_email.strip() or not phone.strip() or not signup_password:
                st.error("Please fill all fields.")

            elif not phone.isdigit() or len(phone) != 10:
                st.error("Please enter a valid 10-digit mobile number.")

            elif signup_email.strip().lower() in users_df["Email"].str.lower().tolist():
                st.error("This email is already registered.")

            else:
                new_user = {
                    "User ID": "U-" + str(uuid.uuid4())[:8].upper(),
                    "Name": name.strip(),
                    "Email": signup_email.strip().lower(),
                    "Password Hash": hash_password(signup_password),
                    "Phone": phone.strip(),
                    "Role": "User",
                    "Preferred Area": preferred_area,
                    "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
                save_csv(users_df, USERS_FILE)

                st.success("Account created successfully. Please login.")


if not st.session_state.logged_in:
    show_login_page()
    st.stop()


# ==================================================
# LOAD DATA
# ==================================================
users_df = read_csv(USERS_FILE, USER_COLUMNS)
vehicles_df = read_csv(VEHICLES_FILE, VEHICLE_COLUMNS)
stations_raw_df = read_csv(STATIONS_FILE, STATION_COLUMNS)
reservations_df = read_csv(RESERVATIONS_FILE, RESERVATION_COLUMNS)

user = st.session_state.user
user_id = user["User ID"]
is_host = user["Role"] == "Host"


# ==================================================
# HEADER AFTER LOGIN
# ==================================================
top_col1, top_col2 = st.columns([3, 1])

with top_col1:
    st.markdown('<p class="main-title">⚡ VoltIQ Technologies Pvt. Ltd</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Smart EV Charging Availability, Queue Management and Station Discovery Platform</p>',
        unsafe_allow_html=True
    )

with top_col2:
    with st.popover("👤 Profile"):
        st.write(f"**Name:** {user['Name']}")
        st.write(f"**Email:** {user['Email']}")
        st.write(f"**Role:** {user['Role']}")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.user_latitude = None
            st.session_state.user_longitude = None
            st.rerun()


# ==================================================
# LOCATION SECTION
# ==================================================
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
        st.write(
            "Allow location access to find the closest available charging station. "
            "You can also select your area manually."
        )

        loc_col1, loc_col2 = st.columns(2)

        with loc_col1:
            if st.button("Allow Browser Location", type="primary"):
                st.session_state.location_requested = True

            if st.session_state.location_requested:
                if get_geolocation is None:
                    st.error("Add streamlit-js-eval in requirements.txt to use browser location.")
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


stations_df = prepare_station_data(stations_raw_df)


# ==================================================
# SIDEBAR FILTERS
# ==================================================
st.sidebar.header("🔎 Smart Filters")

city_options = ["All"] + sorted(stations_df["City"].dropna().unique().tolist())
selected_city = st.sidebar.selectbox("City", city_options)

city_df = stations_df.copy()
if selected_city != "All":
    city_df = city_df[city_df["City"] == selected_city]

area_options = ["All"] + sorted(city_df["Area"].dropna().unique().tolist())
selected_area = st.sidebar.selectbox("Area", area_options)

area_df = city_df.copy()
if selected_area != "All":
    area_df = area_df[area_df["Area"] == selected_area]

network_options = ["All"] + sorted(area_df["Network"].dropna().unique().tolist())
selected_network = st.sidebar.selectbox("Charging Network", network_options)

network_df = area_df.copy()
if selected_network != "All":
    network_df = network_df[network_df["Network"] == selected_network]

charging_options = ["All"] + sorted(network_df["Charging Type"].dropna().unique().tolist())
selected_charging_type = st.sidebar.selectbox("Charging Speed", charging_options)

type_df = network_df.copy()
if selected_charging_type != "All":
    type_df = type_df[type_df["Charging Type"] == selected_charging_type]

connector_options = ["All"] + sorted(type_df["Connector"].dropna().unique().tolist())
selected_connector = st.sidebar.selectbox("Connector Type", connector_options)

availability_filter = st.sidebar.selectbox(
    "Availability",
    ["All", "Available Now", "Currently Full", "Low Queue Only"]
)

open_filter = st.sidebar.selectbox(
    "Operating Hours",
    ["All", "Open 24x7 Only"]
)

amenity_filter = st.sidebar.selectbox(
    "Amenity",
    ["All", "Parking", "Food", "Restroom", "Mall", "Service Center", "Metro Access"]
)

max_price = st.sidebar.slider("Maximum Price per kWh", 10, 30, 25)
minimum_rating = st.sidebar.slider("Minimum Rating", 3.5, 5.0, 3.8, 0.1)

if location_enabled:
    max_distance = st.sidebar.slider("Maximum Distance from You", 1, 50, 15)
else:
    max_distance = None
    st.sidebar.caption("Set location to enable distance filter.")

search_keyword = st.sidebar.text_input(
    "Search Station / Area / Network",
    placeholder="Example: Tata, Madhapur, CCS2"
)


# ==================================================
# APPLY FILTERS
# ==================================================
filtered_df = stations_df.copy()

if selected_city != "All":
    filtered_df = filtered_df[filtered_df["City"] == selected_city]

if selected_area != "All":
    filtered_df = filtered_df[filtered_df["Area"] == selected_area]

if selected_network != "All":
    filtered_df = filtered_df[filtered_df["Network"] == selected_network]

if selected_charging_type != "All":
    filtered_df = filtered_df[filtered_df["Charging Type"] == selected_charging_type]

if selected_connector != "All":
    filtered_df = filtered_df[filtered_df["Connector"] == selected_connector]

if availability_filter == "Available Now":
    filtered_df = filtered_df[filtered_df["Available Chargers"] > 0]

elif availability_filter == "Currently Full":
    filtered_df = filtered_df[filtered_df["Available Chargers"] == 0]

elif availability_filter == "Low Queue Only":
    filtered_df = filtered_df[filtered_df["Queue Length"] <= 2]

if open_filter == "Open 24x7 Only":
    filtered_df = filtered_df[filtered_df["Open 24x7"] == "Yes"]

if amenity_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Amenities"].str.contains(amenity_filter, case=False, na=False)
    ]

filtered_df = filtered_df[filtered_df["Price per kWh"] <= max_price]
filtered_df = filtered_df[filtered_df["Rating"] >= minimum_rating]

if max_distance is not None:
    filtered_df = filtered_df[filtered_df["User Distance km"] <= max_distance]

if search_keyword.strip():
    text = search_keyword.strip()
    filtered_df = filtered_df[
        filtered_df["Station Name"].str.contains(text, case=False, na=False)
        | filtered_df["Area"].str.contains(text, case=False, na=False)
        | filtered_df["Network"].str.contains(text, case=False, na=False)
        | filtered_df["Connector"].str.contains(text, case=False, na=False)
    ]


# ==================================================
# MAIN DASHBOARD
# ==================================================
st.markdown("## 📊 Live Charging Overview")

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Stations Found", len(filtered_df))
m2.metric("Available Chargers", int(filtered_df["Available Chargers"].sum()))
m3.metric("Occupied Chargers", int(filtered_df["Occupied Chargers"].sum()))
m4.metric("Vehicles in Queue", int(filtered_df["Queue Length"].sum()))

if filtered_df.empty:
    m5.metric("Avg Price / kWh", "₹0")
else:
    m5.metric("Avg Price / kWh", f"₹{round(filtered_df['Price per kWh'].mean(), 2)}")

st.divider()


# ==================================================
# TABS
# ==================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🔍 Find Charger",
        "📍 Station Details",
        "🧾 Reserve Slot",
        "🚗 My Vehicles",
        "👤 My Profile",
        "🛠️ Host Dashboard" if is_host else "🏢 Company Details"
    ]
)


# ==================================================
# TAB 1 FIND CHARGER
# ==================================================
with tab1:
    st.markdown("## 🔍 Closest Available Charging Station")

    if filtered_df.empty:
        st.warning("No stations found for the selected filters.")
    else:
        closest_station = get_closest_station(filtered_df)

        if closest_station is None:
            st.error("No available charging station found.")
        else:
            st.success("Closest available station found.")

            c1, c2 = st.columns([2, 1])

            with c1:
                st.subheader(closest_station["Station Name"])
                st.write(f"**Network:** {closest_station['Network']}")
                st.write(f"**Address:** {closest_station['Address']}")
                st.write(f"**Charging Type:** {closest_station['Charging Type']}")
                st.write(f"**Connector:** {closest_station['Connector']}")
                st.write(f"**Amenities:** {closest_station['Amenities']}")
                st.link_button("Open Exact Location in Google Maps", closest_station["Maps Link"])

            with c2:
                st.metric("Available", int(closest_station["Available Chargers"]))
                st.metric("Queue", int(closest_station["Queue Length"]))
                st.metric("Wait Time", f"{int(closest_station['Estimated Wait Time'])} min")
                st.metric("Price", f"₹{closest_station['Price per kWh']} / kWh")

                if pd.notna(closest_station["User Distance km"]):
                    st.metric("Distance", f"{round(closest_station['User Distance km'], 2)} km")
                else:
                    st.metric("Distance", "Set location")


# ==================================================
# TAB 2 STATION DETAILS
# ==================================================
with tab2:
    st.markdown("## 📍 Charging Station Details")

    if filtered_df.empty:
        st.warning("No station data available.")
    else:
        display_df = filtered_df.copy()

        if location_enabled:
            display_df = display_df.sort_values("User Distance km")

        for _, row in display_df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])

                with c1:
                    st.subheader(row["Station Name"])
                    st.write(f"**Network:** {row['Network']}")
                    st.write(f"**Address:** {row['Address']}")
                    st.write(f"**Connector:** {row['Connector']}")
                    st.write(f"**Health:** {row['Health Status']}")
                    st.write(f"**Status:** {row['Availability Status']}")
                    st.link_button("Navigate in Google Maps", row["Maps Link"])

                with c2:
                    st.metric("Total", int(row["Total Chargers"]))
                    st.metric("Available", int(row["Available Chargers"]))
                    st.metric("Occupied", int(row["Occupied Chargers"]))

                with c3:
                    st.metric("Faulty", int(row["Faulty Chargers"]))
                    st.metric("Queue", int(row["Queue Length"]))
                    st.metric("Wait", f"{int(row['Estimated Wait Time'])} min")

                if row["Total Chargers"] > 0:
                    st.progress(row["Available Chargers"] / row["Total Chargers"])


# ==================================================
# TAB 3 RESERVATION
# ==================================================
with tab3:
    st.markdown("## 🧾 Reserve a Charging Slot")

    if filtered_df.empty:
        st.warning("No stations available for reservation.")
    else:
        reservation_df = filtered_df.copy()

        if location_enabled:
            reservation_df = reservation_df.sort_values("User Distance km")

        user_vehicles = vehicles_df[vehicles_df["User ID"] == user_id]

        selected_station_name = st.selectbox(
            "Select Charging Station",
            reservation_df["Station Name"].tolist()
        )

        selected_station = stations_df[stations_df["Station Name"] == selected_station_name].iloc[0]

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
                vehicle_choice = st.selectbox(
                    "Select Saved Vehicle",
                    user_vehicles["Vehicle Number"].tolist()
                )

                selected_vehicle = user_vehicles[user_vehicles["Vehicle Number"] == vehicle_choice].iloc[0]
                vehicle_number = selected_vehicle["Vehicle Number"]
                ev_model = selected_vehicle["EV Model"]

                st.write(f"**EV Model:** {ev_model}")

            driver_name = st.text_input("Driver Name", value=user["Name"])
            mobile_number = st.text_input("Mobile Number", value=str(user["Phone"]))
            reservation_date = st.date_input("Charging Date")
            reservation_time = st.time_input("Preferred Time")
            duration = st.selectbox("Charging Duration", ["30 minutes", "1 hour", "1.5 hours", "2 hours"])

            accept_terms = st.checkbox(
                "I agree that my booking may be moved to queue if the charger becomes unavailable."
            )

            submit_reservation = st.form_submit_button("Confirm Reservation")

        if submit_reservation:
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
                station_index = stations_raw_df[
                    stations_raw_df["Station ID"] == selected_station["Station ID"]
                ].index[0]

                available = to_int(stations_raw_df.loc[station_index, "Available Chargers"])

                if available > 0:
                    stations_raw_df.loc[station_index, "Available Chargers"] = available - 1
                    stations_raw_df.loc[station_index, "Occupied Chargers"] = (
                        to_int(stations_raw_df.loc[station_index, "Occupied Chargers"]) + 1
                    )
                    status = "Confirmed"
                else:
                    stations_raw_df.loc[station_index, "Queue Length"] = (
                        to_int(stations_raw_df.loc[station_index, "Queue Length"]) + 1
                    )
                    status = "Queued"

                new_reservation = {
                    "Reservation ID": "VQ-" + datetime.now().strftime("%Y%m%d%H%M%S"),
                    "User ID": user_id,
                    "Driver Name": driver_name.strip(),
                    "Vehicle Number": vehicle_number,
                    "EV Model": ev_model,
                    "Mobile Number": mobile_number,
                    "Station ID": selected_station["Station ID"],
                    "Station Name": selected_station["Station Name"],
                    "Date": str(reservation_date),
                    "Time": str(reservation_time),
                    "Duration": duration,
                    "Status": status,
                    "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                reservations_df = pd.concat(
                    [reservations_df, pd.DataFrame([new_reservation])],
                    ignore_index=True
                )

                save_csv(stations_raw_df, STATIONS_FILE)
                save_csv(reservations_df, RESERVATIONS_FILE)

                st.success(f"Reservation {status.lower()} successfully.")
                st.rerun()


# ==================================================
# TAB 4 VEHICLES
# ==================================================
with tab4:
    st.markdown("## 🚗 My Saved Vehicles")

    my_vehicles = vehicles_df[vehicles_df["User ID"] == user_id]

    st.dataframe(my_vehicles, use_container_width=True, hide_index=True)

    st.markdown("### Add New Vehicle")

    with st.form("vehicle_form"):
        vehicle_number = st.text_input("Vehicle Number")
        ev_model = st.text_input("EV Model")
        connector = st.selectbox("Connector Type", ["CCS2", "Type 2", "CHAdeMO"])
        battery = st.number_input("Battery Capacity kWh", min_value=10, max_value=150, value=40)

        add_vehicle = st.form_submit_button("Save Vehicle")

    if add_vehicle:
        vehicle_number = vehicle_number.strip().upper()

        duplicate_vehicle = vehicles_df[
            (vehicles_df["User ID"] == user_id)
            & (vehicles_df["Vehicle Number"] == vehicle_number)
        ]

        if not vehicle_number or not ev_model.strip():
            st.error("Vehicle number and EV model are required.")

        elif not duplicate_vehicle.empty:
            st.error("This vehicle is already saved in your profile.")

        else:
            new_vehicle = {
                "Vehicle ID": "VH-" + str(uuid.uuid4())[:8].upper(),
                "User ID": user_id,
                "Vehicle Number": vehicle_number,
                "EV Model": ev_model.strip(),
                "Connector": connector,
                "Battery Capacity kWh": battery,
                "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            vehicles_df = pd.concat([vehicles_df, pd.DataFrame([new_vehicle])], ignore_index=True)
            save_csv(vehicles_df, VEHICLES_FILE)

            st.success("Vehicle saved successfully.")
            st.rerun()


# ==================================================
# TAB 5 PROFILE
# ==================================================
with tab5:
    st.markdown("## 👤 My Profile")

    with st.form("profile_form"):
        new_name = st.text_input("Name", value=user["Name"])
        new_phone = st.text_input("Phone", value=str(user["Phone"]))
        new_area = st.selectbox(
            "Preferred Area",
            list(KNOWN_LOCATIONS.keys()),
            index=list(KNOWN_LOCATIONS.keys()).index(user["Preferred Area"])
            if user["Preferred Area"] in KNOWN_LOCATIONS else 0
        )

        update_profile = st.form_submit_button("Update Profile")

    if update_profile:
        if not new_name.strip() or not new_phone.strip():
            st.error("Name and phone are required.")

        elif not new_phone.isdigit() or len(new_phone) != 10:
            st.error("Please enter a valid 10-digit mobile number.")

        else:
            user_index = users_df[users_df["User ID"] == user_id].index[0]

            users_df.loc[user_index, "Name"] = new_name.strip()
            users_df.loc[user_index, "Phone"] = new_phone.strip()
            users_df.loc[user_index, "Preferred Area"] = new_area

            save_csv(users_df, USERS_FILE)

            st.session_state.user = users_df.loc[user_index].to_dict()

            st.success("Profile updated successfully.")
            st.rerun()


# ==================================================
# TAB 6 HOST DASHBOARD OR COMPANY DETAILS
# ==================================================
with tab6:
    if is_host:
        st.markdown("## 🛠️ Host Dashboard")

        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Total Users", len(users_df))
        h2.metric("Saved Vehicles", len(vehicles_df))
        h3.metric("Reservations", len(reservations_df))
        h4.metric("Stations", len(stations_raw_df))

        host_tab1, host_tab2, host_tab3 = st.tabs(
            ["Reservations", "Station Management", "Users & Vehicles"]
        )

        with host_tab1:
            st.subheader("All Reservations")
            st.dataframe(reservations_df, use_container_width=True, hide_index=True)

            active_res = reservations_df[reservations_df["Status"].isin(["Confirmed", "Queued"])]

            if not active_res.empty:
                selected_res = st.selectbox(
                    "Select reservation to complete",
                    active_res["Reservation ID"].tolist()
                )

                if st.button("Mark Reservation as Completed"):
                    res_index = reservations_df[
                        reservations_df["Reservation ID"] == selected_res
                    ].index[0]

                    station_id = reservations_df.loc[res_index, "Station ID"]
                    old_status = reservations_df.loc[res_index, "Status"]

                    station_index = stations_raw_df[stations_raw_df["Station ID"] == station_id].index[0]

                    if old_status == "Confirmed":
                        stations_raw_df.loc[station_index, "Occupied Chargers"] = max(
                            0,
                            to_int(stations_raw_df.loc[station_index, "Occupied Chargers"]) - 1
                        )
                        stations_raw_df.loc[station_index, "Available Chargers"] = (
                            to_int(stations_raw_df.loc[station_index, "Available Chargers"]) + 1
                        )

                    elif old_status == "Queued":
                        stations_raw_df.loc[station_index, "Queue Length"] = max(
                            0,
                            to_int(stations_raw_df.loc[station_index, "Queue Length"]) - 1
                        )

                    reservations_df.loc[res_index, "Status"] = "Completed"

                    save_csv(reservations_df, RESERVATIONS_FILE)
                    save_csv(stations_raw_df, STATIONS_FILE)

                    st.success("Reservation completed.")
                    st.rerun()

        with host_tab2:
            st.subheader("Edit Charging Stations")

            selected_station_name = st.selectbox(
                "Select Station",
                stations_raw_df["Station Name"].tolist()
            )

            station_index = stations_raw_df[
                stations_raw_df["Station Name"] == selected_station_name
            ].index[0]

            selected_station = stations_raw_df.loc[station_index]

            with st.form("station_edit_form"):
                available = st.number_input(
                    "Available Chargers",
                    min_value=0,
                    value=to_int(selected_station["Available Chargers"])
                )

                occupied = st.number_input(
                    "Occupied Chargers",
                    min_value=0,
                    value=to_int(selected_station["Occupied Chargers"])
                )

                faulty = st.number_input(
                    "Faulty Chargers",
                    min_value=0,
                    value=to_int(selected_station["Faulty Chargers"])
                )

                queue = st.number_input(
                    "Queue Length",
                    min_value=0,
                    value=to_int(selected_station["Queue Length"])
                )

                price = st.number_input(
                    "Price per kWh",
                    min_value=1,
                    value=to_int(selected_station["Price per kWh"])
                )

                rating = st.number_input(
                    "Rating",
                    min_value=1.0,
                    max_value=5.0,
                    value=to_float(selected_station["Rating"]),
                    step=0.1
                )

                update_station = st.form_submit_button("Update Station")

            if update_station:
                total = to_int(selected_station["Total Chargers"])

                if available + occupied + faulty != total:
                    st.error("Available + Occupied + Faulty must equal Total Chargers.")

                else:
                    stations_raw_df.loc[station_index, "Available Chargers"] = available
                    stations_raw_df.loc[station_index, "Occupied Chargers"] = occupied
                    stations_raw_df.loc[station_index, "Faulty Chargers"] = faulty
                    stations_raw_df.loc[station_index, "Queue Length"] = queue
                    stations_raw_df.loc[station_index, "Price per kWh"] = price
                    stations_raw_df.loc[station_index, "Rating"] = rating

                    save_csv(stations_raw_df, STATIONS_FILE)
                    st.success("Station updated successfully.")
                    st.rerun()

            st.subheader("Station Database")
            st.dataframe(stations_raw_df, use_container_width=True, hide_index=True)

        with host_tab3:
            st.subheader("Registered Users")
            st.dataframe(users_df.drop(columns=["Password Hash"]), use_container_width=True, hide_index=True)

            st.subheader("Saved Vehicles")
            st.dataframe(vehicles_df, use_container_width=True, hide_index=True)

    else:
        st.markdown("## 🏢 Company Details")

        st.markdown(
            """
            <div class="company-box">
            <h3>VoltIQ Technologies Pvt. Ltd</h3>

            <p>
            <b>VoltIQ Technologies Pvt. Ltd</b> is a smart EV charging support platform
            designed to make electric vehicle charging more convenient, reliable, and user-friendly.
            </p>

            <p>
            Our platform helps EV users find nearby charging stations, check charger availability,
            view queue length, estimate waiting time, reserve charging slots, save vehicle details,
            and navigate to charging stations using Google Maps.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Our Services")

        service_col1, service_col2 = st.columns(2)

        with service_col1:
            st.write("✅ EV charging station discovery")
            st.write("✅ Closest available charger recommendation")
            st.write("✅ Charging slot reservation")
            st.write("✅ Queue management")

        with service_col2:
            st.write("✅ Vehicle profile management")
            st.write("✅ Station availability tracking")
            st.write("✅ Google Maps-based navigation")
            st.write("✅ Charging station operator dashboard")

        st.markdown("### Our Mission")
        st.write(
            "To reduce EV charging delays and make electric vehicle usage more comfortable, "
            "predictable, and stress-free for every user."
        )

        st.markdown("### Our Vision")
        st.write(
            "To support the growth of electric mobility by providing a smart, connected, "
            "and user-focused EV charging experience."
        )

        st.markdown("### Customer Support")

        contact_col1, contact_col2 = st.columns(2)

        with contact_col1:
            st.write("**Company Name:** VoltIQ Technologies Pvt. Ltd")
            st.write("**Email:** support@voltiq.com")
            st.write("**Phone:** +91 98765 31234")

        with contact_col2:
            st.write("**Location:** Hyderabad, Telangana, India")
            st.write("**Working Hours:** 9:00 AM to 6:00 PM")
            st.write("**Support:** EV charging assistance and station information")

        st.success("Powering smarter journeys, one charge at a time.")