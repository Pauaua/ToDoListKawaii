@echo off
REM Genera el .exe de TodoListKawaii. Ejecutar desde la carpeta del proyecto.
echo Construyendo TodoListKawaii.exe ...
cd /d "%~dp0"

if not exist "icono_unicornio.ico" (
    echo Generando icono .ico ...
    python crear_icono_ico.py
)
pip install pyinstaller -q
REM El icono ya está configurado en TodoListKawaii.spec, no hace falta pasarlo por línea de comandos
pyinstaller --noconfirm TodoListKawaii.spec

if exist "dist\TodoListKawaii.exe" (
    echo.
    echo Listo: dist\TodoListKawaii.exe ^(icono unicornio^)
    echo Puedes copiarlo a otra PC o usar Inno Setup para crear el instalador.
) else (
    echo Error en la construccion.
    exit /b 1
)
