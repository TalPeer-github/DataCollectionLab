import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Data Collection Lab - AI Requirments Analyzer",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


df_reshaped = pd.read_csv('data/final_EM.csv')

positions_list = list(df_reshaped['position'].unique())[::-1]

st.title('Position Selection')
st.write('Please select a position from the list below:')
selected_position = st.selectbox('Select Position', positions_list)

st.write(f'You selected: {selected_position}')
