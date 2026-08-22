# Quick Reference Cheat Sheet

## 🚀 Essential Commands

### **Deploy Claw OS**
```bash
cd Intelligence_Restructured/01_PROJECTS/Claw_OS/docker
docker-compose up -d
docker-compose logs -f
```

### **Deploy New Neo**
```bash
cd Intelligence_Restructured/01_PROJECTS/New_Neo/source
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

### **View Available Models** (OmniRoute)
```bash
cat Intelligence_Restructured/05_DOCUMENTATION/AI_Models/OmniRoute_Analysis.txt
```

### **Check System Status**
```bash
docker ps
docker logs [container_name]
```

---

## 📁 Critical Paths

| What | Path |
|------|------|
| Deploy with Docker | `01_PROJECTS/Claw_OS/docker/` |
| Edit API keys | `06_CONFIGURATION/credentials/` |
| Run scripts | `07_UTILITIES_AND_TOOLS/automation_scripts/` |
| Read docs | `05_DOCUMENTATION/` |
| Access models | `03_MODELS_AND_WEIGHTS/` |
| Training data | `04_KNOWLEDGE_AND_DATA/` |
| System configs | `06_CONFIGURATION/` |

---

## 🔑 Environment Variables

**File Location:** `06_CONFIGURATION/env_files/.env.template`

```env
LLM_PROVIDER=openai              # or 'ollama'
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
TWITTER_BEARER_TOKEN=...
```

---

## 🤖 Recommended Free Models (OmniRoute)

**Tier 1 - Best Quality:**
- Nemotron 3 Ultra :free ⭐⭐⭐⭐⭐
- GPT-OSS-120B :free ⭐⭐⭐⭐⭐
- Qwen3-Coder 480B :free ⭐⭐⭐⭐⭐

**Tier 2 - Good Balance:**
- North Mini Code :free ⭐⭐⭐⭐
- Laguna XS 2.1 :free ⭐⭐⭐⭐
- Gemini 3.6 Flash (free tier) ⭐⭐⭐⭐

**Tier 3 - Fast Inference:**
- Qwen3-Next 80B :free ⭐⭐⭐

---

## 🐳 Docker Essentials

```bash
# Build
docker build -t claw-os:latest .

# Run
docker run -d --env-file .env claw-os:latest

# Compose
docker-compose up -d
docker-compose down

# Logs
docker-compose logs -f
docker logs [container_id]

# Check
docker ps
docker ps -a
```

---

## 📊 File Type Breakdown

| Type | Count | Location |
|------|-------|----------|
| Python (.py) | 2,804 | `01_PROJECTS/`, `02_SYSTEMS/` |
| Bytecode (.pyc) | 2,398 | Various (can delete) |
| JSON/JSONL | 413 | `04_KNOWLEDGE_AND_DATA/` |
| Markdown (.md) | 168 | `05_DOCUMENTATION/` |
| Notebooks (.ipynb) | 67 | `04_KNOWLEDGE_AND_DATA/` |
| Config files | Various | `06_CONFIGURATION/` |

---

## 🛠️ Available Tools

| Tool | Location | Purpose |
|------|----------|---------|
| Omega Engine | `07_UTILITIES_AND_TOOLS/automation_scripts/` | LLM optimization |
| Kaggle Bridge | `07_UTILITIES_AND_TOOLS/automation_scripts/` | Data ingestion |
| Unlazy | `07_UTILITIES_AND_TOOLS/optimization/` | Lazy loading |
| Verification | `07_UTILITIES_AND_TOOLS/verification/` | Math/code validation |

---

## 🔐 Credential Management

**DO:**
- Store in `06_CONFIGURATION/credentials/`
- Mark as `*.SECURE.txt`
- Rotate regularly
- Use `.env` files for deployment

**DON'T:**
- Commit to git
- Share publicly
- Store in source files
- Use production keys in dev

---

## 📖 Read These First

1. `00_START_HERE/README.md` - Overview
2. `05_DOCUMENTATION/AI_Models/OmniRoute_Analysis.txt` - Model strategy
3. `01_PROJECTS/Claw_OS/README.md` - Project info
4. `_INDEX_AND_METADATA/SYSTEM_MAP.md` - Architecture

---

## ⚡ Common Tasks

**Task:** Deploy Claw OS locally
```bash
cd 01_PROJECTS/Claw_OS/docker
# Edit .env with your keys
docker-compose up
```

**Task:** Check available models
```
View: 05_DOCUMENTATION/AI_Models/OmniRoute_Analysis.txt
```

**Task:** Run optimization
```bash
python 07_UTILITIES_AND_TOOLS/automation_scripts/omega_engine_unlimited.py
```

**Task:** View system architecture
```
Read: _INDEX_AND_METADATA/SYSTEM_MAP.md
```

---

## 📋 Directory Size Reference

| Folder | Files | Size |
|--------|-------|------|
| Claw_OS | 14 | ~2 MB |
| New Neo | 1,032 | ~50 MB |
| Intelligence | 5,147 | ~400 MB |
| MegaCompact | 277 | ~30 MB |
| Atlas/Systems | 80+ | ~15 MB |
| Docs | 200+ | ~5 MB |
| **TOTAL** | **6,500+** | **~1 GB** |

---

## 🎯 Next Actions

- [ ] Read `00_START_HERE/README.md`
- [ ] Review `OmniRoute_Analysis.txt`
- [ ] Set up credentials in `06_CONFIGURATION/`
- [ ] Deploy Claw OS with Docker
- [ ] Test with sample prompts
- [ ] Monitor `docker-compose logs`

---

*For detailed info, see the full README in `00_START_HERE/`*
