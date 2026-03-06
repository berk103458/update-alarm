@echo off
title GitHub Giris
echo GitHub'a giris yapiliyor...
echo.
echo Asagidaki adimlari izle:
echo  1) "GitHub.com" seciliyken Enter
echo  2) "HTTPS" seciliyken Enter
echo  3) "Yes" Enter
echo  4) "Login with a web browser" Enter
echo  5) Ekrandaki 8 haneli KODU kopyala
echo  6) Tarayici acilacak - kodu yapistir ve GitHub'a giris yap
echo.
"C:\Program Files\GitHub CLI\gh.exe" auth login
echo.
echo -------- Giris durumu --------
"C:\Program Files\GitHub CLI\gh.exe" auth status
echo.
pause
