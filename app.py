import os
import uuid
import hashlib
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

try:
    from streamlit_js_eval import get_geolocation
except Exception:
    get_geolocation = None


# ==================================================
# APP CONFIG
# ==================================================
st.set_page_config(
    page_title="VoltIQ Smart Charge",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TIMEZONE = ZoneInfo("Asia/Kolkata")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
VEHICLES_FILE = os.path.join(DATA_DIR, "vehicles.csv")
STATIONS_FILE = os.path.join(DATA_DIR, "stations.csv")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.csv")
SESSIONS_FILE = os.path.join(DATA_DIR, "charging_sessions.csv")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.csv")

HOST_LOGIN = "group 1 goated"
HOST_PASSWORD = "shahid is goat"
DEMO_LOGIN = "user@demo.com"
DEMO_PASSWORD = "User@123"

RESERVATION_FEE_RATE = 0.10
NO_SHOW_RATE = 0.05
STATION_COMMISSION_RATE = 0.05
PRIORITY_FEE = 40


# ==================================================
# COLUMNS
# ==================================================
USER_COLUMNS = [
    "User ID",
    "Name",
    "Email",
    "Password Hash",
    "Phone",
    "Role",
    "Preferred Area",
    "Created At",
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
    "Longitude",
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
    "Slot DateTime",
    "Duration",
    "Priority Booking",
    "Status",
    "Charging Cost Estimate",
    "Reservation Fee",
    "Priority Fee",
    "Estimated Payable",
    "No Show Penalty",
    "Created At",
    "Arrived At",
    "Started At",
    "Completed At",
]

SESSION_COLUMNS = [
    "Session ID",
    "Reservation ID",
    "User ID",
    "Station ID",
    "Station Name",
    "Vehicle Number",
    "Energy kWh",
    "Price per kWh",
    "Charging Cost",
    "Reservation Fee",
    "Priority Fee",
    "No Show Penalty",
    "Station Commission",
    "Station Owner Payout",
    "Total Payable",
    "VoltIQ Earnings",
    "Settlement Month",
    "Started At",
    "Completed At",
]

NOTIFICATION_COLUMNS = [
    "Notification ID",
    "User ID",
    "Message",
    "Created At",
    "Read",
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

EV_MODELS = [
    "Tata Nexon EV",
    "Tata Tiago EV",
    "Tata Tigor EV",
    "Tata Punch EV",
    "MG ZS EV",
    "MG Comet EV",
    "Mahindra XUV400 EV",
    "Hyundai Kona Electric",
    "Hyundai IONIQ 5",
    "BYD Atto 3",
    "BYD Seal",
    "Kia EV6",
    "Citroen eC3",
    "Mercedes-Benz EQB",
    "BMW i4",
    "Audi e-tron",
    "Other",
]

DEFAULT_USERS = [
    [
        "U-ADMIN",
        "VoltIQ Host",
        HOST_LOGIN,
        hashlib.sha256(HOST_PASSWORD.encode()).hexdigest(),
        "9999999999",
        "Host",
        "Hyderabad",
        datetime.now(APP_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
    ],
    [
        "U-DEMO",
        "Demo User",
        DEMO_LOGIN,
        hashlib.sha256(DEMO_PASSWORD.encode()).hexdigest(),
        "8888888888",
        "User",
        "Gachibowli",
        datetime.now(APP_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
    ],
]

DEFAULT_STATIONS = [
    ["SC001", "Tata Power EZ Charge - Begumpet", "Tata Power", "Hyderabad", "Begumpet", "Begumpet, Hyderabad", "DC Fast Charging", "CCS2", 4, 2, 1, 1, 1, 22, 4.2, "No", "Parking, Service Center", 17.4435, 78.4622],
    ["SC002", "Statiq EV Charging - Kukatpally", "Statiq", "Hyderabad", "Kukatpally", "Kukatpally, Hyderabad", "DC Fast Charging", "CCS2", 4, 1, 2, 1, 3, 21, 4.1, "Yes", "Parking, Food", 17.4933, 78.3996],
    ["SC003", "ChargeZone Hub - Hitech City", "ChargeZone", "Hyderabad", "Hitech City", "Hitech City, Hyderabad", "DC Fast Charging", "CCS2", 5, 2, 3, 0, 1, 22, 4.5, "Yes", "Parking, Food, Restroom, Mall", 17.4504, 78.3805],
    ["SC004", "Jio-bp Pulse - Madhapur", "Jio-bp", "Hyderabad", "Madhapur", "Madhapur, Hyderabad", "DC Fast Charging", "CCS2", 4, 0, 4, 0, 4, 23, 4.0, "Yes", "Parking, Food, Restroom", 17.4483, 78.3915],
    ["SC005", "GLIDA Green Drive - Gachibowli", "GLIDA", "Hyderabad", "Gachibowli", "Gachibowli, Hyderabad", "DC Fast Charging", "CCS2", 6, 4, 2, 0, 0, 20, 4.4, "Yes", "Parking, Restroom, Food", 17.4401, 78.3489],
    ["SC006", "Public EV Point - Durgam Cheruvu", "Public EV", "Hyderabad", "Durgam Cheruvu", "Durgam Cheruvu, Hyderabad", "AC Charging", "Type 2", 3, 1, 1, 1, 1, 17, 3.9, "No", "Parking", 17.4309, 78.3894],
    ["SC007", "Tata Power EZ Charge - Miyapur", "Tata Power", "Hyderabad", "Miyapur", "Miyapur Metro Station", "AC Charging", "Type 2", 3, 1, 2, 0, 2, 18, 4.0, "No", "Parking, Metro Access", 17.4964, 78.3611],
    ["SC008", "Public EV Station - BHEL", "Public EV", "Hyderabad", "BHEL", "BHEL, Hyderabad", "AC Charging", "Type 2", 4, 2, 2, 0, 1, 16, 4.0, "No", "Parking", 17.4948, 78.3053],
    ["SC009", "VoltIQ FastCharge - Financial District", "VoltIQ", "Hyderabad", "Financial District", "Financial District, Hyderabad", "DC Fast Charging", "CCS2", 8, 5, 3, 0, 0, 19, 4.6, "Yes", "Parking, Food, Restroom", 17.4149, 78.3422],
    ["SC010", "VoltIQ ChargePoint - Kondapur", "VoltIQ", "Hyderabad", "Kondapur", "Kondapur, Hyderabad", "AC Charging", "Type 2", 4, 2, 2, 0, 1, 17, 4.2, "No", "Parking, Food", 17.4698, 78.3578],
]


# ==================================================
# DATA FUNCTIONS
# ==================================================
def save_df(df, path):
    df.to_csv(path, index=False)


def load_df(path, columns, default_rows=None):
    if not os.path.exists(path):
        df = pd.DataFrame(default_rows or [], columns=columns)
        save_df(df, path)
        return df

    try:
        df = pd.read_csv(path, dtype=str).fillna("")
    except Exception:
        df = pd.DataFrame(default_rows or [], columns=columns)
        save_df(df, path)
        return df

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns]


def load_users():
    users = load_df(USERS_FILE, USER_COLUMNS, DEFAULT_USERS)
    host_hash = hashlib.sha256(HOST_PASSWORD.encode()).hexdigest()
    demo_hash = hashlib.sha256(DEMO_PASSWORD.encode()).hexdigest()

    if "U-ADMIN" not in users["User ID"].tolist():
        users = pd.concat([pd.DataFrame([DEFAULT_USERS[0]], columns=USER_COLUMNS), users], ignore_index=True)
    host_idx = users[users["User ID"] == "U-ADMIN"].index[0]
    users.loc[host_idx, "Email"] = HOST_LOGIN
    users.loc[host_idx, "Password Hash"] = host_hash
    users.loc[host_idx, "Role"] = "Host"

    if "U-DEMO" not in users["User ID"].tolist():
        users = pd.concat([users, pd.DataFrame([DEFAULT_USERS[1]], columns=USER_COLUMNS)], ignore_index=True)
    demo_idx = users[users["User ID"] == "U-DEMO"].index[0]
    users.loc[demo_idx, "Email"] = DEMO_LOGIN
    users.loc[demo_idx, "Password Hash"] = demo_hash
    users.loc[demo_idx, "Role"] = "User"

    save_df(users, USERS_FILE)
    return users


def load_vehicles():
    return load_df(VEHICLES_FILE, VEHICLE_COLUMNS, [])


def load_stations():
    return load_df(STATIONS_FILE, STATION_COLUMNS, DEFAULT_STATIONS)


def load_reservations():
    return load_df(RESERVATIONS_FILE, RESERVATION_COLUMNS, [])


def load_sessions():
    return load_df(SESSIONS_FILE, SESSION_COLUMNS, [])


def load_notifications():
    return load_df(NOTIFICATIONS_FILE, NOTIFICATION_COLUMNS, [])


def save_users(df):
    save_df(df, USERS_FILE)


def save_vehicles(df):
    save_df(df, VEHICLES_FILE)


def save_stations(df):
    save_df(df, STATIONS_FILE)


def save_reservations(df):
    save_df(df, RESERVATIONS_FILE)


def save_sessions(df):
    save_df(df, SESSIONS_FILE)


def save_notifications(df):
    save_df(df, NOTIFICATIONS_FILE)


# ==================================================
# HELPERS
# ==================================================
def now_ist():
    return datetime.now(APP_TIMEZONE)


def today_ist():
    return now_ist().date()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def to_number(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def format_money(value):
    return f"Rs. {round(to_number(value)):,}"


def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return round(radius * 2 * atan2(sqrt(a), sqrt(1 - a)), 2)


def wait_time(queue, charging_type):
    queue = int(to_number(queue))
    return queue * 30 if charging_type == "DC Fast Charging" else queue * 55


def availability_text(available):
    available = int(to_number(available))
    if available >= 3:
        return "Good Availability"
    if available >= 1:
        return "Limited Availability"
    return "Currently Full"


def health_text(total, faulty):
    total = int(to_number(total))
    faulty = int(to_number(faulty))
    if total <= 0:
        return "Invalid"
    if faulty == 0:
        return "Excellent"
    ratio = faulty / total
    if ratio <= 0.20:
        return "Good"
    if ratio <= 0.40:
        return "Average"
    return "Poor"


def maps_link(lat, lon):
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"


def extract_location(location_data):
    if not location_data:
        return None, None
    if isinstance(location_data, dict):
        if "coords" in location_data:
            coords = location_data["coords"]
            return coords.get("latitude"), coords.get("longitude")
        return location_data.get("latitude"), location_data.get("longitude")
    return None, None


def round_up_to_next_30_minutes(dt):
    dt = dt.replace(second=0, microsecond=0)
    if dt.minute == 0:
        return dt
    if dt.minute <= 30:
        return dt.replace(minute=30)
    return dt.replace(minute=0) + timedelta(hours=1)


def get_time_options_for_date(date_text):
    selected_date = datetime.strptime(date_text, "%Y-%m-%d").date()
    start_time = datetime.combine(selected_date, datetime.min.time(), tzinfo=APP_TIMEZONE).replace(hour=6, minute=0)
    end_time = datetime.combine(selected_date, datetime.min.time(), tzinfo=APP_TIMEZONE).replace(hour=23, minute=0)

    if selected_date == today_ist():
        start_time = max(start_time, round_up_to_next_30_minutes(now_ist() + timedelta(minutes=15)))

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


def parse_slot_datetime(date_text, time_text):
    return datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M").replace(tzinfo=APP_TIMEZONE)


def duration_minutes(duration):
    mapping = {
        "30 minutes": 30,
        "1 hour": 60,
        "1.5 hours": 90,
        "2 hours": 120,
    }
    return mapping.get(duration, 30)


def estimate_kwh(duration, charging_type, current_battery, target_battery, battery_capacity):
    battery_gap = max(0, target_battery - current_battery)
    battery_based = battery_capacity * (battery_gap / 100)
    speed_kw = 40 if charging_type == "DC Fast Charging" else 7
    time_based = speed_kw * (duration_minutes(duration) / 60)
    return round(max(1, min(battery_based, time_based)), 2)


def calculate_charges(energy_kwh, price_per_kwh, priority=False, no_show=False):
    charging_cost = round(to_number(energy_kwh) * to_number(price_per_kwh), 2)
    reservation_fee = round(charging_cost * RESERVATION_FEE_RATE, 2)
    priority_fee = PRIORITY_FEE if priority else 0
    no_show_penalty = round(charging_cost * NO_SHOW_RATE, 2) if no_show else 0
    station_commission = round(charging_cost * STATION_COMMISSION_RATE, 2)
    station_payout = round(charging_cost - station_commission, 2)
    total_payable = round(charging_cost + reservation_fee + priority_fee + no_show_penalty, 2)
    voltiq_earnings = round(reservation_fee + priority_fee + no_show_penalty + station_commission, 2)
    return {
        "charging_cost": charging_cost,
        "reservation_fee": reservation_fee,
        "priority_fee": priority_fee,
        "no_show_penalty": no_show_penalty,
        "station_commission": station_commission,
        "station_payout": station_payout,
        "total_payable": total_payable,
        "voltiq_earnings": voltiq_earnings,
    }


def prepare_stations():
    df = load_stations().copy()
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

    df["Estimated Wait Time"] = df.apply(lambda row: wait_time(row["Queue Length"], row["Charging Type"]), axis=1)
    df["Availability Status"] = df["Available Chargers"].apply(availability_text)
    df["Health Status"] = df.apply(lambda row: health_text(row["Total Chargers"], row["Faulty Chargers"]), axis=1)
    df["Maps Link"] = df.apply(lambda row: maps_link(row["Latitude"], row["Longitude"]), axis=1)

    if st.session_state.user_lat is not None and st.session_state.user_lon is not None:
        df["Distance km"] = df.apply(
            lambda row: distance_km(
                float(st.session_state.user_lat),
                float(st.session_state.user_lon),
                float(row["Latitude"]),
                float(row["Longitude"]),
            ),
            axis=1,
        )
    else:
        df["Distance km"] = pd.NA

    return df


def apply_filters(df):
    filtered = df.copy()
    if st.session_state.area_filter != "All":
        filtered = filtered[filtered["Area"] == st.session_state.area_filter]
    if st.session_state.network_filter != "All":
        filtered = filtered[filtered["Network"] == st.session_state.network_filter]
    if st.session_state.charger_filter != "All":
        filtered = filtered[filtered["Charging Type"] == st.session_state.charger_filter]
    if st.session_state.connector_filter != "All":
        filtered = filtered[filtered["Connector"] == st.session_state.connector_filter]
    if st.session_state.available_filter == "Available Only":
        filtered = filtered[filtered["Available Chargers"] > 0]
    if st.session_state.open_filter == "Open 24x7":
        filtered = filtered[filtered["Open 24x7"] == "Yes"]
    filtered = filtered[filtered["Price per kWh"] <= st.session_state.max_price]

    search = st.session_state.search_text.strip()
    if search:
        filtered = filtered[
            filtered["Station Name"].str.contains(search, case=False, na=False)
            | filtered["Network"].str.contains(search, case=False, na=False)
            | filtered["Area"].str.contains(search, case=False, na=False)
        ]

    return filtered


def best_station(df):
    available = df[df["Available Chargers"] > 0].copy()
    if available.empty:
        return None
    with_distance = available[pd.notna(available["Distance km"])].copy()
    if not with_distance.empty:
        return with_distance.sort_values(
            ["Distance km", "Estimated Wait Time", "Price per kWh", "Rating"],
            ascending=[True, True, True, False],
        ).iloc[0]
    return available.sort_values(
        ["Estimated Wait Time", "Price per kWh", "Rating"],
        ascending=[True, True, False],
    ).iloc[0]


def add_notification(user_id, message):
    notifications = load_notifications()
    row = pd.DataFrame(
        [[
            "N-" + str(uuid.uuid4())[:8].upper(),
            user_id,
            message,
            now_ist().strftime("%Y-%m-%d %H:%M:%S"),
            "No",
        ]],
        columns=NOTIFICATION_COLUMNS,
    )
    save_notifications(pd.concat([notifications, row], ignore_index=True))


def update_station_counts(station_id, available_delta=0, occupied_delta=0, queue_delta=0):
    stations = load_stations()
    rows = stations[stations["Station ID"] == station_id]
    if rows.empty:
        return
    idx = rows.index[0]
    stations.loc[idx, "Available Chargers"] = max(0, int(to_number(stations.loc[idx, "Available Chargers"])) + available_delta)
    stations.loc[idx, "Occupied Chargers"] = max(0, int(to_number(stations.loc[idx, "Occupied Chargers"])) + occupied_delta)
    stations.loc[idx, "Queue Length"] = max(0, int(to_number(stations.loc[idx, "Queue Length"])) + queue_delta)
    save_stations(stations)


def mark_no_shows():
    reservations = load_reservations()
    if reservations.empty:
        return

    changed = False
    current_time = now_ist()
    for idx, row in reservations.iterrows():
        if row["Status"] != "Confirmed":
            continue
        if str(row.get("Arrived At", "")).strip():
            continue
        slot_text = str(row.get("Slot DateTime", "")).strip()
        if not slot_text:
            continue
        try:
            slot_time = datetime.strptime(slot_text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=APP_TIMEZONE)
        except Exception:
            continue
        if current_time > slot_time + timedelta(minutes=30):
            penalty = round(to_number(row["Charging Cost Estimate"]) * NO_SHOW_RATE, 2)
            reservations.loc[idx, "Status"] = "No Show"
            reservations.loc[idx, "No Show Penalty"] = penalty
            update_station_counts(row["Station ID"], available_delta=1, occupied_delta=-1)
            add_notification(row["User ID"], f"No-show penalty applied for {row['Station Name']}: {format_money(penalty)}")
            changed = True
    if changed:
        save_reservations(reservations)


# ==================================================
# UI HELPERS
# ==================================================
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


def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero-box">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def station_card(row):
    distance = ""
    if pd.notna(row.get("Distance km", pd.NA)):
        distance = f"<p><b>Distance:</b> {row['Distance km']} km</p>"
    st.markdown(
        f"""
        <div class="station-card">
            <span class="badge green">{row['Availability Status']}</span>
            <span class="badge cyan">{row['Charging Type']}</span>
            <span class="badge yellow">{row['Connector']}</span>
            <h3>{row['Station Name']}</h3>
            <p><b>Network:</b> {row['Network']} | <b>Area:</b> {row['Area']}</p>
            <p><b>Health:</b> {row['Health Status']} | <b>Rating:</b> {row['Rating']}</p>
            <p><b>Address:</b> {row['Address']}</p>
            <p><b>Amenities:</b> {row['Amenities']}</p>
            {distance}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# THEME
# ==================================================
st.markdown(
    """
    <style>
    :root {
        --bg: #020c08;
        --panel: #071a12;
        --panel2: #0b2519;
        --line: #234838;
        --accent: #55e09c;
        --accent2: #ff4b4b;
        --text: #f8fffb;
        --muted: #a8d8c4;
    }

    .stApp {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: var(--text) !important;
    }

    .hero-box {
        background: #0a2a1b;
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        padding: 42px 0;
        margin: 18px 0 26px 0;
    }

    .hero-box h1 {
        font-size: 42px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 0;
    }

    .hero-box p {
        color: var(--muted) !important;
        font-size: 18px;
        margin-top: 14px;
    }

    .metric-card {
        background: #07160f;
        border-top: 2px solid var(--accent);
        padding: 20px 16px;
        min-height: 118px;
        margin-bottom: 14px;
    }

    .metric-label {
        color: var(--muted) !important;
        font-size: 13px;
        font-weight: 900;
        text-transform: uppercase;
    }

    .metric-value {
        color: var(--text) !important;
        font-size: 32px;
        font-weight: 900;
        margin-top: 12px;
    }

    .metric-note {
        color: #bcead8 !important;
        font-size: 14px;
        margin-top: 6px;
    }

    .station-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 20px;
        margin: 14px 0;
    }

    .badge {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 900;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .green { background: var(--accent); color: #042015 !important; }
    .cyan { background: #174633; color: #d9fff0 !important; border: 1px solid #2e6d52; }
    .yellow { background: #304d26; color: #e6ffd1 !important; border: 1px solid #5d8b44; }

    section[data-testid="stSidebar"] {
        background: #06150f !important;
        border-right: 1px solid var(--line) !important;
    }

    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }

    .stTextInput input,
    .stNumberInput input,
    textarea,
    div[data-baseweb="select"] > div {
        background: #0b2418 !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        border: 1px solid #275540 !important;
        border-radius: 8px !important;
        min-height: 48px !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="select"] *,
    div[data-baseweb="popover"] *,
    ul[role="listbox"],
    ul[role="listbox"] * {
        background: #0b2418 !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }

    .stButton button,
    .stFormSubmitButton button,
    a[data-testid="stLinkButton"] {
        background: var(--accent) !important;
        color: #042015 !important;
        -webkit-text-fill-color: #042015 !important;
        border: none !important;
        border-radius: 8px !important;
        min-height: 48px !important;
        font-weight: 800 !important;
    }

    .stButton button *,
    .stFormSubmitButton button *,
    a[data-testid="stLinkButton"] * {
        color: #042015 !important;
        -webkit-text-fill-color: #042015 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #06150f !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-weight: 800 !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--accent2) !important;
        border-color: var(--accent2) !important;
    }

    div[data-testid="stDataFrame"] {
        background: #0b1016 !important;
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
    }

    .stAlert {
        border-radius: 8px !important;
    }

    @media (max-width: 700px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .hero-box h1 { font-size: 31px; }
        .metric-value { font-size: 26px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SESSION STATE
# ==================================================
defaults = {
    "logged_in": False,
    "user": None,
    "user_lat": None,
    "user_lon": None,
    "location_requested": False,
    "area_filter": "All",
    "network_filter": "All",
    "charger_filter": "All",
    "connector_filter": "All",
    "available_filter": "All",
    "open_filter": "All",
    "max_price": 30,
    "search_text": "",
    "nav_user": "Discover",
    "nav_host": "Overview",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

mark_no_shows()


# ==================================================
# LOGIN
# ==================================================
def show_login():
    st.markdown("<h3>VoltIQ Technologies Pvt. Ltd</h3>", unsafe_allow_html=True)
    st.markdown("<p>Smart EV Charging Availability, Reservation and Queue Management System</p>", unsafe_allow_html=True)
    hero("Charge faster. Wait less. Drive smarter.", "Find nearby stations, reserve slots, manage charging and track payments.")

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
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
                st.rerun()
        st.info("User Demo: user@demo.com / User@123")
        st.caption("Host Login: group 1 goated / shahid is goat")

    with signup_tab:
        name = st.text_input("Full Name")
        email = st.text_input("Email / Login ID")
        phone = st.text_input("Mobile Number")
        area = st.selectbox("Preferred Area", list(KNOWN_LOCATIONS.keys()))
        password = st.text_input("Create Password", type="password")
        if st.button("Create Account", use_container_width=True):
            users = load_users()
            if not name.strip() or not email.strip() or not phone.strip() or not password:
                st.error("Please fill all fields.")
            elif not phone.isdigit() or len(phone) != 10:
                st.error("Enter a valid 10-digit mobile number.")
            elif email.strip().lower() in users["Email"].str.lower().tolist():
                st.error("This login ID is already registered.")
            else:
                new_user = pd.DataFrame(
                    [[
                        "U-" + str(uuid.uuid4())[:8].upper(),
                        name.strip(),
                        email.strip().lower(),
                        hash_password(password),
                        phone.strip(),
                        "User",
                        area,
                        now_ist().strftime("%Y-%m-%d %H:%M:%S"),
                    ]],
                    columns=USER_COLUMNS,
                )
                save_users(pd.concat([users, new_user], ignore_index=True))
                st.success("Account created successfully. Please login.")


if not st.session_state.logged_in:
    show_login()
    st.stop()


user = st.session_state.user
user_id = user["User ID"]
is_host = user["Role"] == "Host"

top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.markdown("<h2>VoltIQ</h2>", unsafe_allow_html=True)
    st.markdown("<p>Find. Book. Charge.</p>", unsafe_allow_html=True)
with top_col2:
    st.write(f"{user['Name']} · {user['Role']}")


def logout_button():
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_lat = None
        st.session_state.user_lon = None
        st.rerun()


# ==================================================
# HOST DASHBOARD
# ==================================================
if is_host:
    st.sidebar.header("Navigation")
    nav = st.sidebar.radio(
        "Host pages",
        ["Overview", "Reservations", "Stations", "Users", "Analytics", "Finance"],
        key="nav_host",
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    logout_button()

    users = load_users()
    vehicles = load_vehicles()
    stations_raw = load_stations()
    reservations = load_reservations()
    sessions = load_sessions()
    stations = prepare_stations()

    if nav == "Overview":
        hero("Host Control Center", "Monitor users, vehicles, reservations, queues, charger status and station health.")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.container().markdown("")
        with c1:
            metric_card("Users", len(users[users["Role"] == "User"]), "registered")
        with c2:
            metric_card("Vehicles", len(vehicles), "saved")
        with c3:
            metric_card("Reservations", len(reservations), "total")
        with c4:
            active = len(reservations[reservations["Status"].isin(["Confirmed", "Queued", "Arrived", "Charging"])])
            metric_card("Active", active, "current")
        with c5:
            metric_card("Available", int(stations["Available Chargers"].sum()), "chargers")

    elif nav == "Reservations":
        hero("Reservations", "Cross-check bookings, arrivals, charging progress and no-show status.")
        if reservations.empty:
            st.info("No reservations yet.")
        else:
            display = reservations.merge(users[["User ID", "Name", "Email", "Phone"]], on="User ID", how="left")
            st.dataframe(display, use_container_width=True, hide_index=True)

    elif nav == "Stations":
        hero("Station Management", "Update live station availability and add new stations.")
        tab1, tab2 = st.tabs(["Update Station", "Add Station"])
        with tab1:
            if stations_raw.empty:
                st.info("No station data available.")
            else:
                station_choice = st.selectbox("Select Station", stations_raw["Station Name"].tolist())
                idx = stations_raw[stations_raw["Station Name"] == station_choice].index[0]
                row = stations_raw.loc[idx]
                with st.form("station_update_form"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        available = st.number_input("Available Chargers", min_value=0, value=int(to_number(row["Available Chargers"])))
                        queue = st.number_input("Queue Length", min_value=0, value=int(to_number(row["Queue Length"])))
                    with c2:
                        occupied = st.number_input("Occupied Chargers", min_value=0, value=int(to_number(row["Occupied Chargers"])))
                        price = st.number_input("Price per kWh", min_value=1, value=int(to_number(row["Price per kWh"])))
                    with c3:
                        faulty = st.number_input("Faulty Chargers", min_value=0, value=int(to_number(row["Faulty Chargers"])))
                        rating = st.number_input("Rating", min_value=1.0, max_value=5.0, value=float(to_number(row["Rating"])), step=0.1)
                    submit = st.form_submit_button("Update Station", use_container_width=True)
                if submit:
                    total = int(to_number(row["Total Chargers"]))
                    if available + occupied + faulty != total:
                        st.error("Available + Occupied + Faulty must equal Total Chargers.")
                    else:
                        stations_raw.loc[idx, "Available Chargers"] = available
                        stations_raw.loc[idx, "Occupied Chargers"] = occupied
                        stations_raw.loc[idx, "Faulty Chargers"] = faulty
                        stations_raw.loc[idx, "Queue Length"] = queue
                        stations_raw.loc[idx, "Price per kWh"] = price
                        stations_raw.loc[idx, "Rating"] = rating
                        save_stations(stations_raw)
                        st.success("Station updated.")
                        st.rerun()
                st.dataframe(stations_raw, use_container_width=True, hide_index=True)
        with tab2:
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
                    available = st.number_input("Available", min_value=0, value=2)
                    occupied = st.number_input("Occupied", min_value=0, value=2)
                    faulty = st.number_input("Faulty", min_value=0, value=0)
                    queue = st.number_input("Queue Length", min_value=0, value=0)
                    price = st.number_input("Price per kWh", min_value=1, value=20)
                    rating = st.number_input("Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.1)
                open_24 = st.selectbox("Open 24x7", ["Yes", "No"])
                amenities = st.text_input("Amenities", value="Parking, Food")
                lat = st.number_input("Latitude", value=17.3850, format="%.6f")
                lon = st.number_input("Longitude", value=78.4867, format="%.6f")
                add = st.form_submit_button("Add Station", use_container_width=True)
            if add:
                if not name.strip() or not area.strip() or not address.strip():
                    st.error("Station name, area and address are required.")
                elif available + occupied + faulty != total:
                    st.error("Available + Occupied + Faulty must equal Total Chargers.")
                else:
                    new_station = pd.DataFrame(
                        [[
                            "SC-" + str(uuid.uuid4())[:8].upper(),
                            name.strip(),
                            network.strip(),
                            city.strip(),
                            area.strip(),
                            address.strip(),
                            charging_type,
                            connector,
                            total,
                            available,
                            occupied,
                            faulty,
                            queue,
                            price,
                            rating,
                            open_24,
                            amenities.strip(),
                            lat,
                            lon,
                        ]],
                        columns=STATION_COLUMNS,
                    )
                    save_stations(pd.concat([stations_raw, new_station], ignore_index=True))
                    st.success("Station added.")
                    st.rerun()

    elif nav == "Users":
        hero("Users and Vehicles", "View registered users and saved EV details.")
        st.subheader("Registered users")
        st.dataframe(users.drop(columns=["Password Hash"], errors="ignore"), use_container_width=True, hide_index=True)
        st.subheader("Saved vehicles")
        st.dataframe(vehicles, use_container_width=True, hide_index=True)

    elif nav == "Analytics":
        hero("Analytics", "Overview of booking status and station load.")
        if not reservations.empty:
            status_chart = reservations["Status"].value_counts().reset_index()
            status_chart.columns = ["Status", "Count"]
            st.bar_chart(status_chart.set_index("Status"))
        station_chart = stations[["Station Name", "Available Chargers", "Occupied Chargers", "Queue Length"]].set_index("Station Name")
        st.bar_chart(station_chart)

    elif nav == "Finance":
        hero("Finance dashboard", "Track online collections, VoltIQ earnings and monthly station-owner settlements.")
        if sessions.empty:
            c1, c2, c3, c4, c5 = st.columns(5)
            for col, label in zip(c1, ["Online Collected"]):
                pass
            with c1:
                metric_card("Online Collected", "Rs. 0", "money received by VoltIQ")
            with c2:
                metric_card("Monthly Payout", "Rs. 0", "payable to station owners")
            with c3:
                metric_card("Reservation Fee", "Rs. 0", "10 percent")
            with c4:
                metric_card("Priority Fee", "Rs. 0", "optional Rs. 40 add-on")
            with c5:
                metric_card("VoltIQ Earnings", "Rs. 0", "fees + station commission")
            st.info("No completed charging sessions yet.")
        else:
            for col in ["Total Payable", "Station Owner Payout", "Reservation Fee", "Priority Fee", "VoltIQ Earnings"]:
                sessions[col] = pd.to_numeric(sessions[col], errors="coerce").fillna(0)
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                metric_card("Online Collected", format_money(sessions["Total Payable"].sum()), "money received by VoltIQ")
            with c2:
                metric_card("Monthly Payout", format_money(sessions["Station Owner Payout"].sum()), "payable to station owners")
            with c3:
                metric_card("Reservation Fee", format_money(sessions["Reservation Fee"].sum()), "10 percent")
            with c4:
                metric_card("Priority Fee", format_money(sessions["Priority Fee"].sum()), "optional Rs. 40 add-on")
            with c5:
                metric_card("VoltIQ Earnings", format_money(sessions["VoltIQ Earnings"].sum()), "fees + station commission")

            st.subheader("Monthly station-owner settlement")
            settlement = sessions.groupby(["Settlement Month", "Station Name"], dropna=False)[
                ["Charging Cost", "Station Commission", "Station Owner Payout", "Reservation Fee", "Priority Fee", "Total Payable", "VoltIQ Earnings"]
            ].sum().reset_index()
            st.dataframe(settlement, use_container_width=True, hide_index=True)

            no_show = reservations[reservations["Status"] == "No Show"].copy()
            st.subheader("No-show fees and cancelled bookings")
            if no_show.empty:
                st.info("No no-show bookings yet.")
            else:
                st.dataframe(no_show, use_container_width=True, hide_index=True)

    st.stop()


# ==================================================
# USER DASHBOARD
# ==================================================
st.sidebar.header("Navigation")
nav = st.sidebar.radio(
    "User pages",
    ["Discover", "Book", "My trips", "Garage", "Charging", "Notifications", "Profile"],
    key="nav_user",
    label_visibility="collapsed",
)
st.sidebar.divider()
logout_button()

stations = prepare_stations()
vehicles = load_vehicles()
reservations = load_reservations()

if nav == "Discover":
    hero("User Charging Dashboard", "Search stations, find the closest available charger and navigate with confidence.")

    st.subheader("Location")
    loc1, loc2 = st.columns(2)
    with loc1:
        manual_area = st.selectbox("Select Your Area", list(KNOWN_LOCATIONS.keys()))
        if st.button("Use Selected Area", use_container_width=True):
            st.session_state.user_lat, st.session_state.user_lon = KNOWN_LOCATIONS[manual_area]
            st.rerun()
    with loc2:
        if st.button("Allow Browser Location", use_container_width=True):
            st.session_state.location_requested = True
        if st.session_state.location_requested:
            if get_geolocation is None:
                st.warning("Browser location is unavailable. Use manual area selection.")
            else:
                lat, lon = extract_location(get_geolocation())
                if lat is not None and lon is not None:
                    st.session_state.user_lat = float(lat)
                    st.session_state.user_lon = float(lon)
                    st.session_state.location_requested = False
                    st.rerun()
                else:
                    st.info("Allow browser location permission or use manual selection.")

    st.sidebar.header("Filters")
    st.sidebar.selectbox("Area", ["All"] + sorted(stations["Area"].dropna().unique().tolist()), key="area_filter")
    st.sidebar.selectbox("Network", ["All"] + sorted(stations["Network"].dropna().unique().tolist()), key="network_filter")
    st.sidebar.selectbox("Charging Type", ["All"] + sorted(stations["Charging Type"].dropna().unique().tolist()), key="charger_filter")
    st.sidebar.selectbox("Connector", ["All"] + sorted(stations["Connector"].dropna().unique().tolist()), key="connector_filter")
    st.sidebar.selectbox("Availability", ["All", "Available Only"], key="available_filter")
    st.sidebar.selectbox("Operating Hours", ["All", "Open 24x7"], key="open_filter")
    st.sidebar.slider("Maximum Price per kWh", 10, 30, 30, key="max_price")
    st.sidebar.text_input("Search", key="search_text")

    filtered = apply_filters(stations)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Stations", len(filtered), "found")
    with c2:
        metric_card("Available", int(filtered["Available Chargers"].sum()) if not filtered.empty else 0, "chargers")
    with c3:
        metric_card("Queue", int(filtered["Queue Length"].sum()) if not filtered.empty else 0, "vehicles")
    with c4:
        metric_card("Avg Price", format_money(filtered["Price per kWh"].mean() if not filtered.empty else 0), "per kWh")
    with c5:
        closest = best_station(filtered)
        dist = "Set location"
        if closest is not None and pd.notna(closest["Distance km"]):
            dist = f"{closest['Distance km']} km"
        metric_card("Closest", dist, "available")

    st.subheader("Closest available charger")
    closest = best_station(filtered)
    if closest is None:
        st.warning("No available charger found. Try changing filters.")
    else:
        station_card(closest)
        st.link_button("Open in Google Maps", closest["Maps Link"])

    st.subheader("All matching stations")
    if filtered.empty:
        st.info("No station data to show.")
    else:
        display = filtered.sort_values("Distance km", na_position="last") if "Distance km" in filtered.columns else filtered
        for _, row in display.iterrows():
            station_card(row)
            a, b, c, d = st.columns(4)
            a.metric("Available", int(row["Available Chargers"]))
            b.metric("Queue", int(row["Queue Length"]))
            c.metric("Wait", f"{int(row['Estimated Wait Time'])} min")
            d.metric("Price", f"Rs. {int(row['Price per kWh'])}/kWh")

elif nav == "Book":
    hero("Reserve a charging slot", "Select station, vehicle, slot and review the total price breakdown before booking.")
    stations = prepare_stations()
    filtered = stations.copy()
    if filtered.empty:
        st.warning("No stations available.")
    else:
        station_name = st.selectbox("Charging Station", filtered["Station Name"].tolist())
        selected_station = filtered[filtered["Station Name"] == station_name].iloc[0]

        user_vehicles = vehicles[vehicles["User ID"] == user_id]
        if user_vehicles.empty:
            st.warning("No saved vehicle found. You can enter vehicle details now or save it in Garage.")
            vehicle_number = st.text_input("Vehicle Number")
            ev_model = st.selectbox("EV Model", EV_MODELS)
            battery_capacity = st.number_input("Battery Capacity kWh", min_value=10, max_value=150, value=40)
        else:
            vehicle_choice = st.selectbox("Saved Vehicle", user_vehicles["Vehicle Number"].tolist())
            vehicle = user_vehicles[user_vehicles["Vehicle Number"] == vehicle_choice].iloc[0]
            vehicle_number = vehicle["Vehicle Number"]
            ev_model = vehicle["EV Model"]
            battery_capacity = int(to_number(vehicle["Battery Capacity kWh"], 40))
            st.write(f"EV Model: {ev_model}")

        driver_name = st.text_input("Driver Name", value=user["Name"])
        mobile = st.text_input("Mobile Number", value=user["Phone"])

        date_options = get_booking_date_options()
        if not date_options:
            st.error("No booking slots are available right now. Please try again tomorrow.")
            st.stop()
        booking_date = st.selectbox("Date", date_options, key="booking_date_select")
        time_options = get_time_options_for_date(booking_date)
        booking_time = st.selectbox("Start time", time_options, key="booking_time_select")
        duration = st.selectbox("Duration", ["30 minutes", "1 hour", "1.5 hours", "2 hours"], key="booking_duration_select")

        b1, b2 = st.columns(2)
        with b1:
            current_battery = st.slider("Current battery", 0, 100, 20)
        with b2:
            target_battery = st.slider("Target battery", 1, 100, 80)

        priority = st.checkbox("Add priority booking for Rs. 40")
        agree = st.checkbox("Join the queue automatically if this time slot becomes full", value=True)

        estimated_kwh = estimate_kwh(
            duration,
            selected_station["Charging Type"],
            current_battery,
            target_battery,
            battery_capacity,
        )
        charges = calculate_charges(estimated_kwh, selected_station["Price per kWh"], priority=priority)

        st.subheader("Price breakdown")
        p1, p2, p3, p4, p5 = st.columns(5)
        with p1:
            metric_card("Charging Amount", format_money(charges["charging_cost"]), f"{estimated_kwh} kWh")
        with p2:
            metric_card("Reservation Fee", format_money(charges["reservation_fee"]), "10%")
        with p3:
            metric_card("Priority Fee", format_money(charges["priority_fee"]), "optional")
        with p4:
            metric_card("No-show Penalty", format_money(charges["charging_cost"] * NO_SHOW_RATE), "only after 30 min")
        with p5:
            metric_card("Total Payable", format_money(charges["total_payable"]), "before charging")

        if st.button("Confirm reservation", type="primary", use_container_width=True):
            reservations = load_reservations()
            stations_raw = load_stations()
            vehicle_number = vehicle_number.strip().upper()
            mobile = str(mobile).strip()

            duplicate = reservations[
                (reservations["Vehicle Number"] == vehicle_number)
                & (reservations["Status"].isin(["Confirmed", "Queued", "Arrived", "Charging"]))
            ]

            if not vehicle_number or not ev_model or not mobile:
                st.error("Please fill vehicle and mobile details.")
            elif not mobile.isdigit() or len(mobile) != 10:
                st.error("Enter a valid 10-digit mobile number.")
            elif not agree:
                st.error("Please accept queue condition.")
            elif not duplicate.empty:
                st.warning("This vehicle already has an active booking.")
            else:
                station_id = selected_station["Station ID"]
                station_rows = stations_raw[stations_raw["Station ID"] == station_id]
                if station_rows.empty:
                    st.error("Station not found.")
                else:
                    sidx = station_rows.index[0]
                    available = int(to_number(stations_raw.loc[sidx, "Available Chargers"]))
                    if available > 0:
                        status = "Confirmed"
                        stations_raw.loc[sidx, "Available Chargers"] = available - 1
                        stations_raw.loc[sidx, "Occupied Chargers"] = int(to_number(stations_raw.loc[sidx, "Occupied Chargers"])) + 1
                    else:
                        status = "Queued"
                        stations_raw.loc[sidx, "Queue Length"] = int(to_number(stations_raw.loc[sidx, "Queue Length"])) + 1

                    slot_dt = parse_slot_datetime(booking_date, booking_time)
                    new_res = pd.DataFrame(
                        [[
                            "VQ-" + now_ist().strftime("%Y%m%d%H%M%S") + "-" + str(uuid.uuid4())[:4].upper(),
                            user_id,
                            driver_name.strip(),
                            vehicle_number,
                            ev_model,
                            mobile,
                            station_id,
                            selected_station["Station Name"],
                            booking_date,
                            booking_time,
                            slot_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            duration,
                            "Yes" if priority else "No",
                            status,
                            charges["charging_cost"],
                            charges["reservation_fee"],
                            charges["priority_fee"],
                            charges["total_payable"],
                            0,
                            now_ist().strftime("%Y-%m-%d %H:%M:%S"),
                            "",
                            "",
                            "",
                        ]],
                        columns=RESERVATION_COLUMNS,
                    )
                    save_reservations(pd.concat([reservations, new_res], ignore_index=True))
                    save_stations(stations_raw)
                    add_notification(user_id, f"Reservation {status.lower()} for {selected_station['Station Name']} at {booking_date} {booking_time}.")
                    st.success(f"Reservation {status.lower()} successfully.")
                    st.rerun()

elif nav == "My trips":
    hero("My trips", "Track all reservations, status and payment estimates.")
    my_res = reservations[reservations["User ID"] == user_id].copy()
    if my_res.empty:
        st.info("No reservations yet.")
    else:
        st.dataframe(my_res, use_container_width=True, hide_index=True)

elif nav == "Garage":
    hero("Garage", "Save EV details for faster booking.")
    my_vehicles = vehicles[vehicles["User ID"] == user_id]
    if not my_vehicles.empty:
        st.dataframe(my_vehicles, use_container_width=True, hide_index=True)
    with st.form("vehicle_form"):
        vehicle_number = st.text_input("Vehicle Number")
        ev_model = st.selectbox("EV Model", EV_MODELS)
        connector = st.selectbox("Connector", ["CCS2", "Type 2", "CHAdeMO"])
        battery = st.number_input("Battery Capacity kWh", min_value=10, max_value=150, value=40)
        submit = st.form_submit_button("Save Vehicle", use_container_width=True)
    if submit:
        vehicle_number = vehicle_number.strip().upper()
        duplicate = vehicles[(vehicles["User ID"] == user_id) & (vehicles["Vehicle Number"] == vehicle_number)]
        if not vehicle_number:
            st.error("Vehicle number is required.")
        elif not duplicate.empty:
            st.error("This vehicle is already saved.")
        else:
            new_vehicle = pd.DataFrame(
                [[
                    "VH-" + str(uuid.uuid4())[:8].upper(),
                    user_id,
                    vehicle_number,
                    ev_model,
                    connector,
                    battery,
                    now_ist().strftime("%Y-%m-%d %H:%M:%S"),
                ]],
                columns=VEHICLE_COLUMNS,
            )
            save_vehicles(pd.concat([vehicles, new_vehicle], ignore_index=True))
            st.success("Vehicle saved.")
            st.rerun()

elif nav == "Charging":
    hero("Charging control", "Mark arrival, start charging and finish with final payable amount.")
    my_active = reservations[
        (reservations["User ID"] == user_id)
        & (reservations["Status"].isin(["Confirmed", "Arrived", "Charging"]))
    ].copy()
    if my_active.empty:
        st.info("No active confirmed booking found.")
    else:
        options = [
            f"{row['Reservation ID']} | {row['Station Name']} | {row['Vehicle Number']} | {row['Date']} {row['Time']}"
            for _, row in my_active.iterrows()
        ]
        selected = st.selectbox("Select active reservation", options)
        selected_id = selected.split(" | ")[0]
        reservations = load_reservations()
        rows = reservations[reservations["Reservation ID"] == selected_id]
        if rows.empty:
            st.error("Reservation not found.")
        else:
            ridx = rows.index[0]
            row = reservations.loc[ridx]
            st.subheader(f"{row['Station Name']} · {row['Vehicle Number']} · {row['Slot DateTime']}")
            slot_time = None
            try:
                slot_time = datetime.strptime(row["Slot DateTime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=APP_TIMEZONE)
                st.caption(f"Arrival deadline for avoiding no-show: {(slot_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M')}")
            except Exception:
                pass

            if row["Status"] == "Confirmed":
                if st.button("I have arrived", use_container_width=True):
                    reservations.loc[ridx, "Status"] = "Arrived"
                    reservations.loc[ridx, "Arrived At"] = now_ist().strftime("%Y-%m-%d %H:%M:%S")
                    save_reservations(reservations)
                    st.success("Arrival marked.")
                    st.rerun()
            elif row["Status"] == "Arrived":
                if st.button("Start charging", use_container_width=True):
                    reservations.loc[ridx, "Status"] = "Charging"
                    reservations.loc[ridx, "Started At"] = now_ist().strftime("%Y-%m-%d %H:%M:%S")
                    save_reservations(reservations)
                    st.success("Charging started.")
                    st.rerun()
            elif row["Status"] == "Charging":
                station_rows = stations[stations["Station ID"] == row["Station ID"]]
                price = to_number(station_rows.iloc[0]["Price per kWh"] if not station_rows.empty else 20)
                energy = st.number_input("Energy delivered (kWh)", min_value=1.0, max_value=150.0, value=10.0, step=0.5)
                priority = str(row["Priority Booking"]) == "Yes"
                charges = calculate_charges(energy, price, priority=priority)
                st.subheader("Final Price Breakdown")
                f1, f2, f3, f4, f5 = st.columns(5)
                with f1:
                    metric_card("Charging Amount", format_money(charges["charging_cost"]), f"{energy} kWh")
                with f2:
                    metric_card("Reservation Fee", format_money(charges["reservation_fee"]), "10%")
                with f3:
                    metric_card("Priority Fee", format_money(charges["priority_fee"]), "Optional")
                with f4:
                    metric_card("Station Payout", format_money(charges["station_payout"]), "Monthly settlement")
                with f5:
                    metric_card("Final Payable", format_money(charges["total_payable"]), "Total")
                if st.button("Finish charging", use_container_width=True):
                    sessions = load_sessions()
                    completed_at = now_ist().strftime("%Y-%m-%d %H:%M:%S")
                    new_session = pd.DataFrame(
                        [[
                            "CS-" + str(uuid.uuid4())[:8].upper(),
                            row["Reservation ID"],
                            row["User ID"],
                            row["Station ID"],
                            row["Station Name"],
                            row["Vehicle Number"],
                            energy,
                            price,
                            charges["charging_cost"],
                            charges["reservation_fee"],
                            charges["priority_fee"],
                            charges["no_show_penalty"],
                            charges["station_commission"],
                            charges["station_payout"],
                            charges["total_payable"],
                            charges["voltiq_earnings"],
                            now_ist().strftime("%Y-%m"),
                            row["Started At"],
                            completed_at,
                        ]],
                        columns=SESSION_COLUMNS,
                    )
                    reservations.loc[ridx, "Status"] = "Completed"
                    reservations.loc[ridx, "Completed At"] = completed_at
                    reservations.loc[ridx, "Charging Cost Estimate"] = charges["charging_cost"]
                    reservations.loc[ridx, "Reservation Fee"] = charges["reservation_fee"]
                    reservations.loc[ridx, "Priority Fee"] = charges["priority_fee"]
                    reservations.loc[ridx, "Estimated Payable"] = charges["total_payable"]
                    save_reservations(reservations)
                    save_sessions(pd.concat([sessions, new_session], ignore_index=True))
                    update_station_counts(row["Station ID"], available_delta=1, occupied_delta=-1)
                    add_notification(user_id, f"Charging completed at {row['Station Name']}. Final payable: {format_money(charges['total_payable'])}.")
                    st.success("Charging completed.")
                    st.rerun()

elif nav == "Notifications":
    hero("Notifications", "Booking, charging and no-show updates.")
    notifications = load_notifications()
    mine = notifications[notifications["User ID"] == user_id].copy()
    if mine.empty:
        st.info("No notifications.")
    else:
        st.dataframe(mine.sort_values("Created At", ascending=False), use_container_width=True, hide_index=True)

elif nav == "Profile":
    hero("Profile", "Manage account information.")
    users = load_users()
    with st.form("profile_form"):
        name = st.text_input("Name", value=user["Name"])
        phone = st.text_input("Phone", value=user["Phone"])
        area = st.selectbox("Preferred Area", list(KNOWN_LOCATIONS.keys()), index=list(KNOWN_LOCATIONS.keys()).index(user["Preferred Area"]) if user["Preferred Area"] in KNOWN_LOCATIONS else 0)
        submit = st.form_submit_button("Update Profile", use_container_width=True)
    if submit:
        if not name.strip() or not phone.strip():
            st.error("Name and phone are required.")
        elif not phone.isdigit() or len(phone) != 10:
            st.error("Enter a valid 10-digit mobile number.")
        else:
            idx = users[users["User ID"] == user_id].index[0]
            users.loc[idx, "Name"] = name.strip()
            users.loc[idx, "Phone"] = phone.strip()
            users.loc[idx, "Preferred Area"] = area
            save_users(users)
            st.session_state.user = users.loc[idx].to_dict()
            st.success("Profile updated.")
            st.rerun()
