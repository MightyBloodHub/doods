import streamlit as st
import pandas as pd
import plotly.express as px

def show_feed_consumption(feed_df):
    st.header("Feed Consumption Data")
    if feed_df.empty:
        st.write("No feed consumption data available.")
        return

    st.subheader("Raw Data")
    st.dataframe(feed_df, height=300)

    if (
        "Feed Offered (g)" in feed_df.columns
        and "Feed Refused (g)" in feed_df.columns
        and "Date" in feed_df.columns
        and "Group" in feed_df.columns
    ):
        feed_df["Feed Offered (g)"] = pd.to_numeric(feed_df["Feed Offered (g)"], errors="coerce")
        feed_df["Feed Refused (g)"] = pd.to_numeric(feed_df["Feed Refused (g)"], errors="coerce")
        feed_df["Consumed (g)"] = feed_df["Feed Offered (g)"] - feed_df["Feed Refused (g)"]

        consumed_summary = feed_df.groupby(["Date", "Group"])["Consumed (g)"].sum().reset_index()
        fig = px.line(
            consumed_summary,
            x="Date",
            y="Consumed (g)",
            color="Group",
            title="Feed Consumed Over Time",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

