import streamlit as st
import pandas as pd
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from urllib.parse import quote_plus

try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None


# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="VoltIQ Technologies Pvt. Ltd",
    page_icon="⚡",
    layout="wide"
)


# -------------------------------------------------
# Styling
# -------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #0F766E;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #64748B;
        margin-top: 0px;
    }

    .brand-box {
        padding: 18px;
        border-radius: 14px;
        background-color: #E0F2FE;
        border: 1px solid #BAE6FD;
        margin-bottom: 16px;
        color: #075985;
        font-size: 17px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown('<p class="main-title">⚡ VoltIQ Technologies Pvt. Ltd</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Smart EV Charging Availability, Queue Management and Station Discovery Platform</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="brand-box">
    VoltIQ helps EV users find nearby charging stations, check availability, view queue length,
    estimate waiting time, reserve slots, and navigate through Google Maps.
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# Charging Station Data
# -------------------------------------------------
station_data = [
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


# -------------------------------------------------
# Session State
# -------------------------------------------------
if "stations" not in st.session_state:
    st.session_state.stations = pd.DataFrame(station_data)

if "reservations" not in st.session_state:
    st.session_state.reservations = pd.DataFrame(
        columns=[
            "Reservation ID",
            "Driver Name",
            "Vehicle Number",
            "EV Model",
            "Mobile Number",
            "Station Name",
            "Date",
            "Time",
            "Duration",
            "Status",
            "Created At"
        ]
    )

if "user_latitude" not in st.session_state:
    st.session_state.user_latitude = None

if "user_longitude" not in st.session_state:
    st.session_state.user_longitude = None

if "location_requested" not in st.session_state:
    st.session_state.location_requested = False


# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def calculate_wait_time(queue_length, charging_type):
    if charging_type == "DC Fast Charging":
        average_time = 30
    elif charging_type == "AC Charging":
        average_time = 55
    else:
        average_time = 45

    return int(queue_length * average_time)


def get_health_status(total_chargers, faulty_chargers):
    if total_chargers <= 0:
        return "Invalid"

    faulty_ratio = faulty_chargers / total_chargers

    if faulty_ratio == 0:
        return "Excellent"
    if faulty_ratio <= 0.20:
        return "Good"
    if faulty_ratio <= 0.40:
        return "Average"

    return "Poor"


def get_availability_status(available_chargers):
    if available_chargers >= 3:
        return "Good Availability"
    if available_chargers >= 1:
        return "Limited Availability"
    return "Currently Full"


def get_maps_link(station_name, address):
    query = quote_plus(f"{station_name} {address}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


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


def get_unique_options(dataframe, column_name):
    values = dataframe[column_name].dropna().unique().tolist()
    return sorted(values)


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


def check_duplicate_vehicle(vehicle_number):
    reservations_df = st.session_state.reservations

    if reservations_df.empty:
        return False

    active = reservations_df[
        (reservations_df["Vehicle Number"] == vehicle_number)
        & (reservations_df["Status"].isin(["Confirmed", "Queued"]))
    ]

    return not active.empty


def get_best_station(dataframe):
    available_df = dataframe[dataframe["Available Chargers"] > 0].copy()

    if available_df.empty:
        return None

    available_df["Distance Score"] = available_df["User Distance km"].apply(
        lambda value: value if pd.notna(value) else 20
    )

    available_df["Recommendation Score"] = (
        available_df["Distance Score"] * 0.35
        + available_df["Estimated Wait Time"] * 0.35
        + available_df["Price per kWh"] * 0.20
        - available_df["Rating"] * 2
    )

    return available_df.sort_values("Recommendation Score").iloc[0]


# -------------------------------------------------
# Prepare Data
# -------------------------------------------------
df = st.session_state.stations.copy()
df = df.drop_duplicates(subset=["Station ID", "Station Name"], keep="first")

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
    lambda row: get_maps_link(row["Station Name"], row["Address"]),
    axis=1
)


# -------------------------------------------------
# Location Permission Section
# -------------------------------------------------
st.markdown("## 📍 Location Permission")

location_enabled = (
    st.session_state.user_latitude is not None
    and st.session_state.user_longitude is not None
)

if location_enabled:
    with st.container(border=True):
        col_success, col_reset = st.columns([2, 1])

        with col_success:
            st.success("Location enabled successfully. Distance-based recommendations are now active.")
            st.caption(
                f"Detected location: "
                f"{round(float(st.session_state.user_latitude), 5)}, "
                f"{round(float(st.session_state.user_longitude), 5)}"
            )

        with col_reset:
            if st.button("Change Location"):
                st.session_state.user_latitude = None
                st.session_state.user_longitude = None
                st.session_state.location_requested = False
                st.rerun()

else:
    with st.container(border=True):
        st.write(
            "To recommend the nearest and fastest charging station, VoltIQ can use your current browser location. "
            "Your location is used only for distance calculation inside this app."
        )

        if st.button("Allow Location Access", type="primary"):
            st.session_state.location_requested = True

        if st.session_state.location_requested:
            if get_geolocation is None:
                st.error("Location package missing. Add streamlit-js-eval in requirements.txt.")
            else:
                location = get_geolocation()
                latitude, longitude = extract_location(location)

                if latitude is not None and longitude is not None:
                    st.session_state.user_latitude = float(latitude)
                    st.session_state.user_longitude = float(longitude)
                    st.session_state.location_requested = False
                    st.success("Location received successfully.")
                    st.rerun()
                else:
                    st.info(
                        "Waiting for browser location. If the browser already asked permission, please wait a few seconds. "
                        "If nothing happens, use manual location below."
                    )

    manual_location = st.checkbox("Enter location manually instead")

    if manual_location:
        col_manual1, col_manual2 = st.columns(2)

        with col_manual1:
            manual_lat = st.number_input(
                "Your Latitude",
                value=17.3850,
                format="%.6f"
            )

        with col_manual2:
            manual_lon = st.number_input(
                "Your Longitude",
                value=78.4867,
                format="%.6f"
            )

        if st.button("Use Manual Location"):
            st.session_state.user_latitude = float(manual_lat)
            st.session_state.user_longitude = float(manual_lon)
            st.session_state.location_requested = False
            st.success("Manual location saved.")
            st.rerun()


# -------------------------------------------------
# Add Distance From User
# -------------------------------------------------
location_enabled = (
    st.session_state.user_latitude is not None
    and st.session_state.user_longitude is not None
)

if location_enabled:
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


# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------
st.sidebar.header("🔎 Smart Filters")

city_options = ["All"] + get_unique_options(df, "City")
selected_city = st.sidebar.selectbox("City", city_options)

city_filtered_df = df.copy()
if selected_city != "All":
    city_filtered_df = city_filtered_df[city_filtered_df["City"] == selected_city]

area_options = ["All"] + get_unique_options(city_filtered_df, "Area")
selected_area = st.sidebar.selectbox("Area", area_options)

area_filtered_df = city_filtered_df.copy()
if selected_area != "All":
    area_filtered_df = area_filtered_df[area_filtered_df["Area"] == selected_area]

network_options = ["All"] + get_unique_options(area_filtered_df, "Network")
selected_network = st.sidebar.selectbox("Charging Network", network_options)

network_filtered_df = area_filtered_df.copy()
if selected_network != "All":
    network_filtered_df = network_filtered_df[network_filtered_df["Network"] == selected_network]

charging_type_options = ["All"] + get_unique_options(network_filtered_df, "Charging Type")
selected_charging_type = st.sidebar.selectbox("Charging Speed", charging_type_options)

type_filtered_df = network_filtered_df.copy()
if selected_charging_type != "All":
    type_filtered_df = type_filtered_df[type_filtered_df["Charging Type"] == selected_charging_type]

connector_options = ["All"] + get_unique_options(type_filtered_df, "Connector")
selected_connector = st.sidebar.selectbox("Connector Type", connector_options)

availability_filter = st.sidebar.selectbox(
    "Availability",
    ["All", "Available Now", "Currently Full", "Low Queue Only"]
)

open_24x7_filter = st.sidebar.selectbox(
    "Operating Hours",
    ["All", "Open 24x7 Only"]
)

amenity_filter = st.sidebar.selectbox(
    "Preferred Amenity",
    ["All", "Parking", "Food", "Restroom", "Mall", "Service Center", "Metro Access"]
)

max_price = st.sidebar.slider(
    "Maximum Price per kWh",
    min_value=10,
    max_value=30,
    value=25,
    step=1
)

minimum_rating = st.sidebar.slider(
    "Minimum Rating",
    min_value=3.5,
    max_value=5.0,
    value=3.8,
    step=0.1
)

if location_enabled:
    max_distance = st.sidebar.slider(
        "Maximum Distance from Your Location",
        min_value=1,
        max_value=50,
        value=15,
        step=1
    )
else:
    max_distance = None
    st.sidebar.caption("Enable location to use distance filter.")

search_keyword = st.sidebar.text_input(
    "Search Station, Area, Network or Connector",
    placeholder="Example: Tata, Madhapur, CCS2"
)


# -------------------------------------------------
# Apply Filters
# -------------------------------------------------
filtered_df = df.copy()

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

if open_24x7_filter == "Open 24x7 Only":
    filtered_df = filtered_df[filtered_df["Open 24x7"] == "Yes"]

if amenity_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Amenities"].str.contains(amenity_filter, case=False, na=False)
    ]

filtered_df = filtered_df[filtered_df["Price per kWh"] <= max_price]
filtered_df = filtered_df[filtered_df["Rating"] >= minimum_rating]

if max_distance is not None:
    filtered_df = filtered_df[filtered_df["User Distance km"] <= max_distance]

if search_keyword:
    filtered_df = filtered_df[
        filtered_df["Station Name"].str.contains(search_keyword, case=False, na=False)
        | filtered_df["Address"].str.contains(search_keyword, case=False, na=False)
        | filtered_df["Area"].str.contains(search_keyword, case=False, na=False)
        | filtered_df["Network"].str.contains(search_keyword, case=False, na=False)
        | filtered_df["Connector"].str.contains(search_keyword, case=False, na=False)
    ]


# -------------------------------------------------
# Dashboard Metrics
# -------------------------------------------------
st.markdown("## 📊 Live Charging Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Stations Found", len(filtered_df))

with col2:
    st.metric("Available Chargers", int(filtered_df["Available Chargers"].sum()))

with col3:
    st.metric("Occupied Chargers", int(filtered_df["Occupied Chargers"].sum()))

with col4:
    st.metric("Vehicles in Queue", int(filtered_df["Queue Length"].sum()))

with col5:
    if not filtered_df.empty:
        avg_price = round(filtered_df["Price per kWh"].mean(), 2)
    else:
        avg_price = 0
    st.metric("Avg Price / kWh", f"₹{avg_price}")

st.divider()


# -------------------------------------------------
# Tabs
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🔍 Find Charger",
        "📍 Station Details",
        "🧾 Reserve Slot",
        "🗺️ Map & Navigation",
        "📈 Dashboard",
        "💡 Project Info"
    ]
)


