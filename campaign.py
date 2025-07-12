import streamlit as st
import pandas as pd

def analyze_keywords(df):
    # Ensure the required columns are present
    required_columns = [
        "State", "Keyword", "Match type", "Status", "Suggested bid (low) (INR)",
        "Suggested bid (median) (INR)", "Suggested bid (high) (INR)", "Keyword bid (INR)",
        "Top-of-search IS", "Impressions", "Clicks", "CTR", "Spend (INR)", "CPC (INR)",
        "Orders", "Sales (INR)", "ACOS", "ROAS", "NTB orders", "% of orders NTB",
        "NTB sales (INR)", "% of sales NTB"
    ]
    if not all(col in df.columns for col in required_columns):
        return "Missing required columns in the uploaded file. Please check the format."
    
    # Advanced bid adjustment based on performance factors
    def adjust_bid(row):
        if row["ACOS"] > 50 or row["CTR"] < 0.2:  # High ACOS or very low CTR, reduce bid significantly
            return max(row["CPC (INR)"] * 0.6, 0.1)
        elif row["ACOS"] < 20 and row["Orders"] > 10 and row["CTR"] > 1.0:  # Low ACOS, high orders, high CTR, increase bid
            return row["CPC (INR)"] * 1.5
        elif row["Clicks"] > 100 and row["Orders"] < 5:  # Very high clicks but low conversion, reduce bid
            return max(row["CPC (INR)"] * 0.5, 0.1)
        elif row["ROAS"] > 5 and row["Sales (INR)"] > 10000:  # High ROAS and strong sales, increase bid
            return row["CPC (INR)"] * 1.3
        else:
            return row["CPC (INR)"]  # Keep bid the same
    
    df["Recommended Bid (INR)"] = df.apply(adjust_bid, axis=1)
    return df

st.title("Amazon PPC Manual Campaign Bid Optimizer")

uploaded_file = st.file_uploader("Upload your manual campaign report (CSV)", type=["csv"]) 

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    optimized_df = analyze_keywords(df)
    
    if isinstance(optimized_df, str):
        st.error(optimized_df)
    else:
        st.success("Bid optimization completed!")
        st.dataframe(optimized_df)
        st.download_button("Download Optimized Report", optimized_df.to_csv(index=False), "optimized_bids.csv", "text/csv")
