# Resume RAG Matching Agent with MCP

This project is an AI-powered Resume Matching System built using LangGraph, ChromaDB, Sentence Transformers, and the Model Context Protocol (MCP).

The agent analyzes a Job Description, retrieves the most relevant resumes using semantic search, ranks candidates, and generates a detailed matching report.

---

# Features

- Resume semantic search using ChromaDB
- Resume ranking using embeddings
- LangGraph workflow
- Model Context Protocol (MCP) Server
- MCP Client integration
- Requirement extraction
- Candidate comparison
- Interview question generation
- Directory monitoring
- Batch resume processing

---

# Project Structure

```
resume-rag/
│
├── chat_cli.py
├── matching_agent.py
├── filesystem_mcp_server.py
├── mcp_client.py
├── tools.py
├── requirement_parser.py
├── job_matcher.py
├── vector_store.py
├── embedding_service.py
├── resumes/
├── chroma_db/
├── README.md
└── requirements.txt
```

---

# Architecture

```
User
   │
   ▼
chat_cli.py
   │
   ▼
LangGraph Agent
   │
   ▼
MCP Client
   │
   ▼
Filesystem MCP Server
   │
   ▼
Resume Tools
   │
   ▼
ChromaDB + Resume Files
```

---

# LangGraph Workflow

```
START
   │
   ▼
Parse JD
   │
   ▼
Extract Requirements
   │
   ▼
Search Resumes
   │
   ▼
Rank Candidates
   │
   ▼
Generate Report
   │
   ▼
Human Feedback
   │
   ▼
END
```

---

# MCP Resources

The MCP server exposes the following tools.

### extract_requirements

Extracts required skills and experience from a Job Description.

---

### compare_candidates

Compares multiple candidates side by side.

---

### generate_interview_questions

Generates interview questions based on candidate skills.

---

### watch_directory

Monitors a directory for newly added resumes.

---

### batch_process

Processes multiple resume files in a single request.

---

# Installation

Create a virtual environment.

```bash
python3 -m venv .venv
```

Activate it.

Linux/Mac

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Run MCP Server

```bash
python filesystem_mcp_server.py
```

---

# Run Resume Matching Agent

```bash
python chat_cli.py
```

Paste a Job Description and press

Linux / Mac

```
Ctrl + D
```

Windows

```
Ctrl + Z
```

---

# Example Job Description

```
Senior Backend Engineer

Required Skills:
Python
Go
Docker
Kubernetes
AWS
PostgreSQL

Experience:
5+ years
```

---

# Output

The agent displays

- Ranked Candidates
- Matching Score
- Skills
- Experience
- Reasoning
- Human Feedback

---

# Technologies Used

- Python
- LangGraph
- LangChain
- ChromaDB
- Sentence Transformers
- HuggingFace
- MCP SDK
- Watchdog

---

# Milestones Completed

## Milestone 1

- Resume Parser
- Resume Indexing
- ChromaDB Storage

## Milestone 2

- Resume Retrieval
- Semantic Search
- Candidate Ranking

## Milestone 3

- LangGraph Agent
- Human Feedback Loop
- Interactive CLI

## Milestone 4

- MCP Server
- MCP Client
- JSON-RPC Interface
- Resource Discovery
- Directory Monitoring
- Batch Processing

---

# Future Improvements

- Remote MCP Server
- Streamlit UI
- Multi-MCP Integration
- Database MCP Server
- Web Search MCP Server
- LLM-based Candidate Evaluation

---

# Author

Keerthi R