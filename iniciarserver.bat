@echo off
title Servidor Django + Ngrok
echo =============================================
echo  Iniciando servidor Django na porta 8000...
echo =============================================

REM Altere o caminho abaixo para a pasta do seu projeto Django
cd C:\Dev\ConsultorioDigital



if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

start cmd /k "call venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"

timeout /t 3 >nul

echo =============================================
echo  Iniciando Ngrok...
echo =============================================

start cmd /k "ngrok http 8000"