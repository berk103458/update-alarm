@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Update Alarm - Build Pipeline

echo.
echo  ================================================
echo   Update Alarm ^| Build Pipeline
echo  ================================================
echo.

:: ── 1. Bagimliliklar ───────────────────────────────────────────────────────
echo [1/5] Bagimliliklar kuruluyor...
python -m pip install -r requirements.txt --quiet
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo HATA: pip basarisiz. Python yuklu ve PATH'te mi?
    pause & exit /b 1
)
echo       Tamam.

:: ── 2. Ikon olustur ────────────────────────────────────────────────────────
echo [2/5] icon.ico olusturuluyor...
python create_icon.py
if errorlevel 1 (
    echo HATA: Ikon olusturulamadi.
    pause & exit /b 1
)

:: ── 3. EXE derle ───────────────────────────────────────────────────────────
echo [3/5] UpdateAlarm.exe derleniyor (PyInstaller)...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --name=UpdateAlarm ^
    --clean ^
    --noconfirm ^
    --add-data "icon.ico;." ^
    main.py

if errorlevel 1 (
    echo HATA: PyInstaller basarisiz.
    pause & exit /b 1
)
if not exist "dist\UpdateAlarm.exe" (
    echo HATA: dist\UpdateAlarm.exe bulunamadi.
    pause & exit /b 1
)
echo       dist\UpdateAlarm.exe hazir.

:: ── 4. Installer klasorunu hazirla ─────────────────────────────────────────
echo [4/5] Installer olusturuluyor (Inno Setup)...
if not exist "dist\installer" mkdir "dist\installer"

:: Inno Setup yollarini ara
set ISCC=""
for %%P in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
) do (
    if exist %%P set ISCC=%%P
)

if %ISCC%=="" (
    echo.
    echo  [!] Inno Setup bulunamadi.
    echo      Inno Setup'i buradan yukleyin:
    echo      https://jrsoftware.org/isdl.php
    echo.
    echo  Alternatif: dist\UpdateAlarm.exe'yi dogrudan dagitabilirsiniz.
    echo.
    goto :skip_inno
)

%ISCC% setup.iss
if errorlevel 1 (
    echo HATA: Inno Setup basarisiz.
    pause & exit /b 1
)
echo       dist\installer\ altinda Setup dosyasi hazir.

:skip_inno

:: ── 5. Ozet ────────────────────────────────────────────────────────────────
echo.
echo  ================================================
echo   BUILD TAMAMLANDI
echo  ================================================
echo.
echo   EXE      : dist\UpdateAlarm.exe
if exist "dist\installer" (
    echo   SETUP    : dist\installer\UpdateAlarm_Setup_*.exe
)
echo.
echo   YAYINLAMA ADIMLARI:
echo   1. dist\installer\UpdateAlarm_Setup_x.y.z.exe'yi GitHub Release'e yukleyin
echo   2. latest.json'u asagidaki gibi duzenleyin ve GitHub'a gonderin:
echo      version     : yeni versiyon numarasi
echo      download_url: https://github.com/berk103458/update-alarm/releases/download/vX.Y.Z/UpdateAlarm_Setup_X.Y.Z.exe
echo   3. version.py icindeki UPDATE_CHECK_URL'yi GitHub raw linkinizle degistirin
echo.
pause
