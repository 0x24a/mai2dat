@echo off
cd /d "%~dp0"
uv run main.py %1
echo Conversation process exited.
pause