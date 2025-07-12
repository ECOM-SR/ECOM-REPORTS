import streamlit as st
from amazon_order import process_order_report
from amazon_return import process_return_report

st.sidebar.title("📦 Amazon Ecom Reports")
selected_report = st.sidebar.radio(
    "Select Report Type",
    ["Order Report", "Return Report"]
)

if selected_report == "Order Report":
    process_order_report()
elif selected_report == "Return Report":
    process_return_report()
