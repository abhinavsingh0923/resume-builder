from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from .agents import get_interview_question, analyze_and_refine_text, calculate_ats_score, generate_resume_summary
import operator

class AgentState(TypedDict):
    job_description: str
    resume_data: dict
    history: List[str]
    current_question: str
    user_last_response: str
    ats_score: int
    ats_feedback: List[str]
    next_step: str

def interview_node(state: AgentState):
    # If there is a user response, we might want to process it (e.g., extract data)
    # For simplicity, we assume the user response is raw data for now, 
    # but in a real app, we would have an extractor agent here.
    
    # Generate the next question
    question = get_interview_question(
        state["job_description"], 
        state.get("resume_data", {}), 
        state.get("history", [])
    )
    
    return {"current_question": question, "history": [f"AI: {question}"]}

def processing_node(state: AgentState):
    # Process user's last response
    user_response = state.get("user_last_response", "")
    if not user_response:
        # If no user response, maybe this is the start or we just move on
        return {}
        
    resume_data = state.get("resume_data", {})
    job_desc = state.get("job_description", "")
    
    # Analyze and Refine
    try:
        analysis = analyze_and_refine_text(user_response, job_desc, resume_data)
        
        # Update Resume Data based on section
        section = analysis.get("section", "other")
        content = analysis.get("content", [])
        
        if section not in resume_data:
            # Initialize if it's a list-based section
            if section in ["education", "skills", "projects", "experience", "raw_notes"]:
                resume_data[section] = []
            else:
                resume_data[section] = "" # fallback
            
        # Append logic
        if isinstance(resume_data[section], list):
            resume_data[section].extend(content)
        elif isinstance(resume_data[section], str):
            # For singlular fields like summary, we might append or replace. 
            # Let's append with newline
            if resume_data[section]:
                 resume_data[section] += "\n" + "\n".join(content)
            else:
                 resume_data[section] = "\n".join(content)
        
        # Update Experience Level if detected
        exp_level = analysis.get("experience_level_update")
        if exp_level:
            resume_data["experience_level"] = exp_level
            
    except Exception as e:
        # Fallback if AI fails
        print(f"Error in smart agent: {e}")
        if "raw_notes" not in resume_data:
            resume_data["raw_notes"] = []
        resume_data["raw_notes"].append(user_response)
    
    # --- Auto-Generate Summary Check ---
    # If summary is missing, and we have enough data (experience/projects AND skills), generate it.
    if not resume_data.get("summary"):
        # Check for sufficient data
        has_experience = bool(resume_data.get("experience") or resume_data.get("projects"))
        has_skills = bool(resume_data.get("skills"))
        
        if has_experience and has_skills:
            try:
                print("Generating auto-summary...")
                summary = generate_resume_summary(job_desc, resume_data)
                resume_data["summary"] = summary
            except Exception as e:
                print(f"Error generating summary: {e}")

    return {
        "resume_data": resume_data, 
        "history": [f"User: {user_response}"]
    }

def ats_node(state: AgentState):
    resume_data = state.get("resume_data", {})
    job_desc = state.get("job_description", "")
    
    if not resume_data or not job_desc:
        return {"ats_score": 0, "ats_feedback": ["Not enough data"]}
        
    result = calculate_ats_score(job_desc, resume_data)
    return {
        "ats_score": result["score"],
        "ats_feedback": result["feedback"]
    }

# Define the Graph
workflow = StateGraph(AgentState)

workflow.add_node("process_input", processing_node)
workflow.add_node("ats_scan", ats_node)
workflow.add_node("interviewer", interview_node)

# Flow
# Start -> Process Input (if any) -> ATS Scan -> Interviewer -> End (wait for user input)

workflow.set_entry_point("process_input")
workflow.add_edge("process_input", "ats_scan")
workflow.add_edge("ats_scan", "interviewer")
workflow.add_edge("interviewer", END)

app = workflow.compile()
