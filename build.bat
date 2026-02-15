@echo off
REM Genera el .exe de TodoListKawaii. Ejecutar desde la carpeta del proyecto.
echo Construyendo TodoListKawaii.exe ...
cd /d "%~dp0"

REM Si el .exe esta en ejecucion, PyInstaller no puede reemplazarlo (Acceso denegado)
tasklist /FI "IMAGENAME eq TodoListKawaii.exe" 2>NUL | find /I "TodoListKawaii.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ERROR: TodoListKawaii.exe esta abierto. Cierralo y vuelve a ejecutar build.bat
    echo.
    pause
    exit /b 1
)
if exist "dist\TodoListKawaii.exe" (
    del /F /Q "dist\TodoListKawaii.exe" 2>NUL
    if errorlevel 1 (
        echo.
        echo ERROR: No se puede borrar dist\TodoListKawaii.exe. Cierra el .exe o cualquier programa que lo use y vuelve a intentar.
        pause
        exit /b 1
    )
)

if not exist "icono_unicornio.ico" (
    echo Generando icono .ico ...
    python crear_icono_ico.py
)
pip install pyinstaller -q
REM El icono ya esta configurado en TodoListKawaii.spec
pyinstaller --noconfirm TodoListKawaii.spec

if exist "dist\TodoListKawaii.exe" (
    echo.
    echo Listo: dist\TodoListKawaii.exe ^(icono unicornio^)
    echo Puedes copiarlo a otra PC o usar Inno Setup para crear el instalador.
) else (
    echo Error en la construccion.
    exit /b 1
)
