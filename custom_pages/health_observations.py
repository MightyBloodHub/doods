import streamlit as st
import pandas as pd
import plotly.express as px

def show_health_observations(health_df):
    st.header("Health Observations")
    if health_df.empty:
        st.write("No health observations data available.")
        return

    st.subheader("Raw Data")
    st.dataframe(health_df, height=300)

    if "Observation Type" in health_df.columns and "Group" in health_df.columns:
        group_event_counts = (
            health_df.groupby(["Observation Type", "Group"])["Bird ID"]
            .count()
            .reset_index()
        )
        group_event_counts.columns = ["Observation Type", "Group", "Count"]

        fig = px.bar(
            group_event_counts,
            x="Observation Type",
            y="Count",
            color="Group",
            barmode="group",
            title="Health Events by Type and Group",
            text="Count"
        )
        fig.update_traces(textposition='auto')
        st.plotly_chart(fig, use_container_width=True)

