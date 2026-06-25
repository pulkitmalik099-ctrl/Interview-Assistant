@echo off
title AI Interview Copilot Launcher
:menu
cls
echo ==================================================
echo              AI INTERVIEW COPILOT                 
echo ==================================================
echo.
echo  [1] Start Copilot (Real Mode - requires Gemini API key in .env)
echo  [2] Start Copilot (Offline Mock Test Mode - no API key needed)
echo  [3] Run Microphone Diagnostic Tool
echo  [4] Exit
echo.
echo ==================================================
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting Real Copilot...
    venv\Scripts\python.exe interview_assistant.py
    pause
    goto :menu
)
if "%choice%"=="2" (
    echo.
    echo Starting Offline Mock Test Mode...
    venv\Scripts\python.exe interview_assistant.py --mock
    pause
    goto :menu
)
if "%choice%"=="3" (
    echo.
    echo Running Microphone Diagnostics...
    venv\Scripts\python.exe test_mic.py
    pause
    goto :menu
)
if "%choice%"=="4" (
    exit
)

echo Invalid choice, please select 1, 2, 3, or 4.
pause
goto :menu
