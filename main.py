"""
Aplicación TODO List con recordatorios
Permite crear tareas y recibir notificaciones del sistema con efectos visuales
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import threading
import schedule
import time
import json
import os
import sys
from tkcalendar import DateEntry
import pytz
import random

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pystray
    from pystray import MenuItem as item
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False


def get_ruta_base():
    """Ruta donde está el ejecutable (o el script). Para guardar tareas.db."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_ruta_recurso(nombre_archivo):
    """Ruta a un archivo de recursos (icono, etc.). Válido con PyInstaller --onefile."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nombre_archivo)
    return os.path.join(get_ruta_base(), nombre_archivo)


class Database:
    """Maneja la base de datos SQLite para almacenar tareas"""
    
    def __init__(self, db_name="tareas.db"):
        self.db_name = db_name
        # Zona horaria de Chile
        self.tz_chile = pytz.timezone('America/Santiago')
        self.init_db()
    
    def init_db(self):
        """Inicializa la base de datos y crea la tabla si no existe"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                fecha_creacion TEXT NOT NULL,
                fecha_recordatorio TEXT,
                completada INTEGER DEFAULT 0,
                notificacion_sistema INTEGER DEFAULT 1,
                notificacion_correo INTEGER DEFAULT 0,
                importancia TEXT DEFAULT 'Normal'
            )
        ''')
        
        # Agregar columna importancia si no existe (para bases de datos existentes)
        try:
            cursor.execute('ALTER TABLE tareas ADD COLUMN importancia TEXT DEFAULT "Normal"')
        except sqlite3.OperationalError:
            pass  # La columna ya existe
        
        # Agregar columna es_permanente si no existe (para tareas recurrentes diarias)
        try:
            cursor.execute('ALTER TABLE tareas ADD COLUMN es_permanente INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # La columna ya existe
        
        conn.commit()
        conn.close()
    
    def agregar_tarea(self, titulo, descripcion, fecha_recordatorio=None, 
                     notif_sistema=True, notif_correo=False, importancia='Normal', es_permanente=False):
        """Agrega una nueva tarea a la base de datos"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # Usar hora de Chile
        tz_chile = pytz.timezone('America/Santiago')
        fecha_creacion = datetime.now(tz_chile).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO tareas (titulo, descripcion, fecha_creacion, 
                              fecha_recordatorio, notificacion_sistema, 
                              notificacion_correo, importancia, es_permanente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (titulo, descripcion, fecha_creacion, fecha_recordatorio, 
              int(notif_sistema), int(notif_correo), importancia, int(es_permanente)))
        conn.commit()
        tarea_id = cursor.lastrowid
        conn.close()
        return tarea_id
    
    def obtener_tareas(self, completadas=False):
        """Obtiene todas las tareas (completadas o pendientes)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, titulo, descripcion, fecha_creacion, fecha_recordatorio,
                   completada, notificacion_sistema, notificacion_correo, importancia, es_permanente
            FROM tareas
            WHERE completada = ?
            ORDER BY 
                CASE importancia
                    WHEN 'Urgente' THEN 1
                    WHEN 'Importante' THEN 2
                    WHEN 'Normal' THEN 3
                    ELSE 4
                END,
                fecha_recordatorio ASC, fecha_creacion DESC
        ''', (int(completadas),))
        tareas = cursor.fetchall()
        conn.close()
        return tareas
    
    def marcar_completada(self, tarea_id):
        """Marca una tarea como completada"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tareas SET completada = 1 WHERE id = ?
        ''', (tarea_id,))
        conn.commit()
        conn.close()
    
    def eliminar_tarea(self, tarea_id):
        """Elimina una tarea de la base de datos"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tareas WHERE id = ?', (tarea_id,))
        conn.commit()
        conn.close()
    
    def obtener_tarea_por_id(self, tarea_id):
        """Obtiene una tarea específica por su ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, titulo, descripcion, fecha_creacion, fecha_recordatorio,
                   completada, notificacion_sistema, notificacion_correo, importancia, es_permanente
            FROM tareas
            WHERE id = ?
        ''', (tarea_id,))
        tarea = cursor.fetchone()
        conn.close()
        return tarea
    
    def actualizar_tarea(self, tarea_id, titulo=None, descripcion=None, 
                        fecha_recordatorio=None, notif_sistema=None, 
                        notif_correo=None, importancia=None, es_permanente=None):
        """
        Actualiza una tarea existente en la base de datos.
        Solo actualiza los campos que se proporcionen (no None).
        
        Ejemplo de uso:
        - Actualizar solo el título:
          db.actualizar_tarea(1, titulo="Nuevo título")
        
        - Actualizar título y descripción:
          db.actualizar_tarea(1, titulo="Nuevo título", descripcion="Nueva descripción")
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Construir la consulta UPDATE dinámicamente según los campos proporcionados
        campos_actualizar = []
        valores = []
        
        if titulo is not None:
            campos_actualizar.append("titulo = ?")
            valores.append(titulo)
        
        if descripcion is not None:
            campos_actualizar.append("descripcion = ?")
            valores.append(descripcion)
        
        if fecha_recordatorio is not None:
            campos_actualizar.append("fecha_recordatorio = ?")
            valores.append(fecha_recordatorio)
        
        if notif_sistema is not None:
            campos_actualizar.append("notificacion_sistema = ?")
            valores.append(int(notif_sistema))
        
        if notif_correo is not None:
            campos_actualizar.append("notificacion_correo = ?")
            valores.append(int(notif_correo))
        
        if importancia is not None:
            campos_actualizar.append("importancia = ?")
            valores.append(importancia)
        
        if es_permanente is not None:
            campos_actualizar.append("es_permanente = ?")
            valores.append(int(es_permanente))
        
        # Si hay campos para actualizar
        if campos_actualizar:
            valores.append(tarea_id)  # Agregar el ID al final para el WHERE
            consulta = f"UPDATE tareas SET {', '.join(campos_actualizar)} WHERE id = ?"
            cursor.execute(consulta, valores)
            conn.commit()
        
        conn.close()
    
    def obtener_tareas_pendientes_recordatorio(self):
        """Obtiene tareas pendientes que tienen recordatorio programado.
        Para tareas permanentes, verifica si la hora coincide (ignorando la fecha).
        Para tareas normales, verifica fecha y hora específica."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # Usar hora de Chile
        tz_chile = pytz.timezone('America/Santiago')
        ahora = datetime.now(tz_chile)
        ahora_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
        hora_actual = ahora.strftime("%H:%M")
        
        # Obtener todas las tareas pendientes con recordatorio
        cursor.execute('''
            SELECT id, titulo, descripcion, fecha_recordatorio,
                   notificacion_sistema, notificacion_correo, importancia, es_permanente
            FROM tareas
            WHERE completada = 0 AND fecha_recordatorio IS NOT NULL
        ''')
        todas_tareas = cursor.fetchall()
        conn.close()
        
        # Filtrar según tipo de tarea
        tareas_a_notificar = []
        for tarea in todas_tareas:
            tarea_id, titulo, descripcion, fecha_recordatorio, notif_sistema, notif_correo, importancia, es_permanente = tarea
            
            if es_permanente:
                # Tarea permanente: verificar que la fecha de inicio ya pasó Y que la hora coincide
                try:
                    fecha_obj = datetime.strptime(fecha_recordatorio, "%Y-%m-%d %H:%M:%S")
                    fecha_inicio = fecha_obj.date()  # Solo la fecha (sin hora)
                    fecha_actual = ahora.date()
                    hora_recordatorio = fecha_obj.strftime("%H:%M")
                    
                    # Verificar que la fecha de inicio ya pasó (o es hoy) Y que la hora coincide
                    if fecha_inicio <= fecha_actual and hora_recordatorio == hora_actual:
                        tareas_a_notificar.append(tarea)
                except:
                    # Si el formato no es el esperado, intentar solo hora (compatibilidad)
                    try:
                        if fecha_recordatorio.startswith(hora_actual):
                            tareas_a_notificar.append(tarea)
                    except:
                        pass
            else:
                # Tarea normal: verificar fecha y hora específica
                if fecha_recordatorio <= ahora_str:
                    tareas_a_notificar.append(tarea)
        
        return tareas_a_notificar


class NotificacionKawaii:
    """Crea notificaciones personalizadas con efectos de brillo"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.ventanas_notificacion = []
    
    def crear_notificacion(self, titulo, mensaje):
        """Crea una ventana de notificación con efectos de brillo"""
        ventana = tk.Toplevel(self.parent if self.parent else None)
        ventana.title("✨ Recordatorio")
        ventana.geometry("420x260")
        ventana.configure(bg="#FFE4E1")
        ventana.overrideredirect(True)  # Sin bordes
        
        # Asegurar que aparezca siempre en primer plano, incluso si la ventana principal está oculta
        ventana.attributes("-topmost", True)
        ventana.lift()
        ventana.focus_force()
        
        # Posicionar en la esquina superior derecha
        ventana.update_idletasks()
        width = 420
        height = 260
        x = ventana.winfo_screenwidth() - width - 20
        y = 20
        ventana.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal con gradiente y borde decorativo
        frame_principal = tk.Frame(
            ventana, 
            bg="#FFB6C1", 
            padx=20, 
            pady=15,
            relief=tk.RAISED,
            bd=5
        )
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título grande arriba: ¡HEY HEY, TIENES UN PENDIENTE!
        hey_label = tk.Label(
            frame_principal,
            text="¡HEY HEY, TIENES UN PENDIENTE!",
            font=("Arial", 16, "bold"),
            bg="#FFB6C1",
            fg="#FF1493",
            wraplength=380
        )
        hey_label.pack(pady=(0, 10))
        
        # Título de la tarea
        titulo_label = tk.Label(
            frame_principal,
            text=titulo,
            font=("Arial", 14, "bold"),
            bg="#FFB6C1",
            fg="#8B008B",
            wraplength=380
        )
        titulo_label.pack(pady=(0, 8))
        
        # Mensaje
        mensaje_label = tk.Label(
            frame_principal,
            text=mensaje,
            font=("Arial", 11),
            bg="#FFB6C1",
            fg="#8B008B",
            wraplength=350,
            justify=tk.LEFT
        )
        mensaje_label.pack(pady=(0, 12))
        
        # Botón cerrar
        btn_cerrar = tk.Button(
            frame_principal,
            text="💖 Cerrar",
            command=ventana.destroy,
            bg="#FF69B4",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        )
        btn_cerrar.pack()
        
        # Efectos de brillo animados
        self.animar_brillos(ventana, frame_principal)
        
        # Cerrar automáticamente después de 10 segundos
        ventana.after(10000, ventana.destroy)
        
        # Guardar referencia
        self.ventanas_notificacion.append(ventana)
        
        # Hacer que la ventana aparezca con animación
        self.animar_entrada(ventana)
        
        return ventana
    
    def animar_brillos(self, ventana, frame):
        """Crea partículas de brillo animadas"""
        canvas = tk.Canvas(frame, width=420, height=260, bg="#FFB6C1", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        # Bajar el widget canvas al fondo (Canvas.lower() es para ítems, no para el widget)
        frame.tk.call('lower', canvas._w)
        
        particulas = []
        
        def crear_particula():
            x = random.randint(0, 420)
            y = random.randint(0, 260)
            size = random.randint(3, 8)
            particula = canvas.create_oval(
                x, y, x + size, y + size,
                fill="#FFD700",
                outline="#FFA500",
                width=1
            )
            particulas.append({
                'id': particula,
                'x': x,
                'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'life': 100,
                'size': size
            })
        
        def animar_particulas():
            for p in particulas[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['life'] -= 1
                
                # Actualizar posición
                canvas.coords(p['id'], 
                    p['x'], p['y'], 
                    p['x'] + p['size'], p['y'] + p['size']
                )
                
                # Cambiar opacidad según vida
                alpha = p['life'] / 100
                if alpha < 0:
                    canvas.delete(p['id'])
                    particulas.remove(p)
            
            # Crear nuevas partículas ocasionalmente
            if random.random() < 0.3 and len(particulas) < 20:
                crear_particula()
            
            if ventana.winfo_exists():
                ventana.after(50, animar_particulas)
        
        # Crear partículas iniciales con más frecuencia
        for _ in range(15):
            crear_particula()
        
        animar_particulas()
    
    def animar_entrada(self, ventana):
        """Anima la entrada de la notificación"""
        ventana.attributes('-alpha', 0.0)
        
        def fade_in(alpha=0.0):
            alpha += 0.1
            if alpha <= 1.0:
                ventana.attributes('-alpha', alpha)
                ventana.after(30, lambda: fade_in(alpha))
        
        fade_in()


class Notificador:
    """Maneja las notificaciones del sistema"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.notificador_kawaii = NotificacionKawaii(parent)
    
    def notificar_sistema(self, titulo, mensaje):
        """Envía una notificación personalizada con brillos"""
        try:
            self.notificador_kawaii.crear_notificacion(titulo, mensaje)
        except Exception as e:
            print(f"Error al enviar notificación: {e}")


class TodoApp:
    """Aplicación principal de TODO List"""
    
    def __init__(self, root, db_path=None):
        self.root = root
        self.root.title("Agenda Virtual")
        # Tamaño inicial más grande para que se vea todo el contenido (incluyendo checkbox permanente)
        self.root.geometry("950x900")
        # Tamaño mínimo para evitar que se haga muy pequeña
        self.root.minsize(850, 750)
        self.root.configure(bg="#FFE4E1")
        
        self.db = Database(db_name=db_path or "tareas.db")
        self.notificador = Notificador(self.root)
        
        # Cursor normal; "heart" suele verse en tono rosado/rojo en muchos sistemas
        try:
            self.root.config(cursor="heart")
        except tk.TclError:
            self.root.config(cursor="arrow")
        
        # Icono en la bandeja del sistema (system tray)
        self.tray_icon = None
        self.tray_thread = None
        if HAS_PYSTRAY:
            self.configurar_bandeja_sistema()
        
        # Configurar cierre para minimizar a la bandeja en lugar de cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar hilo para verificar recordatorios
        self.iniciar_verificador_recordatorios()
        
        self.crear_interfaz()
        self.actualizar_lista_tareas()
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica de la aplicación"""
        # Frame principal con grid para mejor control del layout
        main_frame = tk.Frame(self.root, bg="#FFE4E1", padx=15, pady=12)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo_label = tk.Label(
            main_frame,
            text="📝 AGENDA VIRTUAL",
            font=("Arial", 22, "bold"),
            bg="#FFE4E1",
            fg="#FF69B4"
        )
        titulo_label.pack(pady=(0, 10))
        
        # Frame para agregar tareas
        frame_agregar = tk.LabelFrame(
            main_frame,
            text="➕ Nueva Tarea",
            font=("Arial", 11, "bold"),
            bg="#FFE4E1",
            fg="#FF69B4",
            padx=8,
            pady=6
        )
        frame_agregar.pack(fill=tk.X, pady=(0, 6))
        
        # Título de la tarea
        tk.Label(
            frame_agregar,
            text="Título:",
            bg="#FFE4E1",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        self.entry_titulo = tk.Entry(frame_agregar, font=("Arial", 11), width=50)
        self.entry_titulo.pack(fill=tk.X, pady=(4, 6))
        
        # Descripción (altura reducida)
        tk.Label(
            frame_agregar,
            text="Descripción:",
            bg="#FFE4E1",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        self.text_descripcion = tk.Text(frame_agregar, font=("Arial", 10), height=2, width=50)
        self.text_descripcion.pack(fill=tk.X, pady=(4, 6))
        
        # Frame para recordatorio (reorganizado en dos filas para mejor visibilidad)
        frame_recordatorio = tk.Frame(frame_agregar, bg="#FFE4E1")
        frame_recordatorio.pack(fill=tk.X, pady=(0, 8))
        
        # Primera fila: Checkbox y controles básicos
        frame_fila1 = tk.Frame(frame_recordatorio, bg="#FFE4E1")
        frame_fila1.pack(fill=tk.X, pady=(0, 5))
        
        # Variable para controlar si se usa recordatorio
        self.var_usar_recordatorio = tk.BooleanVar(value=False)
        
        def toggle_recordatorio():
            """Habilita/deshabilita calendario y hora según el checkbox"""
            estado = self.var_usar_recordatorio.get()
            if estado:
                self.calendario.config(state='normal')
                self.entry_hora.config(state='normal')
            else:
                self.calendario.config(state='disabled')
                self.entry_hora.config(state='disabled')
                self.var_es_permanente.set(False)  # Desactivar permanente si se desactiva recordatorio
        
        self.var_usar_recordatorio.trace('w', lambda *args: toggle_recordatorio())
        
        checkbox_recordatorio = tk.Checkbutton(
            frame_fila1,
            text="Activar recordatorio",
            variable=self.var_usar_recordatorio,
            bg="#FFE4E1",
            font=("Arial", 10, "bold"),
            command=toggle_recordatorio
        )
        checkbox_recordatorio.pack(side=tk.LEFT, padx=(0, 15))
        
        # Checkbox para tarea permanente (solo si tiene recordatorio)
        self.var_es_permanente = tk.BooleanVar(value=False)
        checkbox_permanente = tk.Checkbutton(
            frame_fila1,
            text="🔄 Tarea permanente (diaria desde esta fecha)",
            variable=self.var_es_permanente,
            bg="#FFE4E1",
            font=("Arial", 10),
            fg="#8B008B"
        )
        checkbox_permanente.pack(side=tk.LEFT)
        
        # Segunda fila: Fecha y hora (solo visible cuando recordatorio está activado)
        frame_fila2 = tk.Frame(frame_recordatorio, bg="#FFE4E1")
        frame_fila2.pack(fill=tk.X)
        
        tk.Label(
            frame_fila2,
            text="Fecha:",
            bg="#FFE4E1",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Calendario para seleccionar fecha
        self.calendario = DateEntry(
            frame_fila2,
            width=12,
            background='#FF69B4',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Arial", 10)
        )
        self.calendario.pack(side=tk.LEFT, padx=(0, 15))
        
        # Hora del recordatorio
        tk.Label(
            frame_fila2,
            text="Hora (HH:MM):",
            bg="#FFE4E1",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))
        self.entry_hora = tk.Entry(frame_fila2, font=("Arial", 10), width=8)
        self.entry_hora.pack(side=tk.LEFT)
        self.entry_hora.insert(0, "09:00")  # Hora por defecto
        
        # Inicializar estado deshabilitado
        self.calendario.config(state='disabled')
        self.entry_hora.config(state='disabled')
        
        # Frame para importancia
        frame_importancia = tk.Frame(frame_agregar, bg="#FFE4E1")
        frame_importancia.pack(fill=tk.X, pady=(0, 6))
        
        tk.Label(
            frame_importancia,
            text="Importancia:",
            bg="#FFE4E1",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.var_importancia = tk.StringVar(value="Normal")
        opciones_importancia = ["Normal", "Importante", "Urgente"]
        
        for opcion in opciones_importancia:
            color = "#87CEEB" if opcion == "Normal" else "#FFD700" if opcion == "Importante" else "#FF6347"
            tk.Radiobutton(
                frame_importancia,
                text=opcion,
                variable=self.var_importancia,
                value=opcion,
                bg="#FFE4E1",
                font=("Arial", 10),
                selectcolor=color,
                activebackground="#FFE4E1"
            ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Checkbox para notificaciones (siempre activo)
        frame_notificaciones = tk.Frame(frame_agregar, bg="#FFE4E1")
        frame_notificaciones.pack(fill=tk.X, pady=(0, 6))
        
        self.var_notif_sistema = tk.BooleanVar(value=True)
        
        tk.Label(
            frame_notificaciones,
            text="✨ Las notificaciones se enviarán automáticamente a tu sistema. ✨",
            bg="#FFE4E1",
            font=("Arial", 10, "bold"),
            fg="#FF69B4"
        ).pack(side=tk.LEFT)
        
        # Botón agregar
        btn_agregar = tk.Button(
            frame_agregar,
            text="➕ Agregar Tarea",
            command=self.agregar_tarea,
            bg="#FF69B4",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5,
            cursor="hand2"
        )
        btn_agregar.pack(pady=(5, 0))
        
        # Frame para lista de tareas
        frame_lista = tk.LabelFrame(
            main_frame,
            text="📋 Tareas Pendientes",
            font=("Arial", 11, "bold"),
            bg="#FFE4E1",
            fg="#FF69B4",
            padx=8,
            pady=6
        )
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=(6, 6))
        
        # Treeview para mostrar tareas
        columns = ("ID", "Título", "Descripción", "Importancia", "Recordatorio")
        # Altura ajustada para que quepa todo
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", height=14)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Importancia", text="Importancia")
        self.tree.heading("Recordatorio", text="Recordatorio")
        
        self.tree.column("ID", width=40)
        self.tree.column("Título", width=180)
        self.tree.column("Descripción", width=250)
        self.tree.column("Importancia", width=100)
        self.tree.column("Recordatorio", width=150)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botones de acción (fuera del frame_lista, debajo)
        frame_acciones = tk.Frame(main_frame, bg="#FFE4E1")
        frame_acciones.pack(fill=tk.X, pady=(0, 0))
        
        btn_editar = tk.Button(
            frame_acciones,
            text="✏️ Editar",
            command=self.editar_tarea,
            bg="#FFD700",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        )
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        btn_completar = tk.Button(
            frame_acciones,
            text="✓ Completar",
            command=self.marcar_completada,
            bg="#90EE90",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        )
        btn_completar.pack(side=tk.LEFT, padx=5)
        
        btn_eliminar = tk.Button(
            frame_acciones,
            text="🗑️ Eliminar",
            command=self.eliminar_tarea,
            bg="#FF6347",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        )
        btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        
        btn_refrescar = tk.Button(
            frame_acciones,
            text="🔄 Refrescar",
            command=self.actualizar_lista_tareas,
            bg="#DDA0DD",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        )
        btn_refrescar.pack(side=tk.LEFT, padx=5)
    
    def agregar_tarea(self):
        """Agrega una nueva tarea"""
        titulo = self.entry_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Advertencia", "Por favor ingresa un título para la tarea")
            return
        
        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        
        # Obtener si es permanente (antes de procesar recordatorio)
        es_permanente = self.var_es_permanente.get() if self.var_usar_recordatorio.get() else False
        
        # Obtener fecha y hora del recordatorio
        fecha_recordatorio = None
        if self.var_usar_recordatorio.get():
            fecha_seleccionada = self.calendario.get_date()
            hora_str = self.entry_hora.get().strip()
            
            if not hora_str:
                messagebox.showwarning("Advertencia", "Por favor ingresa una hora para el recordatorio")
                return
            
            try:
                # Validar formato de hora
                hora_parts = hora_str.split(":")
                if len(hora_parts) != 2:
                    raise ValueError
                hora = int(hora_parts[0])
                minuto = int(hora_parts[1])
                if not (0 <= hora <= 23 and 0 <= minuto <= 59):
                    raise ValueError
                
                # Combinar fecha y hora
                # Para tareas permanentes, la fecha es la fecha de inicio (desde cuándo empezar a notificar diariamente)
                # Para tareas normales, es la fecha específica del recordatorio
                fecha_recordatorio = fecha_seleccionada.strftime("%Y-%m-%d") + f" {hora:02d}:{minuto:02d}:00"
                
                # Validar que la fecha/hora no sea en el pasado (solo para tareas no permanentes)
                # Para permanentes, permitimos fecha pasada porque empezará desde hoy en adelante
                if not es_permanente:
                    tz_chile = pytz.timezone('America/Santiago')
                    ahora_chile = datetime.now(tz_chile)
                    fecha_recordatorio_dt = datetime.strptime(fecha_recordatorio, "%Y-%m-%d %H:%M:%S")
                    fecha_recordatorio_dt = tz_chile.localize(fecha_recordatorio_dt)
                    
                    if fecha_recordatorio_dt < ahora_chile:
                        respuesta = messagebox.askyesno(
                            "Advertencia",
                            "La fecha y hora del recordatorio es en el pasado. ¿Deseas continuar de todas formas?"
                        )
                        if not respuesta:
                            return
            except ValueError:
                messagebox.showerror("Error", "Formato de hora incorrecto. Usa: HH:MM (ejemplo: 14:30)")
                return
        
        notif_sistema = self.var_notif_sistema.get()
        importancia = self.var_importancia.get()
        
        # Si es permanente pero no tiene recordatorio, mostrar advertencia
        if es_permanente and not fecha_recordatorio:
            messagebox.showwarning("Advertencia", "Las tareas permanentes requieren un recordatorio con hora.")
            return
        
        self.db.agregar_tarea(
            titulo,
            descripcion,
            fecha_recordatorio,
            notif_sistema,
            False,  # notif_correo siempre False ahora
            importancia,
            es_permanente
        )
        
        # Limpiar campos
        self.entry_titulo.delete(0, tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, "09:00")
        self.var_usar_recordatorio.set(False)
        self.var_importancia.set("Normal")
        self.var_es_permanente.set(False)
        self.var_notif_sistema.set(True)
        
        messagebox.showinfo("Éxito", "Tarea agregada correctamente")
        self.actualizar_lista_tareas()
    
    def actualizar_lista_tareas(self):
        """Actualiza la lista de tareas en el Treeview"""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener tareas pendientes
        tareas = self.db.obtener_tareas(completadas=False)
        
        for tarea in tareas:
            # Manejar formato con o sin es_permanente
            if len(tarea) == 10:
                tarea_id, titulo, descripcion, fecha_creacion, fecha_recordatorio, _, _, _, importancia, es_permanente = tarea
            else:
                tarea_id, titulo, descripcion, fecha_creacion, fecha_recordatorio, _, _, _, importancia = tarea
                es_permanente = False
            
            descripcion_corta = descripcion[:40] + "..." if descripcion and len(descripcion) > 40 else (descripcion or "")
            
            # Formatear fecha de recordatorio: agregar indicador si es permanente
            if fecha_recordatorio:
                try:
                    fecha_obj = datetime.strptime(fecha_recordatorio, "%Y-%m-%d %H:%M:%S")
                    if es_permanente:
                        fecha_recordatorio_str = f"🔄 Diario {fecha_obj.strftime('%H:%M')}"
                    else:
                        fecha_recordatorio_str = fecha_recordatorio
                except:
                    fecha_recordatorio_str = fecha_recordatorio
            else:
                fecha_recordatorio_str = "Sin recordatorio"
            
            importancia_str = importancia or "Normal"
            
            # Colorear según importancia
            tag = ""
            if importancia_str == "Urgente":
                tag = "urgente"
            elif importancia_str == "Importante":
                tag = "importante"
            
            item = self.tree.insert("", tk.END, values=(
                tarea_id,
                titulo,
                descripcion_corta,
                importancia_str,
                fecha_recordatorio_str
            ), tags=(tag,))
        
        # Configurar colores para las etiquetas
        self.tree.tag_configure("urgente", background="#FFE4E1", foreground="#FF0000")
        self.tree.tag_configure("importante", background="#FFF8DC", foreground="#FF8C00")
    
    def marcar_completada(self):
        """Marca la tarea seleccionada como completada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una tarea")
            return
        
        item = self.tree.item(seleccion[0])
        tarea_id = item['values'][0]
        
        self.db.marcar_completada(tarea_id)
        messagebox.showinfo("Éxito", "Tarea marcada como completada")
        self.actualizar_lista_tareas()
    
    def eliminar_tarea(self):
        """Elimina la tarea seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una tarea")
            return
        
        respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta tarea?")
        if respuesta:
            item = self.tree.item(seleccion[0])
            tarea_id = item['values'][0]
            
            self.db.eliminar_tarea(tarea_id)
            messagebox.showinfo("Éxito", "Tarea eliminada")
            self.actualizar_lista_tareas()
    
    def editar_tarea(self):
        """Abre una ventana para editar la tarea seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una tarea para editar")
            return
        
        item = self.tree.item(seleccion[0])
        tarea_id = item['values'][0]
        
        # Obtener los datos completos de la tarea desde la base de datos
        tarea = self.db.obtener_tarea_por_id(tarea_id)
        if not tarea:
            messagebox.showerror("Error", "No se pudo encontrar la tarea")
            return
        
        # Desempaquetar los datos de la tarea (con o sin es_permanente)
        if len(tarea) == 10:
            _, titulo_actual, descripcion_actual, _, fecha_recordatorio_actual, _, notif_sistema_actual, notif_correo_actual, importancia_actual, es_permanente_actual = tarea
        else:
            _, titulo_actual, descripcion_actual, _, fecha_recordatorio_actual, _, notif_sistema_actual, notif_correo_actual, importancia_actual = tarea
            es_permanente_actual = False
        
        # Crear ventana de edición
        ventana_editar = tk.Toplevel(self.root)
        ventana_editar.title("✏️ Editar Tarea")
        ventana_editar.geometry("600x650")
        ventana_editar.minsize(550, 600)
        ventana_editar.configure(bg="#FFE4E1")
        ventana_editar.transient(self.root)  # Hace que la ventana sea modal
        ventana_editar.grab_set()  # Bloquea la ventana principal
        
        # Frame principal con scrollbar si es necesario
        frame_editar = tk.Frame(ventana_editar, bg="#FFE4E1", padx=20, pady=15)
        frame_editar.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            frame_editar,
            text="✏️ Editar Tarea",
            font=("Arial", 18, "bold"),
            bg="#FFE4E1",
            fg="#FF69B4"
        ).pack(pady=(0, 15))
        
        # Título de la tarea
        tk.Label(
            frame_editar,
            text="Título:",
            bg="#FFE4E1",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        entry_titulo_edit = tk.Entry(frame_editar, font=("Arial", 11), width=50)
        entry_titulo_edit.pack(fill=tk.X, pady=(0, 12))
        entry_titulo_edit.insert(0, titulo_actual)
        
        # Descripción
        tk.Label(
            frame_editar,
            text="Descripción:",
            bg="#FFE4E1",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        text_descripcion_edit = tk.Text(frame_editar, font=("Arial", 10), height=4, width=50)
        text_descripcion_edit.pack(fill=tk.X, pady=(0, 12))
        text_descripcion_edit.insert("1.0", descripcion_actual or "")
        
        # Frame para recordatorio
        frame_recordatorio_edit = tk.Frame(frame_editar, bg="#FFE4E1")
        frame_recordatorio_edit.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            frame_recordatorio_edit,
            text="Fecha de recordatorio:",
            bg="#FFE4E1",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Calendario para editar
        calendario_edit = DateEntry(
            frame_recordatorio_edit,
            width=12,
            background='#FF69B4',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Arial", 10)
        )
        calendario_edit.pack(side=tk.LEFT, padx=(0, 10))
        
        # Hora del recordatorio
        tk.Label(
            frame_recordatorio_edit,
            text="Hora (HH:MM):",
            bg="#FFE4E1",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))
        entry_hora_edit = tk.Entry(frame_recordatorio_edit, font=("Arial", 10), width=8)
        entry_hora_edit.pack(side=tk.LEFT)
        
        # Si hay fecha de recordatorio, cargarla
        var_usar_recordatorio_edit = tk.BooleanVar(value=(fecha_recordatorio_actual is not None))
        if fecha_recordatorio_actual:
            try:
                fecha_dt = datetime.strptime(fecha_recordatorio_actual, "%Y-%m-%d %H:%M")
                calendario_edit.set_date(fecha_dt.date())
                entry_hora_edit.insert(0, fecha_dt.strftime("%H:%M"))
            except:
                pass
        
        def toggle_recordatorio_edit():
            estado = var_usar_recordatorio_edit.get()
            if estado:
                calendario_edit.config(state='normal')
                entry_hora_edit.config(state='normal')
            else:
                calendario_edit.config(state='disabled')
                entry_hora_edit.config(state='disabled')
        
        var_usar_recordatorio_edit.trace('w', lambda *args: toggle_recordatorio_edit())
        
        tk.Checkbutton(
            frame_recordatorio_edit,
            text="Activar recordatorio",
            variable=var_usar_recordatorio_edit,
            bg="#FFE4E1",
            font=("Arial", 10),
            command=toggle_recordatorio_edit
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Checkbox para tarea permanente
        var_es_permanente_edit = tk.BooleanVar(value=bool(es_permanente_actual))
        tk.Checkbutton(
            frame_recordatorio_edit,
            text="🔄 Tarea permanente (diaria desde esta fecha)",
            variable=var_es_permanente_edit,
            bg="#FFE4E1",
            font=("Arial", 10),
            fg="#8B008B"
        ).pack(side=tk.LEFT, padx=(15, 0))
        
        toggle_recordatorio_edit()  # Aplicar estado inicial
        
        # Frame para importancia
        frame_importancia_edit = tk.Frame(frame_editar, bg="#FFE4E1")
        frame_importancia_edit.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            frame_importancia_edit,
            text="Importancia:",
            bg="#FFE4E1",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        var_importancia_edit = tk.StringVar(value=importancia_actual or "Normal")
        opciones_importancia = ["Normal", "Importante", "Urgente"]
        
        for opcion in opciones_importancia:
            color = "#87CEEB" if opcion == "Normal" else "#FFD700" if opcion == "Importante" else "#FF6347"
            tk.Radiobutton(
                frame_importancia_edit,
                text=opcion,
                variable=var_importancia_edit,
                value=opcion,
                bg="#FFE4E1",
                font=("Arial", 10),
                selectcolor=color,
                activebackground="#FFE4E1"
            ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Checkbox para notificaciones
        frame_notificaciones_edit = tk.Frame(frame_editar, bg="#FFE4E1")
        frame_notificaciones_edit.pack(fill=tk.X, pady=(0, 15))
        
        var_notif_sistema_edit = tk.BooleanVar(value=bool(notif_sistema_actual))
        
        tk.Label(
            frame_notificaciones_edit,
            text="✨ Las notificaciones se enviarán automáticamente ✨",
            bg="#FFE4E1",
            font=("Arial", 10, "bold"),
            fg="#FF69B4"
        ).pack(side=tk.LEFT)
        
        def guardar_cambios():
            """Guarda los cambios realizados en la tarea"""
            nuevo_titulo = entry_titulo_edit.get().strip()
            if not nuevo_titulo:
                messagebox.showwarning("Advertencia", "El título no puede estar vacío")
                return
            
            nueva_descripcion = text_descripcion_edit.get("1.0", tk.END).strip()
            
            # Obtener fecha y hora del recordatorio
            nueva_fecha_recordatorio = None
            if var_usar_recordatorio_edit.get():
                fecha_seleccionada = calendario_edit.get_date()
                hora_str = entry_hora_edit.get().strip()
                
                if not hora_str:
                    messagebox.showwarning("Advertencia", "Por favor ingresa una hora para el recordatorio")
                    return
                
                try:
                    # Validar formato de hora
                    hora_parts = hora_str.split(":")
                    if len(hora_parts) != 2:
                        raise ValueError
                    hora = int(hora_parts[0])
                    minuto = int(hora_parts[1])
                    if not (0 <= hora <= 23 and 0 <= minuto <= 59):
                        raise ValueError
                    
                    # Combinar fecha y hora
                    # Para tareas permanentes, la fecha es la fecha de inicio (desde cuándo empezar a notificar diariamente)
                    # Para tareas normales, es la fecha específica del recordatorio
                    nueva_fecha_recordatorio = fecha_seleccionada.strftime("%Y-%m-%d") + f" {hora:02d}:{minuto:02d}:00"
                except ValueError:
                    messagebox.showerror("Error", "Formato de hora incorrecto. Usa: HH:MM (ejemplo: 14:30)")
                    return
            
            # Validar que si es permanente, tenga recordatorio
            es_permanente_nuevo = var_es_permanente_edit.get()
            if es_permanente_nuevo and not nueva_fecha_recordatorio:
                messagebox.showwarning("Advertencia", "Las tareas permanentes requieren un recordatorio con hora.")
                return
            
            # Actualizar la tarea en la base de datos
            self.db.actualizar_tarea(
                tarea_id,
                titulo=nuevo_titulo,
                descripcion=nueva_descripcion,
                fecha_recordatorio=nueva_fecha_recordatorio,
                notif_sistema=var_notif_sistema_edit.get(),
                notif_correo=False,  # Siempre False ahora
                importancia=var_importancia_edit.get(),
                es_permanente=es_permanente_nuevo
            )
            
            messagebox.showinfo("Éxito", "Tarea actualizada correctamente")
            ventana_editar.destroy()
            self.actualizar_lista_tareas()
        
        # Botones
        frame_botones_edit = tk.Frame(frame_editar, bg="#FFE4E1")
        frame_botones_edit.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(
            frame_botones_edit,
            text="💾 Guardar Cambios",
            command=guardar_cambios,
            bg="#FF69B4",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            frame_botones_edit,
            text="❌ Cancelar",
            command=ventana_editar.destroy,
            bg="#808080",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
    
    def verificar_recordatorios(self):
        """Verifica y envía recordatorios de tareas pendientes"""
        tareas = self.db.obtener_tareas_pendientes_recordatorio()
        
        for tarea in tareas:
            # Manejar formato con es_permanente (ahora son 8 campos)
            if len(tarea) == 8:
                tarea_id, titulo, descripcion, fecha_recordatorio, notif_sistema, notif_correo, importancia, es_permanente = tarea
            elif len(tarea) == 7:
                tarea_id, titulo, descripcion, fecha_recordatorio, notif_sistema, notif_correo, importancia = tarea
                es_permanente = False
            else:
                tarea_id, titulo, descripcion, fecha_recordatorio, notif_sistema, notif_correo = tarea
                importancia = "Normal"
                es_permanente = False
            
            mensaje = descripcion or ""
            if importancia:
                mensaje += f"\nImportancia: {importancia}" if mensaje else f"Importancia: {importancia}"
            
            if notif_sistema:
                self.notificador.notificar_sistema(titulo, mensaje)
            
            # Marcar como completada después de enviar notificación (opcional)
            # self.db.marcar_completada(tarea_id)
    
    def configurar_bandeja_sistema(self):
        """Configura el icono en la bandeja del sistema"""
        if not HAS_PYSTRAY:
            return
        
        ruta_icono = get_ruta_recurso("icono_unicornio.png")
        if not os.path.isfile(ruta_icono):
            return
        
        try:
            # Cargar imagen para la bandeja (16x16 o 32x32)
            img_tray = Image.open(ruta_icono)
            img_tray = img_tray.resize((32, 32), Image.Resampling.LANCZOS)
            
            # Crear menú contextual
            menu = (
                item("Abrir Agenda Virtual", self.mostrar_ventana),
                item("Cerrar", self.cerrar_aplicacion),
            )
            
            # Crear icono en la bandeja
            self.tray_icon = pystray.Icon("Agenda Virtual", img_tray, "Agenda Virtual", menu)
            
            # Iniciar el icono en un hilo separado
            def ejecutar_tray():
                self.tray_icon.run()
            
            self.tray_thread = threading.Thread(target=ejecutar_tray, daemon=True)
            self.tray_thread.start()
        except Exception as e:
            print(f"Error al configurar bandeja del sistema: {e}")
    
    def mostrar_ventana(self, icon=None, item=None):
        """Muestra la ventana principal desde la bandeja"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def on_closing(self):
        """Se ejecuta cuando intentan cerrar la ventana - minimiza a la bandeja"""
        if HAS_PYSTRAY and self.tray_icon:
            self.root.withdraw()  # Ocultar ventana sin cerrar
        else:
            # Si no hay bandeja, cerrar normalmente
            self.cerrar_aplicacion()
    
    def cerrar_aplicacion(self, icon=None, item=None):
        """Cierra completamente la aplicación"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
    
    def iniciar_verificador_recordatorios(self):
        """Inicia el hilo que verifica recordatorios periódicamente"""
        def ejecutar_verificador():
            schedule.every(1).minutes.do(self.verificar_recordatorios)
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=ejecutar_verificador, daemon=True)
        thread.start()


def main():
    """Función principal"""
    root = tk.Tk()
    # Icono de unicornio (funciona en desarrollo y en .exe empaquetado)
    ruta_icono = get_ruta_recurso("icono_unicornio.png")
    if HAS_PIL and os.path.isfile(ruta_icono):
        try:
            img = Image.open(ruta_icono)
            icono = ImageTk.PhotoImage(img)
            root.iconphoto(True, icono)
            root._icono_unicornio = icono  # mantener referencia
        except Exception:
            pass
    # Base de datos junto al ejecutable (o al script) para que persista al instalar
    ruta_db = os.path.join(get_ruta_base(), "tareas.db")
    app = TodoApp(root, db_path=ruta_db)
    root.mainloop()


if __name__ == "__main__":
    main()
