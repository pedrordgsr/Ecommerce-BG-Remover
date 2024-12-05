@echo off
:: Verifica se o Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python nao esta instalado no sistema.
    pause
    exit /b
)

:: Instalar/Verificar dependencias
echo Instalando/verificando dependencias...
pip install -r requirements.txt

:: Executar o script Python
echo Executando o script...
python app.py

:: Mensagem final
echo Script finalizado.

