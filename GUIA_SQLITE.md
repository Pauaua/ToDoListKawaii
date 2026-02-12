# 📚 Guía: Cómo funciona SQLite en este proyecto

## ¿Qué es SQLite?

SQLite es una base de datos ligera que almacena datos en un archivo local (`tareas.db`). Es perfecta para aplicaciones de escritorio porque no requiere un servidor separado.

## Estructura de la Base de Datos

### Tabla: `tareas`

La tabla `tareas` tiene las siguientes columnas:

```sql
CREATE TABLE tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único de cada tarea
    titulo TEXT NOT NULL,                   -- Título de la tarea (obligatorio)
    descripcion TEXT,                       -- Descripción (opcional)
    fecha_creacion TEXT NOT NULL,           -- Fecha de creación
    fecha_recordatorio TEXT,                -- Fecha/hora del recordatorio
    completada INTEGER DEFAULT 0,           -- 0 = pendiente, 1 = completada
    notificacion_sistema INTEGER DEFAULT 1, -- 0 = no, 1 = sí
    notificacion_correo INTEGER DEFAULT 0   -- 0 = no, 1 = sí
)
```

## Cómo funciona en el código

### 1. Conexión a la Base de Datos

```python
conn = sqlite3.connect(self.db_name)  # Conecta al archivo tareas.db
cursor = conn.cursor()                 # Crea un cursor para ejecutar comandos
```

### 2. Operaciones Básicas

#### **INSERTAR (Agregar)**
```python
cursor.execute('''
    INSERT INTO tareas (titulo, descripcion, fecha_creacion, ...)
    VALUES (?, ?, ?, ...)
''', (titulo, descripcion, fecha_creacion, ...))
conn.commit()  # Guarda los cambios
```

#### **SELECT (Leer/Obtener)**
```python
cursor.execute('''
    SELECT id, titulo, descripcion, ...
    FROM tareas
    WHERE completada = ?
''', (0,))  # 0 = pendientes
tareas = cursor.fetchall()  # Obtiene todos los resultados
```

#### **UPDATE (Actualizar/Editar)**
```python
cursor.execute('''
    UPDATE tareas 
    SET titulo = ?, descripcion = ?
    WHERE id = ?
''', (nuevo_titulo, nueva_descripcion, tarea_id))
conn.commit()  # Guarda los cambios
```

#### **DELETE (Eliminar)**
```python
cursor.execute('DELETE FROM tareas WHERE id = ?', (tarea_id,))
conn.commit()  # Guarda los cambios
```

## Métodos Disponibles en la Clase Database

### `agregar_tarea(titulo, descripcion, fecha_recordatorio, ...)`
Agrega una nueva tarea a la base de datos.

**Ejemplo:**
```python
db.agregar_tarea(
    titulo="Comprar leche",
    descripcion="Ir al supermercado",
    fecha_recordatorio="2026-02-12 10:00",
    notif_sistema=True,
    notif_correo=False
)
```

### `obtener_tareas(completadas=False)`
Obtiene todas las tareas pendientes o completadas.

**Ejemplo:**
```python
tareas_pendientes = db.obtener_tareas(completadas=False)
tareas_completadas = db.obtener_tareas(completadas=True)
```

### `obtener_tarea_por_id(tarea_id)`
Obtiene una tarea específica por su ID.

**Ejemplo:**
```python
tarea = db.obtener_tarea_por_id(1)
# Retorna: (id, titulo, descripcion, fecha_creacion, fecha_recordatorio, 
#           completada, notificacion_sistema, notificacion_correo)
```

### `actualizar_tarea(tarea_id, titulo=None, descripcion=None, ...)`
Actualiza una tarea existente. Solo actualiza los campos que proporciones.

**Ejemplos:**