# -------------------------------------------------
# Tab 1: Find Charger
# -------------------------------------------------
with tab1:
    st.markdown("## 🔍 Recommended Charging Station")

    if filtered_df.empty:
        st.warning("No charging stations found for your selected filters.")
    else:
        best_station = get_best_station(filtered_df)

        if best_station is None:
            st.error("All matching stations are currently full. You may join the queue from the reservation tab.")
        else:
            st.success("Best station recommended based on distance, availability, wait time, price, and rating.")

            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.subheader(best_station["Station Name"])
                st.write(f"**Network:** {best_station['Network']}")
                st.write(f"**Address:** {best_station['Address']}")
                st.write(f"**Charging Speed:** {best_station['Charging Type']}")
                st.write(f"**Connector:** {best_station['Connector']}")
                st.write(f"**Amenities:** {best_station['Amenities']}")
                st.write(f"**Open 24x7:** {best_station['Open 24x7']}")
                st.link_button("Open Location in Google Maps", best_station["Maps Link"])

            with col_right:
                st.metric("Available", int(best_station["Available Chargers"]))
                st.metric("Queue", int(best_station["Queue Length"]))
                st.metric("Wait Time", f"{int(best_station['Estimated Wait Time'])} min")
                st.metric("Price", f"₹{best_station['Price per kWh']} / kWh")

                if pd.notna(best_station["User Distance km"]):
                    st.metric("Distance", f"{round(best_station['User Distance km'], 2)} km")
                else:
                    st.metric("Distance", "Enable Location")


