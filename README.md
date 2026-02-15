# 📝 Agenda Virtual (Todo List Kawaii)

Aplicación de escritorio para gestionar tareas con recordatorios y notificaciones del sistema. Interfaz con varios estilos (Kawaii, Gatos, Azul), ventana responsiva y opción de ejecutable e instalador para Windows.

---

## ✨ Características

- **Tareas:** agregar, editar, completar y eliminar con título, descripción e importancia (Normal, Importante, Urgente).
- **Recordatorios:** fecha y hora con notificaciones del sistema (zona horaria Chile).
- **Tareas permanentes:** recordatorio diario desde una fecha de inicio.
- **Tres estilos visuales:** Kawaii (rosa), Gatos (verde, temática gato), Azul (azul).
- **Tamaño de ventana:** Pantalla completa, Mediano o Pequeño (layout adaptado).
- **Preferencias guardadas:** estilo y tamaño se pueden mantener al iniciar.
- **Interfaz responsiva:** se adapta al redimensionar; en tamaño Pequeño los controles se reorganizan (botones en 2 filas, checkbox “TP” para tarea permanente).
- **Bandeja del sistema:** opción de minimizar a la bandeja en lugar de cerrar.
- **Base de datos SQLite:** persistencia local de tareas y configuración de tema/tamaño.

---

## 📋 Requisitos

- **Python 3.8+**
- Windows (recomendado para .exe e instalador); también puede ejecutarse en Linux/macOS con Python.

---

## 🚀 Instalación y uso desde código

1. Clona o descarga el repositorio.

2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

---

## 📦 Generar ejecutable e instalador (Windows)

### Ejecutable (.exe)

1. Cierra la aplicación si está abierta (para evitar “Acceso denegado”).
2. Ejecuta **`build.bat`** desde la carpeta del proyecto.
3. El ejecutable se genera en **`dist\TodoListKawaii.exe`**.  
   Puedes copiar solo ese .exe a otra PC; no requiere Python.

### Instalador (Inno Setup)

1. Genera antes el .exe con `build.bat`.
2. Ten **`icono_unicornio.ico`** en la carpeta del proyecto (si solo tienes .png, usa **`crear_icono_ico.py`** para generar el .ico).
3. Abre **Inno Setup Compiler** → **File → Open** → **`instalador_todolist.iss`**.
4. **Build → Compile** (F9).  
   El instalador se genera en **`Output\TodoListKawaii_Setup.exe`**.

Detalles y solución de problemas: **`GUIA_INSTALADOR.md`**.

---

## 💻 Uso básico

- **Nueva tarea:** rellena título (obligatorio), opcionalmente descripción, activa recordatorio si quieres (fecha, hora, y opción “Tarea permanente” para recordatorio diario). Elige importancia y pulsa **Agregar Tarea**.
- **Estilo:** selector para Kawaii, Gatos o Azul. Opción **Mantener al iniciar** para recordar el estilo.
- **Tamaño:** Pantalla completa, Mediano o Pequeño; en Pequeño la interfaz se compacta (incluido el checkbox “TP” para tarea permanente).
- **Lista de tareas:** selecciona una tarea y usa **Editar**, **Completar**, **Eliminar** o **Refrescar**.

Las notificaciones se envían automáticamente al sistema cuando llega la fecha/hora del recordatorio (o cada día a esa hora si es tarea permanente).

---

## 📁 Estructura del proyecto

```
TODOLISTKAWAII/
├── main.py                    # Aplicación principal
├── requirements.txt           # Dependencias Python
├── README.md                  # Este archivo
├── build.bat                  # Genera dist\TodoListKawaii.exe
├── TodoListKawaii.spec        # Configuración PyInstaller
├── instalador_todolist.iss    # Script Inno Setup para el instalador
├── crear_icono_ico.py         # Genera icono .ico desde .png
├── GUIA_INSTALADOR.md         # Guía ejecutable e instalador
├── CAMBIAR_ICONO_MANUAL.md    # Cómo cambiar el icono del .exe con Resource Hacker
├── GUIA_SQLITE.md             # Documentación base de datos
├── icono_unicornio.png        # Icono (y .ico para el instalador)
├── tareas.db                  # Base de datos (se crea al usar la app)
└── config_tema.json          # Tema y tamaño guardados (se crea al usar; en .gitignore)
```

---

## 🔧 Dependencias

- **tkinter** – Interfaz gráfica (incluido con Python).
- **tkcalendar** – Selector de fecha.
- **pytz** – Zona horaria (Chile).
- **schedule** – Verificación de recordatorios.
- **python-dateutil** – Manejo de fechas.
- **plyer** – Notificaciones del sistema.
- **Pillow** – Imágenes (icono, bandeja).
- **pystray** – Icono en la bandeja del sistema.

---

## 📝 Notas

- Los recordatorios usan la zona horaria **America/Santiago** (Chile).
- La configuración de tema y tamaño se guarda en **`config_tema.json`** (no se sube al repo).
- La base de datos **`tareas.db`** se crea en la misma carpeta que el script o el .exe.

---

## 📄 Licencia

Proyecto de código abierto para uso personal y educativo.
