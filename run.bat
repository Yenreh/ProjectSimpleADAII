@echo off
setlocal

REM Ask for Python version (e.g. 3.12)
set /p python_version=Enter python version (e.g. 3.12): 

REM Create virtual environment with the specified Python version
python%python_version% -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Install requirements
pip%python_version% install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    exit /b 1
)

REM Run the project
python%python_version% run.py

REM Deactivate the virtual environment
deactivate

endlocal
