import plotly.figure_factory as ff
import streamlit as st

def display_gantt(df):
    # Assuming df is a DataFrame with the correct column names
    df_dict = df.to_dict('records')  # Convert DataFrame to list of dictionaries

    # Modify the labels for each task to display task name prominently
    fig = ff.create_gantt(df_dict, index_col='Task', group_tasks=True, show_colorbar=True, title='Project Gantt Chart')
    st.plotly_chart(fig, use_container_width=True)