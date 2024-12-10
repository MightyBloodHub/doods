import streamlit as st
import pandas as pd

def show_overview(feed_df, weight_df, health_df):
    st.header("Overview")
    st.write(
        "This dashboard provides insights into the BSFL poultry feed experiment data. "
        "The Excel file only contains raw data; all computations and visualizations are handled by this software."
    )

    st.subheader("Key Metrics")

    # Total Feed Consumed
    if (
        not feed_df.empty
        and "Feed Offered (g)" in feed_df.columns
        and "Feed Refused (g)" in feed_df.columns
    ):
        feed_df["Feed Offered (g)"] = pd.to_numeric(feed_df["Feed Offered (g)"], errors="coerce")
        feed_df["Feed Refused (g)"] = pd.to_numeric(feed_df["Feed Refused (g)"], errors="coerce")
        feed_df["Consumed (g)"] = feed_df["Feed Offered (g)"] - feed_df["Feed Refused (g)"]
        total_consumed = feed_df["Consumed (g)"].sum()
        st.metric("Total Feed Consumed (all groups)", f"{total_consumed:.2f} g")

    # Average Bird Weight
    if not weight_df.empty and "Weight (g)" in weight_df.columns:
        weight_df["Weight (g)"] = pd.to_numeric(weight_df["Weight (g)"], errors="coerce")
        avg_weight = weight_df["Weight (g)"].mean()
        st.metric("Average Bird Weight (overall)", f"{avg_weight:.2f} g")

    # Mortality
    if not health_df.empty and "Observation Type" in health_df.columns:
        mortalities = health_df[health_df["Observation Type"] == "Mortality"]
        st.metric("Total Mortalities Recorded", f"{len(mortalities)}")

