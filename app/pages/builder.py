import streamlit as st
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.graph import app
from core.database import db
from ui.components import load_custom_css, ats_score_card
from services.pdf_generator import get_pdf_download_data

st.set_page_config(page_title="Resume Builder Chat", page_icon="💬", layout="wide")

# Load Custom CSS
load_custom_css()

if 'user' not in st.session_state or not st.session_state.user:
    st.warning("Please login first.")
    st.stop()

if 'session_id' not in st.session_state:
    st.warning("No active session. Please start from the dashboard.")
    st.stop()

# Load session data
session = db.get_session(st.session_state.session_id)
if not session:
    st.error("Session not found.")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Graph State
if "graph_state" not in st.session_state:
    stored_resume_data = session.get("resume_data", {})
    
    if not stored_resume_data:
        user_profile = db.get_user_profile(st.session_state.user['email'])
        initial_resume_data = {
            "contact": {
                "phone": user_profile.get("phone"),
                "email": user_profile.get("email"),
                "address": user_profile.get("address"),
                "linkedin": user_profile.get("linkedin"),
                "github": user_profile.get("github"),
                "portfolio": user_profile.get("portfolio")
            },
            "education": user_profile.get("education"),
            "raw_notes": []
        }
        current_question = "👋 Let's start building your resume! Tell me about your most recent work experience or skills."
        initial_history = []
        st.session_state.messages.append({"role": "assistant", "content": current_question})
    else:
        initial_resume_data = stored_resume_data
        current_question = "👋 Welcome back! What would you like to work on next?"
        initial_history = []
        st.session_state.messages.append({"role": "assistant", "content": current_question})
    
    st.session_state.graph_state = {
        "job_description": st.session_state.job_description,
        "resume_data": initial_resume_data,
        "history": initial_history,
        "current_question": current_question,
        "user_last_response": "",
        "ats_score": 0,
        "ats_feedback": []
    }

# --- LAYOUT ---
st.title("📝 Resume Builder")

# Get current state values
ats_score = st.session_state.graph_state.get("ats_score", 0)
ats_feedback = st.session_state.graph_state.get("ats_feedback", [])
resume_data = st.session_state.graph_state.get("resume_data", {})
user_name = st.session_state.user.get('name', 'Your Name')

# Two Column Layout: Preview | Chat
col_preview, col_chat = st.columns([1.1, 1])

