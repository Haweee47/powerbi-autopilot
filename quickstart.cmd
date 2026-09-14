@echo off
REM Double-click: builds the dashboard pilot and opens it in Power BI Desktop.
REM Other options: quickstart.cmd --purpose matrix --theme midnight --lang ja   (see docs\guide)
cd /d "%~dp0"
set PY=python
where python >nul 2>nul || set PY=py
where %PY% >nul 2>nul || (
  echo Python 3.10 or newer is required: https://www.python.org/downloads/
  echo During setup, tick "Add python.exe to PATH", then run this file again.
  pause
  exit /b 1
)
%PY% tools\quickstart.py --open %*
pause