```python
# Actualizar solo el título
db.actualizar_tarea(1, titulo="Nuevo título")

# Actualizar título y descripción
db.actualizar_tarea(
    1, 
    titulo="Nuevo título",
    descripcion="Nueva descripción"
)

# Actualizar todo
db.actualizar_tarea(
    1,
    titulo="Título actualizado",
    descripcion="Descripción actualizada",
    fecha_recordatorio="2026-02-15 14:30",
    notif_sistema=True,
    notif_correo=True
)

# Eliminar recordatorio (establecer a None)
db.actualizar_tarea(1, fecha_recordatorio=None)
```

### `marcar_completada(tarea_id)`
Marca una tarea como completada.

**Ejemplo:**
```python
db.marcar_completada(1)
```

### `eliminar_tarea(tarea_id)`
Elimina una tarea de la base de datos.

**Ejemplo:**
```python
db.eliminar_tarea(1)
```

## Cómo Editar una Tarea desde la Interfaz

1. **Selecciona una tarea** de la lista haciendo clic en ella
2. **Haz clic en el botón "✏️ Editar"**
3. **Modifica los campos** que desees:
   - Título
   - Descripción
   - Fecha y hora del recordatorio
   - Tipo de notificaciones
4. **Haz clic en "💾 Guardar Cambios"**

## Ejemplos de Uso Programático

### Ejemplo 1: Cambiar el título de una tarea
```python
from main import Database

db = Database()
# Cambiar el título de la tarea con ID 1
db.actualizar_tarea(1, titulo="Mi nuevo título")
```

### Ejemplo 2: Obtener y modificar una tarea
```python
from main import Database

db = Database()
# Obtener la tarea con ID 1
tarea = db.obtener_tarea_por_id(1)
id_tarea, titulo, descripcion, _, _, _, _, _ = tarea

# Modificar el título agregando un prefijo
nuevo_titulo = f"[URGENTE] {titulo}"
db.actualizar_tarea(id_tarea, titulo=nuevo_titulo)
```

### Ejemplo 3: Actualizar múltiples tareas
```python
from main import Database

db = Database()
# Obtener todas las tareas pendientes
tareas = db.obtener_tareas(completadas=False)

# Actualizar todas para agregar notificación por correo
for tarea in tareas:
    tarea_id = tarea[0]
    db.actualizar_tarea(tarea_id, notif_correo=True)
```

## Ver el Archivo de Base de Datos

El archivo `tareas.db` contiene todos los datos. Puedes verlo usando herramientas como:

- **DB Browser for SQLite** (gratuito): https://sqlitebrowser.org/
- **SQLite Command Line**: `sqlite3 tareas.db`
- **Extensiones de VS Code**: Busca "SQLite" en el marketplace

### Ver datos desde Python:
```python
import sqlite3

conn = sqlite3.connect('tareas.db')
cursor = conn.cursor()

# Ver todas las tareas
cursor.execute('SELECT * FROM tareas')
for row in cursor.fetchall():
    print(row)

conn.close()
```

## Notas Importantes

1. **Siempre cierra la conexión**: Después de cada operación, se cierra la conexión con `conn.close()`
2. **Usa commit()**: Después de INSERT, UPDATE o DELETE, siempre usa `conn.commit()` para guardar los cambios
3. **Usa parámetros**: Siempre usa `?` en lugar de concatenar strings para evitar inyección SQL
4. **El ID es único**: Cada tarea tiene un ID único que se genera automáticamente

## Preguntas Frecuentes

**P: ¿Puedo editar directamente el archivo tareas.db?**
R: No es recomendable. Es mejor usar los métodos de la clase Database para mantener la integridad de los datos.

**P: ¿Qué pasa si elimino tareas.db?**
R: Se creará automáticamente una nueva base de datos vacía cuando ejecutes la aplicación.

**P: ¿Puedo hacer backup de mis tareas?**
R: Sí, simplemente copia el archivo `tareas.db` a otra ubicación.

**P: ¿Cómo cambio el formato de fecha almacenado?**
R: Las fechas se almacenan como texto en formato `YYYY-MM-DD HH:MM:SS`. Si necesitas cambiar el formato, modifica las funciones que usan `strftime()`.
