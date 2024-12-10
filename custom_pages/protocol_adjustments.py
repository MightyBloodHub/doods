import streamlit as st

def show_protocol_adjustments(protocol_df):
    st.header("Protocol and Adjustments")
    if protocol_df.empty:
        st.write("No protocol data available.")
        return

    st.subheader("Raw Data")
    st.dataframe(protocol_df, height=300)

