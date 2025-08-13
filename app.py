import streamlit as st
import pandas as pd

## Set page_config

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

## laod sample data
data = {
    "client" : pd.read_excel('resources/data/Copy of 10Jul_DummyData_v1.xlsx',sheet_name='ClientGroup'),
    "transactions": pd.read_excel('resources/data/Copy of 10Jul_DummyData_v1.xlsx',sheet_name='TransactionData'),
}

st.session_state['data'] = data
data['client']['RoA'] = data['client']['Total Relationship Revenue']/data['client']['Average Relationship AuM'].astype(float)


pages = [
    st.Page("pages/Management.py",title="Client Management")]
st.logo('resources/images/simon-kucher-seeklogo.png',size = 'large',link = 'https://www.simon-kucher.com')
nav = st.navigation(pages,position='top')


nav.run()

