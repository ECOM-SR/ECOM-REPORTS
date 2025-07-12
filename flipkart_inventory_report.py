import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📦 Flipkart Inventory Dashboard", layout="wide")
st.title("📦 Flipkart Inventory Report Dashboard")

uploaded_file = st.file_uploader("Upload Flipkart Inventory Report (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file:
    # Read file
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)

    # Clean up numeric columns
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0).astype(int)
    df["average_daily_sales"] = pd.to_numeric(df["average_daily_sales"], errors="coerce").fillna(0)
    df["days_stock_will_last"] = pd.to_numeric(df["days_stock_will_last"], errors="coerce").fillna(0)

    # Key Metrics
    total_skus = df["sku"].nunique()
    total_stock = df["stock_quantity"].sum()
    avg_daily_sales = df["average_daily_sales"].mean().round(2)
    low_stock_count = df[df["days_stock_will_last"] <= 7].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total SKUs", f"{total_skus}")
    col2.metric("📊 Total Stock Quantity", f"{total_stock}")
    col3.metric("📈 Avg. Daily Sales", f"{avg_daily_sales}")
    col4.metric("⏳ SKUs with < 7 Days Stock", f"{low_stock_count}")

    # 🔥 SKUs with lowest stock cover
    st.subheader("⚠️ Low Stock Alert (≤ 7 Days Cover)")
    low_stock = df[df["days_stock_will_last"] <= 7].sort_values(by="days_stock_will_last")
    st.dataframe(low_stock.head(10), use_container_width=True)

    # 📋 Raw Data View
    with st.expander("📋 View Full Inventory Data"):
        st.dataframe(df, use_container_width=True)
