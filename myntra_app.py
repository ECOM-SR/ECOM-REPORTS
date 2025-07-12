import streamlit as st
import pandas as pd
import plotly.express as px

st.sidebar.title("🛍️ Myntra Ecom Reports")
selected_report = st.sidebar.radio("Select Report Type", ["Order Report", "Return Report"])

# ---------- ORDER REPORT ----------
if selected_report == "Order Report":
    st.title("🛍️ Myntra Order Report Dashboard")
    uploaded_file = st.file_uploader("📄 Upload Myntra Order Report (.xlsx or .csv)", type=["xlsx", "csv"], key="order_upload")

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

# ---------- RETURN REPORT ----------
elif selected_report == "Return Report":
    st.title("🔁 Myntra Return Report Dashboard")
    uploaded_file = st.file_uploader("📄 Upload Myntra Return Report (.xlsx or .csv)", type=["xlsx", "csv"], key="return_upload")

    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)

        # Date parsing
        date_cols = [
            "order_created_date", "order_delivered_date", "return_created_date",
            "refunded_date", "order_rto_date", "lmdo_last_modified_on"
        ]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Summary
        st.subheader("📊 Summary Metrics")
        total_returns = df['return_id'].notna().sum()
        rto_orders = df['status'].str.upper().eq("RTO").sum()
        refunded_orders = df['is_refunded'].astype(str).str.lower().eq("yes").sum()
        total_quantity = df['quantity'].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Returned Orders", total_returns)
        col2.metric("RTO Orders", rto_orders)
        col3.metric("Refunded Orders", refunded_orders)
        col4.metric("Total Units Returned", int(total_quantity))

        st.divider()

        if 'return_created_date' in df.columns:
            st.subheader("📈 Return Trend Over Time")
            trend_df = df[df['return_created_date'].notna()]
            trend = trend_df.groupby(trend_df['return_created_date'].dt.date).size().reset_index(name="Returns")
            fig = px.line(trend, x='return_created_date', y='Returns', title="Return Volume Over Time")
            st.plotly_chart(fig, use_container_width=True)

        if 'style_id' in df.columns:
            st.subheader("🎯 Top Returned Styles")
            style_counts = df['style_id'].value_counts().head(10).reset_index()
            style_counts.columns = ['Style ID', 'Return Count']
            st.dataframe(style_counts)

        if 'return_reason' in df.columns and df['return_reason'].notna().any():
            st.subheader("❗ Return Reasons Distribution")
            reason_counts = df['return_reason'].value_counts().reset_index()
            reason_counts.columns = ['Return Reason', 'Count']
            fig2 = px.bar(reason_counts, x='Return Reason', y='Count', title="Top Return Reasons", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

        if 'status' in df.columns:
            st.subheader("📦 Return Status")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig3 = px.pie(status_counts, names='Status', values='Count', title="Return Status Split")
            st.plotly_chart(fig3, use_container_width=True)

        with st.expander("📄 View Raw Data"):
            st.dataframe(df.head(100))

    else:
        st.info("Please upload a valid Myntra return report to view insights.")
