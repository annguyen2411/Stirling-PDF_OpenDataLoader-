@echo off
:: Chay file nay bang quyen Run as Administrator
chcp 65001 >nul
echo ========================================================
echo   Chia se thu muc tu dong hoa Stirling-PDF qua mang LAN
echo ========================================================
echo.
echo 1. Thu muc OCR tu dong:
net share Scan-In="D:\Stirling-PDF\pipeline\Scan-In" /grant:Everyone,FULL
net share Scan-Out="D:\Stirling-PDF\pipeline\Scan-Out" /grant:Everyone,FULL
echo.
echo 2. Thu muc Boc tach du lieu AI (OpenDataLoader-PDF):
net share PDF-To-Markdown-In="D:\Stirling-PDF\pipeline\PDF-To-Markdown-In" /grant:Everyone,FULL
net share PDF-To-Markdown-Out="D:\Stirling-PDF\pipeline\PDF-To-Markdown-Out" /grant:Everyone,FULL
echo.
echo Da chia se thanh cong!
echo Nhan vien tu may khac (trong cung mang LAN/Wi-Fi) chi can mo File Explorer:
echo.
echo   [OCR Tu dong]
echo   - Tha file scan: \\172.16.2.87\Scan-In
echo   - Nhan file OCR: \\172.16.2.87\Scan-Out
echo.
echo   [Boc tach bang bieu & Markdown AI]
echo   - Tha file PDF: \\172.16.2.87\PDF-To-Markdown-In
echo   - Nhan file .md & .json: \\172.16.2.87\PDF-To-Markdown-Out
echo.
pause