with col_preview:
    # ATS Score Card
    st.subheader("📊 ATS Score")
    ats_score_card(ats_score, ats_feedback)
    
    st.divider()
    
    # Resume Preview - "Paper" Style
    st.subheader("📄 Live Preview")
    
    # Paper Container
    st.markdown("""
    <div class="resume-paper">
    """, unsafe_allow_html=True)
    
    with st.container():
        # Header
        st.markdown(f"<h2 style='color: #333 !important; text-align: center; margin-bottom: 5px;'>{user_name}</h2>", unsafe_allow_html=True)
        
        contact = resume_data.get('contact', {})
        contact_info = []
        if contact.get('phone'): contact_info.append(contact['phone'])
        if contact.get('email'): contact_info.append(contact['email'])
        if contact.get('address'): contact_info.append(contact['address'].split('\n')[0])
        
        if contact_info:
            st.markdown(f"<p style='color: #666 !important; text-align: center; font-size: 0.9rem;'>{' • '.join(contact_info)}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: #ccc;'>", unsafe_allow_html=True)
        
        # Summary
        summary = resume_data.get('summary', '')
        if summary:
            st.markdown("<h4 style='color: #333 !important;'>Summary</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #444 !important;'>{summary}</p>", unsafe_allow_html=True)
        
        # Experience
        experience = resume_data.get('experience', [])
        if experience:
            st.markdown("<h4 style='color: #333 !important;'>Experience</h4>", unsafe_allow_html=True)
            for item in experience:
                st.markdown(f"<li style='color: #444 !important;'>{item}</li>", unsafe_allow_html=True)
        
        # Projects
        projects = resume_data.get('projects', [])
        if projects:
            st.markdown("<h4 style='color: #333 !important;'>Projects</h4>", unsafe_allow_html=True)
            for project in projects:
                st.markdown(f"<li style='color: #444 !important;'>{project}</li>", unsafe_allow_html=True)
        
        # Skills
        skills = resume_data.get('skills', [])
        if skills:
            st.markdown("<h4 style='color: #333 !important;'>Skills</h4>", unsafe_allow_html=True)
            if isinstance(skills, dict):
                 for category, skill_list in skills.items():
                     if isinstance(skill_list, list):
                         text = f"<b>{category}:</b> {', '.join(skill_list)}"
                     else:
                         text = f"<b>{category}:</b> {str(skill_list)}"
                     st.markdown(f"<p style='color: #444 !important; margin-bottom: 2px;'>{text}</p>", unsafe_allow_html=True)
            else:
                 skills_text = " • ".join(skills) if isinstance(skills, list) else str(skills)
                 st.markdown(f"<p style='color: #444 !important;'>{skills_text}</p>", unsafe_allow_html=True)

        # Education
        education = resume_data.get('education')
        if education:
            st.markdown("<h4 style='color: #333 !important;'>Education</h4>", unsafe_allow_html=True)
            if isinstance(education, list):
                for edu in education:
                    st.markdown(f"<p style='color: #444 !important;'>{edu}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: #444 !important;'>{education}</p>", unsafe_allow_html=True)
                
        # Achievements (Optional)
        achievements = resume_data.get('achievements', [])
        if achievements:
            st.markdown("<h4 style='color: #333 !important;'>Achievements</h4>", unsafe_allow_html=True)
            for ach in achievements:
                st.markdown(f"<li style='color: #444 !important;'>{ach}</li>", unsafe_allow_html=True)
        
        # Fallback for raw notes
        raw_notes = resume_data.get('raw_notes', [])
        if raw_notes and not experience and not projects:
             st.markdown("<h4 style='color: #333 !important;'>Details</h4>", unsafe_allow_html=True)
             for note in raw_notes:
                 st.markdown(f"<li style='color: #444 !important;'>{note}</li>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Debug JSON
    with st.expander("🔍 View Raw Data"):
        st.json(resume_data)

    # --- COMPLETENESS CHECK ---
    def check_completeness(data):
        missing = []
        
        # 1. Contact Info
        contact = data.get("contact", {})
        if not contact.get("phone"): missing.append("Phone Number")
        if not contact.get("email"): missing.append("Email Address")
        
        # 2. Summary
        if not data.get("summary") and not (data.get("raw_notes") and len(data.get("raw_notes")) >= 2):
            missing.append("Professional Summary")
            
        # 3. Education
        if not data.get("education"): missing.append("Education")
        
        # 4. Experience/Projects (Context Dependent)
        exp_level = data.get("experience_level", "fresher")
        if exp_level == "experienced":
            if not data.get("experience"): missing.append("Work Experience")
        else:
            projects = data.get("projects", [])
            if not projects or len(projects) < 3: 
                missing.append(f"Projects (Need {3 - len(projects)} more)")
            
            skills = data.get("skills", [])
            has_enough_skills = False
            if isinstance(skills, dict):
                 # Count total skills inside categories
                 total_skills = sum(len(v) for v in skills.values() if isinstance(v, list))
                 has_enough_skills = total_skills >= 3
            elif isinstance(skills, list):
                 has_enough_skills = len(skills) >= 3
            
            if not has_enough_skills: missing.append("Skills (at least 3)")
            
        # 5. Achievements (Optional but if started, must have 2)
        ach = data.get("achievements", [])
        if ach and len(ach) < 2:
            missing.append("Achievements (Optional - but need >= 2 if included)")
            
        return len(missing) == 0, missing

    is_complete, missing_items = check_completeness(resume_data)

    # PDF Download Section
    st.divider()
    
    col_dl_1, col_dl_2 = st.columns([2, 1])
    
    with col_dl_1:
        st.subheader("📥 Download Resume")
        st.caption("Unlock the download by filling all sections and reaching an ATS score of 85%.")
        
        if is_complete and ats_score >= 85:
            pdf_bytes, filename, mime_type = get_pdf_download_data(resume_data, user_name)
            st.download_button(
                label="⬇️ Download PDF Resume",
                data=pdf_bytes,
                file_name=filename,
                mime=mime_type,
                type="primary",
                use_container_width=True
            )
            st.markdown("""
            <div style="background: rgba(56, 239, 125, 0.1); border: 1px solid #38ef7d; padding: 10px; border-radius: 8px; margin-top: 10px;">
                <p style="color: #38ef7d; margin: 0; font-size: 0.9rem;"><b>🎉 All set!</b> Your resume is complete and optimized.</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.button("🔒 Download Locked", disabled=True, use_container_width=True)
            
            # Show blockers
            st.markdown("### 🛑 Missing Requirements")
            
            # 1. Completeness Blockers
            if not is_complete:
                st.markdown("**incomplete Sections:**")
                for item in missing_items:
                    st.markdown(f"- ❌ {item}")
            else:
                st.markdown("- ✅ All Sections Filled")
                
            # 2. Score Blocker
            if ats_score < 85:
                st.markdown(f"- ❌ ATS Score ({ats_score}%) - Target: 85%")
            else:
                st.markdown("- ✅ ATS Score Target Met")
                
    with col_dl_2:
        # Mini checklist visualization
        st.markdown("**Checklist**")
        st.checkbox("Contact Info", value=bool(resume_data.get("contact", {}).get("phone") and resume_data.get("contact", {}).get("email")), disabled=True)
        st.checkbox("Summary", value=bool(resume_data.get("summary") or (resume_data.get("raw_notes") and len(resume_data.get("raw_notes"))>=2)), disabled=True)
        st.checkbox("Education", value=bool(resume_data.get("education")), disabled=True)
        
        if resume_data.get("experience_level") == "experienced":
            st.checkbox("Experience", value=bool(resume_data.get("experience")), disabled=True)
        else:
            proj_count = len(resume_data.get("projects", []))
            st.checkbox(f"Projects (Has {proj_count}/3)", value=proj_count >= 3, disabled=True)
            
            skills = resume_data.get("skills", [])
            s_count = 0
            if isinstance(skills, dict): s_count = sum(len(v) for v in skills.values())
            elif isinstance(skills, list): s_count = len(skills)
            st.checkbox(f"Skills (Has {s_count}/3)", value=s_count >= 3, disabled=True)
        
        st.checkbox("ATS Score > 85%", value=ats_score >= 85, disabled=True)

with col_chat:
    st.subheader("💬 AI Resume Assistant")
    
    # Chat container with fixed height
    chat_container = st.container(height=550)
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Tell me about your experience, skills, projects..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        st.session_state.graph_state["user_last_response"] = prompt
        
        # Run Graph
        with st.spinner("✨ Analyzing your input..."):
            result = app.invoke(st.session_state.graph_state)
            st.session_state.graph_state = result
            
            bot_response = result.get("current_question", "I have gathered enough information.")
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
            # Save progress to DB
            db.update_session(st.session_state.session_id, result.get("resume_data", {}))
            
            st.rerun()
