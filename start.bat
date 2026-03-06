@echo off
cd /d "%~dp0"
echo Bagimliliklar kontrol ediliyor...
python -m pip install -r requirements.txt --quiet
echo Uygulama baslatiliyor...
start "" pythonw main.py
timeout /t 2 /nobreak >nul
echo Update Alarm sistem tepsisinde calisiyor. Bu pencere kapanabilir.
pause
