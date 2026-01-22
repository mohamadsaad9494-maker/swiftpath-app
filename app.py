import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- الإعدادات والأمان ---
ADMIN_PASSWORD = "SP-961-Admin#Global"
DB_FILE = "logistics_orders.csv"

st.set_page_config(page_title="SwiftPath Pro", layout="wide", page_icon="🚀")

# --- إدارة قاعدة البيانات ---
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["ID", "Customer", "Phone", "Cash", "Status", "Timestamp"])
    df.to_csv(DB_FILE, index=False)

def load_data():
    return pd.read_csv(DB_FILE)

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- الواجهة الرئيسية ---
st.title("🚚 SwiftPath Logistics Pro")
tab1, tab2, tab3 = st.tabs(["📲 Driver Dashboard", "🔐 Admin Control", "📊 History"])

df = load_data()

# --- 1. لوحة السائق ---
with tab1:
    st.subheader("Current Tasks")
    pending_orders = df[df['Status'] == 'Pending']
    
    if pending_orders.empty:
        st.success("No pending orders. Take a break! ☕")
    else:
        for index, row in pending_orders.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                col1.write(f"**Customer:** {row['Customer']}")
                col2.write(f"**Cash:** ${row['Cash']}")
                
                # زر الاتصال وزر التسليم
                if col3.button(f"✅ Delivered", key=f"del_{index}"):
                    df.at[index, 'Status'] = 'Delivered'
                    df.at[index, 'Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    save_data(df)
                    st.rerun()
                
                st.markdown(f"[📞 Call {row['Phone']}](tel:{row['Phone']})")
                st.divider()

# --- 2. لوحة المدير ---
with tab2:
    pwd = st.text_input("Security Key", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Authorized Access")
        with st.form("add_order", clear_on_submit=True):
            c_name = st.text_input("Customer Name")
            c_phone = st.text_input("Phone Number")
            c_cash = st.number_input("Amount ($)", min_value=0.0)
            if st.form_submit_button("Send to Driver"):
                new_order = pd.DataFrame([{
                    "ID": len(df) + 1,
                    "Customer": c_name,
                    "Phone": c_phone,
                    "Cash": c_cash,
                    "Status": "Pending",
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                df = pd.concat([df, new_order], ignore_index=True)
                save_data(df)
                st.rerun()
    elif pwd != "":
        st.error("Invalid Key")

# --- 3. سجل العمليات ---
with tab3:
    st.subheader("Completed Deliveries")
    delivered_orders = df[df['Status'] == 'Delivered']
    st.dataframe(delivered_orders, use_container_width=True)
