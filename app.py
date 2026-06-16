import base64
import hashlib
import hmac
import os
import re
import secrets
import uuid
from datetime import date, datetime, time, timedelta
from math import atan2, cos, radians, sin, sqrt

import pandas as pd
import streamlit as st

try:
    from streamlit_js_eval import get_geolocation
except Exception:
    get_geolocation = None


# ============================================================
# APP CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="VoltIQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "VoltIQ"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

RESERVATION_FEE_RATE = 0.10
STATION_OWNER_COMMISSION_RATE = 0.05
NO_SHOW_FEE_RATE = 0.05
CANCELLATION_FEE_RATE = 0.05
PRIORITY_ADDON_FEE = 40
PRIORITY_ADDON_LABEL = "Priority add-on"

HOST_LOGIN = os.getenv("VOLTIQ_HOST_LOGIN", "group 1 goated")
HOST_PASSWORD = os.getenv("VOLTIQ_HOST_PASSWORD", "shahid is goat")
DEMO_LOGIN = "user@demo.com"
DEMO_PASSWORD = "User@123"

FILES = {
    "users": os.path.join(DATA_DIR, "users.csv"),
    "vehicles": os.path.join(DATA_DIR, "vehicles.csv"),
    "stations": os.path.join(DATA_DIR, "stations.csv"),
    "reservations": os.path.join(DATA_DIR, "reservations.csv"),
    "favorites": os.path.join(DATA_DIR, "favorites.csv"),
    "reviews": os.path.join(DATA_DIR, "reviews.csv"),
    "notifications": os.path.join(DATA_DIR, "notifications.csv"),
    "sessions": os.path.join(DATA_DIR, "sessions.csv"),
}

USER_COLUMNS = [
    "User ID", "Name", "Email", "Password Hash", "Phone", "Role",
    "Preferred Area", "Created At",
]
VEHICLE_COLUMNS = [
    "Vehicle ID", "User ID", "Vehicle Number", "EV Model", "Connector",
    "Battery Type", "Battery Capacity kWh", "Created At",
]
STATION_COLUMNS = [
    "Station ID", "Station Name", "Network", "Area", "Address",
    "Charging Type", "Connector", "Power kW", "Total Chargers",
    "Available Chargers", "Occupied Chargers", "Faulty Chargers",
    "Queue Length", "Price per kWh", "Rating", "Open 24x7",
    "Amenities", "Latitude", "Longitude", "Status",
]
RESERVATION_COLUMNS = [
    "Reservation ID", "User ID", "Driver Name", "Vehicle Number", "EV Model",
    "Mobile Number", "Station ID", "Station Name", "Start At", "End At",
    "Duration Minutes", "Connector", "Status", "Payment Status",
    "Charging Cost", "Platform Fee", "Priority Fee", "Cancellation Fee", "No Show Fee",
    "Station Commission", "Station Owner Payout",
    "Total Payable", "Priority Booking", "Arrived At", "Estimated Cost", "Created At", "Updated At",
]
FAVORITE_COLUMNS = ["User ID", "Station ID", "Created At"]
REVIEW_COLUMNS = [
    "Review ID", "User ID", "Station ID", "Reservation ID", "Rating",
    "Comment", "Created At",
]
NOTIFICATION_COLUMNS = [
    "Notification ID", "User ID", "Title", "Message", "Read", "Created At",
]
SESSION_COLUMNS = [
    "Session ID", "Reservation ID", "User ID", "Station ID", "Vehicle Number",
    "Started At", "Ended At", "Energy kWh", "Amount", "Status",
]

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

EV_SPECS = {
    "Tata Nexon EV": ("CCS2", 40.5),
    "Tata Tiago EV": ("CCS2", 24.0),
    "Tata Tigor EV": ("CCS2", 26.0),
    "Tata Punch EV": ("CCS2", 35.0),
    "MG ZS EV": ("CCS2", 50.3),
    "MG Comet EV": ("Type 2", 17.3),
    "Mahindra XUV400 EV": ("CCS2", 39.4),
    "Hyundai Kona Electric": ("CCS2", 39.2),
    "Hyundai IONIQ 5": ("CCS2", 72.6),
    "BYD Atto 3": ("CCS2", 60.5),
    "BYD Seal": ("CCS2", 82.6),
    "Kia EV6": ("CCS2", 77.4),
    "Citroen eC3": ("CCS2", 29.2),
    "Mercedes-Benz EQB": ("CCS2", 66.5),
    "BMW i4": ("CCS2", 83.9),
    "Audi e-tron": ("CCS2", 95.0),
    "Other": ("CCS2", 40.0),
}

DEFAULT_STATIONS = [
    ["SC001", "Tata Power EZ Charge - Begumpet", "Tata Power", "Begumpet", "Begumpet, Hyderabad", "DC Fast", "CCS2", 50, 4, 3, 0, 1, 0, 22, 4.2, "No", "Parking, Service Center", 17.4435, 78.4622, "Online"],
    ["SC002", "Statiq EV Charging - Kukatpally", "Statiq", "Kukatpally", "Kukatpally, Hyderabad", "DC Fast", "CCS2", 60, 4, 2, 1, 1, 1, 21, 4.1, "Yes", "Parking, Food", 17.4933, 78.3996, "Online"],
    ["SC003", "ChargeZone Hub - Hitech City", "ChargeZone", "Hitech City", "Hitech City, Hyderabad", "DC Fast", "CCS2", 120, 5, 4, 1, 0, 0, 22, 4.5, "Yes", "Parking, Food, Restroom", 17.4504, 78.3805, "Online"],
    ["SC004", "Jio-bp Pulse - Madhapur", "Jio-bp", "Madhapur", "Madhapur, Hyderabad", "DC Fast", "CCS2", 60, 4, 1, 3, 0, 2, 23, 4.0, "Yes", "Parking, Food", 17.4483, 78.3915, "Online"],
    ["SC005", "GLIDA Green Drive - Gachibowli", "GLIDA", "Gachibowli", "Gachibowli, Hyderabad", "DC Fast", "CCS2", 120, 6, 5, 1, 0, 0, 20, 4.4, "Yes", "Parking, Restroom, Food", 17.4401, 78.3489, "Online"],
    ["SC006", "Public EV Point - Durgam Cheruvu", "Public EV", "Durgam Cheruvu", "Durgam Cheruvu, Hyderabad", "AC", "Type 2", 22, 3, 2, 0, 1, 0, 17, 3.9, "No", "Parking", 17.4309, 78.3894, "Online"],
    ["SC007", "Tata Power EZ Charge - Miyapur", "Tata Power", "Miyapur", "Miyapur Metro Station, Hyderabad", "AC", "Type 2", 22, 3, 2, 1, 0, 0, 18, 4.0, "No", "Parking, Metro Access", 17.4964, 78.3611, "Online"],
    ["SC008", "Public EV Station - BHEL", "Public EV", "BHEL", "BHEL, Hyderabad", "AC", "Type 2", 11, 4, 3, 1, 0, 0, 16, 4.0, "No", "Parking", 17.4948, 78.3053, "Online"],
    ["SC009", "VoltIQ FastCharge - Financial District", "VoltIQ", "Financial District", "Financial District, Hyderabad", "DC Fast", "CCS2", 150, 8, 7, 1, 0, 0, 19, 4.6, "Yes", "Parking, Food, Restroom, Wi-Fi", 17.4149, 78.3422, "Online"],
    ["SC010", "VoltIQ ChargePoint - Kondapur", "VoltIQ", "Kondapur", "Kondapur, Hyderabad", "AC", "Type 2", 22, 4, 3, 1, 0, 0, 17, 4.2, "No", "Parking, Food", 17.4698, 78.3578, "Online"],
]


# ============================================================
# DATA AND SECURITY
# ============================================================
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def uid(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def pbkdf2_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"pbkdf2_sha256${salt}${base64.b64encode(digest).decode()}"


def verify_password(password, stored):
    if stored.startswith("pbkdf2_sha256$"):
        try:
            _, salt, expected = stored.split("$", 2)
            actual = pbkdf2_hash(password, salt).split("$", 2)[2]
            return hmac.compare_digest(actual, expected)
        except ValueError:
            return False
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored)


def atomic_save(df, path):
    temp = f"{path}.tmp"
    df.to_csv(temp, index=False)
    os.replace(temp, path)