# -------------------------------------------------
# Tab 2: Station Details
# -------------------------------------------------
with tab2:
    st.markdown("## 📍 Charging Station Details")

    if filtered_df.empty:
        st.warning("No station details available.")
    else:
        for _, row in filtered_df.iterrows():
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([2, 1, 1])

                with col_a:
                    st.subheader(row["Station Name"])
                    st.write(f"**Network:** {row['Network']}")
                    st.write(f"**Address:** {row['Address']}")
                    st.write(f"**Charging Type:** {row['Charging Type']}")
                    st.write(f"**Connector:** {row['Connector']}")
                    st.write(f"**Amenities:** {row['Amenities']}")
                    st.write(f"**Health Status:** {row['Health Status']}")
                    st.write(f"**Availability:** {row['Availability Status']}")
                    st.link_button("Navigate with Google Maps", row["Maps Link"])

                with col_b:
                    st.metric("Total Chargers", int(row["Total Chargers"]))
                    st.metric("Available", int(row["Available Chargers"]))
                    st.metric("Occupied", int(row["Occupied Chargers"]))
                    st.metric("Faulty", int(row["Faulty Chargers"]))

                with col_c:
                    st.metric("Queue", int(row["Queue Length"]))
                    st.metric("Wait Time", f"{int(row['Estimated Wait Time'])} min")
                    st.metric("Rating", row["Rating"])
                    st.metric("Price", f"₹{row['Price per kWh']}")

                    if pd.notna(row["User Distance km"]):
                        st.metric("Distance", f"{round(row['User Distance km'], 2)} km")
                    else:
                        st.metric("Distance", "Enable Location")

                if row["Total Chargers"] > 0:
                    st.progress(row["Available Chargers"] / row["Total Chargers"])


