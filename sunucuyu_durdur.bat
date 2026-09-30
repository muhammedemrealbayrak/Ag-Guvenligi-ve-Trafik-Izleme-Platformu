@echo off
chcp 65001 > nul
title Sunucu Durdurucu
echo 127.0.0.1:8080 uzerindeki tum servisler durduruluyor...
powershell -Command "Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
echo [OK] Sunucu ve baglantilar kapatildi.
pause
