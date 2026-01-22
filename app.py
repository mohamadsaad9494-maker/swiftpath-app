import streamlit as st
import pandas as pd
import os

# --- 🔐 Security ---
ADMIN_PASSWORD = "SP-961-Admin#Global" 

st.set_page_config(page_title="SwiftPath Logistics", layout="wide", page_icon="🚚")

# --- 📂 Database Setup ---
DB_FILE = "logistics_db.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["Customer", "Phone", "Cash", "Status"]).to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE)

# --- 🖥️ Interface ---
st.title("🚚 SwiftPath Logistics Hub")
st.info("CEO Smart Management System")

tab1, tab2 = st.tabs(["📲 Driver Console", "🔐 Admin Hub"])

with tab1:
    st.subheader("Pending Deliveries")
    pending = df[df['Status'] == 'Pending']
    if not pending.empty:
        st.dataframe(pending, use_container_width=True)
    else:
        st.success("Great job! All orders delivered.")

with tab2:
    st.subheader("Control Center")
    pwd = st.text_input("Enter Company Key", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Welcome back, CEO")
        with st.form("new_order", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Customer Name")
            phone = col2.text_input("Phone Number")
            cash = st.number_input("Amount to Collect ($)", min_value=0.0)
            if st.form_submit_button("Add to Fleet"):
                new_data = pd.DataFrame([{"Customer": name, "Phone": phone, "Cash": cash, "Status": "Pending"}])
                pd.concat([df, new_data], ignore_index=True).to_csv(DB_FILE, index=False)
                st.rerun()
    elif pwd != "":
        st.error("Access Denied: Incorrect Security Key")
