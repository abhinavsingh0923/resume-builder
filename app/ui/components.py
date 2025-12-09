import streamlit as st

# ====================
# DESIGN SYSTEM
# ====================
CUSTOM_CSS = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container Background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
    }
    
    h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(30, 30, 60, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* Card Container */
    .card-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }

    .card-container:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(102, 126, 234, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
    }

    /* Text Inputs */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.3) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #a0a0a0;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 0 0 10px 10px !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px;
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 16px !important;
    }

    /* Paper Preview Container */
    .resume-paper {
        background: white !important;
        color: #333 !important;
        border-radius: 8px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }

    /* Success/Info/Warning Messages */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 10px !important;
    }

    /* Download Button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
    }

    /* Form Submit Button */
    [data-testid="stFormSubmitButton"] button {
        width: 100%;
    }

    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Select Box */
    .stSelectbox [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
</style>
"""

def load_custom_css():
    """Inject custom CSS styles into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def profile_form(existing_data=None):
    if existing_data is None:
        existing_data = {}
    
    with st.form("profile_form"):
        st.subheader("📞 Contact Information")
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone Number", value=existing_data.get("phone", ""))
        with col2:
            email = st.text_input("Email", value=existing_data.get("email", ""))
        address = st.text_area("Address", value=existing_data.get("address", ""), height=80)
        
        st.subheader("🔗 Professional Links")
        col1, col2 = st.columns(2)
        with col1:
            linkedin = st.text_input("LinkedIn URL", value=existing_data.get("linkedin", ""))
            github = st.text_input("GitHub URL", value=existing_data.get("github", ""))
        with col2:
            portfolio = st.text_input("Portfolio/Website", value=existing_data.get("portfolio", ""))
            other_links = st.text_input("Other Links", value=existing_data.get("other_links", ""))
        
        st.subheader("🎓 Education")
        education = st.text_area("Education Details (Degree, Institution, Year)", value=existing_data.get("education", ""), height=100)
        
        st.subheader("💼 Experience")
        experience = st.text_area("Experience (Role, Company, Years, Description)", value=existing_data.get("experience", ""), height=150)
        
        st.subheader("🛠 Skills")
        skills = st.text_area("Skills (Comma separated)", value=existing_data.get("skills", ""), height=80)
        
        submitted = st.form_submit_button("💾 Save Profile")
        
        if submitted:
            return {
                "phone": phone,
                "email": email,
                "address": address,
                "linkedin": linkedin,
                "github": github,
                "portfolio": portfolio,
                "other_links": other_links,
                "education": education,
                "experience": experience,
                "skills": skills
            }
    return None

def session_card(session, on_click_key):
    """Renders a single session as a styled card."""
    job_desc = session.get('job_description', '')
    preview_text = job_desc[:80] + "..." if len(job_desc) > 80 else job_desc
    
    with st.container():
        st.markdown(f"""
        <div class="card-container">
            <p style="color: #a0a0a0; font-size: 0.85rem; margin-bottom: 8px;">JOB DESCRIPTION</p>
            <p style="color: #e0e0e0; font-size: 1rem; margin-bottom: 16px;">{preview_text}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➡️ Continue", key=on_click_key):
            return True
    return False

def ats_score_card(score, feedback):
    """Renders an ATS score display with visual gauge."""
    # Determine color based on score
    if score >= 85:
        color = "#38ef7d"  # Green
        status = "🎉 Excellent!"
    elif score >= 60:
        color = "#ffc107"  # Yellow
        status = "⚡ Good Progress"
    else:
        color = "#ff6b6b"  # Red
        status = "📈 Needs Work"

    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <div style="
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient({color} {score}%, rgba(255,255,255,0.1) {score}%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        ">
            <div style="
                width: 90px;
                height: 90px;
                border-radius: 50%;
                background: #1a1a2e;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.8rem;
                font-weight: 700;
                color: {color};
            ">{score}%</div>
        </div>
        <p style="color: {color}; font-weight: 600;">{status}</p>
    </div>
    """, unsafe_allow_html=True)

    if feedback:
        with st.expander("💡 Improvement Tips", expanded=False):
            for item in feedback:
                st.markdown(f"- {item}")
