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
| **Git** | v2.35.0+ | *Not yet detected in PATH* | `winget install --id Git.Git -e --source winget` |

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
  Explicitly invoke `.cmd` binaries instead of `.ps1`:
  ```powershell
  npm.cmd -v
  npx.cmd vite
  ```

### 2.2 Installing and Configuring Git on Windows
If `git` is not recognized in your terminal:
1. Open PowerShell and install Git via winget:
   ```powershell
   winget install --id Git.Git -e --source winget
   ```
2. Restart your terminal to refresh system environment variables (`PATH`).
3. Configure your Git identity:
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

---

## 3. Python Virtual Environment Setup (For Future Phases)

In Phase 3 (Backend Setup), you will configure an isolated Python virtual environment:

1. **Create the virtual environment** in the project root:
   ```powershell
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(If prompted with an execution policy error, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` first).*

3. **Verify Python points to the virtual environment**:
   ```powershell
   Get-Command python | Select-Object -ExpandProperty Source
   # Should output: ...\MediLocate\venv\Scripts\python.exe
   ```

---

## 4. Environment Variables Configuration

Before running backend or frontend servers in subsequent phases:
1. Copy `.env.example` to create a local `.env` file:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` and fill in your local or Supabase development parameters.
3. **Security Rule:** Never check `.env` into version control. Ensure `.gitignore` remains active.

---

---

## 5. Frontend Development & Verification (PowerShell)

The React + Vite frontend application is located inside the `frontend/` directory.

### 5.1 Navigate to the Frontend Directory
```powershell
Set-Location -Path frontend
# Or: cd frontend
```

### 5.2 Install Frontend Dependencies
```powershell
npm.cmd install
```

### 5.3 Start the Local Development Server
```powershell
npm.cmd run dev
# Serves the application locally at: http://localhost:5173
```

### 5.4 Run Frontend Automated Tests
```powershell
npm.cmd test
# Executes the Vitest suite in single-run mode
```

To run tests in watch mode during development:
```powershell
npm.cmd run test:watch
```

### 5.5 Build for Production
```powershell
npm.cmd run build
# Compiles optimized HTML, CSS, and JS bundles to: frontend/dist/
```

---

## 6. Design Intelligence Tooling Setup (Optional References)

### 6.1 UI/UX Pro Max CLI
To install and initialize the UI/UX Pro Max design intelligence skill locally:
```powershell
npm.cmd install -g ui-ux-pro-max-cli
uipro init --ai antigravity
```

### 6.2 21st.dev Component Catalog CLI
To install and authenticate the 21st.dev catalog CLI:
```powershell
npm.cmd install -g @21st-dev/cli
21st login
```

---

## 7. Current Phase Status

> [!IMPORTANT]
> **Phase 2 Status (COMPLETED):**
> - The React + Vite JavaScript frontend shell and **Clinical Minimalism** design system are fully implemented and verified.
> - Vitest component testing passes with 100% success rate (7/7 tests).
> - Production asset building compiles cleanly without warnings.
> 
> Proceed to **Phase 3 (Backend & Supabase Setup)** to configure the Django REST Framework API and database schema.