# -------------------------------------------------
# Tab 3: Reservation
# -------------------------------------------------
with tab3:
    st.markdown("## 🧾 Reserve a Charging Slot")

    if filtered_df.empty:
        st.warning("No charging stations are available for reservation with the selected filters.")
    else:
        selected_station = st.selectbox(
            "Select Charging Station",
            filtered_df["Station Name"].tolist()
        )

        selected_station_data = df[df["Station Name"] == selected_station].iloc[0]

        st.info(
            f"{selected_station_data['Available Chargers']} chargers available | "
            f"{selected_station_data['Queue Length']} vehicles in queue | "
            f"Estimated wait: {selected_station_data['Estimated Wait Time']} minutes"
        )

        with st.form("reservation_form"):
            driver_name = st.text_input("Driver Name")
            vehicle_number = st.text_input("Vehicle Number")
            ev_model = st.text_input("EV Model")
            mobile_number = st.text_input("Mobile Number")
            reservation_date = st.date_input("Charging Date")
            reservation_time = st.time_input("Preferred Time")
            duration = st.selectbox(
                "Charging Duration",
                ["30 minutes", "1 hour", "1.5 hours", "2 hours"]
            )

            accept_terms = st.checkbox(
                "I agree that my reservation may be moved to queue if the charger becomes unavailable."
            )

            submit = st.form_submit_button("Confirm Reservation")

        if submit:
            driver_name = driver_name.strip()
            vehicle_number = vehicle_number.strip().upper()
            ev_model = ev_model.strip()
            mobile_number = mobile_number.strip()

            if not driver_name or not vehicle_number or not ev_model or not mobile_number:
                st.error("Please fill Driver Name, Vehicle Number, EV Model, and Mobile Number.")

            elif not mobile_number.isdigit() or len(mobile_number) != 10:
                st.error("Please enter a valid 10-digit mobile number.")

            elif not accept_terms:
                st.error("Please accept the reservation condition before confirming.")

            elif check_duplicate_vehicle(vehicle_number):
                st.warning("This vehicle already has an active reservation or queue entry.")

            else:
                station_index = st.session_state.stations[
                    st.session_state.stations["Station Name"] == selected_station
                ].index[0]

                available = int(st.session_state.stations.loc[station_index, "Available Chargers"])

                if available > 0:
                    st.session_state.stations.loc[station_index, "Available Chargers"] -= 1
                    st.session_state.stations.loc[station_index, "Occupied Chargers"] += 1
                    reservation_status = "Confirmed"
                else:
                    st.session_state.stations.loc[station_index, "Queue Length"] += 1
                    reservation_status = "Queued"

                reservation_id = f"VQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

                new_reservation = {
                    "Reservation ID": reservation_id,
                    "Driver Name": driver_name,
                    "Vehicle Number": vehicle_number,
                    "EV Model": ev_model,
                    "Mobile Number": mobile_number,
                    "Station Name": selected_station,
                    "Date": str(reservation_date),
                    "Time": str(reservation_time),
                    "Duration": duration,
                    "Status": reservation_status,
                    "Created At": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                }

                st.session_state.reservations = pd.concat(
                    [st.session_state.reservations, pd.DataFrame([new_reservation])],
                    ignore_index=True
                )

                st.success(f"Reservation {reservation_status.lower()} successfully.")
                st.write(f"**Reservation ID:** {reservation_id}")
                st.write(f"**Status:** {reservation_status}")