def load_table(name, columns, defaults=None):
    path = FILES[name]
    if not os.path.exists(path):
        df = pd.DataFrame(defaults or [], columns=columns)
        atomic_save(df, path)
        return df
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
        df = df.loc[:, ~df.columns.duplicated()].copy()
    except Exception:
        backup = f"{path}.broken-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            os.replace(path, backup)
        except OSError:
            pass
        df = pd.DataFrame(defaults or [], columns=columns)

    # Upgrade CSV files created by earlier VoltIQ versions.
    if name == "stations":
        if "Power kW" not in df.columns:
            charging_type = df.get("Charging Type", pd.Series("", index=df.index))
            df["Power kW"] = charging_type.apply(
                lambda value: "60" if "DC" in str(value).upper() else "22"
            )
        if "Status" not in df.columns:
            df["Status"] = "Online"
        df.loc[df["Status"].astype(str).str.strip() == "", "Status"] = "Online"
    elif name == "vehicles":
        if "Battery Capacity kWh" not in df.columns:
            models = df.get("EV Model", pd.Series("Other", index=df.index))
            df["Battery Capacity kWh"] = models.apply(
                lambda model: str(EV_SPECS.get(str(model), EV_SPECS["Other"])[1])
            )
    elif name == "reservations" and "Start At" not in df.columns:
        old_dates = df.get("Date", pd.Series("", index=df.index))
        old_times = df.get("Time", pd.Series("", index=df.index))
        starts = pd.to_datetime(old_dates.astype(str) + " " + old_times.astype(str), errors="coerce")
        duration_text = df.get("Duration", pd.Series("60 minutes", index=df.index))
        duration_minutes = duration_text.astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0]
        duration_minutes = pd.to_numeric(duration_minutes, errors="coerce").fillna(60)
        duration_minutes = duration_minutes.where(
            ~duration_text.astype(str).str.contains("hour", case=False, na=False),
            duration_minutes * 60,
        )
        df["Start At"] = starts.dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
        df["End At"] = (starts + pd.to_timedelta(duration_minutes, unit="m")).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        ).fillna("")
        df["Duration Minutes"] = duration_minutes.astype(int).astype(str)
        df["Connector"] = ""
        df["Payment Status"] = "Pay at station"
        df["Charging Cost"] = "0"
        df["Platform Fee"] = "0"
        df["Priority Fee"] = "0"
        df["Cancellation Fee"] = "0"
        df["No Show Fee"] = "0"
        df["Station Commission"] = "0"
        df["Station Owner Payout"] = "0"
        df["Total Payable"] = "0"
        df["Priority Booking"] = "No priority"
        df["Arrived At"] = ""
        df["Estimated Cost"] = "0"
        df["Updated At"] = df.get("Created At", pd.Series(now_text(), index=df.index))
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    if name == "reservations":
        money_defaults = {
            "Charging Cost": "0",
            "Platform Fee": "0",
            "Priority Fee": "0",
            "Cancellation Fee": "0",
            "No Show Fee": "0",
            "Station Commission": "0",
            "Station Owner Payout": "0",
            "Total Payable": "0",
            "Estimated Cost": "0",
        }
        for column, default in money_defaults.items():
            df.loc[df[column].astype(str).str.strip() == "", column] = default
        df.loc[df["Priority Booking"].astype(str).str.strip() == "", "Priority Booking"] = "No priority"
        df.loc[df["Arrived At"].astype(str).str.strip() == "", "Arrived At"] = ""
        old_estimated = pd.to_numeric(df["Estimated Cost"], errors="coerce").fillna(0)
        current_total = pd.to_numeric(df["Total Payable"], errors="coerce").fillna(0)
        legacy_rows = (current_total <= 0) & (old_estimated > 0)
        for index in df[legacy_rows].index:
            migrated_charges = booking_charges(old_estimated.loc[index], 0)
            df.at[index, "Charging Cost"] = migrated_charges["charging_cost"]
            df.at[index, "Platform Fee"] = migrated_charges["reservation_fee"]
            df.at[index, "Priority Fee"] = migrated_charges["priority_fee"]
            df.at[index, "Cancellation Fee"] = migrated_charges["cancellation_fee"]
            df.at[index, "No Show Fee"] = migrated_charges["no_show_fee"]
            df.at[index, "Station Commission"] = migrated_charges["station_commission"]
            df.at[index, "Station Owner Payout"] = migrated_charges["station_owner_payout"]
            df.at[index, "Total Payable"] = migrated_charges["total_payable"]
            df.at[index, "Estimated Cost"] = migrated_charges["total_payable"]
    return df[columns]


def save_table(name, df):
    df = df.loc[:, ~df.columns.duplicated()].copy()
    atomic_save(df, FILES[name])


def ensure_seed_data():
    users = load_table("users", USER_COLUMNS)
    seed_users = [
        ("U-ADMIN", "VoltIQ Host", HOST_LOGIN, HOST_PASSWORD, "9999999999", "Host", "Hyderabad"),
        ("U-DEMO", "Demo User", DEMO_LOGIN, DEMO_PASSWORD, "8888888888", "User", "Gachibowli"),
    ]
    for user_id, name, email, password, phone, role, area in seed_users:
        match = users["User ID"] == user_id
        if not match.any():
            row = [user_id, name, email, pbkdf2_hash(password), phone, role, area, now_text()]
            users = pd.concat([users, pd.DataFrame([row], columns=USER_COLUMNS)], ignore_index=True)
        else:
            index = users[match].index[0]
            users.at[index, "Email"] = email
            users.at[index, "Role"] = role
            if not verify_password(password, users.at[index, "Password Hash"]):
                users.at[index, "Password Hash"] = pbkdf2_hash(password)
    save_table("users", users)

    stations = load_table("stations", STATION_COLUMNS, DEFAULT_STATIONS)
    if stations.empty:
        stations = pd.DataFrame(DEFAULT_STATIONS, columns=STATION_COLUMNS)
        save_table("stations", stations)

    load_table("vehicles", VEHICLE_COLUMNS)
    load_table("reservations", RESERVATION_COLUMNS)
    load_table("favorites", FAVORITE_COLUMNS)
    load_table("reviews", REVIEW_COLUMNS)
    load_table("notifications", NOTIFICATION_COLUMNS)
    load_table("sessions", SESSION_COLUMNS)


def numeric_stations(df):
    columns = [
        "Power kW", "Total Chargers", "Available Chargers", "Occupied Chargers",
        "Faulty Chargers", "Queue Length", "Price per kWh", "Rating",
        "Latitude", "Longitude",
    ]
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    return df


def add_notification(user_id, title, message):
    df = load_table("notifications", NOTIFICATION_COLUMNS)
    row = [uid("N"), user_id, title, message, "No", now_text()]
    df = pd.concat([df, pd.DataFrame([row], columns=NOTIFICATION_COLUMNS)], ignore_index=True)
    save_table("notifications", df)


# ============================================================
# DOMAIN LOGIC
# ============================================================
def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return round(radius * 2 * atan2(sqrt(a), sqrt(max(0, 1 - a))), 2)


def parse_dt(value):
    return pd.to_datetime(value, errors="coerce")


def overlap_count(reservations, station_id, start_at, end_at, exclude_id=""):
    if reservations.empty:
        return 0
    data = reservations[
        (reservations["Station ID"] == station_id)
        & (reservations["Status"].isin(["Confirmed", "Charging"]))
    ].copy()
    if exclude_id:
        data = data[data["Reservation ID"] != exclude_id]
    if data.empty:
        return 0
    starts = pd.to_datetime(data["Start At"], errors="coerce")
    ends = pd.to_datetime(data["End At"], errors="coerce")
    return int(((starts < end_at) & (ends > start_at)).sum())


def capacity_for_station(station):
    return max(0, int(station["Total Chargers"]) - int(station["Faulty Chargers"]))


def slot_status(station, reservations, start_at, end_at, exclude_id=""):
    capacity = capacity_for_station(station)
    booked = overlap_count(reservations, station["Station ID"], start_at, end_at, exclude_id)
    return ("Confirmed", capacity - booked) if booked < capacity else ("Queued", 0)


def promote_queue(station_id):
    reservations = load_table("reservations", RESERVATION_COLUMNS)
    stations = numeric_stations(load_table("stations", STATION_COLUMNS))
    station_rows = stations[stations["Station ID"] == station_id]
    if station_rows.empty:
        return
    station = station_rows.iloc[0]
    queued = reservations[
        (reservations["Station ID"] == station_id)
        & (reservations["Status"] == "Queued")
    ].copy()
    if queued.empty:
        return
    queued["_start"] = pd.to_datetime(queued["Start At"], errors="coerce")
    queued["_priority_fee"] = pd.to_numeric(queued["Priority Fee"], errors="coerce").fillna(0)
    queued = queued.sort_values(["_start", "_priority_fee", "Created At"], ascending=[True, False, True])
    changed = False
    for index, row in queued.iterrows():
        start_at = parse_dt(row["Start At"])
        end_at = parse_dt(row["End At"])
        if pd.isna(start_at) or pd.isna(end_at):
            continue
        status, _ = slot_status(station, reservations, start_at, end_at, row["Reservation ID"])
        if status == "Confirmed":
            original_index = reservations[reservations["Reservation ID"] == row["Reservation ID"]].index[0]
            reservations.at[original_index, "Status"] = "Confirmed"
            reservations.at[original_index, "Updated At"] = now_text()
            add_notification(
                row["User ID"],
                "Booking confirmed",
                f"Your queued reservation at {row['Station Name']} is now confirmed.",
            )
            changed = True
    if changed:
        save_table("reservations", reservations)


