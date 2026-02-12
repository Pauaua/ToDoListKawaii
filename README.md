# 📝 TODO List Kawaii

Aplicación de escritorio para gestionar tareas con sistema de recordatorios mediante notificaciones del sistema operativo y WhatsApp.

## ✨ Características

- ➕ Agregar tareas con título y descripción
- ⏰ Programar recordatorios con fecha y hora específica
- 🔔 Notificaciones del sistema operativo
- 💬 Notificaciones por WhatsApp
- ✅ Marcar tareas como completadas
- 🗑️ Eliminar tareas
- 💾 Almacenamiento persistente en base de datos SQLite

## 📋 Requisitos

- Python 3.7 o superior
- Sistema operativo: Windows, Linux o macOS

## 🚀 Instalación

1. Clona o descarga este proyecto

2. Instala las dependencias necesarias:
```bash
pip install -r requirements.txt
```

## 💻 Uso

1. Ejecuta la aplicación:
```bash
python main.py
```

2. **Agregar una tarea:**
   - Ingresa el título de la tarea (obligatorio)
   - Opcionalmente agrega una descripción
   - Para establecer un recordatorio:
     - Marca el checkbox "Activar recordatorio"
     - Selecciona la fecha usando el calendario
     - Ingresa la hora en formato HH:MM (ejemplo: 14:30)
   - Selecciona el tipo de notificación deseada (sistema y/o WhatsApp)
   - Haz clic en "➕ Agregar Tarea"
   
   **Nota:** La aplicación usa la zona horaria de Chile (America/Santiago) para todos los recordatorios.

3. **Configurar WhatsApp:**
   - Haz clic en "💬 Configurar WhatsApp"
   - Necesitas una cuenta de Twilio (gratuita para pruebas)
   - Ingresa tus credenciales de Twilio:
     - **Account SID:** Tu Account SID de Twilio
     - **Auth Token:** Tu Auth Token de Twilio
     - **Número WhatsApp Business:** El número proporcionado por Twilio (formato: +56912345678)
     - **Número de destino:** Tu número donde recibirás las notificaciones (formato: +56912345678)
   - Haz clic en "💾 Guardar"
   - Consulta `GUIA_WHATSAPP.md` para más detalles

4. **Gestionar tareas:**
   - Selecciona una tarea de la lista
   - Usa "✓ Completar" para marcarla como completada
   - Usa "🗑️ Eliminar" para eliminar una tarea
   - Usa "🔄 Refrescar" para actualizar la lista

## 💬 Configuración de WhatsApp

La aplicación usa **Twilio** para enviar notificaciones por WhatsApp.

### Requisitos:
1. **Cuenta de Twilio**: Crea una cuenta gratuita en [Twilio](https://www.twilio.com)
2. **Credenciales**: Obtén tu Account SID y Auth Token desde el panel de Twilio
3. **Número de WhatsApp Business**: Twilio te proporciona un número de prueba

### Pasos rápidos:
1. Regístrate en [Twilio](https://www.twilio.com) (cuenta gratuita con créditos de prueba)
2. Obtén tus credenciales desde el Dashboard de Twilio
3. Configura WhatsApp en la aplicación usando el botón "💬 Configurar WhatsApp"
4. Consulta `GUIA_WHATSAPP.md` para instrucciones detalladas

### Formato de números:
- ✅ Correcto: `+56912345678` (con código de país y signo +)
- ❌ Incorrecto: `912345678` (sin código de país)

## 📁 Estructura del Proyecto

```
TODOLISTKAWAII/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias del proyecto
├── README.md           # Este archivo
├── tareas.db           # Base de datos SQLite (se crea automáticamente)
└── config_email.json   # Configuración de correo (se crea automáticamente)
```

## 🔧 Dependencias

- **plyer:** Para notificaciones del sistema operativo
- **schedule:** Para programar verificaciones de recordatorios
- **python-dateutil:** Para manejo de fechas
- **tkcalendar:** Para el selector de calendario
- **pytz:** Para manejo de zonas horarias (Chile)
- **twilio:** Para enviar notificaciones por WhatsApp
- **tkinter:** Interfaz gráfica (incluida con Python)
- **sqlite3:** Base de datos (incluida con Python)

## 📝 Notas

- Las notificaciones del sistema se verifican cada minuto
- Las tareas con recordatorio se notifican cuando la fecha/hora programada llega o pasa
- La configuración de WhatsApp se guarda en `config_whatsapp.json` (no compartas este archivo)
- Las tareas se almacenan en `tareas.db` (base de datos SQLite)

## 🎨 Personalización

La aplicación tiene un diseño "kawaii" con colores rosados. Puedes modificar los colores en el archivo `main.py` cambiando los valores de `bg` (background) y `fg` (foreground) en los widgets.

## ⚠️ Advertencias

- Asegúrate de mantener seguras tus credenciales de Twilio
- El archivo `config_whatsapp.json` contiene información sensible, no lo compartas
- Los números deben estar en formato internacional con código de país (ejemplo: +56912345678)
- Twilio tiene costos por mensaje en producción (consulta los precios en su sitio web)

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.
