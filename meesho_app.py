import streamlit as st
import pandas as pd
import plotly.express as px

# Setup
st.title("🛍️ Meesho Sales Report Dashboard")

# Upload file
uploaded_file = st.file_uploader("📄 Upload Meesho Order Report (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip()

    # Parse date
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

    # Metrics
    st.subheader("📊 Summary Metrics")
    total_orders = len(df)
    total_units = df['Quantity'].sum() if 'Quantity' in df.columns else 0
    total_sales = pd.to_numeric(df.get('Supplier Discounted Price (Incl GST and Commision)', 0), errors='coerce').sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Units Sold", int(total_units))
    col3.metric("Total Sales", f"₹{total_sales:,.2f}")

    st.divider()

    # Orders over time
    if 'Order Date' in df.columns:
        st.subheader("📅 Orders Over Time")
        daily_orders = df.groupby(df['Order Date'].dt.date).size().reset_index(name='Orders')
        fig = px.line(daily_orders, x='Order Date', y='Orders', title="Orders Over Time")
        st.plotly_chart(fig, use_container_width=True)

    # Orders by state
    if 'Customer State' in df.columns:
        st.subheader("📍 Orders by State")
        state_data = df['Customer State'].value_counts().reset_index()
        state_data.columns = ['State', 'Orders']
        fig2 = px.bar(state_data, x='State', y='Orders', title="Orders by State")
        st.plotly_chart(fig2, use_container_width=True)

    # Top products
    if 'Product Name' in df.columns:
        st.subheader("🏆 Top 10 Products")
        top_products = df['Product Name'].value_counts().head(10).reset_index()
        top_products.columns = ['Product Name', 'Orders']
        st.dataframe(top_products)

    # Return/Credit reasons
    if 'Reason for Credit Entry' in df.columns:
        st.subheader("📦 Return Reasons")
        reasons = df['Reason for Credit Entry'].dropna().value_counts().reset_index()
        reasons.columns = ['Reason', 'Count']
        fig3 = px.pie(reasons, names='Reason', values='Count', title="Reasons for Credit Entry")
        st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Please upload a valid Meesho report file.")
