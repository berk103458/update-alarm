@echo off
cd /d "%~dp0"
echo Bagimliliklar kuruluyor...
python -m pip install -r requirements.txt
echo.
echo Uygulama baslatiliyor (debug modu - konsol acik kalir)...
python main.py
pause
