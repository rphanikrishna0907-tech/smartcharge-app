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
# PAGE SETUP
# ==================================================
st.set_page_config(
    page_title="VoltIQ Technologies Pvt. Ltd",
    page_icon="⚡",
    layout="wide",
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
VEHICLES_FILE = os.path.join(DATA_DIR, "vehicles.csv")
STATIONS_FILE = os.path.join(DATA_DIR, "stations.csv")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.csv")

HOST_LOGIN = "group 1 goated"
HOST_PASSWORD = "shahid is goat"

DEMO_LOGIN = "user@demo.com"
DEMO_PASSWORD = "User@123"


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
    "Station ID", "Station Name", "Network", "Area", "Address",
    "Charging Type", "Connector", "Total Chargers", "Available Chargers",
    "Occupied Chargers", "Faulty Chargers", "Queue Length",
    "Price per kWh", "Rating", "Open 24x7", "Amenities",
    "Latitude", "Longitude"
]

RESERVATION_COLUMNS = [
    "Reservation ID", "User ID", "Driver Name", "Vehicle Number",
    "EV Model", "Mobile Number", "Station ID", "Station Name",
    "Date", "Time", "Duration", "Status", "Created At"
]


# ==================================================
# DEFAULT DATA
# ==================================================
LOCATIONS = {
    "Hyderabad": (17.3850, 78.4867),
    "Gachibowli": (17.4401, 78.3489),
    "Hitech City": (17.4504, 78.3805),
    "Madhapur": (17.4483, 78.3915),
    "Kukatpally": (17.4933, 78.3996),
    "Begumpet": (17.4435, 78.4622),
    "Durgam Cheruvu": (17.4309, 78.3894),
    "Miyapur": (17.4964, 78.3611),
    "BHEL": (17.4948, 78.3053),
    "Financial District": (17.4149, 78.3422),
    "Kondapur": (17.4698, 78.3578),
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
        DEMO_LOGIN,
        hashlib.sha256(DEMO_PASSWORD.encode()).hexdigest(),
        "8888888888",
        "User",
        "Gachibowli",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ],
]

