import os
import uuid
import hashlib
from datetime import datetime
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
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
VEHICLES_FILE = os.path.join(DATA_DIR, "vehicles.csv")
STATIONS_FILE = os.path.join(DATA_DIR, "stations.csv")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.csv")


# ==================================================
# LOGIN DETAILS
# ==================================================
HOST_LOGIN = "group 1 goated"
HOST_PASSWORD = "shahid is goat"

DEMO_USER_LOGIN = "user@demo.com"
DEMO_USER_PASSWORD = "User@123"


# ==================================================
# COLUMNS
# ==================================================
USER_COLUMNS = [
    "User ID", "Name", "Email", "Password Hash", "Phone",
    "Role", "Preferred Area", "Created At"
]

VEHICLE_COLUMNS = [
    "Vehicle ID", "User ID", "Vehicle Number", "EV Model",
    "Connector", "Battery Capacity kWh", "Created At"
]

STATION_COLUMNS = [
    "Station ID", "Station Name", "Network", "City", "Area", "Address",
    "Charging Type", "Connector", "Total Chargers", "Available Chargers",
    "Occupied Chargers", "Faulty Chargers", "Queue Length", "Price per kWh",
    "Rating", "Open 24x7", "Amenities", "Latitude", "Longitude"
]

RESERVATION_COLUMNS = [
    "Reservation ID", "User ID", "Driver Name", "Vehicle Number", "EV Model",
    "Mobile Number", "Station ID", "Station Name", "Date", "Time",
    "Duration", "Status", "Created At"
]


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
    [
        "U-ADMIN",
        "VoltIQ Host",
        HOST_LOGIN,
        hashlib.sha256(HOST_PASSWORD.encode()).hexdigest(),
        "9999999999",
        "Host",
        "Hyderabad",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ],
    [
        "U-DEMO",
        "Demo User",
        DEMO_USER_LOGIN,
        hashlib.sha256(DEMO_USER_PASSWORD.encode()).hexdigest(),
        "8888888888",
        "User",
        "Gachibowli",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ],
]

DEFAULT_STATIONS = [
    ["SC001", "Tata Power EZ Charge - Begumpet", "Tata Power EZ Charge", "Hyderabad", "Begumpet", "Begumpet, Hyderabad, Telangana", "DC Fast Charging", "CCS2", 4, 2, 1, 1, 1, 22, 4.2, "No", "Parking, Service Center", 17.4435, 78.4622],
    ["SC002", "Statiq EV Charging Station - Kukatpally", "Statiq", "Hyderabad", "Kukatpally", "Kukatpally, Hyderabad, Telangana", "DC Fast Charging", "CCS2", 4, 1, 2, 1, 3, 21, 4.1, "Yes", "Parking, Food", 17.4933, 78.3996],
    ["SC003", "ChargeZone Charging Hub - Hitech City", "ChargeZone", "Hyderabad", "Hitech City", "Hitech City, Hyderabad, Telangana", "DC Fast Charging", "CCS2", 5, 2, 3, 0, 1, 22, 4.5, "Yes", "Parking, Food, Restroom, Mall", 17.4504, 78.3805],
    ["SC004", "Jio-bp Pulse EV Charging - Madhapur", "Jio-bp", "Hyderabad", "Madhapur", "Madhapur, Hyderabad, Telangana", "DC Fast Charging", "CCS2", 4, 0, 4, 0, 4, 23, 4.0, "Yes", "Parking, Food, Restroom", 17.4483, 78.3915],
    ["SC005", "GLIDA Green Drive - Gachibowli", "GLIDA", "Hyderabad", "Gachibowli", "Gachibowli, Hyderabad, Telangana", "DC Fast Charging", "CCS2", 6, 4, 2, 0, 0, 20, 4.4, "Yes", "Parking, Restroom, Food", 17.4401, 78.3489],
    ["SC006", "Public EV Charging Point - Durgam Cheruvu", "Public EV Network", "Hyderabad", "Durgam Cheruvu", "Durgam Cheruvu, Hyderabad, Telangana", "AC Charging", "Type 2", 3, 1, 1, 1, 1, 17, 3.9, "No", "Parking", 17.4309, 78.3894],
    ["SC007", "Tata Power EZ Charge - Miyapur", "Tata Power EZ Charge", "Hyderabad", "Miyapur", "Miyapur Metro Station, Hyderabad, Telangana", "AC Charging", "Type 2", 3, 1, 2, 0, 2, 18, 4.0, "No", "Parking, Metro Access", 17.4964, 78.3611],
    ["SC008", "Public EV Charging Station - BHEL", "Public EV Network", "Hyderabad", "BHEL", "BHEL, Hyderabad, Telangana", "AC Charging", "Type 2", 4, 2, 2, 0, 1, 16, 4.0, "No", "Parking", 17.4948, 78.3053],
    ["SC009", "VoltIQ FastCharge - Financial District", "VoltIQ", "Hyderabad", "Financial District", "Financial District, Hyderabad, Telangana", "DC Fast Charging", "CCS2", 8, 5, 3, 0, 0, 19, 4.6, "Yes", "Parking, Food, Restroom", 17.4149, 78.3422],
    ["SC010", "VoltIQ ChargePoint - Kondapur", "VoltIQ", "Hyderabad", "Kondapur", "Kondapur, Hyderabad, Telangana", "AC Charging", "Type 2", 4, 2, 2, 0, 1, 17, 4.2, "No", "Parking, Food", 17.4698, 78.3578],
]


