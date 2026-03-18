# Talk2Docker - Autonomous Docker Agent with RAG

Intelligent Docker management and Dockerfile generation using local LLM with RAG knowledge base.

## Prerequisites

- **Python 3.9+** (installed)
- **Docker** (installed and running - for executing docker commands)
- **Ollama** (installed - for running LLM locally)

## Quick Start (3 steps)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```
Installs: Flask, Docker SDK, Ollama, FAISS, Transformers, etc.

### Step 2: Start Ollama with Mistral Model
Open a terminal and run:
```bash
ollama serve
```

In another terminal, pull the model:
```bash
ollama pull mistral:7b
```
(First run will download ~4GB - subsequent runs use cache)

### Step 3: Run the App
```bash
cd backend
python app.py
```
Then open: **http://localhost:5000**

By default, backend auto-reloads when Python files change.
- Disable if needed: set `AUTO_RELOAD=false` before starting backend.

## Features

✨ **Dockerfile Generation**
- 17 instant templates for popular frameworks
- Smart detection for Flask, FastAPI, Django, Express, etc.
- Generate docker-compose.yml for multi-service stacks
- Create .env.example with all needed variables

🔒 **Security Scanning**
- Automatic vulnerability detection in Dockerfiles
- 13 security checks (root user, latest tags, secrets, etc.)
- Actionable remediation suggestions

🐳 **Docker Command Execution**
- 14 Docker commands supported via natural language
- Examples: "run nginx on 8080", "list containers", "show logs"

📚 **Local RAG Knowledge Base**
- Docker documentation available offline
- No external API calls required

## Example Commands

**Dockerfile Generation:**
- "Generate Dockerfile for FastAPI with PostgreSQL"
- "Create docker-compose for Flask with Redis"

**Docker Operations:**
- "Run nginx on port 8080"
- "Show running containers"
- "Stop all containers"
- "View logs from myapp"

**Learning:**
- "How do Docker volumes work?"
- "Explain Docker networks"
- "Best practices for Dockerfile"

## Architecture

```
User Input → Agent Planner → Tool Executor
                ↓
        - Docker command execution (14 tools)
        - Dockerfile generation (17 templates)
        - Security scanning (13 checks)
        - RAG knowledge lookup
```

## What You Can Do

1. **Review Dockerfiles** - Paste code → Get security scan + recommendations
2. **Generate Dockerfiles** - Describe your stack → Instant Dockerfile + compose file
3. **Manage Docker** - Execute commands via natural language
4. **Learn Docker** - Ask questions → Get local knowledge base answers

## Troubleshooting

**"Ollama connection refused"**
- Make sure `ollama serve` is running in another terminal
- Verify model: `ollama list` (should show mistral:7b)

**"Docker connection refused"**
- Ensure Docker daemon is running
- Verify: `docker ps` (should list containers or show empty list)

**"Port 5000 already in use"**
- Use: `cd backend && python app.py --port 5001`
- Or kill existing process: `netstat -ano | findstr :5000`

**Python dependency errors**
- Create venv: `python -m venv venv`
- Activate: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
- Install: `pip install -r requirements.txt`

## System Requirements

- **Minimum**: 4GB RAM, 10GB disk (for Ollama model)
- **Recommended**: 8GB+ RAM, SSD storage
- **Model**: Mistral 7B (~4GB) - lightweight & fast