DEFAULT_STATIONS = [
    ["SC001", "Tata Power EZ Charge - Begumpet", "Tata Power", "Begumpet", "Begumpet, Hyderabad", "DC Fast Charging", "CCS2", 4, 2, 1, 1, 1, 22, 4.2, "No", "Parking, Service Center", 17.4435, 78.4622],
    ["SC002", "Statiq EV Charging - Kukatpally", "Statiq", "Kukatpally", "Kukatpally, Hyderabad", "DC Fast Charging", "CCS2", 4, 1, 2, 1, 3, 21, 4.1, "Yes", "Parking, Food", 17.4933, 78.3996],
    ["SC003", "ChargeZone Hub - Hitech City", "ChargeZone", "Hitech City", "Hitech City, Hyderabad", "DC Fast Charging", "CCS2", 5, 2, 3, 0, 1, 22, 4.5, "Yes", "Parking, Food, Restroom", 17.4504, 78.3805],
    ["SC004", "Jio-bp Pulse - Madhapur", "Jio-bp", "Madhapur", "Madhapur, Hyderabad", "DC Fast Charging", "CCS2", 4, 0, 4, 0, 4, 23, 4.0, "Yes", "Parking, Food", 17.4483, 78.3915],
    ["SC005", "GLIDA Green Drive - Gachibowli", "GLIDA", "Gachibowli", "Gachibowli, Hyderabad", "DC Fast Charging", "CCS2", 6, 4, 2, 0, 0, 20, 4.4, "Yes", "Parking, Restroom, Food", 17.4401, 78.3489],
    ["SC006", "Public EV Point - Durgam Cheruvu", "Public EV", "Durgam Cheruvu", "Durgam Cheruvu, Hyderabad", "AC Charging", "Type 2", 3, 1, 1, 1, 1, 17, 3.9, "No", "Parking", 17.4309, 78.3894],
    ["SC007", "Tata Power EZ Charge - Miyapur", "Tata Power", "Miyapur", "Miyapur Metro Station, Hyderabad", "AC Charging", "Type 2", 3, 1, 2, 0, 2, 18, 4.0, "No", "Parking, Metro Access", 17.4964, 78.3611],
    ["SC008", "Public EV Station - BHEL", "Public EV", "BHEL", "BHEL, Hyderabad", "AC Charging", "Type 2", 4, 2, 2, 0, 1, 16, 4.0, "No", "Parking", 17.4948, 78.3053],
    ["SC009", "VoltIQ FastCharge - Financial District", "VoltIQ", "Financial District", "Financial District, Hyderabad", "DC Fast Charging", "CCS2", 8, 5, 3, 0, 0, 19, 4.6, "Yes", "Parking, Food, Restroom", 17.4149, 78.3422],
    ["SC010", "VoltIQ ChargePoint - Kondapur", "VoltIQ", "Kondapur", "Kondapur, Hyderabad", "AC Charging", "Type 2", 4, 2, 2, 0, 1, 17, 4.2, "No", "Parking, Food", 17.4698, 78.3578],
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

    df = df[columns]

    if df.empty and default_rows:
        df = pd.DataFrame(default_rows, columns=columns)
        save_df(df, path)

    return df


def load_users():
    users = load_df(USERS_FILE, USER_COLUMNS, DEFAULT_USERS)

    host_hash = hashlib.sha256(HOST_PASSWORD.encode()).hexdigest()

    if "U-ADMIN" not in users["User ID"].tolist():
        host = pd.DataFrame([DEFAULT_USERS[0]], columns=USER_COLUMNS)
        users = pd.concat([host, users], ignore_index=True)

    host_index = users[users["User ID"] == "U-ADMIN"].index[0]
    users.at[host_index, "Email"] = HOST_LOGIN
    users.at[host_index, "Password Hash"] = host_hash
    users.at[host_index, "Role"] = "Host"

    if "U-DEMO" not in users["User ID"].tolist():
        demo = pd.DataFrame([DEFAULT_USERS[1]], columns=USER_COLUMNS)
        users = pd.concat([users, demo], ignore_index=True)

    save_df(users, USERS_FILE)
    return users


def load_vehicles():
    return load_df(VEHICLES_FILE, VEHICLE_COLUMNS, [])


def load_stations():
    return load_df(STATIONS_FILE, STATION_COLUMNS, DEFAULT_STATIONS)


def load_reservations():
    return load_df(RESERVATIONS_FILE, RESERVATION_COLUMNS, [])


def save_users(df):
    save_df(df, USERS_FILE)


def save_vehicles(df):
    save_df(df, VEHICLES_FILE)


def save_stations(df):
    save_df(df, STATIONS_FILE)


def save_reservations(df):
    save_df(df, RESERVATIONS_FILE)


# ==================================================
# HELPER FUNCTIONS
# ==================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def make_numeric(df):
    cols = [
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

    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def reset_filters():
    st.session_state.area_filter = "All"
    st.session_state.available_filter = "All"
    st.session_state.charger_filter = "All"
    st.session_state.connector_filter = "All"
    st.session_state.search_text = ""


def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(radius * c, 2)


def wait_time(queue, charging_type):
    queue = int(queue)
    return queue * 30 if charging_type == "DC Fast Charging" else queue * 55


def availability_text(available):
    available = int(available)

    if available >= 3:
        return "Good Availability"

    if available >= 1:
        return "Limited Availability"

    return "Currently Full"


def health_text(total, faulty):
    total = int(total)
    faulty = int(faulty)

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


def get_stations_ready():
    df = load_stations().copy()

    if df.empty:
        df = pd.DataFrame(DEFAULT_STATIONS, columns=STATION_COLUMNS)
        save_stations(df)

    df = make_numeric(df)

    df["Estimated Wait Time"] = df.apply(
        lambda row: wait_time(row["Queue Length"], row["Charging Type"]),
        axis=1,
    )

    df["Availability Status"] = df["Available Chargers"].apply(availability_text)

    df["Health Status"] = df.apply(
        lambda row: health_text(row["Total Chargers"], row["Faulty Chargers"]),
        axis=1,
    )

    df["Maps Link"] = df.apply(
        lambda row: f"https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}",
        axis=1,
    )

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


def find_best_station(df):
    if df.empty:
        return None

    available = df[df["Available Chargers"] > 0].copy()

    if available.empty:
        return None

    distance_df = available[pd.notna(available["Distance km"])].copy()

    if not distance_df.empty:
        return distance_df.sort_values(
            ["Distance km", "Estimated Wait Time", "Price per kWh", "Rating"],
            ascending=[True, True, True, False],
        ).iloc[0]

    return available.sort_values(
        ["Estimated Wait Time", "Price per kWh", "Rating"],
        ascending=[True, True, False],
    ).iloc[0]


def apply_filters(df):
    filtered = df.copy()

    if st.session_state.area_filter != "All":
        filtered = filtered[filtered["Area"] == st.session_state.area_filter]

    if st.session_state.available_filter == "Available Only":
        filtered = filtered[filtered["Available Chargers"] > 0]

    if st.session_state.charger_filter != "All":
        filtered = filtered[filtered["Charging Type"] == st.session_state.charger_filter]

    if st.session_state.connector_filter != "All":
        filtered = filtered[filtered["Connector"] == st.session_state.connector_filter]

    search = st.session_state.search_text.strip()

    if search:
        filtered = filtered[
            filtered["Station Name"].str.contains(search, case=False, na=False)
            | filtered["Network"].str.contains(search, case=False, na=False)
            | filtered["Area"].str.contains(search, case=False, na=False)
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


def station_card(row):
    st.markdown(
        f"""
        <div class="station-card">
            <span class="badge green">{row["Availability Status"]}</span>
            <span class="badge blue">{row["Charging Type"]}</span>
            <span class="badge orange">{row["Connector"]}</span>
            <h3>{row["Station Name"]}</h3>
            <p><b>Network:</b> {row["Network"]} | <b>Area:</b> {row["Area"]} | <b>Health:</b> {row["Health Status"]}</p>
            <p><b>Address:</b> {row["Address"]}</p>
            <p><b>Amenities:</b> {row["Amenities"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# STYLE
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07111F 0%, #0B1F3A 55%, #102A43 100%);
        color: #F8FAFC;
    }

    .title {
        font-size: 42px;
        font-weight: 900;
        color: white;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 17px;
        color: #C7D2FE;
        font-weight: 600;
        margin-bottom: 18px;
    }

    .hero, .station-card, .metric-card {
        background: #FFFFFF;
        color: #0F172A;
        border: 1px solid #CBD5E1;
        border-radius: 24px;
        box-shadow: 0 16px 35px rgba(0,0,0,0.22);
    }

    .hero {
        padding: 24px;
        margin-bottom: 24px;
    }

    .hero h2 {
        color: #0F172A;
        margin-top: 0;
    }

    .hero p, .station-card p {
        color: #334155;
        font-weight: 500;
    }

    .metric-card {
        padding: 18px;
        min-height: 105px;
        margin-bottom: 10px;
    }

    .metric-label {
        color: #475569;
        font-size: 12px;
        font-weight: 900;
        text-transform: uppercase;
    }

    .metric-value {
        color: #0F172A;
        font-size: 30px;
        font-weight: 900;
    }

    .metric-note {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
    }

    .station-card {
        padding: 20px;
        margin-bottom: 16px;
    }

    .station-card h3 {
        color: #0F172A;
        font-weight: 900;
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

    .green {background: #DCFCE7; color: #166534;}
    .blue {background: #DBEAFE; color: #1D4ED8;}
    .orange {background: #FFEDD5; color: #C2410C;}

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #EAF6FF 100%);
    }

    section[data-testid="stSidebar"] * {
        color: #0F172A !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: white;
        color: #0F172A;
        border-radius: 14px;
        margin-right: 6px;
        font-weight: 800;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06B6D4, #2563EB) !important;
        color: white !important;
    }

    .stButton button {
        border-radius: 12px;
        font-weight: 800;
    }

    @media (max-width: 700px) {
        .title {font-size: 30px;}
        .hero {padding: 16px;}
        .metric-value {font-size: 24px;}
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
    "area_filter": "All",
    "available_filter": "All",
    "charger_filter": "All",
    "connector_filter": "All",
    "search_text": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# LOGIN PAGE
# ==================================================
if not st.session_state.logged_in:
    st.markdown('<div class="title">⚡ VoltIQ Technologies Pvt. Ltd</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">EV Charging Availability and Reservation System</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hero">
            <h2>One App. Two Logins.</h2>
            <p>User can register, save vehicle and reserve a charging slot. Host can view all users, vehicles and reservations in the same website.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

        st.info("Demo User: user@demo.com / User@123")
        st.caption("Host Login: group 1 goated / shahid is goat")

    with signup_tab:
        name = st.text_input("Full Name")
        signup_email = st.text_input("Email / Login ID")
        phone = st.text_input("Mobile Number")
        area = st.selectbox("Preferred Area", list(LOCATIONS.keys()))
        signup_password = st.text_input("Create Password", type="password")

        if st.button("Create Account", use_container_width=True):
            users = load_users()

            if not name.strip() or not signup_email.strip() or not phone.strip() or not signup_password:
                st.error("Fill all fields.")
            elif not phone.isdigit() or len(phone) != 10:
                st.error("Enter valid 10-digit mobile number.")
            elif signup_email.strip().lower() in users["Email"].str.lower().tolist():
                st.error("This login ID already exists.")
            else:
                new_user = pd.DataFrame(
                    [[
                        "U-" + str(uuid.uuid4())[:8].upper(),
                        name.strip(),
                        signup_email.strip().lower(),
                        hash_password(signup_password),
                        phone.strip(),
                        "User",
                        area,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ]],
                    columns=USER_COLUMNS,
                )

                users = pd.concat([users, new_user], ignore_index=True)
                save_users(users)
                st.success("Account created. Host can now see this user.")

    st.stop()


# ==================================================
# HEADER
# ==================================================
user = st.session_state.user
user_id = user["User ID"]
is_host = user["Role"] == "Host"

left, right = st.columns([3, 1])

with left:
    st.markdown('<div class="title">⚡ VoltIQ Technologies Pvt. Ltd</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Live EV Charging Platform</div>', unsafe_allow_html=True)

with right:
    st.write(f"**{user['Name']}**")
    st.write(user["Role"])
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


# ==================================================
# HOST DASHBOARD
# ==================================================
if is_host:
    users = load_users()
    vehicles = load_vehicles()
    reservations = load_reservations()
    stations_raw = make_numeric(load_stations())
    stations = get_stations_ready()

    st.markdown(
        """
        <div class="hero">
            <h2>Host Dashboard</h2>
            <p>Click refresh to see latest registrations, vehicles and reservations from users.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Refresh Host Data", type="primary", use_container_width=True):
        st.rerun()

    active = len(reservations[reservations["Status"].isin(["Confirmed", "Queued"])]) if not reservations.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Users", len(users[users["Role"] == "User"]), "registered")
    with m2:
        metric_card("Vehicles", len(vehicles), "saved")
    with m3:
        metric_card("Reservations", len(reservations), "total")
    with m4:
        metric_card("Active", active, "bookings")

    tab1, tab2, tab3, tab4 = st.tabs(["Reservations", "Users", "Vehicles", "Stations"])

    with tab1:
        st.subheader("Reservations")

        if reservations.empty:
            st.info("No reservations yet.")
        else:
            display = reservations.merge(
                users[["User ID", "Name", "Email", "Phone"]],
                on="User ID",
                how="left",
            )

            st.dataframe(display, use_container_width=True, hide_index=True)

            active_rows = reservations[reservations["Status"].isin(["Confirmed", "Queued"])]

            if not active_rows.empty:
                selected = st.selectbox("Select reservation to complete", active_rows["Reservation ID"].tolist())

                if st.button("Mark Reservation Completed", use_container_width=True):
                    reservations = load_reservations()
                    stations_raw = make_numeric(load_stations())

                    reservation_row = reservations[reservations["Reservation ID"] == selected]

                    if reservation_row.empty:
                        st.error("Reservation not found.")
                    else:
                        reservation_index = reservation_row.index[0]
                        station_id = reservations.at[reservation_index, "Station ID"]
                        status = reservations.at[reservation_index, "Status"]

                        station_row = stations_raw[stations_raw["Station ID"] == station_id]

                        if station_row.empty:
                            st.error("Station not found.")
                        else:
                            station_index = station_row.index[0]

                            if status == "Confirmed":
                                stations_raw.at[station_index, "Occupied Chargers"] = max(
                                    0,
                                    int(stations_raw.at[station_index, "Occupied Chargers"]) - 1,
                                )
                                stations_raw.at[station_index, "Available Chargers"] = int(stations_raw.at[station_index, "Available Chargers"]) + 1

                            if status == "Queued":
                                stations_raw.at[station_index, "Queue Length"] = max(
                                    0,
                                    int(stations_raw.at[station_index, "Queue Length"]) - 1,
                                )

                            reservations.at[reservation_index, "Status"] = "Completed"
                            save_reservations(reservations)
                            save_stations(stations_raw)
                            st.success("Reservation completed.")
                            st.rerun()

    with tab2:
        st.subheader("Registered Users")
        st.dataframe(users.drop(columns=["Password Hash"], errors="ignore"), use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Saved Vehicles")

        if vehicles.empty:
            st.info("No vehicles saved yet.")
        else:
            vehicle_display = vehicles.merge(
                users[["User ID", "Name", "Email", "Phone"]],
                on="User ID",
                how="left",
            )
            st.dataframe(vehicle_display, use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Station Management")

        station_name = st.selectbox("Select Station", stations_raw["Station Name"].tolist())
        selected_station = stations_raw[stations_raw["Station Name"] == station_name]

        if not selected_station.empty:
            index = selected_station.index[0]
            row = stations_raw.loc[index]

            with st.form("station_update_form"):
                c1, c2, c3 = st.columns(3)

                with c1:
                    available = st.number_input("Available Chargers", min_value=0, value=int(row["Available Chargers"]))
                    queue = st.number_input("Queue Length", min_value=0, value=int(row["Queue Length"]))

                with c2:
                    occupied = st.number_input("Occupied Chargers", min_value=0, value=int(row["Occupied Chargers"]))
                    price = st.number_input("Price per kWh", min_value=1, value=int(row["Price per kWh"]))

                with c3:
                    faulty = st.number_input("Faulty Chargers", min_value=0, value=int(row["Faulty Chargers"]))
                    rating = st.number_input("Rating", min_value=1.0, max_value=5.0, value=float(row["Rating"]), step=0.1)

                update = st.form_submit_button("Update Station", use_container_width=True)

            if update:
                total = int(row["Total Chargers"])

                if available + occupied + faulty != total:
                    st.error("Available + Occupied + Faulty must equal Total Chargers.")
                else:
                    stations_raw.at[index, "Available Chargers"] = int(available)
                    stations_raw.at[index, "Occupied Chargers"] = int(occupied)
                    stations_raw.at[index, "Faulty Chargers"] = int(faulty)
                    stations_raw.at[index, "Queue Length"] = int(queue)
                    stations_raw.at[index, "Price per kWh"] = int(price)
                    stations_raw.at[index, "Rating"] = float(rating)

                    save_stations(stations_raw)
                    st.success("Station updated. User side will also update.")
                    st.rerun()

        st.dataframe(stations_raw, use_container_width=True, hide_index=True)

        if st.button("Reset Stations to Default", use_container_width=True):
            save_stations(pd.DataFrame(DEFAULT_STATIONS, columns=STATION_COLUMNS))
            st.success("Stations reset.")
            st.rerun()

    st.stop()


# ==================================================
# USER DASHBOARD
# ==================================================
st.markdown(
    """
    <div class="hero">
        <h2>User Dashboard</h2>
        <p>Step 1: select your area. Step 2: find a charger. Step 3: reserve slot. Host can see your details.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Step 1: Select Your Area")

area = st.selectbox("Your Area", list(LOCATIONS.keys()))

if st.button("Use This Area", type="primary", use_container_width=True):
    st.session_state.user_lat, st.session_state.user_lon = LOCATIONS[area]
    st.success(f"Location set to {area}")
    st.rerun()

stations = get_stations_ready()

if stations.empty:
    save_stations(pd.DataFrame(DEFAULT_STATIONS, columns=STATION_COLUMNS))
    st.warning("Station data was reset. Refresh the page.")
    st.stop()

st.sidebar.header("Filters")
st.sidebar.selectbox("Area", ["All"] + sorted(stations["Area"].dropna().unique().tolist()), key="area_filter")
st.sidebar.selectbox("Availability", ["All", "Available Only"], key="available_filter")
st.sidebar.selectbox("Charging Type", ["All"] + sorted(stations["Charging Type"].dropna().unique().tolist()), key="charger_filter")
st.sidebar.selectbox("Connector", ["All"] + sorted(stations["Connector"].dropna().unique().tolist()), key="connector_filter")
st.sidebar.text_input("Search", key="search_text")

if st.sidebar.button("Clear Filters"):
    reset_filters()
    st.rerun()

filtered = apply_filters(stations)

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Stations", len(filtered), "found")
with m2:
    metric_card("Available", int(filtered["Available Chargers"].sum()) if not filtered.empty else 0, "chargers")
with m3:
    metric_card("Queue", int(filtered["Queue Length"].sum()) if not filtered.empty else 0, "vehicles")
with m4:
    avg = "₹0" if filtered.empty else f"₹{round(filtered['Price per kWh'].mean(), 2)}"
    metric_card("Avg Price", avg, "per kWh")

if filtered.empty:
    st.warning("No stations found. Click Clear Filters in sidebar.")

tab1, tab2, tab3, tab4 = st.tabs(["Find Charger", "Reserve Slot", "My Vehicles", "My Reservations"])

with tab1:
    st.subheader("Closest Available Charger")

    best = find_best_station(filtered)

    if best is None:
        st.warning("No available charger found.")
    else:
        station_card(best)
        st.link_button("Open in Google Maps", best["Maps Link"])

    st.subheader("All Stations")

    if filtered.empty:
        st.info("No station data to show.")
    else:
        display = filtered.copy()

        if st.session_state.user_lat is not None:
            display = display.sort_values("Distance km", na_position="last")

        for _, row in display.iterrows():
            station_card(row)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Available", int(row["Available Chargers"]))
            c2.metric("Queue", int(row["Queue Length"]))
            c3.metric("Wait", f"{int(row['Estimated Wait Time'])} min")
            c4.metric("Price", f"₹{int(row['Price per kWh'])}/kWh")
            st.link_button("Maps", row["Maps Link"])

with tab2:
    st.subheader("Reserve Charging Slot")

    if filtered.empty:
        st.warning("No stations available. Clear filters first.")
    else:
        booking_df = filtered.copy()

        if st.session_state.user_lat is not None:
            booking_df = booking_df.sort_values("Distance km", na_position="last")

        station_choice = st.selectbox("Select Station", booking_df["Station Name"].tolist())
        selected = booking_df[booking_df["Station Name"] == station_choice].iloc[0]

        st.info(
            f"{int(selected['Available Chargers'])} available | "
            f"{int(selected['Queue Length'])} in queue | "
            f"{int(selected['Estimated Wait Time'])} min wait"
        )

        vehicles = load_vehicles()
        my_vehicles = vehicles[vehicles["User ID"] == user_id]

        with st.form("reservation_form"):
            if my_vehicles.empty:
                vehicle_number = st.text_input("Vehicle Number")
                ev_model = st.text_input("EV Model")
            else:
                chosen_vehicle = st.selectbox("Select Saved Vehicle", my_vehicles["Vehicle Number"].tolist())
                vehicle_data = my_vehicles[my_vehicles["Vehicle Number"] == chosen_vehicle].iloc[0]
                vehicle_number = vehicle_data["Vehicle Number"]
                ev_model = vehicle_data["EV Model"]
                st.write(f"EV Model: {ev_model}")

            driver_name = st.text_input("Driver Name", value=user["Name"])
            mobile = st.text_input("Mobile Number", value=user["Phone"])
            date = st.date_input("Date")
            time = st.time_input("Time")
            duration = st.selectbox("Duration", ["30 minutes", "1 hour", "1.5 hours", "2 hours"])
            agree = st.checkbox("I agree to join queue if charger becomes unavailable.")
            submit = st.form_submit_button("Confirm Reservation", use_container_width=True)

        if submit:
            reservations = load_reservations()
            stations_raw = make_numeric(load_stations())

            vehicle_number = vehicle_number.strip().upper()
            ev_model = ev_model.strip()
            mobile = str(mobile).strip()

            duplicate = reservations[
                (reservations["Vehicle Number"] == vehicle_number)
                & (reservations["Status"].isin(["Confirmed", "Queued"]))
            ]

            if not vehicle_number or not ev_model or not mobile:
                st.error("Fill vehicle and mobile details.")
            elif not mobile.isdigit() or len(mobile) != 10:
                st.error("Enter valid 10-digit mobile number.")
            elif not agree:
                st.error("Accept the condition.")
            elif not duplicate.empty:
                st.warning("This vehicle already has an active reservation.")
            else:
                station_id = selected["Station ID"]
                station_rows = stations_raw[stations_raw["Station ID"] == station_id]

                if station_rows.empty:
                    st.error("Station not found.")
                else:
                    idx = station_rows.index[0]
                    available = int(stations_raw.at[idx, "Available Chargers"])

                    if available > 0:
                        status = "Confirmed"
                        stations_raw.at[idx, "Available Chargers"] = available - 1
                        stations_raw.at[idx, "Occupied Chargers"] = int(stations_raw.at[idx, "Occupied Chargers"]) + 1
                    else:
                        status = "Queued"
                        stations_raw.at[idx, "Queue Length"] = int(stations_raw.at[idx, "Queue Length"]) + 1

                    new_reservation = pd.DataFrame(
                        [[
                            "VQ-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(uuid.uuid4())[:4].upper(),
                            user_id,
                            driver_name.strip(),
                            vehicle_number,
                            ev_model,
                            mobile,
                            station_id,
                            selected["Station Name"],
                            str(date),
                            str(time),
                            duration,
                            status,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ]],
                        columns=RESERVATION_COLUMNS,
                    )

                    reservations = pd.concat([reservations, new_reservation], ignore_index=True)
                    save_reservations(reservations)
                    save_stations(stations_raw)

                    st.success(f"Reservation {status.lower()} successfully. Host can now view it.")
                    st.rerun()

with tab3:
    st.subheader("My Vehicles")

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
        save_vehicle = st.form_submit_button("Save Vehicle", use_container_width=True)

    if save_vehicle:
        vehicles = load_vehicles()
        vehicle_number = vehicle_number.strip().upper()

        duplicate = vehicles[
            (vehicles["User ID"] == user_id)
            & (vehicles["Vehicle Number"] == vehicle_number)
        ]

        if not vehicle_number or not ev_model.strip():
            st.error("Vehicle number and model are required.")
        elif not duplicate.empty:
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

with tab4:
    st.subheader("My Reservations")

    reservations = load_reservations()
    my_reservations = reservations[reservations["User ID"] == user_id]

    if my_reservations.empty:
        st.info("No reservations yet.")
    else:
        st.dataframe(my_reservations, use_container_width=True, hide_index=True)