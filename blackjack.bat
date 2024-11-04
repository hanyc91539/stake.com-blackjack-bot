@echo off
if not exist "C:\chrome\blackjack" mkdir "C:\chrome\blackjack"
echo.
set /p input=Do you have a browser open for Stake Blackjack?(y/n):
if /I "%input%"=="n" (
    start chrome.exe -remote-debugging-port=9035 --user-data-dir="C:\chrome\blackjack"
)
echo.
set /p input=Make sure you are logged in to the Stake.(y/n):
echo.
if /I "%input%"=="y" (
    python blackjack.py
)
pause