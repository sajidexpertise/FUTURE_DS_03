@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 generate_data.py && py -3 analyze.py
) else (
  python generate_data.py && python analyze.py
)
if errorlevel 1 (
  echo Analysis failed. Check that Python 3.9 or newer is installed.
  pause
  exit /b 1
)
start "CONVERT Dashboard" "%~dp0index.html"
pause