def estimated_charge(battery_kwh, current_percent, target_percent, price):
    energy = max(0, battery_kwh * (target_percent - current_percent) / 100)
    billable_energy = energy * 1.10
    return round(energy, 2), round(billable_energy * price, 2)


def booking_charges(charging_cost, priority_fee=0):
    charging_cost = round(float(charging_cost), 2)
    priority_fee = round(float(priority_fee), 2)
    booking_subtotal = round(charging_cost + priority_fee, 2)
    reservation_fee = round(booking_subtotal * RESERVATION_FEE_RATE, 2)
    total_payable = round(booking_subtotal + reservation_fee, 2)
    cancellation_fee = round(total_payable * CANCELLATION_FEE_RATE, 2)
    no_show_fee = round(total_payable * NO_SHOW_FEE_RATE, 2)
    station_commission = round(charging_cost * STATION_OWNER_COMMISSION_RATE, 2)
    station_owner_payout = round(charging_cost - station_commission, 2)
    voltiq_earning = round(reservation_fee + priority_fee + station_commission, 2)
    return {
        "charging_cost": charging_cost,
        "booking_subtotal": booking_subtotal,
        "platform_fee": reservation_fee,
        "reservation_fee": reservation_fee,
        "priority_fee": priority_fee,
        "cancellation_fee": cancellation_fee,
        "no_show_fee": no_show_fee,
        "total_payable": total_payable,
        "station_commission": station_commission,
        "station_owner_payout": station_owner_payout,
        "station_payout": station_owner_payout,
        "voltiq_earning": voltiq_earning,
    }


def can_apply_no_show(reservation_row):
    start_at = parse_dt(reservation_row.get("Start At", ""))
    arrived_at = str(reservation_row.get("Arrived At", "")).strip()
    if pd.isna(start_at):
        return False
    if arrived_at:
        return False
    return datetime.now() >= start_at.to_pydatetime() + timedelta(minutes=30)


def clear_charging_amounts_for_penalty(df, index, penalty_amount):
    df.at[index, "Charging Cost"] = 0
    df.at[index, "Platform Fee"] = 0
    df.at[index, "Priority Fee"] = 0
    df.at[index, "Cancellation Fee"] = 0
    df.at[index, "Station Commission"] = 0
    df.at[index, "Station Owner Payout"] = 0
    df.at[index, "Total Payable"] = penalty_amount
    df.at[index, "Estimated Cost"] = penalty_amount


def station_rating(station_id, fallback):
    reviews = load_table("reviews", REVIEW_COLUMNS)
    rows = reviews[reviews["Station ID"] == station_id]
    if rows.empty:
        return float(fallback)
    ratings = pd.to_numeric(rows["Rating"], errors="coerce").dropna()
    return round(float(ratings.mean()), 1) if not ratings.empty else float(fallback)


def get_station_data():
    stations = numeric_stations(load_table("stations", STATION_COLUMNS))
    reservations = load_table("reservations", RESERVATION_COLUMNS)
    now = datetime.now()
    next_hour = now + timedelta(hours=1)
    stations["Live Booked"] = stations.apply(
        lambda row: overlap_count(reservations, row["Station ID"], now, next_hour), axis=1
    )
    stations["Bookable Now"] = stations.apply(
        lambda row: max(0, capacity_for_station(row) - int(row["Live Booked"])), axis=1
    )
    stations["Display Rating"] = stations.apply(
        lambda row: station_rating(row["Station ID"], row["Rating"]), axis=1
    )
    if st.session_state.user_lat is not None and st.session_state.user_lon is not None:
        stations["Distance km"] = stations.apply(
            lambda row: distance_km(
                float(st.session_state.user_lat), float(st.session_state.user_lon),
                float(row["Latitude"]), float(row["Longitude"]),
            ),
            axis=1,
        )
    else:
        stations["Distance km"] = pd.NA
    return stations


def reservation_receipt(row):
    return (
        f"VOLTIQ RESERVATION RECEIPT\n"
        f"Reservation: {row['Reservation ID']}\n"
        f"Station: {row['Station Name']}\n"
        f"Vehicle: {row['Vehicle Number']} ({row['EV Model']})\n"
        f"Start: {row['Start At']}\n"
        f"End: {row['End At']}\n"
        f"Status: {row['Status']}\n"
        f"Payment: {row['Payment Status']}\n"
        f"Charging cost: Rs. {row['Charging Cost']}\n"
        f"Reservation fee: Rs. {row['Platform Fee']}\n"
        f"Priority booking fee: Rs. {row['Priority Fee']}\n"
        f"Total payable: Rs. {row['Total Payable']}\n"
        f"Possible no-show fee after 30 minutes: Rs. {row['No Show Fee']}\n"
        f"Arrived at: {row['Arrived At']}\n"
        f"Station owner payout after commission: Rs. {row['Station Owner Payout']}\n"
    )


