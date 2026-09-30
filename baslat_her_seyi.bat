@echo off
chcp 65001 > nul
title Laboratuvar Baslatici

echo =======================================================================
echo   AĞ GÜVENLİĞİ VE TRAFİK İZLEME MERKEZİ BAŞLATILIYOR (JÜRİ MODU)
echo =======================================================================
echo.
echo 1. Web Sunucusu ve Canlı Dashboard baslatiliyor (127.0.0.1:8080)...
start "SOC Web Dashboard Sunucusu" python src\server.py

timeout /t 2 /nobreak > nul

echo 2. Web Tarayicisi (Dashboard) aciliyor...
start http://127.0.0.1:8080/

echo 3. Canli Terminal Ag Izleyicisi (NOC Console) baslatiliyor...
start "Canli Ag Trafigi ve IDS Paneli" python monitor.py

echo.
echo =======================================================================
echo [OK] Tum sistemler hazir!
echo      - Web Dashboard tarayicinizda acildi.
echo      - Canli terminal izleyicisi yan pencerede baslatildi.
echo      - Simdi Slowloris saldirisini calistirabilirsiniz!
echo =======================================================================
pause
