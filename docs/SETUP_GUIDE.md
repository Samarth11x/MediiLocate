# MediLocate AI — Developer Setup Guide (Windows & PowerShell)

This guide walks developers through setting up the local development environment for **MediLocate AI** on a Windows workstation using PowerShell.

---

## 1. Required Tooling

Ensure the following prerequisites are installed before beginning later implementation phases:

| Tool | Minimum Version | Verified on Host | Installation Command (Windows `winget`) |
| :--- | :--- | :--- | :--- |
| **Node.js** | v18.0.0+ | **v24.22.0** (Detected) | `winget install OpenJS.NodeJS.LTS` |
| **npm** | v9.0.0+ | **v11.19.1** (Detected) | Included with Node.js |
| **Python** | v3.11.0+ | **v3.13.5** (Detected) | `winget install Python.Python.3.13` |
| **Git** | v2.35.0+ | **v2.48.1** (`C:\Program Files\Git\cmd\git.exe`) | `winget install --id Git.Git -e --source winget` |

---

## 2. Windows PowerShell Nuances & Troubleshooting

### 2.1 PowerShell Script Execution Policy
On Windows, PowerShell by default restricts running scripts (`.ps1`). If you encounter an error like:
```powershell
File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled on this system.
```
You have two options:

- **Option A (Recommended for current session/user):**
  Open PowerShell and permit local unsigned scripts for your user account:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```

- **Option B (Direct Command Execution):**
  Explicitly invoke `.cmd` binaries or full executable paths instead of `.ps1`:
  ```powershell
  npm.cmd -v
  npx.cmd vite
  & "C:\Program Files\Git\cmd\git.exe" status
  ```

### 2.2 Installing and Configuring Git on Windows
If `git` is not recognized in your terminal:
1. Open PowerShell and install Git via winget:
   ```powershell
   winget install --id Git.Git -e --source winget
   ```
2. Restart your terminal or add Git to your user PATH:
   ```powershell
   $env:Path += ";C:\Program Files\Git\cmd"
   ```
3. Configure your Git identity:
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

---

## 3. Python Virtual Environment Setup & Backend Dependencies

The project uses an isolated Python virtual environment (`venv`) located at the project root.

### 3.1 Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
*(If script execution is disabled, you can directly invoke the virtual environment's Python binary: `.\venv\Scripts\python.exe`).*

### 3.2 Install Backend Dependencies
```powershell
.\venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```
Pinned dependencies include:
- `Django==5.2.18` (LTS series)
- `djangorestframework==3.18.3`
- `psycopg[binary]==3.3.6` (Psycopg 3 with precompiled Windows wheels)
- `django-cors-headers==4.9.0`
- `python-dotenv==1.2.4`

---

## 4. Backend Development & Verification (PowerShell)

### 4.1 Django System Integrity Check
```powershell
.\venv\Scripts\python.exe backend/manage.py check
```

### 4.2 Run Database Migrations
```powershell
.\venv\Scripts\python.exe backend/manage.py migrate
```
*(By default, if Supabase credentials are not provided in `.env`, Django safely initializes a local development SQLite database: `backend/db.sqlite3`)*.

### 4.3 Run Automated Backend Tests
```powershell
.\venv\Scripts\python.exe backend/manage.py test tests apps
```
Runs 29 unit and API tests covering `/api/v1/health/`, model integrity, geo-coordinate validation, dynamic availability evaluation, and the `/api/v1/chat/` conversational endpoint.

### 4.4 Start the Django Development Server
```powershell
.\venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000
```
Server runs at: `http://127.0.0.1:8000/`

