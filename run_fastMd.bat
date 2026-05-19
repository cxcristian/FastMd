@echo off
title fastMd v1.0
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Error al iniciar fastMd. Verifica que las dependencias esten instaladas:
    echo   pip install -r requirements.txt
    pause
)
