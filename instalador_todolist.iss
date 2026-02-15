; Script Inno Setup para Agenda Virtual
; Compilar desde Inno Setup Compiler (Build -> Compile).
;
; ARCHIVOS NECESARIOS (en la carpeta del proyecto, junto a este .iss):
;   1. dist\TodoListKawaii.exe  -> generado antes con: build.bat (o pyinstaller TodoListKawaii.spec)
;   2. icono_unicornio.ico      -> icono del instalador y del desinstalador (mismo que la app)
;      Si solo tienes .png, ejecuta crear_icono_ico.py para generar el .ico

#define MyAppName "Agenda Virtual"
#define MyAppVersion "1.0"
#define MyAppPublisher "Agenda Virtual"
#define MyAppExeName "TodoListKawaii.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\TodoListKawaii
DefaultGroupName=Agenda Virtual
AllowNoIcons=yes
; Carpeta donde está el .exe (relativa a la carpeta donde está este .iss)
SourceDir=dist
OutputDir=Output
OutputBaseFilename=TodoListKawaii_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
; Icono unicornio: instalador y desinstalador (icono_unicornio.ico en la misma carpeta que este .iss)
SetupIconFile=icono_unicornio.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
Source: "{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Sin [Run]: evitar que el instalador se quede enlazado al programa. El usuario abre la app desde el escritorio o menú Inicio.

[Code]
// La base de datos tareas.db se creará en {app} la primera vez que se ejecute la aplicación.
