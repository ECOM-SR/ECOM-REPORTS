import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🛍️ Myntra Order Report Dashboard")

uploaded_file = st.file_uploader("📄 Upload Myntra Order Report (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
    
    df['created on'] = pd.to_datetime(df['created on'], errors='coerce')
    df['delivered on'] = pd.to_datetime(df['delivered on'], errors='coerce')

    st.subheader("📊 Summary Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Total Orders", len(df))
    col2.metric("Delivered Orders", df['order status'].str.lower().eq("delivered").sum())

    st.divider()

    st.subheader("📅 Order Trend by Date")
    daily_orders = df.groupby(df['created on'].dt.date).size().reset_index(name='orders')
    fig = px.line(daily_orders, x='created on', y='orders', title="Orders Over Time")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💰 Revenue & Discounts")
    df['final amount'] = pd.to_numeric(df['final amount'], errors='coerce')
    df['discount'] = pd.to_numeric(df['discount'], errors='coerce')
    df['coupon discount'] = pd.to_numeric(df['coupon discount'], errors='coerce')
    revenue = df['final amount'].sum()
    discount = df['discount'].sum() + df['coupon discount'].sum()
    col1, col2 = st.columns(2)
    col1.metric("Total Revenue", f"₹{revenue:,.2f}")
    col2.metric("Total Discounts", f"₹{discount:,.2f}")

    st.subheader("🎯 Top 10 Selling Styles")
    top_styles = df['style name'].value_counts().head(10).reset_index()
    top_styles.columns = ['Style Name', 'Orders']
    st.dataframe(top_styles)

    st.subheader("📍 Orders by State")
    state_dist = df['state'].value_counts().reset_index()
    state_dist.columns = ['State', 'Orders']
    fig2 = px.bar(state_dist, x='State', y='Orders', title="Orders by State")
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Please upload a valid Myntra order report to view insights.")
