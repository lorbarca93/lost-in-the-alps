@echo off
REM ============================================================================
REM AI Hut Enrichment - Quick Start Script
REM ============================================================================

echo.
echo ============================================================================
echo    AI HUT ENRICHMENT - Quick Start
echo ============================================================================
echo.
echo This script will enrich your mountain huts database with AI-generated
echo historical information using a LOCAL language model (no cloud costs!).
echo.
echo Requirements:
echo   1. Ollama installed and running
echo   2. Model downloaded (e.g., llama3.2)
echo   3. Python packages installed
echo.
echo ============================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if Ollama is accessible
echo Checking Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Cannot connect to Ollama!
    echo.
    echo Please make sure Ollama is running:
    echo   1. Install from: https://ollama.ai/download/windows
    echo   2. Ollama should start automatically
    echo   3. Run: ollama pull llama3.2
    echo.
    pause
    exit /b 1
)

echo Ollama is running!
echo.

REM Prompt for mode
echo Select mode:
echo   1. Test run (first 5 huts only)
echo   2. Full run (all huts, 30s delay) - Recommended
echo   3. Fast run (15s delay)
echo   4. Slow run (60s delay) - Good for overnight
echo.
set /p mode="Enter choice (1-4): "

if "%mode%"=="1" (
    echo.
    echo Starting TEST RUN (5 huts)...
    python tools\enrich_huts_with_ai.py --limit 5
) else if "%mode%"=="2" (
    echo.
    echo Starting FULL RUN (30s delay)...
    echo Press Ctrl+C to stop anytime (progress will be saved)
    echo.
    timeout /t 3
    python tools\enrich_huts_with_ai.py
) else if "%mode%"=="3" (
    echo.
    echo Starting FAST RUN (15s delay)...
    echo Press Ctrl+C to stop anytime (progress will be saved)
    echo.
    timeout /t 3
    python tools\enrich_huts_with_ai.py --delay 15
) else if "%mode%"=="4" (
    echo.
    echo Starting SLOW RUN (60s delay)...
    echo Press Ctrl+C to stop anytime (progress will be saved)
    echo.
    timeout /t 3
    python tools\enrich_huts_with_ai.py --delay 60
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Script finished!
echo ============================================================================
echo.
echo Check results:
echo   - Log: logs\ai_enrichment.log
echo   - Progress: data\ai_enrichment_progress.json
echo.
echo To see enriched huts on the website:
echo   1. Run: python website\api\export_huts.py
echo   2. Start server: cd website ^&^& python -m http.server 8080
echo   3. Open: http://localhost:8080/mountain_huts_map.html
echo.
pause