# ==================================================
# CSV FUNCTIONS
# ==================================================
def load_csv(file_path, columns, default_rows=None):
    if not os.path.exists(file_path):
        df = pd.DataFrame(default_rows or [], columns=columns)
        df.to_csv(file_path, index=False)
        return df

    try:
        df = pd.read_csv(file_path, dtype=str).fillna("")
    except Exception:
        df = pd.DataFrame(default_rows or [], columns=columns)
        df.to_csv(file_path, index=False)
        return df

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns]


def save_csv(df, file_path):
    df.to_csv(file_path, index=False)


def load_users():
    users = load_csv(USERS_FILE, USER_COLUMNS, DEFAULT_USERS)

    host_hash = hashlib.sha256(HOST_PASSWORD.encode()).hexdigest()
    host_rows = users[users["User ID"] == "U-ADMIN"]

    if host_rows.empty:
        host_df = pd.DataFrame(
            [[
                "U-ADMIN",
                "VoltIQ Host",
                HOST_LOGIN,
                host_hash,
                "9999999999",
                "Host",
                "Hyderabad",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ]],
            columns=USER_COLUMNS,
        )
        users = pd.concat([host_df, users], ignore_index=True)
    else:
        idx = host_rows.index[0]
        users.loc[idx, "Email"] = HOST_LOGIN
        users.loc[idx, "Password Hash"] = host_hash
        users.loc[idx, "Role"] = "Host"

    save_csv(users, USERS_FILE)
    return users


def load_vehicles():
    return load_csv(VEHICLES_FILE, VEHICLE_COLUMNS, [])


def load_stations():
    return load_csv(STATIONS_FILE, STATION_COLUMNS, DEFAULT_STATIONS)


def load_reservations():
    return load_csv(RESERVATIONS_FILE, RESERVATION_COLUMNS, [])


def save_users(df):
    save_csv(df, USERS_FILE)


def save_vehicles(df):
    save_csv(df, VEHICLES_FILE)


def save_stations(df):
    save_csv(df, STATIONS_FILE)


def save_reservations(df):
    save_csv(df, RESERVATIONS_FILE)


# ==================================================
# HELPERS
# ==================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def to_numeric_columns(df, columns):
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


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


def maps_link(latitude, longitude):
    return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"


def wait_time(queue_length, charging_type):
    queue_length = int(float(queue_length or 0))

    if charging_type == "DC Fast Charging":
        return queue_length * 30

    return queue_length * 55


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


