import streamlit as st
from core.auth import init_session_state, login_user, register_user, logout
from core.database import db
from ui.components import profile_form, load_custom_css, session_card

# Page Config
st.set_page_config(page_title="AI Resume Builder", page_icon="📄", layout="wide")

# Load Custom CSS
load_custom_css()

# Initialize Session State
init_session_state()

def login_page():
    # Centered Login Card
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔐 Login")
        st.caption("Welcome back! Please enter your credentials.")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                user = login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")

def signup_page():
    # Centered Signup Card
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("✨ Create Account")
        st.caption("Join us and build your perfect resume.")
        
        with st.form("signup_form"):
            name = st.text_input("👤 Full Name")
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            submit = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submit:
                success, msg = register_user(email, password, name)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def dashboard_page():
    st.title(f"👋 Welcome, {st.session_state.user['name']}")
    st.caption("Manage your profile and resume sessions below.")
    
    tab1, tab2 = st.tabs(["👤 Profile", "📁 My Resumes"])
    
    with tab1:
        st.header("Your Profile")
        current_profile = db.get_user_profile(st.session_state.user['email'])
        updated_profile = profile_form(current_profile)
        
        if updated_profile:
            db.update_user_profile(st.session_state.user['email'], updated_profile)
            st.success("Profile updated successfully!")
            st.rerun()
            
    with tab2:
        # Two Column Layout: Sessions | New Resume
        col1, col2 = st.columns([2, 1.2])
        
        with col1:
            st.subheader("📂 Your Sessions")
            sessions = db.get_user_sessions(st.session_state.user['email'])
            
            if not sessions:
                st.info("You haven't created any resumes yet. Start by pasting a job description!")
            else:
                # Grid layout for session cards
                num_cols = 2
                rows = [sessions[i:i + num_cols] for i in range(0, len(sessions), num_cols)]
                for row in rows:
                    cols = st.columns(num_cols)
                    for i, session in enumerate(row):
                        with cols[i]:
                            if session_card(session, on_click_key=f"btn_{session['_id']}"):
                                st.session_state.session_id = str(session['_id'])
                                st.session_state.job_description = session['job_description']
                                st.switch_page("pages/builder.py")

        with col2:
            st.subheader("🚀 New Resume")
            st.markdown("""
            <div class="card-container">
                <p style="color: #a0a0a0; font-size: 0.9rem;">Paste the job description to get started. Our AI will tailor your resume for this role.</p>
            </div>
            """, unsafe_allow_html=True)
            job_description = st.text_area("Job Description", height=220, placeholder="Paste job description here...")
            
            # Check Profile Completeness
            # Fetch profile again to be sure (or reuse current_profile if available in scope - it is not available in tab2 scope easily, so fetch)
            user_profile = db.get_user_profile(st.session_state.user['email'])
            
            has_skills = bool(user_profile.get("skills"))
            has_experience = bool(user_profile.get("experience"))
            has_education = bool(user_profile.get("education"))
            
            is_profile_complete = has_skills and has_experience and has_education
            
            if is_profile_complete:
                if st.button("🎯 Start Building", type="primary", use_container_width=True):
                    if job_description:
                        session_id = db.create_session(st.session_state.user['email'], job_description)
                        st.session_state.session_id = session_id
                        st.session_state.job_description = job_description
                        st.switch_page("pages/builder.py")
                    else:
                        st.warning("Please enter a job description.")
            else:
                st.warning("⚠️ Please complete your profile (Education, Experience, Skills) in the 'Profile' tab before creating a resume.")
                st.button("🎯 Start Building", type="primary", use_container_width=True, disabled=True)

def main():
    if not st.session_state.authenticated:
        # Sidebar for Login/Signup selection
        st.sidebar.title("🌟 AI Resume Builder")
        option = st.sidebar.radio("Menu", ["Login", "Sign Up"], label_visibility="collapsed")
        if option == "Login":
            login_page()
        else:
            signup_page()
    else:
        # Sidebar for logged-in user
        st.sidebar.title("🌟 AI Resume Builder")
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.user['name']}")
        st.sidebar.divider()
        st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True)
        dashboard_page()

if __name__ == "__main__":
    main()
