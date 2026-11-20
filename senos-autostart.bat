@echo off
chcp 65001 >nul
title Tu khoi dong SenOS
REM Tu khoi dong SenOS cung Windows. Dung: senos-autostart.bat install | uninstall | status
REM Logic nam trong senos-autostart.ps1 (ghi/xoa muc SenOS trong HKCU Run, khong can quyen
REM admin). Bat roi thi dang nhap may la server tu chay nen va tu mo dashboard (0.306.0).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0senos-autostart.ps1" %1
