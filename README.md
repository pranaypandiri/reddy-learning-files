# IT Support Multi-Agent System with LangGraph

Production-grade agentic AI system for IT support built with LangGraph, Vertex AI, and GCP services.

## Architecture

**3-Agent System:**
- **Agent 1 (Triage)**: Categorizes issues, creates tickets, manages sessions
- **Agent 2 (KB RAG)**: Searches knowledge base using FAISS vector store
- **Agent 3 (Ticket DB)**: Handles ticket database operations

**Tech Stack:**
- LangGraph for multi-agent orchestration
- Vertex AI (Gemini 2.0 Flash) for LLM
- Firestore for short-term session storage
- Cloud SQL (PostgreSQL) for long-term ticket storage
- FAISS for knowledge base vector search
- Streamlit for UI

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure GCP credentials:
```bash
gcloud auth application-default login
gcloud config set project ai-practice-388514
```

3. Create `.env` file from `.env.example` and update values

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
.
├── agents/
│   ├── agent1_triage.py       # Triage agent with categorization tools
│   ├── agent2_kb_rag.py       # Knowledge base RAG agent
│   └── agent3_ticket_db.py    # Ticket database agent
├── tools/
│   ├── categorization.py      # Issue categorization tool
│   ├── ticket_management.py   # Ticket CRUD tools
│   ├── session_management.py  # Firestore session tools
│   └── kb_search.py          # Knowledge base search tool
├── storage/
│   ├── firestore_client.py    # Firestore initialization
│   ├── cloudsql_client.py     # Cloud SQL connection
│   └── vector_store.py        # FAISS vector store
├── orchestration/
│   └── langgraph_workflow.py  # LangGraph StateGraph orchestration
├── data/
│   └── kb_documents/          # IT knowledge base documents
├── app.py                     # Streamlit UI
├── requirements.txt
└── README.md
```

## Features

- Real-time IT issue triage and categorization
- RAG-based knowledge base search
- Session persistence and recovery
- Long-term ticket analytics
- Multi-agent workflow visualization
- Cloud-native observability (Logging, Tracing)
