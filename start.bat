@echo off
cd /d "%~dp0"
echo Bagimliliklar kontrol ediliyor...
python -m pip install -r requirements.txt --quiet
echo Uygulama baslatiliyor...
start "" pythonw main.py
timeout /t 2 /nobreak >nul
echo OYYA1UPDATE ALARM sistem tepsisinde calisiyor. Bu pencere kapanabilir.
pause
