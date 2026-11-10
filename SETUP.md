# Environment Setup & Deployment Runbook — WordPress Contact Form 7 → n8n CRM Integration Lab

This guide covers running the **WordPress CF7 → n8n CRM Integration Lab** via **Docker Compose** or via the **Local Host Runner**.

---

## Method A: Standard Docker Compose Deployment (Recommended)

### Prerequisites:
- Windows 11 with Docker Desktop installed and WSL 2 backend enabled.
- 4GB+ available RAM, 5GB+ free disk space.

### 1. Clone & Configure
```bash
git clone https://github.com/Jk-7bod7/wordpress-cf7-n8n-crm-integration-lab.git
cd wordpress-cf7-n8n-crm-integration-lab
cp .env.example .env
```

### 2. Start Services
```bash
docker compose up -d --build
```

### 3. Verify Container Health
```bash
docker compose ps
```
Expected output:
- `cf7_lab_wordpress`: Up (healthy) on `127.0.0.1:8088->80/tcp` (or configured WP_PORT)
- `cf7_lab_mariadb`: Up (healthy) on `3306/tcp`
- `cf7_lab_n8n`: Up on `127.0.0.1:5678->5678/tcp`
- `cf7_lab_crm`: Up (healthy) on `127.0.0.1:8000->8000/tcp`
- `cf7_lab_mailpit`: Up on `127.0.0.1:8025->8025/tcp, 127.0.0.1:1025->1025/tcp`

### 4. Stopping the Stack
```bash
docker compose stop    # Pause services without deleting data
docker compose down    # Stop containers, keeping persistent volumes intact
```

---

## Method B: Native Host Execution (No Docker Required)

If Docker Desktop is not installed or administrator elevation is restricted on your machine, you can run the services natively using local Python, Mailpit, and the included test harness:

### 1. Python Environment Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r crm/requirements.txt
```

### 2. Launch Mock CRM Service
```bash
python -m uvicorn crm.app:app --host 127.0.0.1 --port 8000
```
Verify endpoint: `curl http://127.0.0.1:8000/health`

### 3. Launch Local Mailpit Sandbox
```bash
.\mailpit\mailpit.exe --smtp 127.0.0.1:1025 --listen 127.0.0.1:8025
```
Open Mailpit Web UI in browser: [http://localhost:8025](http://localhost:8025)

### 4. Run Automated Acceptance Tests
```bash
python -m unittest tests/test_portfolio_024.py
```

---

## Windows 11 Administrative Prerequisites Note

If installing Docker Desktop on Windows 11 Home from scratch:
1. Docker Desktop installer requires Windows Administrator elevation to install the `Docker Desktop Service` and configure local network adapters.
2. WSL 2 requires enabling the `VirtualMachinePlatform` and `Microsoft-Windows-Subsystem-Linux` features via an elevated PowerShell prompt (`wsl --install`), followed by a system reboot.
3. In headless or un-elevated agent sessions, run via **Method B** for 100% test verification.
