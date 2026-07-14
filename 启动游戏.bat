@echo off
setlocal
cd /d "%~dp0"

python pvz.py
if errorlevel 1 (
    echo.
    echo Failed to start the game.
    echo Check that Python and Pygame are installed, then try again.
    pause
)

endlocal
