@echo off
title CampusBridge - NSUT Placement System
echo ========================================================
echo       CampusBridge - NSUT Placement Portal
echo ========================================================
echo.
cd /d "%~dp0"

echo [1/2] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [2/2] Launching CampusBridge on http://127.0.0.1:8000 ...
echo.
echo Login Credentials:
echo   - Admin Portal:   NSUT ID: ADMIN001      Password: admin123
echo   - Student Portal: NSUT ID: 2024NSUT1001  Password: student123
echo.
echo Press CTRL+C to stop the server anytime.
echo ========================================================
echo.

start "" "http://127.0.0.1:8000"
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

if %errorlevel% neq 0 (
    echo.
    echo Server stopped with error.
    pause
)
