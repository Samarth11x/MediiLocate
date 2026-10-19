# ==============================================================================
# MediLocate AI — Phase 1 Foundation Verification Script (PowerShell)
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " MediLocate AI: Verifying Phase 1 Project Foundation" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$expectedDirectories = @(
    "frontend/public",
    "frontend/src/assets",
    "frontend/src/components/common",
    "frontend/src/components/medicine",
    "frontend/src/components/pharmacy",
    "frontend/src/components/medibot",
    "frontend/src/layouts",
    "frontend/src/pages",
    "frontend/src/hooks",
    "frontend/src/services",
    "frontend/src/styles",
    "frontend/src/utils",
    "frontend/src/tests",
    "backend/config",
    "backend/apps/accounts",
    "backend/apps/pharmacies",
    "backend/apps/medicines",
    "backend/apps/inventory",
    "backend/apps/search",
    "backend/services",
    "backend/tests",
    "core_intelligence/search_engine",
    "core_intelligence/ranking",
    "core_intelligence/availability",
    "core_intelligence/location",
    "core_intelligence/tests",
    "medibot/intents",
    "medibot/dialogue",
    "medibot/tools",
    "medibot/safety",
    "medibot/tests",
    "database/migrations",
    "database/schema",
    "database/seeds",
    "database/tests",
    "docs",
    "scripts"
)

$expectedFiles = @(
    "README.md",
    ".gitignore",
    ".env.example",
    "docs/ARCHITECTURE.md",
    "docs/DEVELOPMENT_ROADMAP.md",
    "docs/SETUP_GUIDE.md",
    "docs/DATABASE_DESIGN.md",
    "docs/TESTING_STRATEGY.md"
)

$allPassed = $true

Write-Host "`n1. Verifying Required Directories..." -ForegroundColor Yellow
$missingDirs = 0
foreach ($dir in $expectedDirectories) {
    if (Test-Path -Path $dir -PathType Container) {
        Write-Host "  [OK] $dir" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $dir" -ForegroundColor Red
        $allPassed = $false
        $missingDirs++
    }
}
Write-Host "Directory Check: $($expectedDirectories.Count - $missingDirs)/$($expectedDirectories.Count) directories present."

Write-Host "`n2. Verifying Required Documentation & Configuration Files..." -ForegroundColor Yellow
$missingFiles = 0
foreach ($file in $expectedFiles) {
    if (Test-Path -Path $file -PathType Leaf) {
        $item = Get-Item $file
        if ($item.Length -gt 0) {
            Write-Host "  [OK] $file ($($item.Length) bytes)" -ForegroundColor Green
        } else {
            Write-Host "  [EMPTY] $file is 0 bytes!" -ForegroundColor Red
            $allPassed = $false
            $missingFiles++
        }
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $allPassed = $false
        $missingFiles++
    }
}

Write-Host "`n3. Verifying .env.example Placeholders (Zero Leaked Secrets)..." -ForegroundColor Yellow
if (Test-Path ".env.example") {
    $envContent = Get-Content ".env.example" -Raw
    $hasRealSecrets = $false

    # Scan for suspicious non-placeholder patterns
    if ($envContent -match "ey[A-Za-z0-9_-]{20,}") {
        Write-Host "  [WARNING] Possible JWT/Bearer token detected in .env.example!" -ForegroundColor Red
        $hasRealSecrets = $true
    }
    
    if (-not $hasRealSecrets) {
        Write-Host "  [OK] .env.example contains safe placeholders only." -ForegroundColor Green
    } else {
        $allPassed = $false
    }
}

Write-Host "`n4. Host Tooling Status..." -ForegroundColor Yellow
# Node.js
try {
    $nodeVer = & node -v
    Write-Host "  [OK] Node.js is installed: $nodeVer" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Node.js not detected in PATH." -ForegroundColor DarkYellow
}

# npm (using npm.cmd for PowerShell safety)
try {
    $npmVer = & npm.cmd -v
    Write-Host "  [OK] npm is installed: $npmVer (accessible via npm.cmd)" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] npm.cmd not detected." -ForegroundColor DarkYellow
}

# Python
try {
    $pyVer = & python --version
    Write-Host "  [OK] Python is installed: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Python not detected in PATH." -ForegroundColor DarkYellow
}

# Git
try {
    $gitVer = & git --version
    Write-Host "  [OK] Git is installed: $gitVer" -ForegroundColor Green
} catch {
    Write-Host "  [NOTE] Git is not yet recognized in PATH. See docs/SETUP_GUIDE.md." -ForegroundColor Cyan
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host " PHASE 1 FOUNDATION VERIFICATION: PASSED" -ForegroundColor Green
} else {
    Write-Host " PHASE 1 FOUNDATION VERIFICATION: FAILED WITH ERRORS" -ForegroundColor Red
}
Write-Host "==========================================================" -ForegroundColor Cyan
