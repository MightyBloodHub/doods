import streamlit as st
import pandas as pd
import plotly.express as px

def show_weight_measurements(weight_df):
    st.header("Weight Measurements")
    if weight_df.empty:
        st.write("No weight data available.")
        return

    st.subheader("Raw Data")
    st.dataframe(weight_df, height=300)

    if "Weight (g)" in weight_df.columns and "Date" in weight_df.columns and "Group" in weight_df.columns:
        weight_df["Weight (g)"] = pd.to_numeric(weight_df["Weight (g)"], errors="coerce")
        avg_over_time = weight_df.groupby(["Date", "Group"])["Weight (g)"].mean().reset_index()
        fig = px.line(
            avg_over_time,
            x="Date",
            y="Weight (g)",
            color="Group",
            title="Average Weight Over Time",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

