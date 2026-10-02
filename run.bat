@echo off
chcp 65001 >nul
echo ===================================================
echo     Stirling-PDF & OpenDataLoader-PDF Manager
echo ===================================================
echo.
echo [1] Khoi dong toan bo he thong (Start Services)
echo [2] Dung he thong (Stop Services)
echo [3] Xem trang thai & nhat ky (Status / Logs)
echo [4] Cap nhat / Build lai Service
echo [5] Thoat
echo.
set /p choice="Chon thao tac (1-5): "

if "%choice%"=="1" (
    docker compose up -d
    echo.
    echo He thong dang chay thanh cong!
    echo ===================================================
    echo 1. Stirling-PDF (Xu ly moi tac vu PDF):
    echo    - May chu: http://localhost:9280
    echo    - Mang LAN: http://172.16.2.87:9280
    echo.
    echo 2. OpenDataLoader (Boc tach bang bieu & Markdown AI):
    echo    - May chu: http://localhost:9281
    echo    - Mang LAN: http://172.16.2.87:9281
    echo ===================================================
    pause
)
if "%choice%"=="2" (
    docker compose down
    echo He thong da dung!
    pause
)
if "%choice%"=="3" (
    docker compose ps
    docker compose logs --tail=50
    pause
)
if "%choice%"=="4" (
    docker compose build opendataloader
    docker compose pull stirling-pdf
    docker compose up -d
    echo Da cap nhat thanh cong!
    pause
)