def prepared_stations():
    df = load_stations().copy()
    df = df.drop_duplicates(subset=["Station ID", "Station Name"], keep="first")

    number_columns = [
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

    df = to_numeric_columns(df, number_columns)

    df["Estimated Wait Time"] = df.apply(
        lambda row: wait_time(row["Queue Length"], row["Charging Type"]),
        axis=1,
    )

    df["Health Status"] = df.apply(
        lambda row: health_status(row["Total Chargers"], row["Faulty Chargers"]),
        axis=1,
    )

    df["Availability Status"] = df["Available Chargers"].apply(availability_status)

    df["Maps Link"] = df.apply(
        lambda row: maps_link(row["Latitude"], row["Longitude"]),
        axis=1,
    )

    if st.session_state.user_lat is not None and st.session_state.user_lon is not None:
        user_lat = float(st.session_state.user_lat)
        user_lon = float(st.session_state.user_lon)

        df["Distance km"] = df.apply(
            lambda row: distance_km(
                user_lat,
                user_lon,
                float(row["Latitude"]),
                float(row["Longitude"]),
            ),
            axis=1,
        )
    else:
        df["Distance km"] = pd.NA

    return df


def closest_station(df):
    if df is None or df.empty:
        return None

    if "Available Chargers" not in df.columns:
        return None

    available_df = df[df["Available Chargers"] > 0].copy()

    if available_df.empty:
        return None

    distance_df = available_df[pd.notna(available_df["Distance km"])].copy()

    if not distance_df.empty:
        distance_df = distance_df.sort_values(
            ["Distance km", "Estimated Wait Time", "Price per kWh", "Rating"],
            ascending=[True, True, True, False],
        )

        if not distance_df.empty:
            return distance_df.iloc[0]

    available_df = available_df.sort_values(
        ["Estimated Wait Time", "Price per kWh", "Rating"],
        ascending=[True, True, False],
    )

    if available_df.empty:
        return None

    return available_df.iloc[0]


def safe_sidebar_selectbox(label, options, key):
    if not options:
        options = ["All"]

    if key not in st.session_state or st.session_state[key] not in options:
        st.session_state[key] = options[0]

    return st.sidebar.selectbox(label, options, key=key)


def filter_stations(df):
    filtered = df.copy()

    if st.session_state.city_filter != "All":
        filtered = filtered[filtered["City"] == st.session_state.city_filter]

    if st.session_state.area_filter != "All":
        filtered = filtered[filtered["Area"] == st.session_state.area_filter]

    if st.session_state.network_filter != "All":
        filtered = filtered[filtered["Network"] == st.session_state.network_filter]

    if st.session_state.charging_filter != "All":
        filtered = filtered[filtered["Charging Type"] == st.session_state.charging_filter]

    if st.session_state.connector_filter != "All":
        filtered = filtered[filtered["Connector"] == st.session_state.connector_filter]

    if st.session_state.availability_filter == "Available Now":
        filtered = filtered[filtered["Available Chargers"] > 0]

    if st.session_state.availability_filter == "Currently Full":
        filtered = filtered[filtered["Available Chargers"] == 0]

    if st.session_state.availability_filter == "Low Queue Only":
        filtered = filtered[filtered["Queue Length"] <= 2]

    if st.session_state.open_filter == "Open 24x7 Only":
        filtered = filtered[filtered["Open 24x7"] == "Yes"]

    if st.session_state.amenity_filter != "All":
        filtered = filtered[
            filtered["Amenities"].str.contains(
                st.session_state.amenity_filter,
                case=False,
                na=False,
            )
        ]

    filtered = filtered[filtered["Price per kWh"] <= st.session_state.max_price]
    filtered = filtered[filtered["Rating"] >= st.session_state.min_rating]

    if st.session_state.user_lat is not None and st.session_state.user_lon is not None:
        filtered = filtered[filtered["Distance km"] <= st.session_state.max_distance]

    search_text = st.session_state.search_text.strip()

    if search_text:
        filtered = filtered[
            filtered["Station Name"].str.contains(search_text, case=False, na=False)
            | filtered["Area"].str.contains(search_text, case=False, na=False)
            | filtered["Network"].str.contains(search_text, case=False, na=False)
            | filtered["Connector"].str.contains(search_text, case=False, na=False)
        ]

    return filtered


def metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_station_card(row):
    st.markdown(
        f"""
        <div class="station-card">
            <span class="badge green">{row['Availability Status']}</span>
            <span class="badge blue">{row['Charging Type']}</span>
            <span class="badge orange">{row['Connector']}</span>
            <h3>{row['Station Name']}</h3>
            <p><b>Network:</b> {row['Network']} | <b>Area:</b> {row['Area']} | <b>Health:</b> {row['Health Status']}</p>
            <p><b>Address:</b> {row['Address']}</p>
            <p><b>Amenities:</b> {row['Amenities']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# FINAL DARK + WHITE CONTRAST STYLE
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(6,182,212,0.22), transparent 30%),
            radial-gradient(circle at bottom right, rgba(59,130,246,0.20), transparent 35%),
            linear-gradient(135deg, #07111F 0%, #0B1F3A 45%, #102A43 100%);
        color: #F8FAFC;
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .title {
        font-size: 44px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 2px;
        text-shadow: 0 3px 18px rgba(0,0,0,0.35);
    }

    .subtitle {
        font-size: 18px;
        color: #C7D2FE;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 20px;
    }

    .hero {
        padding: 28px;
        border-radius: 28px;
        background: linear-gradient(135deg, #FFFFFF 0%, #EEF6FF 50%, #E0F2FE 100%);
        border: 1px solid #BAE6FD;
        box-shadow: 0 22px 50px rgba(0,0,0,0.28);
        margin-bottom: 24px;
        color: #0F172A;
    }

    .hero h2 {
        margin: 0 0 8px 0;
        font-size: 30px;
        color: #0F172A;
        font-weight: 900;
    }

    .hero p {
        color: #334155;
        font-size: 16px;
        font-weight: 500;
    }

    .metric-card {
        padding: 20px;
        border-radius: 22px;
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        box-shadow: 0 16px 35px rgba(0,0,0,0.22);
        min-height: 112px;
        color: #0F172A;
    }

    .metric-label {
        color: #475569;
        font-size: 12px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .metric-value {
        color: #0F172A;
        font-size: 30px;
        font-weight: 900;
        margin-top: 6px;
    }

    .metric-note {
        color: #64748B;
        font-size: 12px;
        margin-top: 4px;
        font-weight: 600;
    }

    .station-card {
        padding: 22px;
        border-radius: 24px;
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        box-shadow: 0 16px 35px rgba(0,0,0,0.22);
        margin-bottom: 18px;
        color: #0F172A;
    }

    .station-card h2, .station-card h3 {
        color: #0F172A;
        font-weight: 900;
    }

    .station-card p {
        color: #334155;
        font-weight: 500;
    }

    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-weight: 900;
        font-size: 12px;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .green {
        background: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
    }

    .blue {
        background: #DBEAFE;
        color: #1D4ED8;
        border: 1px solid #93C5FD;
    }

    .orange {
        background: #FFEDD5;
        color: #C2410C;
        border: 1px solid #FDBA74;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #EAF6FF 100%);
        border-right: 1px solid #CBD5E1;
    }

    section[data-testid="stSidebar"] * {
        color: #0F172A !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF;
        color: #0F172A;
        border-radius: 14px;
        padding: 10px 16px;
        border: 1px solid #CBD5E1;
        font-weight: 800;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06B6D4, #2563EB) !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8;
    }

    div[data-testid="stDataFrame"] {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 8px;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 12px;
        border: 1px solid #CBD5E1;
        color: #0F172A;
    }

    .stAlert {
        border-radius: 14px;
    }

    .stButton button {
        border-radius: 12px;
        font-weight: 800;
    }

    .stTextInput input, .stSelectbox div, .stNumberInput input, .stTextArea textarea {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SESSION STATE
# ==================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "user_lat" not in st.session_state:
    st.session_state.user_lat = None

if "user_lon" not in st.session_state:
    st.session_state.user_lon = None

if "location_requested" not in st.session_state:
    st.session_state.location_requested = False


# ==================================================
# LOGIN PAGE
# ==================================================
if not st.session_state.logged_in:
    st.markdown('<div class="title">⚡ VoltIQ Technologies Pvt. Ltd</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Smart EV Charging Availability, Reservation and Queue Management System</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">
            <h2>Charge faster. Wait less. Drive smarter.</h2>
            <p>Find charging stations, check live availability, reserve slots, save vehicles and let hosts monitor everything from one dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(["🔐 Login", "✨ Create Account"])

    with login_tab:
        with st.container(border=True):
            st.subheader("Login")

            login_id = st.text_input("Login ID / Email")
            password = st.text_input("Password", type="password")

            if st.button("Login", type="primary", use_container_width=True):
                users = load_users()

                matched = users[
                    (users["Email"].str.lower() == login_id.strip().lower())
                    & (users["Password Hash"] == hash_password(password))
                ]

                if matched.empty:
                    st.error("Invalid login ID or password.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user = matched.iloc[0].to_dict()
                    st.success("Login successful.")
                    st.rerun()

            st.info("Demo User: user@demo.com / User@123")
            st.caption("Host Login: group 1 goated / shahid is goat")

    with signup_tab:
        with st.container(border=True):
            st.subheader("Create User Account")

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
                    st.error("Enter a valid 10-digit mobile number.")

                elif signup_email.strip().lower() in users["Email"].str.lower().tolist():
                    st.error("This login ID is already registered.")

                else:
                    new_user = pd.DataFrame(
                        [[
                            "U-" + str(uuid.uuid4())[:8].upper(),
                            name.strip(),
                            signup_email.strip().lower(),
                            hash_password(signup_password),
                            phone.strip(),
                            "User",
                            preferred_area,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ]],
                        columns=USER_COLUMNS,
                    )

                    users = pd.concat([users, new_user], ignore_index=True)
                    save_users(users)

                    st.success("Account created successfully. Host can now see this user in the dashboard.")

    st.stop()


# ==================================================
# MAIN HEADER
# ==================================================
user = st.session_state.user
user_id = user["User ID"]
is_host = user["Role"] == "Host"

header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown('<div class="title">⚡ VoltIQ Technologies Pvt. Ltd</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Live EV Charging Platform for Users and Station Hosts</div>',
        unsafe_allow_html=True,
    )

with header_col2:
    with st.popover("👤 Profile"):
        st.write(f"**Name:** {user['Name']}")
        st.write(f"**Login ID:** {user['Email']}")
        st.write(f"**Role:** {user['Role']}")

        if st.button("🔄 Refresh"):
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.user_lat = None
            st.session_state.user_lon = None
            st.session_state.location_requested = False
            st.rerun()


# ==================================================
# HOST DASHBOARD
# ==================================================
if is_host:
    users = load_users()
    vehicles = load_vehicles()
    reservations = load_reservations()
    stations_raw = load_stations()
    stations = prepared_stations()

    st.markdown(
        """
        <div class="hero">
            <h2>🛠️ Host Control Center</h2>
            <p>Monitor users, vehicles, reservations, queue load, charger status and station health. User registrations and reservations are saved in shared CSV files.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Refresh Latest User & Reservation Data", type="primary"):
        st.rerun()

    active_reservations = 0

    if not reservations.empty:
        active_reservations = len(reservations[reservations["Status"].isin(["Confirmed", "Queued"])])

    host_metrics = st.columns(5)

    with host_metrics[0]:
        metric_card("Users", len(users[users["Role"] == "User"]), "registered users")

    with host_metrics[1]:
        metric_card("Vehicles", len(vehicles), "saved vehicles")

    with host_metrics[2]:
        metric_card("Reservations", len(reservations), "total bookings")

    with host_metrics[3]:
        metric_card("Active", active_reservations, "confirmed + queued")

    with host_metrics[4]:
        metric_card("Available", int(stations["Available Chargers"].sum()), "chargers now")

    st.markdown("### 📈 Host Analytics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if reservations.empty:
            st.info("No reservations yet.")
        else:
            reservation_chart = reservations["Status"].value_counts().reset_index()
            reservation_chart.columns = ["Status", "Count"]
            st.bar_chart(reservation_chart.set_index("Status"))

    with chart_col2:
        station_chart = stations.set_index("Station Name")[["Available Chargers", "Occupied Chargers", "Queue Length"]]
        st.bar_chart(station_chart)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📋 Reservations",
            "👥 Users",
            "🚗 Vehicles",
            "⚙️ Station Management",
            "➕ Add Station",
        ]
    )

    with tab1:
        st.subheader("Reservation Cross-Check")

        if reservations.empty:
            st.info("No reservations yet.")
        else:
            reservation_display = reservations.merge(
                users[["User ID", "Name", "Email", "Phone"]],
                on="User ID",
                how="left",
            )

            search_reservation = st.text_input("Search reservation / user / vehicle / station")

            if search_reservation.strip():
                search_text = search_reservation.strip()

                reservation_display = reservation_display[
                    reservation_display.apply(
                        lambda row: row.astype(str).str.contains(search_text, case=False, na=False).any(),
                        axis=1,
                    )
                ]

            st.dataframe(reservation_display, use_container_width=True, hide_index=True)

            active_rows = reservations[reservations["Status"].isin(["Confirmed", "Queued"])]

            if not active_rows.empty:
                selected_reservation = st.selectbox(
                    "Select active reservation to complete",
                    active_rows["Reservation ID"].tolist(),
                )

                if st.button("✅ Mark Reservation as Completed"):
                    reservations = load_reservations()
                    stations_raw = load_stations()

                    selected_rows = reservations[reservations["Reservation ID"] == selected_reservation]

                    if selected_rows.empty:
                        st.error("Reservation not found.")
                    else:
                        reservation_index = selected_rows.index[0]
                        station_id = reservations.loc[reservation_index, "Station ID"]
                        old_status = reservations.loc[reservation_index, "Status"]

                        station_rows = stations_raw[stations_raw["Station ID"] == station_id]

                        if station_rows.empty:
                            st.error("Station not found.")
                        else:
                            station_index = station_rows.index[0]

                            if old_status == "Confirmed":
                                stations_raw.loc[station_index, "Occupied Chargers"] = max(
                                    0,
                                    int(float(stations_raw.loc[station_index, "Occupied Chargers"])) - 1,
                                )
                                stations_raw.loc[station_index, "Available Chargers"] = (
                                    int(float(stations_raw.loc[station_index, "Available Chargers"])) + 1
                                )

                            if old_status == "Queued":
                                stations_raw.loc[station_index, "Queue Length"] = max(
                                    0,
                                    int(float(stations_raw.loc[station_index, "Queue Length"])) - 1,
                                )

                            reservations.loc[reservation_index, "Status"] = "Completed"

                            save_reservations(reservations)
                            save_stations(stations_raw)

                            st.success("Reservation completed and station updated.")
                            st.rerun()

    with tab2:
        st.subheader("Registered Users")

        users_display = users.drop(columns=["Password Hash"], errors="ignore")
        st.dataframe(users_display, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Saved Vehicles")

        if vehicles.empty:
            st.info("No vehicles saved yet.")
        else:
            vehicles_display = vehicles.merge(
                users[["User ID", "Name", "Email", "Phone"]],
                on="User ID",
                how="left",
            )
            st.dataframe(vehicles_display, use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Station Management")

        if stations_raw.empty:
            st.warning("No stations available.")
        else:
            selected_station_name = st.selectbox(
                "Select station",
                stations_raw["Station Name"].tolist(),
            )

            selected_rows = stations_raw[stations_raw["Station Name"] == selected_station_name]

            if selected_rows.empty:
                st.error("Station not found.")
            else:
                station_index = selected_rows.index[0]
                station_row = stations_raw.loc[station_index]

                with st.form("edit_station_form"):
                    edit_col1, edit_col2, edit_col3 = st.columns(3)

                    with edit_col1:
                        available = st.number_input(
                            "Available Chargers",
                            min_value=0,
                            value=int(float(station_row["Available Chargers"])),
                        )
                        queue = st.number_input(
                            "Queue Length",
                            min_value=0,
                            value=int(float(station_row["Queue Length"])),
                        )

                    with edit_col2:
                        occupied = st.number_input(
                            "Occupied Chargers",
                            min_value=0,
                            value=int(float(station_row["Occupied Chargers"])),
                        )
                        price = st.number_input(
                            "Price per kWh",
                            min_value=1,
                            value=int(float(station_row["Price per kWh"])),
                        )

                    with edit_col3:
                        faulty = st.number_input(
                            "Faulty Chargers",
                            min_value=0,
                            value=int(float(station_row["Faulty Chargers"])),
                        )
                        rating = st.number_input(
                            "Rating",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(station_row["Rating"]),
                            step=0.1,
                        )

                    update_station = st.form_submit_button("Update Station", use_container_width=True)

                if update_station:
                    total = int(float(station_row["Total Chargers"]))

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

                        st.success("Station updated. Users will see the new status.")
                        st.rerun()

            st.markdown("### Full Station Database")
            st.dataframe(stations_raw, use_container_width=True, hide_index=True)

    with tab5:
        st.subheader("Add New Charging Station")

        with st.form("add_station_form"):
            add_col1, add_col2 = st.columns(2)

            with add_col1:
                new_station_name = st.text_input("Station Name")
                new_network = st.text_input("Network", value="VoltIQ")
                new_city = st.text_input("City", value="Hyderabad")
                new_area = st.text_input("Area")
                new_address = st.text_input("Address")
                new_charging_type = st.selectbox("Charging Type", ["DC Fast Charging", "AC Charging"])
                new_connector = st.selectbox("Connector", ["CCS2", "Type 2", "CHAdeMO"])

            with add_col2:
                new_total = st.number_input("Total Chargers", min_value=1, value=4)
                new_available = st.number_input("Available Chargers", min_value=0, value=2)
                new_occupied = st.number_input("Occupied Chargers", min_value=0, value=2)
                new_faulty = st.number_input("Faulty Chargers", min_value=0, value=0)
                new_queue = st.number_input("Queue Length", min_value=0, value=0)
                new_price = st.number_input("Price per kWh", min_value=1, value=20)
                new_rating = st.number_input("Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.1)

            new_open_24 = st.selectbox("Open 24x7", ["Yes", "No"])
            new_amenities = st.text_input("Amenities", value="Parking, Food")
            new_latitude = st.number_input("Latitude", value=17.3850, format="%.6f")
            new_longitude = st.number_input("Longitude", value=78.4867, format="%.6f")

            add_station = st.form_submit_button("Add Station", use_container_width=True)

        if add_station:
            if not new_station_name.strip() or not new_area.strip() or not new_address.strip():
                st.error("Station name, area and address are required.")

            elif new_available + new_occupied + new_faulty != new_total:
                st.error("Available + Occupied + Faulty must equal Total Chargers.")

            elif new_station_name.strip().lower() in stations_raw["Station Name"].str.lower().tolist():
                st.error("This station already exists.")

            else:
                new_station = pd.DataFrame(
                    [[
                        "SC-" + str(uuid.uuid4())[:8].upper(),
                        new_station_name.strip(),
                        new_network.strip(),
                        new_city.strip(),
                        new_area.strip(),
                        new_address.strip(),
                        new_charging_type,
                        new_connector,
                        new_total,
                        new_available,
                        new_occupied,
                        new_faulty,
                        new_queue,
                        new_price,
                        new_rating,
                        new_open_24,
                        new_amenities.strip(),
                        new_latitude,
                        new_longitude,
                    ]],
                    columns=STATION_COLUMNS,
                )

                stations_raw = pd.concat([stations_raw, new_station], ignore_index=True)
                save_stations(stations_raw)

                st.success("Station added successfully.")
                st.rerun()

    st.stop()


# ==================================================
# USER DASHBOARD
# ==================================================
st.markdown(
    """
    <div class="hero">
        <h2>🚗 User Charging Dashboard</h2>
        <p>Search stations, find the closest available charger, reserve a slot and save your EV details. Your bookings will appear in the host dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 📍 Location Settings")

location_on = st.session_state.user_lat is not None and st.session_state.user_lon is not None

if location_on:
    loc_col1, loc_col2 = st.columns([3, 1])

    with loc_col1:
        st.success(
            f"Location enabled: {round(float(st.session_state.user_lat), 5)}, "
            f"{round(float(st.session_state.user_lon), 5)}"
        )

    with loc_col2:
        if st.button("Change Location"):
            st.session_state.user_lat = None
            st.session_state.user_lon = None
            st.session_state.location_requested = False
            st.rerun()

else:
    with st.container(border=True):
        location_col1, location_col2 = st.columns(2)

        with location_col1:
            if st.button("Allow Browser Location", type="primary"):
                st.session_state.location_requested = True

            if st.session_state.location_requested:
                if get_geolocation is None:
                    st.warning("Browser location package unavailable. Use manual area selection.")
                else:
                    browser_location = get_geolocation()
                    latitude, longitude = extract_location(browser_location)

                    if latitude is not None and longitude is not None:
                        st.session_state.user_lat = float(latitude)
                        st.session_state.user_lon = float(longitude)
                        st.session_state.location_requested = False
                        st.rerun()
                    else:
                        st.info("Waiting for browser location permission.")

        with location_col2:
            manual_area = st.selectbox("Select Your Area", list(KNOWN_LOCATIONS.keys()))

            if st.button("Use Selected Area"):
                st.session_state.user_lat, st.session_state.user_lon = KNOWN_LOCATIONS[manual_area]
                st.rerun()


stations = prepared_stations()

st.sidebar.header("🔎 Smart Filters")

city_options = ["All"] + sorted(stations["City"].dropna().unique().tolist())
safe_sidebar_selectbox("City", city_options, "city_filter")

city_base = stations.copy()

if st.session_state.city_filter != "All":
    city_base = city_base[city_base["City"] == st.session_state.city_filter]

area_options = ["All"] + sorted(city_base["Area"].dropna().unique().tolist())
safe_sidebar_selectbox("Area", area_options, "area_filter")

area_base = city_base.copy()

if st.session_state.area_filter != "All":
    area_base = area_base[area_base["Area"] == st.session_state.area_filter]

network_options = ["All"] + sorted(area_base["Network"].dropna().unique().tolist())
safe_sidebar_selectbox("Charging Network", network_options, "network_filter")

charging_options = ["All"] + sorted(area_base["Charging Type"].dropna().unique().tolist())
safe_sidebar_selectbox("Charging Speed", charging_options, "charging_filter")

connector_options = ["All"] + sorted(area_base["Connector"].dropna().unique().tolist())
safe_sidebar_selectbox("Connector", connector_options, "connector_filter")

if "availability_filter" not in st.session_state:
    st.session_state.availability_filter = "All"

if "open_filter" not in st.session_state:
    st.session_state.open_filter = "All"

if "amenity_filter" not in st.session_state:
    st.session_state.amenity_filter = "All"

if "max_price" not in st.session_state:
    st.session_state.max_price = 25

if "min_rating" not in st.session_state:
    st.session_state.min_rating = 3.8

if "max_distance" not in st.session_state:
    st.session_state.max_distance = 15

if "search_text" not in st.session_state:
    st.session_state.search_text = ""

st.sidebar.selectbox(
    "Availability",
    ["All", "Available Now", "Currently Full", "Low Queue Only"],
    key="availability_filter",
)

st.sidebar.selectbox(
    "Operating Hours",
    ["All", "Open 24x7 Only"],
    key="open_filter",
)

st.sidebar.selectbox(
    "Amenity",
    ["All", "Parking", "Food", "Restroom", "Mall", "Service Center", "Metro Access"],
    key="amenity_filter",
)

st.sidebar.slider("Maximum Price per kWh", 10, 30, key="max_price")
st.sidebar.slider("Minimum Rating", 3.5, 5.0, step=0.1, key="min_rating")

if location_on:
    st.sidebar.slider("Maximum Distance from You", 1, 50, key="max_distance")
else:
    st.session_state.max_distance = 50
    st.sidebar.caption("Set location to enable distance filter.")

st.sidebar.text_input("Search", placeholder="Tata, Madhapur, CCS2", key="search_text")

filtered_stations = filter_stations(stations)

st.markdown("## 📊 Live Charging Overview")

overview_cols = st.columns(5)

with overview_cols[0]:
    metric_card("Stations", len(filtered_stations), "found")

with overview_cols[1]:
    metric_card(
        "Available",
        int(filtered_stations["Available Chargers"].sum()) if not filtered_stations.empty else 0,
        "chargers",
    )

with overview_cols[2]:
    metric_card(
        "Occupied",
        int(filtered_stations["Occupied Chargers"].sum()) if not filtered_stations.empty else 0,
        "busy",
    )

with overview_cols[3]:
    metric_card(
        "Queue",
        int(filtered_stations["Queue Length"].sum()) if not filtered_stations.empty else 0,
        "vehicles",
    )

with overview_cols[4]:
    avg_price = "₹0"

    if not filtered_stations.empty:
        avg_price = f"₹{round(filtered_stations['Price per kWh'].mean(), 2)}"

    metric_card("Avg Price", avg_price, "per kWh")

st.divider()

user_tab1, user_tab2, user_tab3, user_tab4, user_tab5, user_tab6 = st.tabs(
    [
        "🔍 Find Charger",
        "📍 Station Details",
        "🧾 Reserve Slot",
        "🚗 My Vehicles",
        "👤 My Profile",
        "🏢 Company Details",
    ]
)

with user_tab1:
    st.markdown("## 🔍 Closest Available Charging Station")

    best_station = closest_station(filtered_stations)

    if best_station is None:
        st.warning("No available charging station found. Please change filters or location.")
    else:
        show_station_card(best_station)

        best_cols = st.columns(4)

        with best_cols[0]:
            metric_card("Available", int(best_station["Available Chargers"]), "chargers")

        with best_cols[1]:
            metric_card("Queue", int(best_station["Queue Length"]), "vehicles")

        with best_cols[2]:
            metric_card("Wait", f"{int(best_station['Estimated Wait Time'])} min", "estimated")

        with best_cols[3]:
            distance_value = "Set location"

            if pd.notna(best_station["Distance km"]):
                distance_value = f"{round(best_station['Distance km'], 2)} km"

            metric_card("Distance", distance_value, "from you")

        st.link_button("📍 Open Exact Location in Google Maps", best_station["Maps Link"])

with user_tab2:
    st.markdown("## 📍 Station Details")

    if filtered_stations.empty:
        st.warning("No station data available.")
    else:
        display_stations = filtered_stations.copy()

        if location_on:
            display_stations = display_stations.sort_values("Distance km", na_position="last")

        for _, station_row in display_stations.iterrows():
            show_station_card(station_row)

            station_metrics = st.columns(5)

            station_metrics[0].metric("Available", int(station_row["Available Chargers"]))
            station_metrics[1].metric("Occupied", int(station_row["Occupied Chargers"]))
            station_metrics[2].metric("Faulty", int(station_row["Faulty Chargers"]))
            station_metrics[3].metric("Queue", int(station_row["Queue Length"]))
            station_metrics[4].metric("Price", f"₹{station_row['Price per kWh']}/kWh")

            if int(station_row["Total Chargers"]) > 0:
                st.progress(float(station_row["Available Chargers"]) / float(station_row["Total Chargers"]))

            st.link_button("Navigate in Google Maps", station_row["Maps Link"])

with user_tab3:
    st.markdown("## 🧾 Reserve a Charging Slot")

    if filtered_stations.empty:
        st.warning("No stations available for reservation.")
    else:
        reservation_station_df = filtered_stations.copy()

        if location_on:
            reservation_station_df = reservation_station_df.sort_values("Distance km", na_position="last")

        selected_station_name = st.selectbox(
            "Select Charging Station",
            reservation_station_df["Station Name"].tolist(),
        )

        selected_station = reservation_station_df[
            reservation_station_df["Station Name"] == selected_station_name
        ].iloc[0]

        st.info(
            f"{int(selected_station['Available Chargers'])} chargers available | "
            f"{int(selected_station['Queue Length'])} in queue | "
            f"estimated wait {int(selected_station['Estimated Wait Time'])} min"
        )

        vehicles = load_vehicles()
        my_vehicles = vehicles[vehicles["User ID"] == user_id]

        with st.form("reservation_form"):
            if my_vehicles.empty:
                vehicle_number = st.text_input("Vehicle Number")
                ev_model = st.text_input("EV Model")
            else:
                chosen_vehicle = st.selectbox(
                    "Select Saved Vehicle",
                    my_vehicles["Vehicle Number"].tolist(),
                )

                vehicle_row = my_vehicles[my_vehicles["Vehicle Number"] == chosen_vehicle].iloc[0]
                vehicle_number = vehicle_row["Vehicle Number"]
                ev_model = vehicle_row["EV Model"]

                st.write(f"**EV Model:** {ev_model}")

            driver_name = st.text_input("Driver Name", value=user["Name"])
            mobile_number = st.text_input("Mobile Number", value=str(user["Phone"]))
            booking_date = st.date_input("Charging Date")
            booking_time = st.time_input("Preferred Time")
            duration = st.selectbox("Duration", ["30 minutes", "1 hour", "1.5 hours", "2 hours"])

            agree = st.checkbox(
                "I agree that my booking may be moved to queue if the charger becomes unavailable."
            )

            submit_reservation = st.form_submit_button("Confirm Reservation", use_container_width=True)

        if submit_reservation:
            reservations = load_reservations()
            stations_raw = load_stations()

            vehicle_number = vehicle_number.strip().upper()
            ev_model = ev_model.strip()
            mobile_number = str(mobile_number).strip()

            duplicate = reservations[
                (reservations["Vehicle Number"] == vehicle_number)
                & (reservations["Status"].isin(["Confirmed", "Queued"]))
            ]

            if not vehicle_number or not ev_model or not mobile_number:
                st.error("Please provide vehicle and mobile details.")

            elif not mobile_number.isdigit() or len(mobile_number) != 10:
                st.error("Enter a valid 10-digit mobile number.")

            elif not agree:
                st.error("Please accept the reservation condition.")

            elif not duplicate.empty:
                st.warning("This vehicle already has an active reservation or queue entry.")

            else:
                station_id = selected_station["Station ID"]
                station_rows = stations_raw[stations_raw["Station ID"] == station_id]

                if station_rows.empty:
                    st.error("Station not found. Refresh the app.")
                else:
                    station_index = station_rows.index[0]
                    available = int(float(stations_raw.loc[station_index, "Available Chargers"]))

                    if available > 0:
                        stations_raw.loc[station_index, "Available Chargers"] = available - 1
                        stations_raw.loc[station_index, "Occupied Chargers"] = (
                            int(float(stations_raw.loc[station_index, "Occupied Chargers"])) + 1
                        )
                        reservation_status = "Confirmed"
                    else:
                        stations_raw.loc[station_index, "Queue Length"] = (
                            int(float(stations_raw.loc[station_index, "Queue Length"])) + 1
                        )
                        reservation_status = "Queued"

                    reservation_id = "VQ-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(uuid.uuid4())[:4].upper()

                    new_reservation = pd.DataFrame(
                        [[
                            reservation_id,
                            user_id,
                            driver_name.strip(),
                            vehicle_number,
                            ev_model,
                            mobile_number,
                            station_id,
                            selected_station["Station Name"],
                            str(booking_date),
                            str(booking_time),
                            duration,
                            reservation_status,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ]],
                        columns=RESERVATION_COLUMNS,
                    )

                    reservations = pd.concat([reservations, new_reservation], ignore_index=True)

                    save_reservations(reservations)
                    save_stations(stations_raw)

                    st.success(f"Reservation {reservation_status.lower()} successfully. Host can now view it.")
                    st.rerun()

    st.markdown("### My Reservations")

    my_reservations = load_reservations()
    my_reservations = my_reservations[my_reservations["User ID"] == user_id]

    if my_reservations.empty:
        st.info("No reservations yet.")
    else:
        st.dataframe(my_reservations, use_container_width=True, hide_index=True)

with user_tab4:
    st.markdown("## 🚗 My Saved Vehicles")

    vehicles = load_vehicles()
    my_vehicles = vehicles[vehicles["User ID"] == user_id]

    if my_vehicles.empty:
        st.info("No vehicles saved yet.")
    else:
        st.dataframe(my_vehicles, use_container_width=True, hide_index=True)

    with st.form("vehicle_form"):
        vehicle_number = st.text_input("Vehicle Number")
        ev_model = st.text_input("EV Model")
        connector = st.selectbox("Connector", ["CCS2", "Type 2", "CHAdeMO"])
        battery = st.number_input("Battery Capacity kWh", min_value=10, max_value=150, value=40)

        add_vehicle = st.form_submit_button("Save Vehicle", use_container_width=True)

    if add_vehicle:
        vehicles = load_vehicles()
        vehicle_number = vehicle_number.strip().upper()

        duplicate_vehicle = vehicles[
            (vehicles["User ID"] == user_id)
            & (vehicles["Vehicle Number"] == vehicle_number)
        ]

        if not vehicle_number or not ev_model.strip():
            st.error("Vehicle number and model are required.")

        elif not duplicate_vehicle.empty:
            st.error("This vehicle is already saved.")

        else:
            new_vehicle = pd.DataFrame(
                [[
                    "VH-" + str(uuid.uuid4())[:8].upper(),
                    user_id,
                    vehicle_number,
                    ev_model.strip(),
                    connector,
                    battery,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]],
                columns=VEHICLE_COLUMNS,
            )

            vehicles = pd.concat([vehicles, new_vehicle], ignore_index=True)
            save_vehicles(vehicles)

            st.success("Vehicle saved. Host can now view it.")
            st.rerun()

with user_tab5:
    st.markdown("## 👤 My Profile")

    with st.form("profile_form"):
        updated_name = st.text_input("Name", value=user["Name"])
        updated_phone = st.text_input("Phone", value=str(user["Phone"]))

        area_list = list(KNOWN_LOCATIONS.keys())
        current_area = user["Preferred Area"] if user["Preferred Area"] in area_list else "Hyderabad"

        updated_area = st.selectbox(
            "Preferred Area",
            area_list,
            index=area_list.index(current_area),
        )

        update_profile = st.form_submit_button("Update Profile", use_container_width=True)

    if update_profile:
        users = load_users()
        user_rows = users[users["User ID"] == user_id]

        if not updated_name.strip() or not updated_phone.strip():
            st.error("Name and phone are required.")

        elif not updated_phone.isdigit() or len(updated_phone) != 10:
            st.error("Enter a valid 10-digit mobile number.")

        elif user_rows.empty:
            st.error("User not found. Please login again.")

        else:
            user_index = user_rows.index[0]

            users.loc[user_index, "Name"] = updated_name.strip()
            users.loc[user_index, "Phone"] = updated_phone.strip()
            users.loc[user_index, "Preferred Area"] = updated_area

            save_users(users)

            st.session_state.user = users.loc[user_index].to_dict()

            st.success("Profile updated.")
            st.rerun()

with user_tab6:
    st.markdown("## 🏢 Company Details")

    st.markdown(
        """
        <div class="station-card">
            <h2>VoltIQ Technologies Pvt. Ltd</h2>
            <p><b>VoltIQ Technologies Pvt. Ltd</b> is a smart EV charging platform designed to make electric vehicle charging more convenient, reliable and user-friendly.</p>
            <p>Users can find stations, check availability, view queue length, reserve slots, save vehicles and navigate through Google Maps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    company_col1, company_col2 = st.columns(2)

    with company_col1:
        st.markdown("### Services")
        st.write("✅ EV station discovery")
        st.write("✅ Closest charger recommendation")
        st.write("✅ Slot reservation")
        st.write("✅ Queue management")
        st.write("✅ Host control dashboard")

    with company_col2:
        st.markdown("### Contact")
        st.write("**Email:** support@voltiq.com")
        st.write("**Phone:** +91 98765 43210")
        st.write("**Location:** Hyderabad, Telangana, India")
        st.write("**Working Hours:** 9:00 AM to 6:00 PM")

    st.markdown("### Mission")
    st.write(
        "To reduce EV charging delays and make electric vehicle usage more comfortable, predictable and stress-free."
    )

    st.markdown("### Vision")
    st.write(
        "To support the growth of electric mobility through a smart, connected and user-focused charging experience."
    )

    st.success("Powering smarter journeys, one charge at a time.")