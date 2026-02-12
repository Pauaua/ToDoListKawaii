# Cambiar el icono del .exe manualmente (unicornio)

Si el .exe sigue mostrando el icono de Python, puedes poner el unicornio a mano con **Resource Hacker**.

## 1. Descargar Resource Hacker

- Página oficial: **https://www.angusj.com/resourcehacker/**
- Descarga **Resource Hacker** (gratis, sin instalador pesado; suele ser un .zip con el .exe).
- Descomprime y abre `ResourceHacker.exe`.

## 2. Hacer una copia del .exe

- Copia `dist\TodoListKawaii.exe` a otra carpeta (por ejemplo el escritorio) y trabaja sobre esa copia, o
- Guarda una copia como `TodoListKawaii_respaldo.exe` por si acaso.

## 3. Abrir el .exe en Resource Hacker

1. En Resource Hacker: **File → Open**.
2. Elige **`dist\TodoListKawaii.exe`** (o la copia con la que quieras trabajar).
3. En el panel izquierdo abre **Icon Group** (o **Icon**). Ahí verás el icono actual del .exe.

## 4. Reemplazar por el icono unicornio

1. Clic derecho en **Icon Group** (o en el primer icono de la lista) → **Replace Icon** (o **Replace Resource**).
2. Pulsa **“Open file with new icon”** y selecciona **`icono_unicornio.ico`** (está en la carpeta del proyecto, junto a `main.py`).
3. Acepta para reemplazar.
4. **File → Save** y cierra Resource Hacker.

## 5. Comprobar

- Abre la carpeta donde está el .exe que modificaste.
- Si no ves el icono nuevo, cierra el Explorador y vuelve a abrirlo, o cambia la vista a “Iconos grandes”.

El .exe ya tendrá el icono del unicornio. Puedes enviar ese .exe a otra persona igual que antes.
