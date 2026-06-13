import hashlib
import uuid
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
    layout="wide"
)


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
# HELPER FUNCTIONS
# ==================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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
    queue_length = int(queue_length)

    if charging_type == "DC Fast Charging":
        return queue_length * 30

    if charging_type == "AC Charging":
        return queue_length * 55

    return queue_length * 45


def health_status(total, faulty):
    total = int(total)
    faulty = int(faulty)

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
    available = int(available)

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


def prepare_station_data():
    df = st.session_state.stations.copy()
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
    if dataframe is None:
        return None

    if dataframe.empty:
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

    fallback_df = available_df.copy()

    if fallback_df.empty:
        return None

    fallback_df = fallback_df.sort_values(
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
            filtered["Amenities"].str.contains(
                st.session_state.amenity_filter,
                case=False,
                na=False,
            )
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


# ==================================================
# SESSION STATE
# ==================================================
if "users" not in st.session_state:
    st.session_state.users = pd.DataFrame(DEFAULT_USERS)

if "vehicles" not in st.session_state:
    st.session_state.vehicles = pd.DataFrame(
        columns=[
            "Vehicle ID",
            "User ID",
            "Vehicle Number",
            "EV Model",
            "Connector",
            "Battery Capacity kWh",
            "Created At",
        ]
    )

if "stations" not in st.session_state:
    st.session_state.stations = pd.DataFrame(DEFAULT_STATIONS)

if "reservations" not in st.session_state:
    st.session_state.reservations = pd.DataFrame(
        columns=[
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
    )

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
        color: #64748B;
        margin-top: 0px;
    }

    .hero-box {
        padding: 22px;
        border-radius: 18px;
        background: linear-gradient(135deg, #ECFEFF, #EFF6FF, #F5F3FF);
        border: 1px solid #CBD5E1;
        margin-bottom: 18px;
        color: #0F172A;
    }

    .company-box {
        padding: 22px;
        border-radius: 18px;
        background: linear-gradient(135deg, #F0FDFA, #EFF6FF, #FAF5FF);
        border: 1px solid #CBD5E1;
        margin-bottom: 18px;
        color: #0F172A;
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
        '<p class="subtitle">Smart EV Charging Availability and Queue Management System</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-box">
        Find nearby EV charging stations, view queue length, reserve charging slots,
        save your vehicles, and navigate using Google Maps.
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        st.subheader("Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            users = st.session_state.users.copy()
            email_clean = email.strip().lower()

            matched = users[
                (users["Email"].str.lower() == email_clean)
                & (users["Password Hash"] == hash_password(password))
            ]

            if matched.empty:
                st.error("Invalid email or password.")
            else:
                st.session_state.logged_in = True
                st.session_state.user = matched.iloc[0].to_dict()
                st.success("Login successful.")
                st.rerun()

        st.info("Demo User: user@demo.com / User@123")
        st.caption("Host Login: group 1 goated / shahid is goat")

    with signup_tab:
        st.subheader("Create New Account")

        name = st.text_input("Full Name")
        signup_email = st.text_input("Email Address")
        phone = st.text_input("Mobile Number")
        preferred_area = st.selectbox("Preferred Area", list(KNOWN_LOCATIONS.keys()))
        signup_password = st.text_input("Create Password", type="password")

        if st.button("Create Account"):
            if not name.strip() or not signup_email.strip() or not phone.strip() or not signup_password:
                st.error("Please fill all fields.")

            elif not phone.isdigit() or len(phone) != 10:
                st.error("Please enter a valid 10-digit mobile number.")

            elif signup_email.strip().lower() in st.session_state.users["Email"].str.lower().tolist():
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
                    "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                st.session_state.users = pd.concat(
                    [st.session_state.users, pd.DataFrame([new_user])],
                    ignore_index=True,
                )

                st.success("Account created successfully. Please login.")


if not st.session_state.logged_in:
    show_login_page()
    st.stop()


# ==================================================
# CURRENT USER
# ==================================================
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
        '<p class="subtitle">Smart EV Charging Availability, Queue Management and Station Discovery Platform</p>',
        unsafe_allow_html=True,
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
            st.session_state.location_requested = False
            st.rerun()


# ==================================================
# HOST PAGE - SEPARATE SAFE DASHBOARD
# ==================================================
if is_host:
    st.markdown("## 🛠️ Host Dashboard")

    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Total Users", len(st.session_state.users))
    h2.metric("Saved Vehicles", len(st.session_state.vehicles))
    h3.metric("Reservations", len(st.session_state.reservations))
    h4.metric("Stations", len(st.session_state.stations))

    host_tab1, host_tab2, host_tab3, host_tab4 = st.tabs(
        ["📋 Reservations", "⚙️ Station Management", "➕ Add Station", "👥 Users & Vehicles"]
    )

    with host_tab1:
        st.subheader("All Reservations")

        if st.session_state.reservations.empty:
            st.info("No reservations yet.")
        else:
            st.dataframe(st.session_state.reservations, use_container_width=True, hide_index=True)

        active_res = st.session_state.reservations[
            st.session_state.reservations["Status"].isin(["Confirmed", "Queued"])
        ]

        if not active_res.empty:
            selected_res = st.selectbox(
                "Select reservation to complete",
                active_res["Reservation ID"].tolist(),
            )

            if st.button("Mark Reservation as Completed"):
                res_rows = st.session_state.reservations[
                    st.session_state.reservations["Reservation ID"] == selected_res
                ]

                if res_rows.empty:
                    st.error("Reservation not found.")
                else:
                    res_index = res_rows.index[0]
                    station_id = st.session_state.reservations.loc[res_index, "Station ID"]
                    old_status = st.session_state.reservations.loc[res_index, "Status"]

                    station_rows = st.session_state.stations[
                        st.session_state.stations["Station ID"] == station_id
                    ]

                    if station_rows.empty:
                        st.error("Station not found.")
                    else:
                        station_index = station_rows.index[0]

                        if old_status == "Confirmed":
                            occupied = int(st.session_state.stations.loc[station_index, "Occupied Chargers"])
                            available = int(st.session_state.stations.loc[station_index, "Available Chargers"])
                            st.session_state.stations.loc[station_index, "Occupied Chargers"] = max(0, occupied - 1)
                            st.session_state.stations.loc[station_index, "Available Chargers"] = available + 1

                        elif old_status == "Queued":
                            queue = int(st.session_state.stations.loc[station_index, "Queue Length"])
                            st.session_state.stations.loc[station_index, "Queue Length"] = max(0, queue - 1)

                        st.session_state.reservations.loc[res_index, "Status"] = "Completed"
                        st.success("Reservation completed.")
                        st.rerun()

    with host_tab2:
        st.subheader("Edit Charging Stations")

        if st.session_state.stations.empty:
            st.warning("No stations available.")
        else:
            selected_station_name = st.selectbox(
                "Select Station",
                st.session_state.stations["Station Name"].tolist(),
            )

            station_rows = st.session_state.stations[
                st.session_state.stations["Station Name"] == selected_station_name
            ]

            if station_rows.empty:
                st.error("Selected station not found.")
            else:
                station_index = station_rows.index[0]
                selected_station = st.session_state.stations.loc[station_index]

                with st.form("station_edit_form"):
                    available = st.number_input(
                        "Available Chargers",
                        min_value=0,
                        value=int(selected_station["Available Chargers"]),
                    )

                    occupied = st.number_input(
                        "Occupied Chargers",
                        min_value=0,
                        value=int(selected_station["Occupied Chargers"]),
                    )

                    faulty = st.number_input(
                        "Faulty Chargers",
                        min_value=0,
                        value=int(selected_station["Faulty Chargers"]),
                    )

                    queue = st.number_input(
                        "Queue Length",
                        min_value=0,
                        value=int(selected_station["Queue Length"]),
                    )

                    price = st.number_input(
                        "Price per kWh",
                        min_value=1,
                        value=int(selected_station["Price per kWh"]),
                    )

                    rating = st.number_input(
                        "Rating",
                        min_value=1.0,
                        max_value=5.0,
                        value=float(selected_station["Rating"]),
                        step=0.1,
                    )

                    update_station = st.form_submit_button("Update Station")

                if update_station:
                    total = int(selected_station["Total Chargers"])

                    if available + occupied + faulty != total:
                        st.error("Available + Occupied + Faulty must equal Total Chargers.")
                    else:
                        st.session_state.stations.loc[station_index, "Available Chargers"] = available
                        st.session_state.stations.loc[station_index, "Occupied Chargers"] = occupied
                        st.session_state.stations.loc[station_index, "Faulty Chargers"] = faulty
                        st.session_state.stations.loc[station_index, "Queue Length"] = queue
                        st.session_state.stations.loc[station_index, "Price per kWh"] = price
                        st.session_state.stations.loc[station_index, "Rating"] = rating

                        st.success("Station updated successfully.")
                        st.rerun()

            st.subheader("Station Database")
            st.dataframe(st.session_state.stations, use_container_width=True, hide_index=True)

    with host_tab3:
        st.subheader("Add New Charging Station")

        with st.form("add_station_form"):
            name = st.text_input("Station Name")
            network = st.text_input("Network", value="VoltIQ")
            city = st.text_input("City", value="Hyderabad")
            area = st.text_input("Area")
            address = st.text_input("Address")
            charging_type = st.selectbox("Charging Type", ["DC Fast Charging", "AC Charging"])
            connector = st.selectbox("Connector", ["CCS2", "Type 2", "CHAdeMO"])
            total = st.number_input("Total Chargers", min_value=1, value=4)
            available = st.number_input("Available Chargers", min_value=0, value=2)
            occupied = st.number_input("Occupied Chargers", min_value=0, value=2)
            faulty = st.number_input("Faulty Chargers", min_value=0, value=0)
            queue = st.number_input("Queue Length", min_value=0, value=0)
            price = st.number_input("Price per kWh", min_value=1, value=20)
            rating = st.number_input("Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.1)
            open_24 = st.selectbox("Open 24x7", ["Yes", "No"])
            amenities = st.text_input("Amenities", value="Parking")
            latitude = st.number_input("Latitude", value=17.3850, format="%.6f")
            longitude = st.number_input("Longitude", value=78.4867, format="%.6f")

            add_station = st.form_submit_button("Add Station")

        if add_station:
            if not name.strip() or not area.strip() or not address.strip():
                st.error("Station name, area, and address are required.")

            elif available + occupied + faulty != total:
                st.error("Available + Occupied + Faulty must equal Total Chargers.")

            elif name.strip().lower() in st.session_state.stations["Station Name"].str.lower().tolist():
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

                st.session_state.stations = pd.concat(
                    [st.session_state.stations, pd.DataFrame([new_station])],
                    ignore_index=True,
                )

                st.success("Station added successfully.")
                st.rerun()

    with host_tab4:
        st.subheader("Registered Users")
        users_display = st.session_state.users.drop(columns=["Password Hash"], errors="ignore")
        st.dataframe(users_display, use_container_width=True, hide_index=True)

        st.subheader("Saved Vehicles")

        if st.session_state.vehicles.empty:
            st.info("No saved vehicles yet.")
        else:
            st.dataframe(st.session_state.vehicles, use_container_width=True, hide_index=True)

    st.stop()


# ==================================================
# USER LOCATION
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


# ==================================================
# USER STATION FILTERS
# ==================================================
stations_df = prepare_station_data()

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

st.sidebar.slider("Maximum Price per kWh", 10, 30, 25, key="max_price")
st.sidebar.slider("Minimum Rating", 3.5, 5.0, 3.8, 0.1, key="minimum_rating")

if location_enabled:
    st.sidebar.slider("Maximum Distance from You", 1, 50, 15, key="max_distance")
else:
    st.session_state.max_distance = 50
    st.sidebar.caption("Set location to enable distance filter.")

st.sidebar.text_input(
    "Search Station / Area / Network",
    placeholder="Example: Tata, Madhapur, CCS2",
    key="search_keyword",
)

filtered_df = get_filtered_stations(stations_df)


# ==================================================
# USER DASHBOARD
# ==================================================
st.markdown("## 📊 Live Charging Overview")

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Stations Found", len(filtered_df))
m2.metric("Available Chargers", int(filtered_df["Available Chargers"].sum()) if not filtered_df.empty else 0)
m3.metric("Occupied Chargers", int(filtered_df["Occupied Chargers"].sum()) if not filtered_df.empty else 0)
m4.metric("Vehicles in Queue", int(filtered_df["Queue Length"].sum()) if not filtered_df.empty else 0)

if filtered_df.empty:
    m5.metric("Avg Price / kWh", "₹0")
else:
    m5.metric("Avg Price / kWh", f"₹{round(filtered_df['Price per kWh'].mean(), 2)}")

st.divider()


# ==================================================
# USER TABS
# ==================================================
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


with tab2:
    st.markdown("## 📍 Charging Station Details")

    if filtered_df.empty:
        st.warning("No station data available.")
    else:
        display_df = filtered_df.copy()

        if location_enabled and "User Distance km" in display_df.columns:
            display_df = display_df.sort_values("User Distance km", na_position="last")

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

                    if pd.notna(row["User Distance km"]):
                        st.metric("Distance", f"{round(row['User Distance km'], 2)} km")
                    else:
                        st.metric("Distance", "Set location")

                if int(row["Total Chargers"]) > 0:
                    st.progress(float(row["Available Chargers"]) / float(row["Total Chargers"]))


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

            user_vehicles = st.session_state.vehicles[
                st.session_state.vehicles["User ID"] == user_id
            ]

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
                        user_vehicles["Vehicle Number"].tolist(),
                    )

                    selected_vehicle = user_vehicles[
                        user_vehicles["Vehicle Number"] == vehicle_choice
                    ].iloc[0]

                    vehicle_number = selected_vehicle["Vehicle Number"]
                    ev_model = selected_vehicle["EV Model"]
                    st.write(f"**EV Model:** {ev_model}")

                driver_name = st.text_input("Driver Name", value=user["Name"])
                mobile_number = st.text_input("Mobile Number", value=str(user["Phone"]))
                reservation_date = st.date_input("Charging Date")
                reservation_time = st.time_input("Preferred Time")
                duration = st.selectbox(
                    "Charging Duration",
                    ["30 minutes", "1 hour", "1.5 hours", "2 hours"],
                )

                accept_terms = st.checkbox(
                    "I agree that my booking may be moved to queue if the charger becomes unavailable."
                )

                submit_reservation = st.form_submit_button("Confirm Reservation")

            if submit_reservation:
                vehicle_number = vehicle_number.strip().upper()
                ev_model = ev_model.strip()
                mobile_number = str(mobile_number).strip()

                active_duplicate = st.session_state.reservations[
                    (st.session_state.reservations["Vehicle Number"] == vehicle_number)
                    & (st.session_state.reservations["Status"].isin(["Confirmed", "Queued"]))
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
                    station_rows = st.session_state.stations[
                        st.session_state.stations["Station ID"] == station_id
                    ]

                    if station_rows.empty:
                        st.error("Station not found. Please refresh the app.")
                    else:
                        station_index = station_rows.index[0]
                        available = int(st.session_state.stations.loc[station_index, "Available Chargers"])

                        if available > 0:
                            st.session_state.stations.loc[station_index, "Available Chargers"] = available - 1
                            st.session_state.stations.loc[station_index, "Occupied Chargers"] = (
                                int(st.session_state.stations.loc[station_index, "Occupied Chargers"]) + 1
                            )
                            status = "Confirmed"
                        else:
                            st.session_state.stations.loc[station_index, "Queue Length"] = (
                                int(st.session_state.stations.loc[station_index, "Queue Length"]) + 1
                            )
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

                        st.session_state.reservations = pd.concat(
                            [st.session_state.reservations, pd.DataFrame([new_reservation])],
                            ignore_index=True,
                        )

                        st.success(f"Reservation {status.lower()} successfully.")
                        st.rerun()


with tab4:
    st.markdown("## 🚗 My Saved Vehicles")

    my_vehicles = st.session_state.vehicles[
        st.session_state.vehicles["User ID"] == user_id
    ]

    if my_vehicles.empty:
        st.info("No vehicles saved yet.")
    else:
        st.dataframe(my_vehicles, use_container_width=True, hide_index=True)

    st.markdown("### Add New Vehicle")

    with st.form("vehicle_form"):
        vehicle_number_input = st.text_input("Vehicle Number")
        ev_model_input = st.text_input("EV Model")
        connector_input = st.selectbox("Connector Type", ["CCS2", "Type 2", "CHAdeMO"])
        battery_input = st.number_input(
            "Battery Capacity kWh",
            min_value=10,
            max_value=150,
            value=40,
        )

        add_vehicle = st.form_submit_button("Save Vehicle")

    if add_vehicle:
        vehicle_number_clean = vehicle_number_input.strip().upper()

        duplicate_vehicle = st.session_state.vehicles[
            (st.session_state.vehicles["User ID"] == user_id)
            & (st.session_state.vehicles["Vehicle Number"] == vehicle_number_clean)
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

            st.session_state.vehicles = pd.concat(
                [st.session_state.vehicles, pd.DataFrame([new_vehicle])],
                ignore_index=True,
            )

            st.success("Vehicle saved successfully.")
            st.rerun()


with tab5:
    st.markdown("## 👤 My Profile")

    with st.form("profile_form"):
        new_name = st.text_input("Name", value=user["Name"])
        new_phone = st.text_input("Phone", value=str(user["Phone"]))

        area_list = list(KNOWN_LOCATIONS.keys())
        current_area = user["Preferred Area"] if user["Preferred Area"] in area_list else "Hyderabad"
        new_area = st.selectbox("Preferred Area", area_list, index=area_list.index(current_area))

        update_profile = st.form_submit_button("Update Profile")

    if update_profile:
        if not new_name.strip() or not new_phone.strip():
            st.error("Name and phone are required.")

        elif not new_phone.isdigit() or len(new_phone) != 10:
            st.error("Please enter a valid 10-digit mobile number.")

        else:
            user_rows = st.session_state.users[
                st.session_state.users["User ID"] == user_id
            ]

            if user_rows.empty:
                st.error("User not found. Please login again.")
            else:
                user_index = user_rows.index[0]
                st.session_state.users.loc[user_index, "Name"] = new_name.strip()
                st.session_state.users.loc[user_index, "Phone"] = new_phone.strip()
                st.session_state.users.loc[user_index, "Preferred Area"] = new_area
                st.session_state.user = st.session_state.users.loc[user_index].to_dict()

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
        designed to make electric vehicle charging more convenient, reliable, and user-friendly.
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
        st.write("**Phone:** +91 98765 43210")

    with contact_col2:
        st.write("**Location:** Hyderabad, Telangana, India")
        st.write("**Working Hours:** 9:00 AM to 6:00 PM")
        st.write("**Support:** EV charging assistance and station information")

    st.success("Powering smarter journeys, one charge at a time.")