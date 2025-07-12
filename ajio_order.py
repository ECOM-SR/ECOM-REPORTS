import streamlit as st
import pandas as pd

def analyze_ajio_report(file_path):
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()

        required_columns = [
            'Status', 'Total Value', 'CGST_AMOUNT', 'SGST_AMOUNT', 'IGST_AMOUNT',
            'Listing MRP', 'Selling Price', 'Seller SKU', 'Order Qty',
            'Customer Cancelled QTY', 'Seller Cancelled QTY', 'SLA Status', 'Description'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return None

        numeric_cols = [
            'Total Value', 'CGST_AMOUNT', 'SGST_AMOUNT', 'IGST_AMOUNT', 
            'Listing MRP', 'Selling Price', 'Order Qty', 
            'Customer Cancelled QTY', 'Seller Cancelled QTY'
        ]
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Convert dates if available
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
            sales_by_day = df.groupby(df['Order Date'].dt.date)['Total Value'].sum()
            orders_by_day = df.groupby(df['Order Date'].dt.date).size()
        else:
            sales_by_day = pd.Series([], dtype=float)
            orders_by_day = pd.Series([], dtype=int)

        total_orders = len(df)
        cancelled_orders = len(df[df['Status'].str.contains('Cancelled', na=False)])
        total_sales = df['Total Value'].sum()
        total_tax = df['CGST_AMOUNT'].sum() + df['SGST_AMOUNT'].sum() + df['IGST_AMOUNT'].sum()
        total_discounts = df['Listing MRP'].sum() - df['Selling Price'].sum()
        customer_cancellations = df['Customer Cancelled QTY'].sum()
        seller_cancellations = df['Seller Cancelled QTY'].sum()
        on_time_shipments = len(df[df['SLA Status'].str.contains('On Time', na=False)])
        delayed_shipments = len(df[df['SLA Status'].str.contains('Delayed', na=False)])

        # Top SKUs
        top_selling = df.groupby(['Seller SKU', 'Description'])['Order Qty'].sum().sort_values(ascending=False).head(10).reset_index()
        slow_moving = df.groupby(['Seller SKU', 'Description'])['Order Qty'].sum().sort_values().head(10).reset_index()

        # Cancelled and sales summary
        sku_summary = df.groupby(['Seller SKU', 'Description']).agg({
            'Order Qty': 'sum',
            'Customer Cancelled QTY': 'sum',
            'Total Value': 'sum'
        }).reset_index().sort_values(by='Order Qty', ascending=False)

        # Dashboard
        st.title("✅ Ajio Order Report Analysis")

        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Total Orders", total_orders)
        col2.metric("❌ Cancelled Orders", cancelled_orders)
        col3.metric("💰 Total Sales", f"₹{total_sales:,.2f}")

        col4, col5, col6 = st.columns(3)
        col4.metric("🧾 Total Tax", f"₹{total_tax:,.2f}")
        col5.metric("🏷️ Discounts", f"₹{total_discounts:,.2f}")
        col6.metric("🙍 Customer Cancellations", int(customer_cancellations))

        col7, col8, col9 = st.columns(3)
        col7.metric("🏭 Seller Cancellations", int(seller_cancellations))
        col8.metric("⏱️ On-Time Shipments", on_time_shipments)
        col9.metric("🐌 Delayed Shipments", delayed_shipments)

        st.subheader("🔥 Top 10 Best-Selling SKUs")
        st.dataframe(top_selling.rename(columns={"Order Qty": "Total Orders"}))

        st.subheader("❄️ Top 10 Slow-Moving SKUs")
        st.dataframe(slow_moving.rename(columns={"Order Qty": "Total Orders"}))

        st.subheader("📦 SKU Summary (Orders, Cancelled, Sales)")
        st.dataframe(sku_summary.rename(columns={
            'Order Qty': 'Total Orders',
            'Customer Cancelled QTY': 'Cancelled Qty',
            'Total Value': 'Sales (₹)'
        }))

        # Charts
        if not sales_by_day.empty:
            st.subheader("📈 Sales by Day")
            st.line_chart(sales_by_day)

        if not orders_by_day.empty:
            st.subheader("📅 Number of Orders by Day")
            st.bar_chart(orders_by_day)

    except Exception as e:
        st.error(f"Error: {e}")

# Streamlit UI
st.set_page_config(page_title="Ajio Order Report", layout="wide")
st.title("📊 Ajio Order Report Uploader")

uploaded_file = st.file_uploader("Upload your Ajio Excel report", type=["xlsx"])

if uploaded_file is not None:
    analyze_ajio_report(uploaded_file)
