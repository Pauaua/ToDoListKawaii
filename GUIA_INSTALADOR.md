# Guía para generar el instalador – Agenda Virtual

Esta guía te permite generar un **ejecutable** (.exe) y, opcionalmente, un **instalador** para que otra persona instale la app en su PC sin tener Python.

---

## Requisitos en tu PC (solo para generar)

- **Python 3** con el proyecto y dependencias instaladas (`pip install -r requirements.txt`).
- **PyInstaller** (se instala al ejecutar `build.bat`).
- Opcional: **Inno Setup** (solo si quieres crear el instalador .exe de instalación).

---

## Paso 1: Generar el ejecutable (.exe)

1. Abre **Símbolo del sistema** o **PowerShell** en la carpeta del proyecto:
   ```
   cd "d:\Users\Wasp\Documents\Programasound\TODOLISTKAWAII"
   ```

2. Ejecuta el script de construcción:
   - **Doble clic** en `build.bat`, o
   - En la terminal: `.\build.bat`

3. Al terminar, el ejecutable estará en:
   ```
   dist\TodoListKawaii.exe
   ```

4. **Probar:** ejecuta `dist\TodoListKawaii.exe`. Debe abrir la app con el mismo estilo, notificaciones y sin ventana de consola. La base de datos `tareas.db` se creará en la misma carpeta que el .exe.

**Para entregar a otra persona (sin instalador):**  
Puedes **enviar solo** `dist\TodoListKawaii.exe`. En el otro PC lo ejecutan con doble clic y la app funciona igual: no necesitan Python ni instalar nada. Las tareas se guardan en la misma carpeta que el .exe. Si Windows o el antivirus preguntan, que elijan “Ejecutar de todos modos” o añadan una excepción.

---

## Paso 2 (opcional): Crear el instalador con Inno Setup

Así generas un **instalador** que instala la app en “Programas”, crea un acceso directo y desinstalador.

### 2.1 Instalar Inno Setup

1. Descarga Inno Setup (gratis):  
   https://jrsoftware.org/isdl.php  
   Elige la versión estándar (ej. `innosetup-6.x.x.exe`).

2. Instálalo con las opciones por defecto.

### 2.2 Crear el instalador

1. Asegúrate de haber generado antes el .exe (Paso 1), para que exista `dist\TodoListKawaii.exe`.

2. En la carpeta del proyecto hay un script de Inno Setup:  
   `instalador_todolist.iss`

3. Abre **Inno Setup Compiler** y abre el archivo `instalador_todolist.iss`.

4. Menú **Build → Compile** (o F9).  
   Se generará el instalador en:
   ```
   Output\TodoListKawaii_Setup.exe
   ```

5. Entrega a la otra persona el archivo **`TodoListKawaii_Setup.exe`**. Al ejecutarlo podrán elegir carpeta de instalación, se creará el acceso directo y la desinstalación desde “Agregar o quitar programas”. Al finalizar, que abran la app desde el escritorio o el menú Inicio.

---

## Qué no se pierde

- **Funcionalidad:** tareas, recordatorios, importancia, notificaciones con “¡HEY HEY, TIENES UN PENDIENTE!” y brillos.
- **Estilo:** colores kawaii, icono de unicornio, cursor, ventana de notificación.
- **Responsividad:** tamaños y comportamiento de la ventana se mantienen.
- **Datos:** la base de datos `tareas.db` se guarda junto al ejecutable (o en la carpeta de instalación si usas el instalador), así que las tareas persisten.

---

## Solución de problemas

| Problema | Qué hacer |
|----------|-----------|
| “PyInstaller no encontrado” | Ejecuta `pip install pyinstaller` y vuelve a correr `build.bat`. |
| Falta un módulo al abrir el .exe | En `TodoListKawaii.spec`, en `hiddenimports`, añade el nombre del módulo que falta (ej. `'nombre_modulo'`), guarda y vuelve a ejecutar `build.bat`. |
| El icono no se ve en la ventana | Comprueba que `icono_unicornio.png` está en la misma carpeta que `main.py` al hacer el build. El .spec ya lo incluye en el .exe. |
| El instalador no se genera | Verifica que la ruta en `instalador_todolist.iss` apunte a tu carpeta `dist` y que `TodoListKawaii.exe` exista. |

Si quieres, en el siguiente paso puedes revisar o ajustar el contenido del archivo `instalador_todolist.iss` para personalizar nombre, carpeta por defecto o iconos.