# -------------------------------------------------
# Tab 4: Map and Navigation
# -------------------------------------------------
with tab4:
    st.markdown("## 🗺️ Map and Navigation")

    if filtered_df.empty:
        st.warning("No stations to show on map.")
    else:
        map_df = filtered_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
        st.map(map_df[["lat", "lon"]])

        st.markdown("### Quick Navigation Links")

        for _, row in filtered_df.iterrows():
            col_nav1, col_nav2, col_nav3 = st.columns([2, 1, 1])

            with col_nav1:
                st.write(f"**{row['Station Name']}**")
                st.caption(row["Address"])

            with col_nav2:
                if pd.notna(row["User Distance km"]):
                    st.write(f"{round(row['User Distance km'], 2)} km away")
                else:
                    st.write("Enable location")

            with col_nav3:
                st.link_button("Open Maps", row["Maps Link"])


# -------------------------------------------------
# Tab 5: Dashboard
# -------------------------------------------------
with tab5:
    st.markdown("## 📈 Operator Dashboard")

    if filtered_df.empty:
        st.warning("No data available.")
    else:
        chart_df = filtered_df.set_index("Station Name")[
            ["Available Chargers", "Occupied Chargers", "Faulty Chargers"]
        ]

        st.markdown("### Charger Status")
        st.bar_chart(chart_df)

        st.markdown("### Queue Length")
        queue_df = filtered_df.set_index("Station Name")["Queue Length"]
        st.bar_chart(queue_df)

        st.markdown("### Station Database")

        station_display_columns = [
            "Station Name",
            "Network",
            "Area",
            "Charging Type",
            "Connector",
            "Available Chargers",
            "Queue Length",
            "Estimated Wait Time",
            "Price per kWh",
            "Rating",
            "Open 24x7",
            "Amenities",
            "User Distance km"
        ]

        st.dataframe(
            filtered_df[station_display_columns],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Reservation Records")

        if st.session_state.reservations.empty:
            st.info("No reservations yet.")
        else:
            clean_reservations = st.session_state.reservations.drop_duplicates(
                subset=["Vehicle Number", "Status"],
                keep="first"
            )

            st.dataframe(
                clean_reservations,
                use_container_width=True,
                hide_index=True
            )


# -------------------------------------------------
# Tab 6: Project Info
# -------------------------------------------------
with tab6:
    st.markdown("## 💡 Project Information")

    st.markdown(
        """
        ### Problem Statement

        EV drivers face uncertainty and long waiting times because real-time charger availability,
        queue length, charger health, and location information are not clearly available in one place.

        ### Proposed Solution

        **VoltIQ Technologies Pvt. Ltd** provides a smart and user-friendly platform where users can:

        - Allow location access
        - Find nearby EV charging stations
        - View charger availability
        - Check queue length
        - Estimate waiting time
        - Reserve a slot
        - Navigate using Google Maps
        - Filter by network, connector, charging speed, price, rating, and amenities

        ### Unique Value Proposition

        **"Never waste time searching for a charger again."**

        ### Future Scope

        - Live charger API integration
        - Online payment
        - OTP-based booking confirmation
        - AI demand prediction
        - Fleet dashboard
        - Dynamic pricing
        - Charger fault reporting
        - Google Maps API integration
        """
    )


# -------------------------------------------------
# Footer
# -------------------------------------------------
st.divider()
st.caption("VoltIQ Technologies Pvt. Ltd | Smart EV Charging Availability and Queue Management Platform")