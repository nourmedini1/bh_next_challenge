<p align="center">
  <img src="assets/bot-avatar.png" alt="BH Assurance AI" width="150" />
</p>

<h1 align="center">BH Assurance AI Platform</h1>
<p align="center">
  <strong>An intelligent, multi-agent insurance assistant platform for BH Assurance</strong>
</p>

---

## Overview

BH Assurance AI is a full-stack, multi-agent platform that serves as an intelligent insurance assistant for **BH Assurance**. The system combines conversational AI, retrieval-augmented generation (RAG), real-time security enforcement, and a comprehensive admin dashboard to deliver accurate, context-aware insurance guidance across all product lines.

Users can chat with the AI assistant, ask about coverage options, retrieve personal contract and claims data, generate automobile insurance quotes, and upload attachments, all secured by multi-layered threat detection.

---

## Features

- **Conversational AI**: Natural language assistant powered by Mistral AI via the Parlant SDK, with French & Arabic support
- **RAG System**: 7 specialized FAISS vector stores covering Life, Health, Transport, Property & Casualty, Engineering, Automobile, and General Knowledge domains
- **Multi-Layer Security**: Prompt injection detection, content violation screening, file malware scanning (ClamAV), and JWT authentication
- **Observability**: Kafka-based log pipeline with ClickHouse persistence, analytics API, and LLM-powered insights via Google Gemini
- **MCP Tool Servers**: Product descriptions, automobile quote generation, and database access via the Model Context Protocol
- **Dual Frontend**: React 19 user chat interface + admin dashboard with vector store management, analytics, and agent configuration

---

## Architecture

<p align="center">
  <img src="assets/architecture.jpeg" alt="BH Assurance AI Architecture" />
</p>

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **AI / NLP** | Mistral AI, Parlant SDK, LangChain, LangGraph, Sentence Transformers, Google Gemini |
| **RAG** | FAISS, LangChain, HuggingFace Embeddings, Marker PDF |
| **Agent Protocols** | A2A SDK (Agent-to-Agent), MCP (Model Context Protocol) via FastMCP |
| **Backend** | FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic |
| **Databases** | PostgreSQL, MongoDB, ClickHouse, FAISS (vector) |
| **Messaging** | Apache Kafka (Confluent), Zookeeper |
| **Security** | JWT (PyJWT / python-jose), ClamAV, Custom prompt injection detection |
| **Frontend** | React 19, React Bootstrap, Recharts, React Router, React Markdown |
| **DevOps** | Docker Compose |
| **Language** | Python 3.13+, JavaScript (ES6+) |

---

## Getting Started

### Prerequisites

- **Python** 3.13+ &nbsp;·&nbsp; **Node.js** 18+ &nbsp;·&nbsp; **Docker & Docker Compose**
- **PostgreSQL** &nbsp;·&nbsp; **MongoDB** &nbsp;·&nbsp; **ClamAV** (optional, for malware scanning)

### Environment Variables

Create a `.env` file with the following:

```bash
MISTRAL_SERVICE_API_KEY=your_mistral_api_key
SECURITY_AGENT_API_KEY=your_mistral_api_key
TITLE_GENERATOR_API_KEY=your_mistral_api_key
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/insurance_db
CH_HOST=localhost
CH_PORT=9000
CH_DB=logs_db
CH_USER=default
CH_PASS=your_secure_password
```

### Start Services

```bash
# 1. Infrastructure (Kafka & Zookeeper)
cd logs && docker-compose up -d

# 2. RAG Server (port 5001)
cd rag && pip install -r requirements.txt && python server.py

# 3. Database API (port 8000)
cd infrastructure/db && pip install -r requirements.txt && uvicorn db.main:app --host 0.0.0.0 --port 8000

# 4. Security Agent (port 3002)
cd agents/security_agent && pip install -e . && python server.py

# 5. Attachment Handler (port 3001)
cd agents/attachment_handler && pip install -e . && python server.py

# 6. Orchestrator (port 8800)
cd agents/orchestrator && pip install -e . && python main.py

# 7. Admin API (port 6001)
cd admin/api && python app.py

# 8. Analytics & Log Manager
cd logs && python analytics_processor.py   # port 6002
cd logs && python log_manager.py

# 9. Frontends
cd user-frontend && npm install && npm start   # port 3000
cd admin-frontend && npm install && npm start   # different port
```

---

## Project Structure

| Folder | Purpose |
|---|---|
| `agents/orchestrator/` | Main AI orchestrator: Parlant SDK agent, tools, security hooks, and Kafka logging |
| `agents/security_agent/` | Security Agent (A2A): LangGraph workflow for prompt injection & content violation detection |
| `agents/attachment_handler/` | Attachment Handler Agent (A2A): multi-step file validation pipeline |
| `rag/` | RAG vector store server: FAISS stores, query API, and document ingestion pipeline |
| `infrastructure/db/` | Insurance Database API: FastAPI + SQLAlchemy + PostgreSQL |
| `mcp_tools/` | MCP tool servers: product descriptions, quote generation, database access |
| `admin/` | Admin backend API: CRUD for agents, guidelines, tags, terms, journeys |
| `admin-frontend/` | Admin dashboard (React 19): analytics, vector store management, agent config |
| `user-frontend/` | User chat interface (React 19): landing page, authentication, chat UI |
| `logs/` | Logging infrastructure: Kafka consumers, ClickHouse persistence, analytics API |
| `title_generation/` | Conversation title generator: FastAPI service using Mistral AI |

---

## Security Architecture

Security is enforced at multiple layers:

1. **Message-level**: Every incoming user message passes through the Security Interceptor hook, which calls the Security Agent via A2A. If a prompt injection or content violation is detected, the message is rejected before reaching the AI.

2. **Attachment-level**: Uploaded files go through a 4-step validation pipeline:
   - Gateway validation (type whitelist, size limit)
   - Prompt injection detection in document content
   - Embedded code / archive bomb detection
   - ClamAV malware scanning

3. **Authentication**: JWT-based auth with custom Parlant authorization policies. Guest users are restricted from accessing personal data.

4. **Observability**: All security events are logged to Kafka, persisted in ClickHouse, with real-time email alerts to administrators.

---

## Monitoring

The platform includes a full observability stack:

- **Kafka Topics**: Per-tool logging (16 topics including security logs)
- **ClickHouse**: Durable storage with per-topic tables
- **Analytics API**: Aggregated metrics: overview, time-series, per-tool breakdown, latency distribution, error analysis, day/hour heatmaps
- **LLM Insights**: Google Gemini analyzes anonymized log samples to identify trending topics, recurring failures, knowledge gaps, and action items
- **Admin Dashboard**: Recharts-powered visualizations accessible from the admin frontend

---

<p align="center">
  Built for the <strong>BH Next Challenge</strong> hackathon
</p>

