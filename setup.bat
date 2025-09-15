@echo off
setlocal enabledelayedexpansion

echo Setting up project environment...

REM Ensure we're in the script's directory
cd /d %~dp0

REM Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo No requirements.txt found!
)

echo Setup complete! Virtual environment is ready.
echo Run "venv\Scripts\activate.bat" to activate later.

endlocal