### 4.5 Verify the Health Check Endpoint
In PowerShell:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/health/
# Returns: @{status=ok; service=MediLocate API}
```
Or via curl:
```bash
curl http://127.0.0.1:8000/api/v1/health/
```

### 4.6 Verify the MediBot Chat Endpoint
In PowerShell:
```powershell
# Test greeting
$body = @{ message = "Hello MediBot" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/chat/ -Method Post -Body $body -ContentType "application/json"

# Test medicine lookup
$body = @{ message = "Find Paracetamol 500mg" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/chat/ -Method Post -Body $body -ContentType "application/json"

# Test acute emergency safety interceptor
$body = @{ message = "I have severe chest pain" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/chat/ -Method Post -Body $body -ContentType "application/json"
```
Or via curl:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/ -H "Content-Type: application/json" -d "{\"message\": \"Hello\"}"
```

---

## 5. Connecting to Supabase PostgreSQL

To switch from the local SQLite fallback to your live Supabase database:

1. Copy `.env.example` to create your local `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. In Supabase Dashboard -> **Project Settings** -> **Database**:
   - For **IPv4 networks (recommended)**: Copy the **Session pooler** connection string:
     - Host: `aws-0-[REGION].pooler.supabase.com`
     - Port: `5432` or `6543`
     - User: `postgres.[YOUR_PROJECT_REF]`
     - Password: Your project database password
   - For **IPv6 networks**: Copy direct connection:
     - Host: `db.[YOUR_PROJECT_REF].supabase.co`
     - Port: `5432`
     - User: `postgres`
3. Update `.env`:
   ```ini
   SUPABASE_DB_HOST=aws-0-ap-south-1.pooler.supabase.com
   SUPABASE_DB_PORT=5432
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres.yourprojectref
   SUPABASE_DB_PASSWORD=YourSecurePassword
   SUPABASE_DB_SSLMODE=require
   ```
4. Run migrations to provision tables on Supabase:
   ```powershell
   .\venv\Scripts\python.exe backend/manage.py migrate
   ```

---

## 6. Frontend Development & Verification (PowerShell)

The React + Vite frontend application is located inside `frontend/`.

### 6.1 Install Frontend Dependencies
```powershell
cd frontend
npm.cmd install
```

### 6.2 Start the Local Development Server
```powershell
npm.cmd run dev
# Serves the application locally at: http://localhost:5173
```

### 6.3 Run Frontend Automated Tests
```powershell
npm.cmd test
# Executes the Vitest suite (7/7 tests passing)
```

### 6.4 Build for Production
```powershell
npm.cmd run build
# Compiles optimized bundles to: frontend/dist/
```

---

## 7. Core Intelligence Development & Testing (PowerShell)

The `core_intelligence/` package contains pure Python algorithms (search matching, availability rules, Haversine distance, transparent ranking).

### 7.1 Install Test Runner Dependencies
```powershell
.\venv\Scripts\python.exe -m pip install -r core_intelligence/requirements-dev.txt
```

### 7.2 Run Core Intelligence Pytest Suite
```powershell
.\venv\Scripts\python.exe -m pytest core_intelligence/tests -q
```
Executes all 67 isolated unit tests across normalization, medicine matching, availability, freshness, distance, and ranking.

---

## 8. MediBot Conversational Intelligence & Safety Testing (PowerShell)

The `medibot/` package contains the rule-based assistant, medical safety guardrails, intent parser, and tool interfaces.

### 8.1 Run MediBot Pytest Suite
```powershell
.\venv\Scripts\python.exe -m pytest medibot/tests -v
```
Executes all 48 tests verifying input sanitization, acute emergency interceptor (chest pain, breathing difficulty, overdose, stroke), medical advice guardrails (treatment, dosage, drug interaction), intent patterns, tool protocols, and dialogue manager workflows.

### 8.2 Run Combined Python Intelligence Pytest Suite
```powershell
.\venv\Scripts\python.exe -m pytest core_intelligence/tests medibot/tests -q
```
Executes all 115 pure-Python tests across Core Intelligence and MediBot.

---

## 9. Current Phase Status

> [!IMPORTANT]
> **Phase 5 Status (COMPLETED):**
> - Independent rule-based conversational assistant implemented in `medibot/`.
> - Acute emergency interception (112/108/911 guidance) and strict medical advice refusal guardrails verified.
> - Decoupled tool integration: `MedicineSearchTool` bridges to `core_intelligence.search_engine.matching.search_medicines` via injected Django providers; `PharmacySearchTool` provides honest placeholder contract.
> - Stateless privacy: Zero persistence of chat transcripts or user queries in database.
> - REST API endpoint active: `POST /api/v1/chat/` with full validation, HTTP 400 for malformed input, and HTTP 405 for invalid methods.
> - Verification metrics: **115/115 pytest tests pass** (67 Core Intelligence + 48 MediBot), **29/29 Django backend tests pass**, and **7/7 frontend Vitest tests pass** with clean production build.
> 
> Proceed to **Phase 6 (Search & Pharmacy Workflows)** to connect the React frontend to the backend search, geolocation, and chat APIs.
