import json
import socket
import psutil
import requests
import configparser
from datetime import datetime, timezone
import time
from pathlib import Path
import logging
import logging.handlers

# ---------------- Paths ----------------
APP_DIR = Path(getattr(__file__, "__file__", ".")).resolve().parent
CONFIG_PATH = APP_DIR / "agent.ini"
LOG_PATH = APP_DIR / "agent.log"

# ---------------- Logger ----------------
logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=512_000, backupCount=2, encoding="utf-8")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# ---------------- Load config ----------------
def load_config():
    cfg = configparser.ConfigParser()
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing {CONFIG_PATH}")
    cfg.read(CONFIG_PATH, encoding="utf-8")
    if "agent" not in cfg:
        raise ValueError("Missing [agent] section in config.ini")
    section = cfg["agent"]
    return {
        "backend_url": section.get("api_url", "").strip(),
        "api_key": section.get("api_key", "").strip(),
        "interval_sec": section.getint("interval_seconds", fallback=0),
        "connect_timeout": 5,
        "read_timeout": 10,
        "max_retries": 3
    }

# ---------------- Collect processes ----------------
# ---------------- Collect processes ----------------
def collect_processes():
    processes = []

    # Initialize CPU counters
    for p in psutil.process_iter(['pid', 'ppid', 'name']):
        try:
            p.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(0.2)  # sampling window

    # Collect actual snapshot
    for p in psutil.process_iter(['pid', 'ppid', 'name', 'memory_info']):
        try:
            info = p.info
            name = info.get('name') or ""
            if not name.strip():
                continue  # skip blank names to avoid backend errors

            # Safely get memory RSS
            try:
                mem_rss = info['memory_info'].rss if info.get('memory_info') else 0
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                mem_rss = 0

            # Safely get memory %
            try:
                mem_percent = round(p.memory_percent(), 2)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                mem_percent = 0

            processes.append({
                "pid": info['pid'],
                "ppid": info['ppid'],
                "name": name,
                "cpu_percent": round(p.cpu_percent(None), 2),
                "memory_rss": mem_rss,
                "memory_percent": mem_percent
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes



# ---------------- Prepare payload ----------------
def make_payload():
    return {
        "hostname": socket.gethostname(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "processes": collect_processes()
    }

# ---------------- Send data ----------------
def send_snapshot(cfg, data):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": cfg["api_key"]
    }
    attempts = 0
    backoff = 1.5
    while attempts < cfg["max_retries"]:
        try:
            r = requests.post(cfg["backend_url"], headers=headers, json=data,
                            timeout=(cfg["connect_timeout"], cfg["read_timeout"]))
            if r.status_code // 100 == 2:
                logger.info(f"Snapshot sent successfully: {r.status_code}")
                return True
            else:
                logger.error(f"Server responded {r.status_code}: {r.text[:200]}")
        except requests.RequestException as e:
            logger.error(f"POST failed: {e}")
        attempts += 1
        time.sleep(backoff)
        backoff *= 2
    return False

# ---------------- Main ----------------
def main():
    cfg = load_config()
    interval = cfg.get("interval_sec", 0)

    if interval <= 0:
        data = make_payload()
        send_snapshot(cfg, data)
        input("Snapshot sent. Press Enter to exit...")  # keeps window open
        return

    logger.info(f"Running continuously every {interval} sec")
    while True:
        data = make_payload()
        send_snapshot(cfg, data)
        time.sleep(interval)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        input("Press Enter to exit...")






# import json
# import socket
# import psutil
# import requests
# import configparser
# from datetime import datetime, timezone
# import time

# # ---------------- Load config ----------------
# cfg = configparser.ConfigParser()
# cfg.read("agent.ini")

# API_URL = cfg.get("agent", "api_url", fallback="http://127.0.0.1:8000/api/v1/process-snapshots/")
# API_KEY = cfg.get("agent", "api_key", fallback="changeme")

# hostname = socket.gethostname()

# # ---------------- Collect processes ----------------
# def collect_processes():
#     processes = []

#     # First pass: initialize CPU percent counters
#     for proc in psutil.process_iter(['pid', 'name', 'ppid']):
#         try:
#             proc.cpu_percent(None)
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue

#     time.sleep(0.2)  # small sample window for accurate CPU %

#     # Second pass: collect real data
#     for proc in psutil.process_iter(['pid', 'name', 'ppid', 'memory_info']):
#         try:
#             info = proc.info
#             if not info['name']:
#                 continue
#             processes.append({
#                 "pid": info['pid'],
#                 "name": info['name'],
#                 "ppid": info['ppid'],
#                 "cpu_percent": round(proc.cpu_percent(None), 2),
#                 "memory_rss": info['memory_info'].rss if info['memory_info'] else 0,
#                 "memory_percent": round(proc.memory_percent(), 2)
#             })
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue

#     return processes


# # ---------------- Prepare payload ----------------
# def payload():
#     return {
#         "hostname": hostname,
#         "created_at": datetime.now(timezone.utc).isoformat(),
#         "processes": collect_processes()
#     }

# # ---------------- Send data ----------------
# def send_once():
#     data = payload()
#     headers = {'Content-Type': 'application/json', 'X-API-KEY': API_KEY}

#     try:
#         r = requests.post(API_URL, json=data, headers=headers, timeout=15)
#         r.raise_for_status()
#         print("Snapshot sent successfully!")
#     except requests.exceptions.RequestException as e:
#         print("Failed to send snapshot:", e)

# # ---------------- Main ----------------
# if __name__ == "__main__":
#     send_once()
#     # input("Press Enter to exit...")  # Keeps terminal open after sending

#     print("Closing in 50 seconds...")
#     time.sleep(50)  # Keeps window open for 50 sec






# import json
# import socket
# import psutil
# import requests
# import configparser
# from datetime import datetime, timezone

# # ---------------- Load config ----------------
# cfg = configparser.ConfigParser()
# cfg.read("agent.ini")

# API_URL = cfg.get("agent", "api_url", fallback="http://127.0.0.1:8000/api/v1/process-snapshots/")
# API_KEY = cfg.get("agent", "api_key", fallback="changeme")

# hostname = socket.gethostname()

# # ---------------- Collect processes ----------------
# def collect_processes():
#     processes = []
#     for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cpu_percent', 'memory_info']):
#         try:
#             info = proc.info
#             if not info['name']:
#                 continue
#             processes.append({
#                 "pid": info['pid'],
#                 "name": info['name'],
#                 "ppid": info['ppid'],
#                 "cpu_percent": info['cpu_percent'],
#                 "memory_rss": info['memory_info'].rss if info['memory_info'] else 0
#             })
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue
#     return processes

# # ---------------- Prepare payload ----------------
# def payload():
#     return {
#         "hostname": hostname,
#         "created_at": datetime.now(timezone.utc).isoformat(),
#         "processes": collect_processes()
#     }

# # ---------------- Send data ----------------
# def send_once():
#     data = payload()
#     headers = {'Content-Type': 'application/json', 'X-API-KEY': API_KEY}

#     try:
#         r = requests.post(API_URL, json=data, headers=headers, timeout=15)
#         r.raise_for_status()
#         print("Snapshot sent successfully!")
#     except requests.exceptions.RequestException as e:
#         print("Failed to send snapshot:", e)

# # ---------------- Main ----------------
# if __name__ == "__main__":
#     send_once()
#     input("Press Enter to exit...")  # Keeps terminal open until user presses Enter




# import os
# import json
# import socket
# import psutil
# import requests
# import configparser
# from datetime import datetime, timezone
# import time


# # Load config
# cfg = configparser.ConfigParser()
# cfg.read("agent.ini")

# API_URL = cfg.get("agent", "api_url", fallback="http://127.0.0.1:8000/api/v1/process-snapshots/")
# API_KEY = cfg.get("agent", "api_key", fallback="changeme")
# INTERVAL = int(cfg.get("agent", "interval_seconds", fallback="0"))

# hostname = socket.gethostname()

# # ---------------- Collect processes ----------------
# def collect_processes():
#     processes = []
#     for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cpu_percent', 'memory_info']):
#         try:
#             info = proc.info
#             if not info['name']:  # Skip if name is empty or None
#                 continue
#             processes.append({
#                 "pid": info['pid'],
#                 "name": info['name'],
#                 "ppid": info['ppid'],
#                 "cpu_percent": info['cpu_percent'],
#                 "memory_rss": info['memory_info'].rss if info['memory_info'] else 0
#             })
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue
#     return processes


# # ---------------- Prepare payload ----------------
# def payload():
#     return {
#         "hostname": hostname,
#         "created_at": datetime.now(timezone.utc).isoformat(),
#         "processes": collect_processes()
#     }

# # ---------------- Send data ----------------
# def send_once():
#     data = payload()
#     headers = {'Content-Type': 'application/json', 'X-API-KEY': API_KEY}

#     print("\n--- DEBUG REQUEST ---")
#     print("URL:", API_URL)
#     print("Headers:", headers)
#     print("Payload:", json.dumps(data, indent=2))
#     print("--- END DEBUG ---\n")

#     try:
#         r = requests.post(API_URL, json=data, headers=headers, timeout=15)
#         r.raise_for_status()
#         print('Sent snapshot:', r.json())
#     except requests.exceptions.RequestException as e:
#         print('Send failed:', e)
#         if 'r' in locals():
#             print("Response text:", r.text)

# # ---------------- Main loop ----------------
# if __name__ == "__main__":
#     if INTERVAL == 0:
#         send_once()
#     else:
#         while True:
#             send_once()
#             time.sleep(INTERVAL)





# import os, time, json, socket, configparser
# from datetime import datetime, timezone

# import psutil
# import requests

# CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'agent.ini')

# # ------------- Load config
# cfg = configparser.ConfigParser()
# cfg.read(CONFIG_FILE)
# backend_url = os.environ.get('BACKEND_URL', cfg.get('agent', 'backend_url', fallback='http://127.0.0.1:8000/api/v1/process-snapshots/'))
# api_key = os.environ.get('API_KEY', cfg.get('agent', 'api_key', fallback='changeme'))
# interval = int(os.environ.get('INTERVAL_SECONDS', cfg.get('agent', 'interval_seconds', fallback='0')))

# hostname = socket.gethostname()

# # ------------- Collect once

# def collect_processes():
#     # Prime CPU% measurement
#     procs = []
#     proc_objs = {}
#     for p in psutil.process_iter(['pid','ppid','name']):
#         try:
#             proc_objs[p.info['pid']] = p
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue
#     # brief sleep to allow cpu_percent measurement to compute
#     time.sleep(0.4)
#     for pid, p in proc_objs.items():
#         try:
#             with p.oneshot():
#                 cpu = p.cpu_percent(interval=None)
#                 mem = p.memory_info()
#                 mem_percent = p.memory_percent()
#                 info = {
#                     'pid': pid,
#                     'ppid': p.ppid() or 0,
#                     'name': p.name(),
#                     'cpu_percent': float(cpu) if cpu is not None else None,
#                     'mem_rss': int(mem.rss) if mem else None,
#                     'mem_percent': float(mem_percent) if mem_percent is not None else None,
#                 }
#                 procs.append(info)
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             continue
#     return procs


# def payload():
#     return {
#         'hostname': hostname,
#         'created_at': datetime.now(timezone.utc).isoformat(),
#         'processes': collect_processes(),
#     }


# def send_once():
#     data = payload()
#     headers = {'Content-Type': 'application/json', 'X-API-Key': api_key}
#     try:
#         r = requests.post(backend_url, data=json.dumps(data), headers=headers, timeout=15)
#         r.raise_for_status()
#         print('Sent snapshot:', r.json())
#     except Exception as e:
#         print('Send failed:', e)


# def main():
#     if interval <= 0:
#         send_once()
#         return
#     while True:
#         send_once()
#         time.sleep(interval)

# if __name__ == '__main__':
#     main()
