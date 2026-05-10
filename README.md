# AI HR Shortlisting Agent (Task 1)

This project is an AI-powered HR shortlisting prototype that evaluates candidate resumes against a Job Description using high-performance LLMs. It features a premium "Glassmorphism" dashboard and a "Human-in-the-Loop" scoring system.

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
**Model**: `llama-3.1-70b-versatile` (via Groq)
**Justification**: 
- **Latency**: Groq's LPU™ Inference Engine provides near-instant processing, which is critical for HR teams uploading 50+ resumes at once.
- **Cost**: Groq provides a generous free tier for developers, making the prototype highly accessible without upfront billing setup.
- **Capability**: Llama 3.1 70B shows excellent performance in following the strict Pydantic output schemas required for our scoring rubric.

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

## 📂 Sample Outputs
- **Dashboard**: Real-time leaderboard and metrics.
- **HTML Report**: Professional summary report generated via Jinja2 templates.
- **JSON Export**: Full structured dataset of all evaluations for integration with other ATS systems.
