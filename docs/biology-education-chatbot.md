## Sri Lanka — Biology Education Chatbot (LangChain + LangGraph)

### Goals & scope

- **Input**: English biology text or student question.
- **Output**: Localised answer aligned to the Sri Lankan biology curriculum and grade (Grade 6–A/L), in Sinhala/Tamil/English, plus: very clear explanatory note, one formative practice question with answer, and sources.
- **Non-goals**: Replace teacher judgement; provide medical/clinical diagnoses.

---

### High-level architecture

- **Frontend Chat UI** (React/web or mobile)
  - Sends: student query, grade, language preference.
- **Backend API** (FastAPI or Flask)
  - Endpoints: `/ask`, `/health`, `/glossary`, `/feedback`.
  - Orchestrates retrieval, explanation, translation, safety.
- **LangChain components**
  - Retriever (Chroma/FAISS/Milvus) over curriculum-aligned docs.
  - Explanation chain: grade-aware pedagogy, step-by-step notes.
  - Translation/localization chain: Sinhala/Tamil terminology.
  - Safety & verification: moderation + teacher review hooks.
- **LangGraph** (optional) to visually compose nodes and flows.
- **Vector DB**: Chroma/FAISS/Milvus with curriculum docs + teacher notes.
- **Model provider**: OpenAI or local (Llama/Mistral/HF) via LangChain.

---

### Prerequisites & tools

- Python 3.10+
- Node.js/npm (for React frontend)
- Accounts/keys: OpenAI (or other LLM provider)
- Docker (optional but recommended)

Python libraries:

```
pip install -U langchain openai fastapi uvicorn chromadb sentence-transformers faiss-cpu transformers pydantic python-multipart langgraph
```

Notes:
- On Windows, `faiss-cpu` may install better via conda. On Linux, pip is fine.
- Install `langgraph` if using LangGraph orchestration.

---

### Project skeleton

```
biology-chatbot/
├─ backend/
│  ├─ app.py               # FastAPI server
│  ├─ agents/
│  │  ├─ retriever.py
│  │  ├─ chains.py
│  │  └─ translation.py
│  ├─ data/
│  └─ Dockerfile
├─ frontend/
│  └─ (React chat app)
├─ docs/
│  └─ curriculum_mapping.json
├─ data/
│  ├─ textbooks/          # PDFs or text
│  ├─ syllabi/            # official syllabus files
│  └─ parallel_corpus/    # English <-> Sinhala/Tamil pairs (if available)
└─ infra/
   └─ docker-compose.yml
```

---

### Curriculum & data preparation (critical)

1) Collect authoritative artifacts
- GCE O/L & A/L syllabi, National Institute of Education (NIE) materials, approved textbooks, teacher guides.

2) Create curriculum mapping JSON
- Map `topic_id → grade_range → learning_objectives → keywords`.

Example `docs/curriculum_mapping.json`:

```json
{
  "photosynthesis": {
    "grade_range": [9, 12],
    "learning_objectives": ["explain photosynthesis", "write equation"],
    "keywords": ["chlorophyll", "light reaction", "Calvin cycle"]
  }
}
```

3) Canonical glossary
- CSV/JSON with biology terms in English + Sinhala + Tamil. Example fields: `term_en, term_si, term_ta, grade_min, grade_max, notes`.

4) Prepare documents
- Slice textbooks into 200–800 word passages.
- Add metadata: `{title, source, topic_id, grade, page, section}`.
- Prefer open-licensed content; ensure rights for scans/PDFs.

---

### Vector store & retrieval

- Embeddings: OpenAI (`text-embedding-3-large`) or local `sentence-transformers` (e.g., `all-MiniLM-L6-v2`).
- Vector DB: Chroma for ease; FAISS for local speed; Milvus/Pinecone for scale.
- Tune retriever `k` (3–8). Optionally dynamic by grade/topic.

Example (Chroma + OpenAI embeddings):

```python
# backend/agents/retriever.py
import os
from typing import List
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

PERSIST_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
DATA_DIR = os.getenv("DATA_DIR", "./data/prepared")


def load_documents() -> List[Document]:
    loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
    raw_docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    docs = splitter.split_documents(raw_docs)
    return docs


def build_or_load_vectordb() -> Chroma:
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
    if os.path.isdir(PERSIST_DIR) and len(os.listdir(PERSIST_DIR)) > 0:
        return Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
    docs = load_documents()
    vectordb = Chroma.from_documents(docs, embedding=embeddings, persist_directory=PERSIST_DIR)
    return vectordb


def get_retriever(k: int = 5):
    vectordb = build_or_load_vectordb()
    return vectordb.as_retriever(search_kwargs={"k": k})
```

