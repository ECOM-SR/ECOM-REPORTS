import streamlit as st
import pandas as pd
import plotly.express as px
st.title("📦 Flipkart Order Lifecycle Dashboard")

uploaded_file = st.file_uploader("Upload Flipkart Order Report (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file:
    # Load data
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)

    # Convert date columns
    date_columns = [
        "order_date", "order_approval_date", "order_cancellation_date",
        "order_return_approval_date", "dispatched_date", "order_delivery_date"
    ]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Fill missing titles if needed
    if "product_title" in df.columns:
        df["product_title"] = df["product_title"].fillna("Unknown Product")

    # Date filter
    if "order_date" in df.columns:
        st.sidebar.header("📅 Filter by Order Date")
        min_date, max_date = df["order_date"].min(), df["order_date"].max()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df = df[(df["order_date"] >= start_date) & (df["order_date"] <= end_date)]

    # Key metrics
    total_orders = df["order_id"].nunique()
    cancelled_orders = df[df["order_item_status"].astype(str).str.lower() == "cancelled"].shape[0]
    returned_orders = df[df["order_item_status"].astype(str).str.lower() == "returned"].shape[0]
    total_quantity = df["quantity"].sum() if "quantity" in df.columns else 0

    # Revenue estimate
    if "quantity" in df.columns and "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        estimated_revenue = (df["quantity"] * df["price"]).sum()
    else:
        estimated_revenue = 0

    # SLA breaches
    dispatch_sla_breaches = df["dispatch_sla_breached"].astype(str).str.lower().eq("yes").sum() if "dispatch_sla_breached" in df.columns else 0
    delivery_sla_breaches = df["delivery_sla_breached"].astype(str).str.lower().eq("yes").sum() if "delivery_sla_breached" in df.columns else 0

    # Display metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("📦 Total Orders", f"{total_orders}")
    col2.metric("❌ Cancelled Orders", f"{cancelled_orders}")
    col3.metric("↩️ Returned Orders", f"{returned_orders}")
    col4.metric("🧮 Total Quantity", f"{total_quantity}")
    col5.metric("💰 Estimated Revenue", f"₹{estimated_revenue:,.2f}")
    col6.metric("🚚 SLA Breaches", f"{dispatch_sla_breaches + delivery_sla_breaches}")

    # Orders over time
    if "order_date" in df.columns:
        st.subheader("📈 Orders Over Time")
        daily_orders = df.groupby(df["order_date"].dt.date).size().reset_index(name="Orders")
        fig = px.line(daily_orders, x="order_date", y="Orders", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # Top and least moving products
    if {"sku", "product_title", "quantity"}.issubset(df.columns):
        sku_title_sales = (
            df.groupby(["sku", "product_title"])["quantity"]
            .sum()
            .reset_index()
            .sort_values(by="quantity", ascending=False)
        )

        top_movers = sku_title_sales.head(10).rename(columns={"quantity": "Total Quantity Sold"})
        least_movers = sku_title_sales[sku_title_sales["quantity"] > 0].tail(10).rename(columns={"quantity": "Total Quantity Sold"})

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🚀 Top Moving Products")
            st.dataframe(top_movers, use_container_width=True)

        with col2:
            st.markdown("### 🐢 Least Moving Products")
            st.dataframe(least_movers, use_container_width=True)
    else:
        st.warning("Required columns missing: 'sku', 'product_title', or 'quantity'.")

    # SLA breakdown chart
    if dispatch_sla_breaches > 0 or delivery_sla_breaches > 0:
        st.subheader("📊 SLA Breach Breakdown")
        sla_df = pd.DataFrame({
            "SLA Type": ["Dispatch SLA", "Delivery SLA"],
            "Breached": [dispatch_sla_breaches, delivery_sla_breaches]
        })
        fig_sla = px.bar(sla_df, x="SLA Type", y="Breached", text_auto=True, color="SLA Type")
        st.plotly_chart(fig_sla, use_container_width=True)

    # Raw data
    with st.expander("🔍 View Raw Uploaded Data"):
        st.dataframe(df.head(50), use_container_width=True)
