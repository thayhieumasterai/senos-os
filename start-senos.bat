@echo off
chcp 65001 >nul
title Khoi dong SenOS
cd /d "%~dp0"

echo Bat SenOS chay NEN - khong con cua so den (port 7777)...
REM Viec tat instance cu + chay server AN giao het cho start-senos.vbs (cua so an hoan toan).
REM Log ghi vao server\senos.log (mo file do neu can xem loi). Tat server: stop-senos.bat.
wscript //nologo start-senos.vbs

echo.
echo Da bat. Cho ~10 giay roi mo http://localhost:7777 va bam Ctrl+Shift+R.
echo (Tat server: chay stop-senos.bat. Xem loi: mo file server\senos.log)
timeout /t 4 >nul