Local embeddings example:

```python
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
```

---

### Building the LangChain pipeline (translation + explanation)

- Goal: RAG grounded answers with pedagogy-aware explanations.
- Output: JSON with `short_answer, clear_explanatory_note, misconceptions, practice_q, practice_a, key_terms, sources`.
- Respect `grade` and `language` preferences.

Prompt template:

```python
# backend/agents/chains.py
from langchain.prompts import PromptTemplate

ANSWER_PROMPT = PromptTemplate(
    input_variables=["context", "question", "grade", "language", "glossary"],
    template=(
        "You are an experienced Sri Lankan biology teacher aligned with the national syllabus.\n"
        "Use the context to answer in {language} for Grade {grade}.\n"
        "Prefer Sri Lankan examples and terms.\n\n"
        "Context:\n{context}\n\n"
        "Student question:\n{question}\n\n"
        "Glossary (English=Sinhala=Tamil):\n{glossary}\n\n"
        "Deliver JSON with keys: short_answer, clear_explanatory_note, misconceptions, "
        "practice_q, practice_a, key_terms, sources. Return only valid JSON."
    )
)
```

Chain orchestration:

```python
# backend/agents/chains.py
import json
from typing import Dict, Any
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

from .retriever import get_retriever


def build_answer_chain(model: str = "gpt-4o-mini", temperature: float = 0.0) -> LLMChain:
    llm = ChatOpenAI(model=model, temperature=temperature)
    return LLMChain(llm=llm, prompt=ANSWER_PROMPT)


def generate_answer(question: str, grade: int, language: str, k: int = 5, glossary_text: str = "") -> Dict[str, Any]:
    retriever = get_retriever(k=k)
    docs = retriever.get_relevant_documents(question)
    context_blocks = []
    sources = []
    for d in docs:
        context_blocks.append(d.page_content)
        meta = d.metadata or {}
        src = meta.get("source") or meta.get("title") or "Unknown"
        if src not in sources:
            sources.append(src)
    context = "\n---\n".join(context_blocks)

    chain = build_answer_chain()
    output = chain.run({
        "context": context,
        "question": question,
        "grade": grade,
        "language": language,
        "glossary": glossary_text
    })

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        data = {"short_answer": output.strip(), "clear_explanatory_note": output.strip(),
                "misconceptions": [], "practice_q": "", "practice_a": "", "key_terms": [], "sources": sources}
    if not data.get("sources"):
        data["sources"] = sources
    return data
```

Translation/localization helper (when language != English):

```python
# backend/agents/translation.py
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

LOCALIZE_PROMPT = PromptTemplate(
    input_variables=["text", "language", "glossary"],
    template=(
        "Translate the text into {language} for Sri Lankan biology students.\n"
        "Honor glossary preferred terms. Output only the translated text.\n\n"
        "Glossary:\n{glossary}\n\n"
        "Text:\n{text}"
    )
)


def localize_text(text: str, language: str, glossary: str = "") -> str:
    if language.lower() in ["english", "en"]:
        return text
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm.invoke(LOCALIZE_PROMPT.format(text=text, language=language, glossary=glossary)).content
```

Safety/moderation (example):

```python
# backend/middleware/safety.py
from typing import Tuple

SAFE_TOPICS = {"biology", "health education", "environment"}


def moderate(question: str) -> Tuple[bool, str]:
    lower = question.lower()
    if any(x in lower for x in ["diagnose", "treat my", "prescribe", "emergency"]):
        return False, (
            "I cannot provide medical advice or diagnoses. For health concerns, consult a qualified professional. "
            "I can, however, explain the underlying biology if you wish."
        )
    return True, ""
```

---

### Integrating with LangGraph (orchestration)

Represent nodes: Input → Moderation → Retrieval → Explanation → Localization → Output.

Example LangGraph sketch:

```python
# backend/agents/graph.py
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .chains import generate_answer
from ..middleware.safety import moderate

def build_graph():
    graph = StateGraph(dict)

    def node_moderate(state: Dict[str, Any]):
        ok, msg = moderate(state["question"])
        state["moderation_ok"] = ok
        state["moderation_msg"] = msg
        return state

    def node_answer(state: Dict[str, Any]):
        if not state.get("moderation_ok", True):
            state["result"] = {"short_answer": state["moderation_msg"], "sources": []}
            return state
        result = generate_answer(
            state["question"], state["grade"], state["language"], glossary_text=state.get("glossary", "")
        )
        state["result"] = result
        return state

    graph.add_node("moderate", node_moderate)
    graph.add_node("answer", node_answer)

    graph.set_entry_point("moderate")
    graph.add_edge("moderate", "answer")
    graph.add_edge("answer", END)

    return graph
```

