import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Pydantic Models ---
class ATSScore(BaseModel):
    score: int = Field(description="ATS score out of 100")
    feedback: List[str] = Field(description="List of specific feedback points")
    missing_keywords: List[str] = Field(description="List of keywords from job description missing in resume")

class AnalyzedContent(BaseModel):
    section: str = Field(description="The section of the resume the input belongs to (education, skills, projects, experience, summary, etc.)")
    content: List[str] = Field(description="The refined content points to add to the resume in professional tone")
    experience_level_update: Optional[str] = Field(description="If the input suggests an experience level (Junior, Mid, Senior), include it here.")
    feedback: str = Field(description="Brief feedback to the user on what was extracted")

# --- LLM Setup ---
# Ensure GOOGLE_API_KEY is available in environment or handle it.
# Assuming streamlint or docker compose env checks this.
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.7)

# --- Prompts ---
ats_prompt = ChatPromptTemplate.from_template(
    """You are an ATS (Applicant Tracking System) Scanner. Evaluate the current resume data against the job description.
    
    Job Description: {job_description}
    Current Resume Data: {resume_data}
    
    Provide a score out of 100, a list of feedback points for improvement, and matching/missing keywords.
    Return the output as a JSON object with keys: "score", "feedback", "missing_keywords".
    """
)

interview_prompt = ChatPromptTemplate.from_template(
    """You are an expert technical recruiter and resume builder. Your goal is to gather information to build a strong resume tailored to the Job Description.

    Job Description: {job_description}
    Current Resume Data: {resume_data}
    Conversation History: {history}

    Ask the NEXT ONE relevant question to gather missing or detailed information for the resume (e.g., specific metrics for a project, details about a skill, missing education dates).
    Only ask ONE question at a time. Be encouraging and professional.
    """
)

smart_content_prompt = ChatPromptTemplate.from_template(
    """You are a professional resume writer. Analyze the User Input in the context of the Job Description and Current Resume.
    
    Job Description: {job_description}
    Current Resume Data: {resume_data}
    User Input: {user_input}

    1. Identify which section of the resume this input belongs to (e.g., 'education', 'skills', 'projects', 'experience', 'summary', 'other').
    2. Refine the user's input into professional, impact-driven bullet points (or text for summary). Use action verbs and metrics where possible.
    3. If the user mentions their seniority level, note it.

    Return JSON matching the AnalyzedContent structure.
    """
)

summary_prompt = ChatPromptTemplate.from_template(
    """You are a professional resume writer. Write a compelling professional summary for a resume based on the following data.
    
    Job Description: {job_description}
    Resume Data (Skills, Experience, Projects): {resume_data}
    
    The summary should be:
    - 3-4 sentences long.
    - Tailored to the Job Description.
    - Highlight key skills and achievements from the resume data.
    - Professional and impactful.
    
    Return ONLY the summary text.
    """
)

# --- Chains ---
interview_chain = interview_prompt | llm | StrOutputParser()
smart_content_chain = smart_content_prompt | llm | JsonOutputParser(pydantic_object=AnalyzedContent)
ats_chain = ats_prompt | llm | JsonOutputParser(pydantic_object=ATSScore)
summary_chain = summary_prompt | llm | StrOutputParser()

# --- Functions ---
def get_interview_question(job_description, resume_data, history):
    return interview_chain.invoke({
        "job_description": job_description,
        "resume_data": resume_data,
        "history": history
    })

def analyze_and_refine_text(user_input, job_description, resume_data):
    return smart_content_chain.invoke({
        "user_input": user_input,
        "job_description": job_description,
        "resume_data": resume_data
    })

def calculate_ats_score(job_description, resume_data):
    return ats_chain.invoke({
        "job_description": job_description,
        "resume_data": resume_data
    })

def generate_resume_summary(job_description, resume_data):
    return summary_chain.invoke({
        "job_description": job_description,
        "resume_data": resume_data
    })
