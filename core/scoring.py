import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from .models import JobDescription, CandidateEvaluation

WEIGHTS = {
    "skills_match": 0.30,
    "experience_relevance": 0.25,
    "education_certs": 0.15,
    "project_portfolio": 0.20,
    "communication_quality": 0.10
}

def extract_jd_requirements(jd_text: str) -> JobDescription:
    parser = PydanticOutputParser(pydantic_object=JobDescription)
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)
    
    prompt = PromptTemplate(
        template="You are an expert HR recruiter. Extract key requirements from the Job Description.\n{format_instructions}\nJD:\n{jd_text}",
        input_variables=["jd_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    return chain.invoke({"jd_text": jd_text})

def score_candidate(candidate_text: str, jd: JobDescription) -> dict:
    parser = PydanticOutputParser(pydantic_object=CandidateEvaluation)
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)
    
    prompt = PromptTemplate(
        template="""You are an expert HR recruiter evaluating a candidate resume against a Job Description.

Requirements:
Skills: {skills}
Experience: {experience}
Qualifications: {qualifications}

Resume:
{resume}

{format_instructions}
Evaluate the candidate on the 5 dimensions. Provide a score from 0-10 and a one-line justification for: Skills Match, Experience Relevance, Education & Certs, Project/Portfolio, Communication Quality.""",
        input_variables=["skills", "experience", "qualifications", "resume"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    
    eval_result = chain.invoke({
        "skills": ", ".join(jd.skills),
        "experience": jd.experience,
        "qualifications": jd.qualifications,
        "resume": candidate_text
    })
    
    scores = {
        "skills_match": {"score": eval_result.skills_match.score, "justification": eval_result.skills_match.justification},
        "experience_relevance": {"score": eval_result.experience_relevance.score, "justification": eval_result.experience_relevance.justification},
        "education_certs": {"score": eval_result.education_certs.score, "justification": eval_result.education_certs.justification},
        "project_portfolio": {"score": eval_result.project_portfolio.score, "justification": eval_result.project_portfolio.justification},
        "communication_quality": {"score": eval_result.communication_quality.score, "justification": eval_result.communication_quality.justification}
    }
    
    total = sum(scores[k]["score"] * w for k, w in WEIGHTS.items())
    scores["total_score"] = round(total, 2)
    return scores
