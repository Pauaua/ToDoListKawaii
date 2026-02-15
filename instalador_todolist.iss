; Script Inno Setup para Agenda Virtual
; Compilar desde Inno Setup Compiler (Build -> Compile). Requiere haber generado antes dist\TodoListKawaii.exe

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
; Ruta donde está el .exe generado por PyInstaller (relativa a esta carpeta .iss)
SourceDir=dist
OutputDir=Output
OutputBaseFilename=TodoListKawaii_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
; Icono del instalador: si usas SetupIconFile y falla al compilar, déjalo comentado.
; El .exe instalado (TodoListKawaii.exe) ya lleva el icono unicornio por PyInstaller.
; SetupIconFile=icono_unicornio.ico
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
