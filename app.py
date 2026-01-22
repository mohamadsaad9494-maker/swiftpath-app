import streamlit as st
import pandas as pd
import os
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# ---------------- CONFIG ----------------
DB_FILE = "orders.csv"
ADMIN_PASSWORD = "SP-ADMIN-001"

st.set_page_config("SwiftPath MVP", layout="wide", page_icon="🚚")

# ---------------- UTILITIES ----------------
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return round(6371 * c, 2)  # km

def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=[
            "ID","Customer","Phone","Cash",
            "Lat","Lon","Status","Timestamp"
        ])
        df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE)

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# ---------------- DATA ----------------
df = load_data()

# ---------------- UI ----------------
st.title("🚀 SwiftPath – Field Logistics MVP")

tab1, tab2, tab3 = st.tabs([
    "📲 Driver",
    "🔐 Admin",
    "📊 History"
])

# ---------------- DRIVER ----------------
with tab1:
    st.subheader("🚚 Driver Dashboard")

    st.markdown("### 📍 Your Current Location")
    d_lat = st.number_input("Latitude", value=33.89, key="dlat")
    d_lon = st.number_input("Longitude", value=35.50, key="dlon")

    pending = df[df["Status"] == "Pending"].copy()

    if pending.empty:
        st.success("No pending orders.")
    else:
        pending["Distance (km)"] = pending.apply(
            lambda r: haversine(d_lat, d_lon, r["Lat"], r["Lon"]),
            axis=1
        )
        pending = pending.sort_values("Distance (km)")

        st.markdown("### 🧭 Next Best Deliveries")

        for i, row in pending.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2,2,1,1])

                c1.markdown(f"**{row['Customer']}**")
                c2.markdown(f"📏 {row['Distance (km)']} km")
                c3.markdown(f"💵 ${row['Cash']}")

                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={row['Lat']},{row['Lon']}"
                c4.markdown(f"[🚗 Navigate]({maps_url})")

                if st.button("✅ Delivered", key=f"done_{row['ID']}"):
                    df.loc[df["ID"] == row["ID"], "Status"] = "Delivered"
                    df.loc[df["ID"] == row["ID"], "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    save_data(df)
                    st.rerun()

                st.markdown(f"[📞 Call {row['Phone']}](tel:{row['Phone']})")
                st.divider()

# ---------------- ADMIN ----------------
with tab2:
    st.subheader("🔐 Admin Panel")
    pwd = st.text_input("Password", type="password")

    if pwd == ADMIN_PASSWORD:
        with st.form("add"):
            name = st.text_input("Customer")
            phone = st.text_input("Phone")
            cash = st.number_input("Cash", min_value=0.0)
            lat = st.number_input("Latitude")
            lon = st.number_input("Longitude")

            if st.form_submit_button("➕ Add Order"):
                new = {
                    "ID": len(df) + 1,
                    "Customer": name,
                    "Phone": phone,
                    "Cash": cash,
                    "Lat": lat,
                    "Lon": lon,
                    "Status": "Pending",
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                save_data(df)
                st.success("Order added")
                st.rerun()
    elif pwd:
        st.error("Wrong password")

# ---------------- HISTORY ----------------
with tab3:
    st.subheader("📊 Delivery History")
    st.dataframe(df[df["Status"] == "Delivered"], use_container_width=True)
