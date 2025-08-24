# Process-Monitoring-Agent
Process Monitoring Agent with Django Backend
# Process Monitor

Minimal Process Monitoring system with:
- **Agent** (Python script → EXE)
- **Django + DRF backend** (SQLite)
- **Frontend** (HTML + JS) for viewing process tree

---

## Backend Setup (Django + DRF)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install django djangorestframework

# set API key for this session
set AGENT_API_KEY=dev-api-key-please-change

# DB setup
python manage.py makemigrations monitoring
python manage.py migrate

# run backend
python manage.py runserver 0.0.0.0:8000
```
---
---


# 1 Start the backend (Django + DRF)
Open PowerShell (recommended) or Command Prompt and run these commands.

### PowerShell (recommended)
```
cd C:\process-monitor\backend
python -m venv .venv
# activate venv (PowerShell)
.\.venv\Scripts\Activate.ps1
# If ExecutionPolicy prevents activating, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
pip install --upgrade pip
pip install django djangorestframework
```
### Run DB migrations and start the server:
```
python manage.py makemigrations monitoring
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
The server will listen at http://127.0.0.1:8000.

# 2. Run the agent (send one snapshot)
Open a new PowerShell window (so backend keeps running in the first one), then:
```
cd C:\process-monitor\agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
# Quick test run (overrides config.ini values on the command line)
python monitor_agent.py --backend http://127.0.0.1:8000/api/ingest/ --api-key dev-api-key-please-change
```
Open browser to: http://127.0.0.1:8000/

# 3. Build the agent EXE so you can double-click
From C:\process-monitor\agent:
```
# use the agent venv or a new one
.\.venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller --onefile monitor_agent.py
```
# 4. Quick extra commands (admin / test)
Create Django admin user:
```
python manage.py createsuperuser
```
Then open http://127.0.0.1:8000/admin to inspect Snapshots and Processes.

# Fast test summary (1-minute checklist)
```
1. Start backend (PowerShell): create venv → install → python manage.py migrate → runserver.
2. Open new PowerShell: create agent venv → pip install -r requirements.txt → python monitor_agent.py --backend http://127.0.0.1:8000/api/ingest/ --api-key dev-api-key-please-change.
3. Browser → http://127.0.0.1:8000/ → enter hostname → Load.
```
