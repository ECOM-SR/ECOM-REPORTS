import streamlit as st
import os

# Set page config once at the top

st.sidebar.title("📦 Flipkart Reports Dashboard")

# Sidebar menu
selected_report = st.sidebar.radio(
    "Select Report Type",
    ["📦 Order Report", "↩️ Return Report"]
)

# Utility function to run a Streamlit script
def run_script(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, globals())

# Run appropriate script
if selected_report == "📦 Order Report":
    run_script("flipkart_order.py")

elif selected_report == "↩️ Return Report":
    run_script("flipkart_returns_report.py")
