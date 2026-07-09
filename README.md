# Instalación — Assessment Door Cards (HTML + PDF)

Este repositorio contiene dos scripts:

- **`assessment-door.py`** — genera tarjetas HTML por puerta a partir de un Excel y una plantilla.
- **`html_to_pdf_batch.py`** — convierte esas tarjetas HTML en PDF usando Playwright.

## 1. Requisitos

- Python 3.8 o superior
- pip

## 2. Instalación de dependencias

### Recomendado: usar un entorno virtual

```bash
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
```

### Instalar módulos de Python

```bash
pip install pandas openpyxl playwright
```

| Módulo | Para qué sirve |
|---|---|
| `pandas` | Leer el archivo Excel (`assessment-door.xlsx`) |
| `openpyxl` | Motor que usa pandas para leer archivos `.xlsx` |
| `playwright` | Motor de navegador para convertir HTML a PDF |

> `base64`, `pathlib`, `argparse`, `os` y `sys` vienen incluidos con Python — no requieren instalación.

### Instalar el navegador de Playwright

Este paso es obligatorio y aparte del `pip install`:

```bash
playwright install chromium
```

## 3. Solución de problemas con `playwright install`

Si el comando anterior no funciona, prueba en este orden:

### a) Instalar también las dependencias del sistema (Linux / WSL)

```bash
playwright install --with-deps chromium
```

Esto instala automáticamente las librerías de sistema operativo que Chromium necesita (puede pedir `sudo`).

### b) "playwright: command not found"

Ejecuta el comando como módulo de Python en vez de comando directo:

```bash
python -m playwright install chromium
```

### c) Descarga lenta, bloqueada o interrumpida

```bash
pip install --upgrade playwright
playwright install chromium --force
```

Si sigue sin descargar, puede deberse a un proxy o firewall corporativo que bloquea la descarga del navegador (~150–300 MB).

### d) Problemas de permisos en Windows

Abre la terminal (CMD o PowerShell) **como administrador** y vuelve a intentar.

### e) Verificar que playwright sí se instaló

```bash
pip show playwright
```

Si no muestra nada, el problema está en el `pip install playwright`, no en el `playwright install`.

## 4. Uso

### Generar las tarjetas HTML

```bash
python assessment-door.py
```

Requiere en la misma carpeta:
- `historic_door_registration_card_template.html`
- `assessment-door.xlsx`
- Carpeta `photos/<Door ID>/` con las fotos de cada puerta (opcional)

Genera los archivos en `html_cards/`.

### Convertir las tarjetas a PDF

```bash
python html_to_pdf_batch.py --input ./html_cards --output ./pdf_cards
```

Genera los archivos en `pdf_cards/`.
