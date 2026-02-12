"""
Genera icono_unicornio.ico desde icono_unicornio.png para el .exe y el instalador.
Ejecutar una vez: python crear_icono_ico.py
"""
import os
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
png_path = os.path.join(script_dir, "icono_unicornio.png")
ico_path = os.path.join(script_dir, "icono_unicornio.ico")

if not os.path.isfile(png_path):
    print("No se encuentra icono_unicornio.png")
    exit(1)

img = Image.open(png_path).convert("RGBA")
# Tamaños típicos para .ico en Windows
sizes = [(256, 256), (48, 48), (32, 32), (16, 16)]
img.save(ico_path, format="ICO", sizes=sizes)
print("Creado:", ico_path)
