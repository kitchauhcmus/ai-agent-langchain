@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py main.py --demo
) else (
    python main.py --demo
)
echo.
echo Demo finished. Read README.md to explore other modes.
echo Open outputs\course_averages.svg to see the chart.
pause
