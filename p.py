import streamlit as st
import pandas as pd

# Load data from uploaded file
st.title("🚀 Seller Rocket Brand Dashboard")

uploaded_file = st.file_uploader("Upload the OVERALL file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("Columns in uploaded file:", df.columns.tolist())  # Debugging step
    
    # Convert 'Seller Potential' to numeric to avoid errors
    if "Seller Potential" in df.columns:
        df["Seller Potential"] = pd.to_numeric(df["Seller Potential"], errors="coerce")
    
    # Update column names based on provided structure
    seller_column = "Account Manager"
    
    if seller_column in df.columns:
        st.sidebar.header("Filter Options")
        selected_category = st.sidebar.multiselect("Select Category", df["Category"].unique())
        selected_seller = st.sidebar.multiselect("Select Account Manager", df[seller_column].unique())
        
        # Filtering Data
        filtered_df = df.copy()
        if selected_category:
            filtered_df = filtered_df[filtered_df["Category"].isin(selected_category)]
        if selected_seller:
            filtered_df = filtered_df[filtered_df[seller_column].isin(selected_seller)]
        
        # Display Data
        st.dataframe(filtered_df)
        
        # Insights Section
        st.subheader("📊 Insights")
        st.write(f"Total Brands: {len(filtered_df)}")
        if "Seller Potential" in filtered_df.columns and not filtered_df["Seller Potential"].isnull().all():
            st.write(f"Average Seller Potential: {filtered_df['Seller Potential'].mean():.2f}")
        
        # AI Recommendation Placeholder
        st.subheader("🤖 AI Recommendations")
        st.write("Coming Soon: AI-powered marketplace and growth insights!")
    else:
        st.error("Column for Account Manager not found. Please check your file format.")
