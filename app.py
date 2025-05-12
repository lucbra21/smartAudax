import streamlit as st
import common.login as login


st.set_page_config(layout="wide", initial_sidebar_state="collapsed", menu_items=None)
login.generarLogin()
