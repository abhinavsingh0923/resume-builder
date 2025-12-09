import bcrypt
import streamlit as st
from .database import db

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def login_user(email, password):
    user = db.get_user(email)
    if user and verify_password(password, user['password']):
        return user
    return None

def register_user(email, password, name):
    if db.get_user(email):
        return False, "User already exists"
    
    hashed_password = hash_password(password)
    user_data = {
        "email": email,
        "password": hashed_password,
        "name": name
    }
    db.create_user(user_data)
    return True, "User registered successfully"

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def logout():
    st.session_state.user = None
    st.session_state.authenticated = False
    st.rerun()
