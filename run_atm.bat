@echo off
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1
where py >nul 2>nul
if %errorlevel%==0 (
    py -B main.py
) else (
    python -B main.py
)
pause
