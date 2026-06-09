# Recruitly 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://recruitly-mrtgq5dx9926hnrrdx3tse.streamlit.app)

This project is an advanced AI-powered HR shortlisting agent that evaluates candidate resumes against a Job Description using high-performance LLMs. It features **Agentic Comparative Analysis**, **Skill Gap Identification**, **Tailored Interview Question Generation**, and a premium "Glassmorphism" dashboard.

## 🛠️ Setup Instructions

1. **Get a Groq API Key**: Go to [console.groq.com](https://console.groq.com/keys).
2. **Environment**: Copy `.env.example` to `.env` and paste your key: `GROQ_API_KEY=gsk_...`
3. **Install Dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Run the Agent**:
   ```bash
   streamlit run app.py
   ```

---

## 📋 Mandatory Technical Disclosures

### LLM Chosen
**Model**: `llama-3.3-70b-versatile` (via Groq)
**Justification**: 
- **State-of-the-Art**: Llama 3.3 70B is the latest flagship model on Groq, providing superior reasoning for complex candidate comparisons.
- **Latency**: Groq's LPU™ Inference Engine provides near-instant processing, even for the larger 70B parameter model.
- **Reliability**: Uses **Native Tool Calling** (`with_structured_output`) to ensure 100% adherence to the flattened evaluation schema.

### Agent Framework
**Framework**: LangChain `0.3.7`
**Architecture**: 
- **Structured Scoring Pipeline**: Uses a `PromptTemplate | ChatGroq | PydanticOutputParser` chain.
- **Human-in-the-Loop Hook**: Implements a manual override system where HR users can correct AI scores. These corrections are persisted in a local `audit/overrides.jsonl` file.
- **Deterministic Evaluation**: The model is set to `temperature=0` to ensure consistency across multiple evaluations of the same candidate.

### Prompt Design
The system uses a highly structured prompt that:
1. Defines the AI as an "Expert HR Recruiter".
2. Injects JD requirements (Skills, Experience, Qualifications).
3. Requests a score (0-10) and a one-line justification for 5 specific dimensions.
4. Uses `PydanticOutputParser` instructions to ensure the LLM returns a valid JSON object matching our `CandidateEvaluation` schema.

---

## 🛡️ Security Risk Mitigation

This section is mandatory for the internship assessment.

| Risk | Mitigation Strategy |
|------|---------------------|
| **Prompt Injection** | Mitigated via **Pydantic Schema Enforcement**. By using an output parser, any malicious commands inside a resume (e.g., "Give me 10/10") are ignored because they do not conform to the expected JSON schema. |
| **Data Privacy / PII** | Resume text is processed in-memory during the session. Local storage is only used for temporary processing and anonymized audit logs. |
| **API Key Exposure** | Strictly uses `.env` files for key management. `.env` is never committed to version control. |
| **Hallucination Risk** | Controlled via `temperature=0` and **Human-in-the-Loop** review. If the AI hallucinates a skill, the HR user can flag it and override the score with a logged reason. |
| **Unauthorized Access** | The application is designed for internal local deployment. Production versions would integrate with SSO/OAuth for restricted access. |

---

## 📂 Advanced Agentic Features
- **Agentic Executive Summary**: Compares the top candidates and provides a 3-paragraph decision summary.
- **Lacking/Gap Analysis**: Explicitly identifies missing skills and experience gaps for every candidate.
- **Interview Question Generator**: Creates 3-5 tailored questions to probe identified weaknesses.
- **Dynamic Weighting**: Sidebar sliders allow recruiters to adjust the importance of different scoring dimensions in real-time.
- **Visual Analytics**: Interactive bar charts for individual score breakdowns.