Use the graph in the API or call `generate_answer` directly.

---

### Backend API (FastAPI)

```python
# backend/app.py
import os
from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from agents.chains import generate_answer
from middleware.safety import moderate

class AskRequest(BaseModel):
    question: str
    grade: int
    language: str = "English"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask(req: AskRequest):
    ok, msg = moderate(req.question)
    if not ok:
        return {"short_answer": msg, "clear_explanatory_note": msg, "sources": []}
    result = generate_answer(req.question, req.grade, req.language)
    return result
```

---

### Frontend: simple chat UI (outline)

- Fields: text input, grade selector (6–13/A-L), language selector (Sinhala/Tamil/English).
- Display: short answer, explanatory note, practice Q&A, key terms, sources.
- Accessibility: Sinhala/Tamil fonts, large-text toggle, export to PDF.

Fetch example:

```javascript
async function askBackend(question, grade, language) {
  const res = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, grade, language })
  });
  return res.json();
}
```

---

### Testing, evaluation & teacher-in-the-loop workflow

- Seed test set: 200–500 student questions per grade with teacher-written expected answers.
- Automatic checks: JSON parses; at least one source; retrieval latency < target; content length bounds.
- Human review: daily spot-checks by teachers; flag errors; track corrections.
- Feedback loop: store student feedback and corrections; refine prompts and glossary.
- A/B testing: compare prompt variants (e.g., analogy strength, step granularity) for comprehension gains.

Evaluation rubrics:
- **Accuracy** (teacher-rated)
- **Clarity** (student-rated)
- **Curriculum alignment** (teacher-rated)
- **Engagement** (practice question attempts)

---

### Deployment & scaling

- Containerize backend; serve with `uvicorn`/`gunicorn` workers.
- Vector DB: move to managed (Pinecone/Milvus/Chroma Cloud) as usage grows.
- LLM scaling: enable caching, batch similar queries, fallback to smaller local models where suitable.
- Latency: limit context size, pre-compute embeddings, cache frequent queries.

Backend Dockerfile:

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

requirements.txt:

```
fastapi
uvicorn
langchain
openai
chromadb
faiss-cpu
sentence-transformers
transformers
pydantic
python-multipart
langgraph
```

Example `infra/docker-compose.yml`:

```yaml
version: "3.9"
services:
  api:
    build: ./backend
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CHROMA_DIR=/data/chroma_db
    volumes:
      - ./data:/app/data
      - ./backend:/app
    ports:
      - "8000:8000"
```

---

### Monitoring, logging & maintenance

- Log each Q/A with metadata: `grade, topic_id (if inferred), selected sources, model version, latency`.
- Minimize PII; anonymize where possible; retain with consent.
- Track usage, errors, and hallucination flags; set alerts on spikes.
- Version prompts and glossary; record which version generated each answer.

---

### Ethics, accuracy & safety

- No medical/diagnostic claims; redirect to professionals for health issues.
- Bias & fairness: validate translations and examples with diverse teacher reviewers.
- Privacy: comply with local data protection; store transcripts only with consent and for educational improvement.

---

### Appendix: sample prompt templates

Answer prompt (compact JSON-only):

```
You are an experienced Sri Lankan biology teacher aligned with the national syllabus.
Answer in {language} for Grade {grade}. Use Sri Lankan examples and age-appropriate language.
Provide JSON with keys exactly: short_answer, clear_explanatory_note, misconceptions, practice_q, practice_a, key_terms, sources.
Use the context to ground your answer. If unsure, say so and ask for clarification.

Context:
{context}

Student question:
{question}

Glossary (English=Sinhala=Tamil):
{glossary}

Return only JSON.
```

Moderation fallback message:

```
I cannot provide medical advice or diagnoses. For health concerns, consult a qualified professional. I can explain the biology concepts involved if you wish.
```

Acceptance criteria
- API returns valid JSON with all required fields for 95%+ of queries.
- At least one source is cited for 90%+ of answers.
- Teacher review rates: Accuracy ≥ 4/5, Clarity ≥ 4/5, Curriculum alignment ≥ 4/5.
- Average latency ≤ 3.0s with cached embeddings and k ≤ 5.
- No medical/diagnostic content is generated without the safety fallback.