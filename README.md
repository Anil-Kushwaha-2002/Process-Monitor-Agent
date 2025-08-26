# Process-Monitoring-Agent
Process Monitoring Agent with Django Backend + Python + API
# 1. Project Overview
### Collects system & process data → sends to backend → visual dashboard.
- **1. Agent** (Python script → EXE) -Runs on each system, collects CPU, RAM, process tree using psutil → REST API → Django backend. and sends it to backend.
- **2. Backend** (Django + DRF + SQLite) - Stores data in database, provides REST APIs.
- **3. Frontend** (HTML + JS) - Shows process tree, system metrics in real-time.

---

## 2. Backend Setup (Django + DRF)
```bash
cd C:\process-monitor-agent\backend

# Create Virtual Environment
python -m venv .venv
# activate venv (PowerShell)
.venv\Scripts\activate           # Windows
# or source .venv/bin/activate   # Linux/Mac

# Install Dependencies
pip install --upgrade pip
pip install django djangorestframework

# set API key for this session
set AGENT_API_KEY=dev-api-key-please-change

# DB and Backend setup
python manage.py makemigrations monitoring
python manage.py migrate

# Run backend
python manage.py runserver 0.0.0.0:8000
```
- The server will listen at
- Frontend: http://127.0.0.1:8000/
- APIs: http://127.0.0.1:8000/api/v1/
---

# 3. Setup Agent (send one snapshot)
```bash
cd C:\process-monitor-agent\agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
# Quick test run (overrides config.ini values on the command line)

python monitor_agent.py     # Run agent
python monitor_agent.py --backend http://127.0.0.1:8000/api/ingest/ --api-key dev-api-key-please-change
```
- The server will listen at
- http://127.0.0.1:8000/api/v1/process-snapshots/
- http://127.0.0.1:8000/api/v1/process-snapshots/latest

# 4. Convert Agent to EXE / Build the agent EXE so you can double-click
From C:\process-monitor-agent\agent
```
# use the agent venv or a new one
.\.venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller --onefile monitor_agent.py
```
Run EXE → Agent sends data automatically.

# 5. Testing the Workflow
### Test API Manually
```bash
curl -H "X-API-Key: changeme" http://127.0.0.1:8000/api/v1/process-snapshots/latest
```

# 6. Quick extra commands (admin / test)
Create Django admin user:
```
python manage.py createsuperuser
```
Then open http://127.0.0.1:8000/admin to inspect Snapshots and Processes.

---
---

# Fast test summary (1-minute checklist)
```
1. Start backend (PowerShell): create venv → install → python manage.py migrate → runserver.
2. Open new PowerShell: create agent venv → pip install -r requirements.txt → python monitor_agent.py --backend http://127.0.0.1:8000/api/ingest/ --api-key dev-api-key-please-change.
3. Browser → http://127.0.0.1:8000/ → enter hostname → Load.
```
# Professional Flow Diagram
```
[Agent] --> (POST) --> [Backend API] --> [Database]
   |                                   |
   +-------> (GET) <------------------ [Frontend]
```
---
# Workflow Explanation

| Step        | Component     | Action                                         |
| ----------- | ------------- | --------------------------------------------   |
| 1. Agent    | Python Script | Collects system metrics using `psutil`         |
| 2. API POST | Backend (DRF) | Sends JSON snapshot to `/process-snapshots/`   |
| 3. Database | Django ORM    | Stores snapshot & processes in DB              |
| 4. API GET  | Backend (DRF) | Fetch via `/process-snapshots/latest` to view  |
| 5. Frontend | HTML + JS     | Displays process data in table/tree format.    |
---
---
# 🧱 Project Structure
```
process-monitor-agent/
├─ backend/
│ ├─ manage.py
│ ├─ requirements.txt
│ ├─ config/
│ │ ├─ __init__.py
│ │ ├─ settings.py
│ │ ├─ urls.py
| | ├─ wsgi.py
│ │ └─ asgi.py
│ ├─ monitoring/
│ │ ├─ __init__.py
│ │ ├─ models.py
│ │ ├─ admin.py
│ │ ├─ serializers.py
│ │ ├─ views.py
│ │ ├─ urls.py
│ │ └─ auth.py
│ └─ static/
│    └─ index.html
└─ agent/
   ├─ monitor_agent.py
   ├─ agent.ini
   └─ requirements.txt
```