# ============================================================
# VISUAL SYSTEM
# ============================================================
st.markdown(
    """
    <style>
    :root {
        --bg: #07100d;
        --panel: #0d1915;
        --panel-2: #12221c;
        --line: #244337;
        --text: #f2f7f4;
        --muted: #9db5aa;
        --accent: #55e39f;
        --accent-dark: #062f20;
        --danger: #ff7b7b;
        --warning: #ffd166;
    }
    .stApp { background: var(--bg); color: var(--text); }
    .block-container { max-width: 1320px; padding-top: 1.2rem; padding-bottom: 4rem; }
    h1, h2, h3, h4, p, label, span, div { color: var(--text); letter-spacing: 0 !important; }
    h1 { font-size: 2.25rem !important; }
    h2 { margin-top: 1.2rem !important; }
    [data-testid="stSidebar"] { background: #091510; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] * { color: var(--text) !important; }
    .brandbar {
        display:flex; justify-content:space-between; align-items:center; gap:16px;
        border-bottom:1px solid var(--line); padding:8px 0 18px; margin-bottom:22px;
    }
    .brand { font-size:1.7rem; font-weight:900; color:var(--accent) !important; }
    .brandcopy { color:var(--muted) !important; font-size:.9rem; }
    .welcome {
        padding:24px 0 12px; margin-bottom:14px;
        background:linear-gradient(90deg, rgba(85,227,159,.12), transparent 70%);
        border-top:1px solid var(--line);
    }
    .welcome h1 { margin:0; font-weight:850; }
    .welcome p { color:var(--muted) !important; max-width:760px; }
    .station {
        border-top:1px solid var(--line); padding:20px 2px 14px; margin-top:8px;
    }
    .station-title { font-size:1.13rem; font-weight:850; margin-bottom:5px; }
    .station-meta { color:var(--muted) !important; line-height:1.7; }
    .pill {
        display:inline-block; padding:4px 9px; margin:0 6px 5px 0; border-radius:6px;
        color:var(--accent) !important; background:var(--accent-dark); font-size:.78rem; font-weight:800;
    }
    .pill-warn { color:#161207 !important; background:var(--warning); }
    .kpi {
        border-top:2px solid var(--accent); padding:13px 4px 8px; min-height:96px;
        background:linear-gradient(180deg, rgba(85,227,159,.07), transparent);
    }
    .kpi-label { color:var(--muted) !important; font-size:.77rem; font-weight:800; text-transform:uppercase; }
    .kpi-value { font-size:1.75rem; font-weight:900; }
    .kpi-note { color:var(--muted) !important; font-size:.78rem; }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div,
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input,
    textarea {
        background:var(--panel-2) !important; color:var(--text) !important;
        border:1px solid var(--line) !important; border-radius:7px !important;
    }
    div[data-baseweb="popover"] *, ul[role="listbox"] * {
        background:var(--panel-2) !important; color:var(--text) !important;
    }
    .stButton button, .stFormSubmitButton button, a[data-testid="stLinkButton"] {
        background:var(--accent) !important; color:#052416 !important;
        border:0 !important; border-radius:7px !important; font-weight:850 !important;
        min-height:42px;
    }
    .stButton button *, .stFormSubmitButton button *, a[data-testid="stLinkButton"] * {
        color:#052416 !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap:4px; border-bottom:1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { border-radius:6px 6px 0 0; padding:9px 14px; }
    .stTabs [aria-selected="true"] { background:var(--panel-2); }
    div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:7px; overflow:hidden; }
    .stAlert { border-radius:7px; }
    [data-testid="stMetricValue"] { color:var(--accent) !important; }
    @media (max-width: 700px) {
        .brandbar { align-items:flex-start; flex-direction:column; }
        h1 { font-size:1.75rem !important; }
        .block-container { padding-left:1rem; padding-right:1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def brandbar(user=None):
    right = "Smart EV charging"
    if user:
        right = f"{user['Name']} · {user['Role']}"
    st.markdown(
        f'<div class="brandbar"><div><div class="brand">⚡ VoltIQ</div>'
        f'<div class="brandcopy">Find. Book. Charge.</div></div>'
        f'<div class="brandcopy">{right}</div></div>',
        unsafe_allow_html=True,
    )


def page_intro(title, text):
    st.markdown(
        f'<div class="welcome"><h1>{title}</h1><p>{text}</p></div>',
        unsafe_allow_html=True,
    )


def kpi(label, value, note=""):
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def station_summary(row):
    distance = ""
    if pd.notna(row.get("Distance km", pd.NA)):
        distance = f" · {row['Distance km']} km away"
    availability_class = "" if int(row["Bookable Now"]) > 0 else " pill-warn"
    st.markdown(
        f"""
        <div class="station">
            <span class="pill{availability_class}">{int(row["Bookable Now"])} bookable now</span>
            <span class="pill">{row["Charging Type"]} · {int(row["Power kW"])} kW</span>
            <span class="pill">{row["Connector"]}</span>
            <div class="station-title">{row["Station Name"]}</div>
            <div class="station-meta">
                {row["Area"]}{distance} · ★ {row["Display Rating"]} · Rs. {row["Price per kWh"]}/kWh<br>
                {row["Address"]} · {row["Amenities"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SESSION SETUP
# ============================================================
ensure_seed_data()

SESSION_DEFAULTS = {
    "logged_in": False,
    "user": None,
    "user_lat": None,
    "user_lon": None,
    "geo_requested": False,
    "nav": "Discover",
}
for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# AUTHENTICATION
# ============================================================
if not st.session_state.logged_in:
    brandbar()
    page_intro(
        "Charge with certainty.",
        "Discover nearby chargers, compare live capacity, reserve a time slot and manage every charging trip.",
    )
    login_tab, signup_tab = st.tabs(["Login", "Create account"])

    with login_tab:
        with st.form("login_form"):
            login_id = st.text_input("Email or login ID")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            users = load_table("users", USER_COLUMNS)
            matched = users[users["Email"].str.lower() == login_id.strip().lower()]
            if matched.empty or not verify_password(password, matched.iloc[0]["Password Hash"]):
                st.error("Invalid login ID or password.")
            else:
                st.session_state.logged_in = True
                st.session_state.user = matched.iloc[0].to_dict()
                st.rerun()
        st.caption("Demo: user@demo.com / User@123")

    with signup_tab:
        with st.form("signup_form"):
            name = st.text_input("Full name")
            email = st.text_input("Email")
            phone = st.text_input("Mobile number")
            area = st.selectbox("Preferred area", list(LOCATIONS))
            new_password = st.text_input("Create password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            signup = st.form_submit_button("Create account", use_container_width=True)
        if signup:
            users = load_table("users", USER_COLUMNS)
            email_clean = email.strip().lower()
            strong_password = (
                len(new_password) >= 8
                and re.search(r"[A-Z]", new_password)
                and re.search(r"[a-z]", new_password)
                and re.search(r"\d", new_password)
            )
            if not name.strip() or not email_clean or not phone.strip():
                st.error("Complete all required fields.")
            elif "@" not in email_clean or "." not in email_clean.split("@")[-1]:
                st.error("Enter a valid email address.")
            elif not phone.isdigit() or len(phone) != 10:
                st.error("Enter a valid 10-digit mobile number.")
            elif email_clean in users["Email"].str.lower().tolist():
                st.error("This email already has an account.")
            elif not strong_password:
                st.error("Password must have 8 characters, uppercase, lowercase and a number.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                row = [
                    uid("U"), name.strip(), email_clean, pbkdf2_hash(new_password),
                    phone, "User", area, now_text(),
                ]
                users = pd.concat([users, pd.DataFrame([row], columns=USER_COLUMNS)], ignore_index=True)
                save_table("users", users)
                st.success("Account created. You can now log in.")
    st.stop()


user = st.session_state.user
user_id = user["User ID"]
is_host = user["Role"] == "Host"
brandbar(user)

with st.sidebar:
    st.markdown("### Navigation")
    options = ["Overview", "Reservations", "Stations", "Users", "Analytics", "Finance"] if is_host else [
        "Discover", "Book", "My trips", "Garage", "Charging", "Notifications", "Profile"
    ]
    if st.session_state.nav not in options:
        st.session_state.nav = options[0]
    nav = st.radio("Go to", options, key="nav", label_visibility="collapsed")
    st.divider()
    if st.button("Log out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ============================================================
# HOST APP
# ============================================================
if is_host:
    users = load_table("users", USER_COLUMNS)
    vehicles = load_table("vehicles", VEHICLE_COLUMNS)
    reservations = load_table("reservations", RESERVATION_COLUMNS)
    stations = numeric_stations(load_table("stations", STATION_COLUMNS))
    sessions = load_table("sessions", SESSION_COLUMNS)

    if nav == "Overview":
        page_intro("Operations overview", "Current network capacity, bookings and charging activity.")
        active = reservations[reservations["Status"].isin(["Confirmed", "Queued", "Charging"])]
        total_payable = pd.to_numeric(reservations["Total Payable"], errors="coerce").fillna(0)
        reservation_fee = pd.to_numeric(reservations["Platform Fee"], errors="coerce").fillna(0)
        priority_fee = pd.to_numeric(reservations["Priority Fee"], errors="coerce").fillna(0)
        station_commission = pd.to_numeric(reservations["Station Commission"], errors="coerce").fillna(0)
        voltiq_amount = reservation_fee.sum() + priority_fee.sum() + station_commission.sum()
        cols = st.columns(5)
        values = [
            ("Users", len(users[users["Role"] == "User"]), "registered"),
            ("Stations", len(stations), "network"),
            ("Active trips", len(active), "booked or charging"),
            ("Available", int(stations["Available Chargers"].sum()), "chargers"),
            ("VoltIQ earnings", f"Rs. {voltiq_amount:,.0f}", "fees + commission"),
        ]
        for col, item in zip(cols, values):
            with col:
                kpi(*item)
        st.subheader("Upcoming workload")
        upcoming = reservations[reservations["Status"].isin(["Confirmed", "Queued"])].copy()
        if upcoming.empty:
            st.info("No upcoming reservations.")
        else:
            upcoming["_start"] = pd.to_datetime(upcoming["Start At"], errors="coerce")
            display_cols = ["Reservation ID", "Station Name", "Vehicle Number", "Start At", "Status", "Payment Status", "Total Payable"]
            st.dataframe(upcoming.sort_values("_start")[display_cols], use_container_width=True, hide_index=True)

    elif nav == "Reservations":
        page_intro("Reservation control", "Complete, cancel or promote bookings while preserving slot capacity.")
        status_filter = st.multiselect(
            "Status", ["Confirmed", "Queued", "Arrived", "Charging", "Completed", "Cancelled", "No Show"],
            default=["Confirmed", "Queued", "Charging"],
        )
        shown = reservations[reservations["Status"].isin(status_filter)] if status_filter else reservations
        st.dataframe(shown, use_container_width=True, hide_index=True)
        actionable = reservations[reservations["Status"].isin(["Confirmed", "Queued", "Arrived", "Charging"])]
        if not actionable.empty:
            selected_id = st.selectbox("Select reservation", actionable["Reservation ID"].tolist())
            selected = actionable[actionable["Reservation ID"] == selected_id].iloc[0]
            c1, c2, c3 = st.columns(3)
            if c1.button("Mark completed", use_container_width=True):
                idx = reservations[reservations["Reservation ID"] == selected_id].index[0]
                reservations.at[idx, "Status"] = "Completed"
                reservations.at[idx, "Updated At"] = now_text()
                save_table("reservations", reservations)
                add_notification(selected["User ID"], "Trip completed", f"Your visit to {selected['Station Name']} is complete.")
                promote_queue(selected["Station ID"])
                st.rerun()
            if c2.button("Cancel reservation", use_container_width=True):
                idx = reservations[reservations["Reservation ID"] == selected_id].index[0]
                reservations.at[idx, "Status"] = "Cancelled"
                reservations.at[idx, "Payment Status"] = "Cancelled - refund initiated"
                clear_charging_amounts_for_penalty(reservations, idx, 0)
                reservations.at[idx, "Updated At"] = now_text()
                save_table("reservations", reservations)
                add_notification(
                    selected["User ID"],
                    "Reservation cancelled",
                    f"{selected_id} was cancelled. Refund has been initiated.",
                )
                promote_queue(selected["Station ID"])
                st.rerun()
            if c3.button("Mark no-show", use_container_width=True):
                idx = reservations[reservations["Reservation ID"] == selected_id].index[0]
                no_show_fee = float(pd.to_numeric(pd.Series([selected["No Show Fee"]]), errors="coerce").fillna(0).iloc[0])
                if selected["Status"] in ["Arrived", "Charging", "Completed"]:
                    st.error("This user has already arrived or started charging.")
                elif not can_apply_no_show(selected):
                    st.error("No-show can be applied only 30 minutes after the booked start time if the user has not arrived.")
                else:
                    reservations.at[idx, "Status"] = "No Show"
                    reservations.at[idx, "Payment Status"] = f"No-show fee retained by VoltIQ: Rs. {no_show_fee:.2f}"
                    clear_charging_amounts_for_penalty(reservations, idx, no_show_fee)
                    reservations.at[idx, "Updated At"] = now_text()
                    save_table("reservations", reservations)
                    add_notification(
                        selected["User ID"],
                        "No-show fee applied",
                        f"You did not arrive within 30 minutes for {selected['Station Name']}. No-show fee: Rs. {no_show_fee:.2f}.",
                    )
                    promote_queue(selected["Station ID"])
                    st.rerun()

    elif nav == "Stations":
        page_intro("Station management", "Maintain capacity, faults, pricing and operating status.")
        station_name = st.selectbox("Station", stations["Station Name"].tolist())
        selected = stations[stations["Station Name"] == station_name].iloc[0]
        idx = stations[stations["Station ID"] == selected["Station ID"]].index[0]
        with st.form("station_edit"):
            c1, c2, c3 = st.columns(3)
            total = c1.number_input("Total chargers", 1, 100, int(selected["Total Chargers"]))
            occupied = c1.number_input("Occupied now", 0, 100, int(selected["Occupied Chargers"]))
            faulty = c2.number_input("Faulty chargers", 0, 100, int(selected["Faulty Chargers"]))
            queue = c2.number_input("Walk-in queue", 0, 100, int(selected["Queue Length"]))
            price = c3.number_input("Price per kWh", 1.0, 200.0, float(selected["Price per kWh"]), 0.5)
            status = c3.selectbox("Status", ["Online", "Maintenance", "Offline"], index=["Online", "Maintenance", "Offline"].index(selected["Status"]) if selected["Status"] in ["Online", "Maintenance", "Offline"] else 0)
            save_station = st.form_submit_button("Save station", use_container_width=True)
        if save_station:
            if occupied + faulty > total:
                st.error("Occupied plus faulty chargers cannot exceed total chargers.")
            else:
                stations.at[idx, "Total Chargers"] = total
                stations.at[idx, "Occupied Chargers"] = occupied
                stations.at[idx, "Faulty Chargers"] = faulty
                stations.at[idx, "Available Chargers"] = total - occupied - faulty
                stations.at[idx, "Queue Length"] = queue
                stations.at[idx, "Price per kWh"] = price
                stations.at[idx, "Status"] = status
                save_table("stations", stations[STATION_COLUMNS])
                st.success("Station updated.")
                st.rerun()
        st.dataframe(stations, use_container_width=True, hide_index=True)

    elif nav == "Users":
        page_intro("Users and vehicles", "Review registered drivers and their saved EVs.")
        t1, t2 = st.tabs(["Users", "Vehicles"])
        with t1:
            st.dataframe(users.drop(columns=["Password Hash"]), use_container_width=True, hide_index=True)
        with t2:
            joined = vehicles.merge(users[["User ID", "Name", "Email"]], on="User ID", how="left")
            st.dataframe(joined, use_container_width=True, hide_index=True)

    elif nav == "Analytics":
        page_intro("Network analytics", "Demand, revenue and station performance from recorded activity.")
        if reservations.empty:
            st.info("Analytics will appear after reservations are created.")
        else:
            by_station = reservations.groupby("Station Name").size().sort_values(ascending=False)
            st.subheader("Reservations by station")
            st.bar_chart(by_station)
            reservations["_created"] = pd.to_datetime(reservations["Created At"], errors="coerce")
            daily = reservations.dropna(subset=["_created"]).groupby(reservations["_created"].dt.date).size()
            st.subheader("Daily reservations")
            st.line_chart(daily)
            status_counts = reservations["Status"].value_counts()
            st.subheader("Reservation status")
            st.bar_chart(status_counts)
        if not sessions.empty:
            session_amount = pd.to_numeric(sessions["Amount"], errors="coerce").fillna(0)
            revenue = sessions.assign(AmountNumeric=session_amount).groupby("Station ID")["AmountNumeric"].sum()
            st.subheader("Revenue by station")
            st.bar_chart(revenue)

    elif nav == "Finance":
        page_intro("Finance dashboard", "Track online collections, VoltIQ earnings and monthly station-owner settlements.")
        finance = reservations.copy()
        for column in [
            "Charging Cost", "Platform Fee", "Priority Fee", "Cancellation Fee",
            "No Show Fee", "Station Commission", "Station Owner Payout", "Total Payable",
        ]:
            finance[column] = pd.to_numeric(finance[column], errors="coerce").fillna(0)

        payable_statuses = ["Confirmed", "Queued", "Arrived", "Charging", "Completed", "No Show"]
        payable = finance[finance["Status"].isin(payable_statuses)].copy()
        charging_value = payable["Charging Cost"].sum()
        reservation_fee_value = payable["Platform Fee"].sum()
        priority_value = payable["Priority Fee"].sum()
        no_show_value = finance[finance["Status"] == "No Show"]["Total Payable"].sum()
        station_commission_value = payable["Station Commission"].sum()
        station_payout = payable["Station Owner Payout"].sum()
        voltiq_earnings = (
            reservation_fee_value
            + priority_value
            + station_commission_value
            + no_show_value
        )
        total_collected = payable["Total Payable"].sum()

        cols = st.columns(5)
        finance_cards = [
            ("Online collected", f"Rs. {total_collected:,.0f}", "money received by VoltIQ"),
            ("Monthly payout", f"Rs. {station_payout:,.0f}", "payable to station owners"),
            ("Reservation fee", f"Rs. {reservation_fee_value:,.0f}", "10 percent"),
            ("Priority fee", f"Rs. {priority_value:,.0f}", "optional Rs. 40 add-on"),
            ("VoltIQ earnings", f"Rs. {voltiq_earnings:,.0f}", "fees + station commission"),
        ]
        for col, card in zip(cols, finance_cards):
            with col:
                kpi(*card)

        if finance.empty:
            st.info("Finance data will appear after bookings.")
        else:
            finance["_created"] = pd.to_datetime(finance["Created At"], errors="coerce")
            finance["Settlement Month"] = finance["_created"].dt.strftime("%Y-%m").fillna("Unknown")

            st.subheader("Monthly station-owner settlement")
            settlement = payable.groupby(["Settlement Month", "Station Name"], dropna=False)[
                [
                    "Charging Cost", "Station Commission", "Station Owner Payout",
                    "Platform Fee", "Priority Fee", "Total Payable",
                ]
            ].sum().reset_index()
            settlement["VoltIQ Earnings"] = (
                settlement["Platform Fee"]
                + settlement["Priority Fee"]
                + settlement["Station Commission"]
            )
            st.dataframe(settlement, use_container_width=True, hide_index=True)

            st.subheader("No-show fees and cancelled bookings")
            penalty = finance[finance["Status"].isin(["Cancelled", "No Show"])][
                ["Reservation ID", "Station Name", "Vehicle Number", "Status", "Total Payable", "Payment Status"]
            ]
            if penalty.empty:
                st.info("No no-show fees or cancelled bookings yet.")
            else:
                st.dataframe(penalty, use_container_width=True, hide_index=True)

            st.subheader("Booking finance ledger")
            st.dataframe(
                finance[
                    [
                        "Reservation ID", "Station Name", "Vehicle Number", "Status",
                        "Charging Cost", "Platform Fee", "Priority Fee",
                        "Cancellation Fee", "No Show Fee", "Station Commission",
                        "Station Owner Payout", "Total Payable", "Payment Status",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            csv_data = finance.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download finance CSV",
                csv_data,
                file_name="voltiq_finance_report.csv",
                mime="text/csv",
                use_container_width=True,
            )
    st.stop()


# ============================================================
# USER APP
# ============================================================
stations = get_station_data()
vehicles = load_table("vehicles", VEHICLE_COLUMNS)
my_vehicles = vehicles[vehicles["User ID"] == user_id]
reservations = load_table("reservations", RESERVATION_COLUMNS)
my_reservations = reservations[reservations["User ID"] == user_id]
favorites = load_table("favorites", FAVORITE_COLUMNS)
my_favorite_ids = favorites[favorites["User ID"] == user_id]["Station ID"].tolist()

if nav == "Discover":
    page_intro("Find your next charge", "Compare distance, connector compatibility, price and current bookable capacity.")
    l1, l2, l3 = st.columns([2, 2, 1])
    with l1:
        manual_area = st.selectbox("Starting area", list(LOCATIONS), index=list(LOCATIONS).index(user["Preferred Area"]) if user["Preferred Area"] in LOCATIONS else 0)
    with l2:
        if st.button("Use selected area", use_container_width=True):
            st.session_state.user_lat, st.session_state.user_lon = LOCATIONS[manual_area]
            st.rerun()
    with l3:
        if st.button("Use GPS", use_container_width=True):
            st.session_state.geo_requested = True
            st.rerun()

    if st.session_state.geo_requested:
        if get_geolocation is None:
            st.warning("GPS helper is unavailable. Use the area selector.")
        else:
            location = get_geolocation()
            coords = location.get("coords", location) if isinstance(location, dict) else {}
            if coords.get("latitude") is not None:
                st.session_state.user_lat = float(coords["latitude"])
                st.session_state.user_lon = float(coords["longitude"])
                st.session_state.geo_requested = False
                st.rerun()
            st.info("Allow location access in your browser, or use the area selector.")

    f1, f2, f3, f4 = st.columns(4)
    search = f1.text_input("Search station or area")
    connector_options = ["All"] + sorted(stations["Connector"].unique().tolist())
    connector = f2.selectbox("Connector", connector_options)
    charging_type = f3.selectbox("Charging type", ["All"] + sorted(stations["Charging Type"].unique().tolist()))
    sort_by = f4.selectbox("Sort by", ["Recommended", "Distance", "Price", "Rating", "Availability"])

    filtered = stations[stations["Status"] == "Online"].copy()
    if search.strip():
        query = search.strip()
        mask = (
            filtered["Station Name"].str.contains(query, case=False, na=False)
            | filtered["Area"].str.contains(query, case=False, na=False)
            | filtered["Network"].str.contains(query, case=False, na=False)
        )
        filtered = filtered[mask]
    if connector != "All":
        filtered = filtered[filtered["Connector"] == connector]
    if charging_type != "All":
        filtered = filtered[filtered["Charging Type"] == charging_type]

    if sort_by == "Distance" and filtered["Distance km"].notna().any():
        filtered = filtered.sort_values("Distance km")
    elif sort_by == "Price":
        filtered = filtered.sort_values("Price per kWh")
    elif sort_by == "Rating":
        filtered = filtered.sort_values("Display Rating", ascending=False)
    elif sort_by == "Availability":
        filtered = filtered.sort_values("Bookable Now", ascending=False)
    else:
        filtered["_distance"] = pd.to_numeric(filtered["Distance km"], errors="coerce").fillna(50)
        filtered["_score"] = (
            filtered["Bookable Now"] * 5
            + filtered["Display Rating"] * 3
            - filtered["Price per kWh"] * 0.1
            - filtered["_distance"] * 0.2
        )
        filtered = filtered.sort_values("_score", ascending=False)

    cols = st.columns(4)
    metrics = [
        ("Stations", len(filtered), "matching"),
        ("Bookable now", int(filtered["Bookable Now"].sum()) if not filtered.empty else 0, "connectors"),
        ("Best price", f"Rs. {filtered['Price per kWh'].min():.0f}" if not filtered.empty else "-", "per kWh"),
        ("Favourites", len(my_favorite_ids), "saved"),
    ]
    for col, metric in zip(cols, metrics):
        with col:
            kpi(*metric)

    if not filtered.empty:
        map_data = filtered.rename(columns={"Latitude": "lat", "Longitude": "lon"})[["lat", "lon"]]
        st.map(map_data, use_container_width=True)
        for _, row in filtered.iterrows():
            station_summary(row)
            c1, c2, c3 = st.columns([1, 1, 4])
            map_url = f"https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}"
            c1.link_button("Directions", map_url, use_container_width=True)
            fav_label = "Remove favourite" if row["Station ID"] in my_favorite_ids else "Add favourite"
            if c2.button(fav_label, key=f"fav-{row['Station ID']}", use_container_width=True):
                favorites = load_table("favorites", FAVORITE_COLUMNS)
                exists = (favorites["User ID"] == user_id) & (favorites["Station ID"] == row["Station ID"])
                if exists.any():
                    favorites = favorites[~exists]
                else:
                    new = [user_id, row["Station ID"], now_text()]
                    favorites = pd.concat([favorites, pd.DataFrame([new], columns=FAVORITE_COLUMNS)], ignore_index=True)
                save_table("favorites", favorites)
                st.rerun()
    else:
        st.warning("No stations match these filters.")

elif nav == "Book":
    page_intro("Reserve a charger", "Choose your charging details and see the full payable amount before booking.")
    if my_vehicles.empty:
        st.warning("Add a vehicle in Garage before making a reservation.")
    else:
        vehicle_number = st.selectbox("Vehicle", my_vehicles["Vehicle Number"].tolist())
        vehicle = my_vehicles[my_vehicles["Vehicle Number"] == vehicle_number].iloc[0]
        compatible = stations[
            (stations["Connector"] == vehicle["Connector"]) & (stations["Status"] == "Online")
        ].copy()
        station_names = compatible["Station Name"].tolist()

        if not station_names:
            st.warning("No online station is compatible with this vehicle connector.")
        else:
            station_name = st.selectbox("Compatible station", station_names)
            selected_station = compatible[compatible["Station Name"] == station_name].iloc[0]

            c1, c2, c3 = st.columns(3)
            booking_date = c1.date_input(
                "Date",
                min_value=date.today(),
                max_value=date.today() + timedelta(days=30),
            )
            booking_time = c2.time_input(
                "Start time",
                value=(datetime.now() + timedelta(hours=1)).replace(minute=0, second=0).time(),
            )
            duration = c3.selectbox(
                "Duration",
                [30, 60, 90, 120],
                format_func=lambda x: f"{x} minutes",
            )

            c4, c5 = st.columns(2)
            current_percent = c4.slider("Current battery", 0, 95, 25)
            target_percent = c5.slider("Target battery", 5, 100, 80)

            priority_selected = st.checkbox(
                "Add priority booking for Rs. 40",
                value=False,
                help="Optional add-on: priority bookings are promoted before normal queued bookings for the same time slot.",
            )
            priority_choice = PRIORITY_ADDON_LABEL if priority_selected else "No priority"
            priority_fee = PRIORITY_ADDON_FEE if priority_selected else 0
            payment = st.radio(
                "Payment",
                ["Demo online payment"],
                horizontal=True,
                help="In the real app, VoltIQ collects the full amount online and settles station-owner payouts monthly.",
            )
            accept_queue = st.checkbox("Join the queue automatically if this time slot is full", value=True)

            battery_kwh = float(vehicle["Battery Capacity kWh"] or EV_SPECS.get(vehicle["EV Model"], ("CCS2", 40))[1])
            energy, charging_cost = estimated_charge(
                battery_kwh, current_percent, target_percent, float(selected_station["Price per kWh"])
            )
            charges = booking_charges(charging_cost, priority_fee)
            st.subheader("Total Price Breakdown")
            fee_cols = st.columns(5)
            with fee_cols[0]:
                kpi("Charging Amount", f"Rs. {charges['charging_cost']:,.0f}", f"{energy} kWh")
            with fee_cols[1]:
                kpi("Reservation Fee", f"Rs. {charges['reservation_fee']:,.0f}", "10%")
            with fee_cols[2]:
                kpi("Priority Fee", f"Rs. {charges['priority_fee']:,.0f}", "Optional")
            with fee_cols[3]:
                kpi("Total Payable", f"Rs. {charges['total_payable']:,.0f}", "Payable now")
            with fee_cols[4]:
                kpi("No-show Penalty", f"Rs. {charges['no_show_fee']:,.0f}", "If applicable")

            if st.button("Confirm reservation", use_container_width=True):
                start_at = datetime.combine(booking_date, booking_time)
                end_at = start_at + timedelta(minutes=duration)
                fresh_reservations = load_table("reservations", RESERVATION_COLUMNS)
                duplicate = fresh_reservations[
                    (fresh_reservations["User ID"] == user_id)
                    & (fresh_reservations["Vehicle Number"] == vehicle_number)
                    & (fresh_reservations["Status"].isin(["Confirmed", "Queued", "Charging"]))
                ].copy()
                duplicate_overlap = False
                if not duplicate.empty:
                    dup_starts = pd.to_datetime(duplicate["Start At"], errors="coerce")
                    dup_ends = pd.to_datetime(duplicate["End At"], errors="coerce")
                    duplicate_overlap = bool(((dup_starts < end_at) & (dup_ends > start_at)).any())

                status, remaining = slot_status(selected_station, fresh_reservations, start_at, end_at)
                if start_at < datetime.now():
                    st.error("Select a future time.")
                elif target_percent <= current_percent:
                    st.error("Target battery must be higher than current battery.")
                elif duplicate_overlap:
                    st.error("This vehicle already has an overlapping reservation.")
                elif status == "Queued" and not accept_queue:
                    st.warning("That slot is full. Choose another time or allow queueing.")
                else:
                    reservation_id = uid("VQ")
                    payment_status = "Collected online by VoltIQ (Demo)"
                    row = [
                        reservation_id, user_id, user["Name"], vehicle_number, vehicle["EV Model"],
                        user["Phone"], selected_station["Station ID"], selected_station["Station Name"],
                        start_at.strftime("%Y-%m-%d %H:%M:%S"), end_at.strftime("%Y-%m-%d %H:%M:%S"),
                        duration, vehicle["Connector"], status, payment_status,
                        charges["charging_cost"], charges["platform_fee"], charges["priority_fee"],
                        charges["cancellation_fee"], charges["no_show_fee"],
                        charges["station_commission"], charges["station_owner_payout"],
                        charges["total_payable"], priority_choice,
                        "", charges["total_payable"], now_text(), now_text(),
                    ]
                    fresh_reservations = pd.concat(
                        [fresh_reservations, pd.DataFrame([row], columns=RESERVATION_COLUMNS)],
                        ignore_index=True,
                    )
                    save_table("reservations", fresh_reservations)
                    add_notification(
                        user_id,
                        f"Reservation {status.lower()}",
                        f"{reservation_id} at {selected_station['Station Name']} on {start_at:%d %b, %I:%M %p}.",
                    )
                    st.success(f"Reservation {status.lower()}. Reference: {reservation_id}")
                    st.rerun()

elif nav == "My trips":
    page_intro("My trips", "Review, reschedule, cancel and download receipts for your reservations.")
    if my_reservations.empty:
        st.info("You have no reservations yet.")
    else:
        my_reservations = my_reservations.copy()
        my_reservations["_start"] = pd.to_datetime(my_reservations["Start At"], errors="coerce")
        my_reservations = my_reservations.sort_values("_start", ascending=False)
        status_filter = st.multiselect(
            "Show status", ["Confirmed", "Queued", "Arrived", "Charging", "Completed", "Cancelled", "No Show"],
            default=["Confirmed", "Queued", "Arrived", "Charging", "Completed"],
        )
        shown = my_reservations[my_reservations["Status"].isin(status_filter)]
        st.dataframe(
            shown[
                [
                    "Reservation ID", "Station Name", "Vehicle Number", "Start At", "End At",
                    "Status", "Payment Status", "Charging Cost", "Platform Fee",
                    "Priority Fee", "Total Payable",
                ]
            ],
            use_container_width=True, hide_index=True,
        )
        active = my_reservations[my_reservations["Status"].isin(["Confirmed", "Queued", "Arrived"])]
        if not active.empty:
            selected_id = st.selectbox("Manage reservation", active["Reservation ID"].tolist())
            selected = active[active["Reservation ID"] == selected_id].iloc[0]
            c1, c2 = st.columns(2)
            if c1.button("Cancel", use_container_width=True):
                all_reservations = load_table("reservations", RESERVATION_COLUMNS)
                idx = all_reservations[all_reservations["Reservation ID"] == selected_id].index[0]
                all_reservations.at[idx, "Status"] = "Cancelled"
                all_reservations.at[idx, "Payment Status"] = "Cancelled - refund initiated"
                clear_charging_amounts_for_penalty(all_reservations, idx, 0)
                all_reservations.at[idx, "Updated At"] = now_text()
                save_table("reservations", all_reservations)
                add_notification(
                    user_id,
                    "Reservation cancelled",
                    f"{selected_id} has been cancelled. Refund has been initiated.",
                )
                promote_queue(selected["Station ID"])
                st.rerun()
            c2.download_button(
                "Download receipt", reservation_receipt(selected),
                file_name=f"{selected_id}-receipt.txt", mime="text/plain", use_container_width=True,
            )
            with st.expander("Reschedule"):
                new_date = st.date_input("New date", min_value=date.today(), key="reschedule_date")
                new_time = st.time_input("New time", key="reschedule_time")
                if st.button("Save new time", use_container_width=True):
                    all_reservations = load_table("reservations", RESERVATION_COLUMNS)
                    all_stations = numeric_stations(load_table("stations", STATION_COLUMNS))
                    station = all_stations[all_stations["Station ID"] == selected["Station ID"]].iloc[0]
                    start_at = datetime.combine(new_date, new_time)
                    end_at = start_at + timedelta(minutes=int(float(selected["Duration Minutes"])))
                    status, _ = slot_status(station, all_reservations, start_at, end_at, selected_id)
                    idx = all_reservations[all_reservations["Reservation ID"] == selected_id].index[0]
                    all_reservations.at[idx, "Start At"] = start_at.strftime("%Y-%m-%d %H:%M:%S")
                    all_reservations.at[idx, "End At"] = end_at.strftime("%Y-%m-%d %H:%M:%S")
                    all_reservations.at[idx, "Status"] = status
                    all_reservations.at[idx, "Updated At"] = now_text()
                    save_table("reservations", all_reservations)
                    promote_queue(selected["Station ID"])
                    add_notification(user_id, "Reservation rescheduled", f"{selected_id} is now {status.lower()} for {start_at:%d %b, %I:%M %p}.")
                    st.rerun()

        completed = my_reservations[my_reservations["Status"] == "Completed"]
        if not completed.empty:
            st.subheader("Rate a completed trip")
            review_reservation = st.selectbox("Completed reservation", completed["Reservation ID"].tolist())
            with st.form("review_form"):
                rating = st.slider("Rating", 1, 5, 5)
                comment = st.text_area("Review")
                submit_review = st.form_submit_button("Submit review")
            if submit_review:
                reviews = load_table("reviews", REVIEW_COLUMNS)
                if review_reservation in reviews["Reservation ID"].tolist():
                    st.warning("You already reviewed this reservation.")
                else:
                    trip = completed[completed["Reservation ID"] == review_reservation].iloc[0]
                    row = [uid("R"), user_id, trip["Station ID"], review_reservation, rating, comment.strip(), now_text()]
                    reviews = pd.concat([reviews, pd.DataFrame([row], columns=REVIEW_COLUMNS)], ignore_index=True)
                    save_table("reviews", reviews)
                    st.success("Review submitted.")

elif nav == "Garage":
    page_intro("My garage", "Save EV specifications once and show only compatible charging stations.")
    if not my_vehicles.empty:
        st.dataframe(my_vehicles, use_container_width=True, hide_index=True)
    with st.form("vehicle_form"):
        number = st.text_input("Vehicle number").upper().strip()
        model = st.selectbox("EV model", list(EV_SPECS))
        default_connector, default_capacity = EV_SPECS[model]
        c1, c2 = st.columns(2)
        connector = c1.selectbox("Connector", ["CCS2", "Type 2", "CHAdeMO"], index=["CCS2", "Type 2", "CHAdeMO"].index(default_connector) if default_connector in ["CCS2", "Type 2", "CHAdeMO"] else 0)
        capacity = c2.number_input("Battery capacity (kWh)", 5.0, 200.0, float(default_capacity), 0.5)
        battery_type = st.selectbox("Battery type", ["LFP", "NMC", "Lithium-ion", "Other"])
        add_vehicle = st.form_submit_button("Add vehicle", use_container_width=True)
    if add_vehicle:
        fresh = load_table("vehicles", VEHICLE_COLUMNS)
        exists = (fresh["User ID"] == user_id) & (fresh["Vehicle Number"].str.upper() == number)
        if not re.fullmatch(r"[A-Z0-9 -]{5,15}", number):
            st.error("Enter a valid vehicle number.")
        elif exists.any():
            st.error("This vehicle is already in your garage.")
        else:
            row = [uid("VH"), user_id, number, model, connector, battery_type, capacity, now_text()]
            fresh = pd.concat([fresh, pd.DataFrame([row], columns=VEHICLE_COLUMNS)], ignore_index=True)
            save_table("vehicles", fresh)
            st.success("Vehicle added.")
            st.rerun()
    if not my_vehicles.empty:
        remove_number = st.selectbox("Remove vehicle", my_vehicles["Vehicle Number"].tolist())
        if st.button("Remove selected vehicle"):
            fresh = load_table("vehicles", VEHICLE_COLUMNS)
            active = my_reservations[
                (my_reservations["Vehicle Number"] == remove_number)
                & (my_reservations["Status"].isin(["Confirmed", "Queued", "Charging"]))
            ]
            if not active.empty:
                st.error("Cancel active reservations for this vehicle first.")
            else:
                fresh = fresh[~((fresh["User ID"] == user_id) & (fresh["Vehicle Number"] == remove_number))]
                save_table("vehicles", fresh)
                st.rerun()

elif nav == "Charging":
    page_intro("Charging sessions", "Mark arrival, start charging and finish your charging session.")
    current = my_reservations[my_reservations["Status"].isin(["Confirmed", "Arrived", "Charging"])]
    if current.empty:
        st.info("No confirmed or active charging sessions.")
    else:
        selected_id = st.selectbox("Reservation", current["Reservation ID"].tolist())
        trip = current[current["Reservation ID"] == selected_id].iloc[0]
        st.write(f"**{trip['Station Name']}** · {trip['Vehicle Number']} · {trip['Start At']}")
        start_at = parse_dt(trip["Start At"])
        if pd.notna(start_at):
            deadline = start_at.to_pydatetime() + timedelta(minutes=30)
            st.caption(f"Arrival deadline for avoiding no-show: {deadline:%Y-%m-%d %H:%M}")
        sessions = load_table("sessions", SESSION_COLUMNS)
        session_match = sessions[sessions["Reservation ID"] == selected_id]
        if trip["Status"] == "Confirmed":
            st.info("First mark that you have reached the station. Charging can be started after arrival.")
            if st.button("I have reached the station", use_container_width=True):
                all_reservations = load_table("reservations", RESERVATION_COLUMNS)
                idx = all_reservations[all_reservations["Reservation ID"] == selected_id].index[0]
                all_reservations.at[idx, "Status"] = "Arrived"
                all_reservations.at[idx, "Arrived At"] = now_text()
                all_reservations.at[idx, "Updated At"] = now_text()
                save_table("reservations", all_reservations)
                add_notification(user_id, "Arrival confirmed", f"You marked arrival at {trip['Station Name']}.")
                st.rerun()
        elif trip["Status"] == "Arrived":
            st.success(f"Arrived at: {trip['Arrived At']}")
            if st.button("Start charging now", use_container_width=True):
                all_reservations = load_table("reservations", RESERVATION_COLUMNS)
                idx = all_reservations[all_reservations["Reservation ID"] == selected_id].index[0]
                all_reservations.at[idx, "Status"] = "Charging"
                all_reservations.at[idx, "Updated At"] = now_text()
                save_table("reservations", all_reservations)
                row = [uid("S"), selected_id, user_id, trip["Station ID"], trip["Vehicle Number"], now_text(), "", 0, 0, "Charging"]
                sessions = pd.concat([sessions, pd.DataFrame([row], columns=SESSION_COLUMNS)], ignore_index=True)
                save_table("sessions", sessions)
                add_notification(user_id, "Charging started", f"Session started at {trip['Station Name']}.")
                st.rerun()
        elif trip["Status"] == "Charging":
            station = stations[stations["Station ID"] == trip["Station ID"]].iloc[0]
            energy = st.number_input(
                "Energy delivered (kWh)",
                min_value=0.1,
                max_value=200.0,
                value=10.0,
                step=0.5,
                key=f"energy_delivered_{selected_id}",
            )
            actual_charging_cost = round(energy * float(station["Price per kWh"]), 2)
            existing_priority_fee = float(
                pd.to_numeric(pd.Series([trip["Priority Fee"]]), errors="coerce").fillna(0).iloc[0]
            )
            final_charges = booking_charges(actual_charging_cost, existing_priority_fee)

            st.subheader("Final Price Breakdown")
            final_cols = st.columns(5)
            with final_cols[0]:
                kpi("Charging Amount", f"Rs. {final_charges['charging_cost']:,.0f}", f"{energy} kWh")
            with final_cols[1]:
                kpi("Reservation Fee", f"Rs. {final_charges['reservation_fee']:,.0f}", "10%")
            with final_cols[2]:
                kpi("Priority Fee", f"Rs. {final_charges['priority_fee']:,.0f}", "Optional")
            with final_cols[3]:
                kpi("Station Payout", f"Rs. {final_charges['station_owner_payout']:,.0f}", "Monthly settlement")
            with final_cols[4]:
                kpi("Final Payable", f"Rs. {final_charges['total_payable']:,.0f}", "Total")

            if st.button("Finish charging", use_container_width=True):
                all_reservations = load_table("reservations", RESERVATION_COLUMNS)
                reservation_updates = {
                    "Status": "Completed",
                    "Charging Cost": final_charges["charging_cost"],
                    "Platform Fee": final_charges["platform_fee"],
                    "Priority Fee": final_charges["priority_fee"],
                    "Cancellation Fee": final_charges["cancellation_fee"],
                    "No Show Fee": final_charges["no_show_fee"],
                    "Station Commission": final_charges["station_commission"],
                    "Station Owner Payout": final_charges["station_owner_payout"],
                    "Total Payable": final_charges["total_payable"],
                    "Estimated Cost": final_charges["total_payable"],
                    "Updated At": now_text(),
                }
                reservation_records = all_reservations.to_dict("records")
                for record in reservation_records:
                    if record.get("Reservation ID") == selected_id:
                        for column, value in reservation_updates.items():
                            record[column] = str(value)
                all_reservations = pd.DataFrame(reservation_records, columns=RESERVATION_COLUMNS)
                save_table("reservations", all_reservations)
                sessions = load_table("sessions", SESSION_COLUMNS)
                if session_match.empty:
                    row = [
                        uid("S"), selected_id, user_id, trip["Station ID"], trip["Vehicle Number"],
                        now_text(), now_text(), energy, final_charges["total_payable"], "Completed",
                    ]
                    sessions = pd.concat([sessions, pd.DataFrame([row], columns=SESSION_COLUMNS)], ignore_index=True)
                else:
                    sidx = sessions[sessions["Reservation ID"] == selected_id].index[-1]
                    sessions.at[sidx, "Ended At"] = now_text()
                    sessions.at[sidx, "Energy kWh"] = energy
                    sessions.at[sidx, "Amount"] = final_charges["total_payable"]
                    sessions.at[sidx, "Status"] = "Completed"
                save_table("sessions", sessions)
                add_notification(
                    user_id,
                    "Charging complete",
                    f"{energy} kWh delivered. Final amount: Rs. {final_charges['total_payable']}.",
                )
                promote_queue(trip["Station ID"])
                st.rerun()
    history = load_table("sessions", SESSION_COLUMNS)
    history = history[history["User ID"] == user_id]
    if not history.empty:
        st.subheader("Session history")
        st.dataframe(history, use_container_width=True, hide_index=True)

elif nav == "Notifications":
    page_intro("Notifications", "Booking, queue and charging updates in one place.")
    notifications = load_table("notifications", NOTIFICATION_COLUMNS)
    mine = notifications[notifications["User ID"] == user_id].copy()
    if mine.empty:
        st.info("No notifications.")
    else:
        mine["_created"] = pd.to_datetime(mine["Created At"], errors="coerce")
        mine = mine.sort_values("_created", ascending=False)
        for _, item in mine.iterrows():
            unread = "● " if item["Read"] != "Yes" else ""
            st.markdown(f"**{unread}{item['Title']}**  \n{item['Message']}  \n`{item['Created At']}`")
            st.divider()
        if st.button("Mark all as read"):
            mask = notifications["User ID"] == user_id
            notifications.loc[mask, "Read"] = "Yes"
            save_table("notifications", notifications)
            st.rerun()

elif nav == "Profile":
    page_intro("Profile", "Keep your contact details, preferred area and password up to date.")
    users = load_table("users", USER_COLUMNS)
    idx = users[users["User ID"] == user_id].index[0]
    with st.form("profile_form"):
        name = st.text_input("Name", value=user["Name"])
        phone = st.text_input("Mobile number", value=user["Phone"])
        area = st.selectbox("Preferred area", list(LOCATIONS), index=list(LOCATIONS).index(user["Preferred Area"]) if user["Preferred Area"] in LOCATIONS else 0)
        save_profile = st.form_submit_button("Save profile", use_container_width=True)
    if save_profile:
        if not phone.isdigit() or len(phone) != 10:
            st.error("Enter a valid 10-digit mobile number.")
        else:
            users.at[idx, "Name"] = name.strip()
            users.at[idx, "Phone"] = phone
            users.at[idx, "Preferred Area"] = area
            save_table("users", users)
            st.session_state.user = users.loc[idx].to_dict()
            st.success("Profile updated.")
            st.rerun()
    with st.expander("Change password"):
        with st.form("password_form"):
            current_password = st.text_input("Current password", type="password")
            new_password = st.text_input("New password", type="password")
            confirm = st.text_input("Confirm new password", type="password")
            change = st.form_submit_button("Change password")
        if change:
            strong = len(new_password) >= 8 and re.search(r"[A-Z]", new_password) and re.search(r"[a-z]", new_password) and re.search(r"\d", new_password)
            if not verify_password(current_password, users.at[idx, "Password Hash"]):
                st.error("Current password is incorrect.")
            elif not strong:
                st.error("Use at least 8 characters with uppercase, lowercase and a number.")
            elif new_password != confirm:
                st.error("New passwords do not match.")
            else:
                users.at[idx, "Password Hash"] = pbkdf2_hash(new_password)
                save_table("users", users)
                st.success("Password changed.")
