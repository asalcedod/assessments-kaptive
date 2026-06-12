import base64
import pandas as pd
from pathlib import Path

# ── Leer archivos ─────────────────────────────────────────────────────────────
template = Path("historic_door_registration_card_template.html").read_text(encoding="utf-8")

# La fila de encabezados reales está en la fila 5 (índice 4)
df = pd.read_excel("WLA_B13DoorsAssessment.xlsx", sheet_name="Door", header=4)

# Carpeta raíz de fotos:  photos/<Door ID>/foto1.jpg, foto2.jpg …
PHOTOS_DIR = Path("photos")

# Carpeta de salida
Path("html_cards").mkdir(exist_ok=True)

# ── Valores estáticos del encabezado ─────────────────────────────────────────
PROJECT_NAME        = "WLA - B13"
GENERAL_CONTRACTOR  = "Walton Construction Inc."
SUBCONTRACTOR       = "KAPTIVE C&P"
DATE_OF_PREPARATION = "May 16, 2026"

# Extensiones de imagen soportadas
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def clean(val):
    """Convierte NaN y valores vacíos a cadena vacía."""
    if pd.isna(val):
        return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s
 
 
def img_to_base64(path: Path) -> str:
    """Devuelve un data-URI base64 para incrustar la imagen en el HTML."""
    ext = path.suffix.lower()
    mime = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png",  ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"
 
 
def build_photo_html(door_id: str) -> str:
    """
    Busca fotos en photos/<door_id>/ y devuelve el HTML del grid.
    Si no hay fotos devuelve el placeholder.
    """
    door_photo_dir = PHOTOS_DIR / door_id
    if not door_photo_dir.is_dir():
        return (
            '<div class="w-full min-h-[120px] border-2 border-dashed border-gray-300 '
            'flex items-center justify-center bg-gray-50 text-gray-400 italic text-sm">'
            'No photo available</div>'
        )
 
    photos = sorted(
        p for p in door_photo_dir.iterdir()
        if p.suffix.lower() in IMAGE_EXTS
    )
 
    if not photos:
        return (
            '<div class="w-full min-h-[120px] border-2 border-dashed border-gray-300 '
            'flex items-center justify-center bg-gray-50 text-gray-400 italic text-sm">'
            'No photo available</div>'
        )
 
    cols = "grid-cols-1" if len(photos) == 1 else "grid-cols-2"
 
    items = []
    for i, photo_path in enumerate(photos, start=1):
        src = img_to_base64(photo_path)
        items.append(
            f'<div class="relative flex items-center justify-center bg-gray-50 border border-gray-200 rounded overflow-hidden">'
            f'  <img src="{src}" alt="Photo {i}" '
            f'       style="max-width:100%; max-height:120px; width:auto; height:auto; object-fit:contain; display:block;">'
            f'  <span class="absolute bottom-1 left-1 bg-[#0a3a70] text-white '
            f'               text-[8px] font-bold px-1 rounded opacity-80"></span>'
            f'</div>'
        )
 
    return (
        f'<div class="grid {cols} gap-2">'
        + "\n".join(items) +
        f'</div>'
    )
 

 
# ── Generar una tarjeta por puerta ────────────────────────────────────────────
for _, row in df.iterrows():
    door_id = clean(row.get("ID Door", ""))
    logo = "logo"
    if not door_id:
        continue

    replacements = {
        # ── Encabezado ──────────────────────────────────────────────────────
        "{{ PROJECT_NAME }}":                           PROJECT_NAME,
        "{{ GENERAL_CONTRACTOR }}":                     GENERAL_CONTRACTOR,
        "{{ SUBCONTRACTOR }}":                          SUBCONTRACTOR,
        "{{ DATE_OF_PREPARATION }}":                    DATE_OF_PREPARATION,
        "{{ ID_DOOR }}":                                door_id,

        # ── 01. Location & Site Logic ────────────────────────────────────────
        "{{ INSPECTION_LEVEL }}":                       clean(row.get("Inspection Level")),
        "{{ ROOM_NAME }}":                              clean(row.get("Room Name")),
        "{{ ACCESS_STATUS }}":                          clean(row.get("Access Status")),
        "{{ DOOR_ORIGIN }}":                            clean(row.get("Door Origin")),

        # ── 02. Field Notes & Pathologies ────────────────────────────────────
        "{{ DOOR_MATERIAL }}":                          clean(row.get("Door Material")),
        "{{ DOOR_TYPE }}":                              clean(row.get("Door Type")),
        "{{ DOOR_NOTES }}":                             clean(row.get("Door - Notes")),
        "{{ FRAME_NOTES }}":                            clean(row.get("Frame - Notes")),
        "{{ TRANSOM_NOTES }}":                          clean(row.get("Transom - Notes")),

        # ── 03. Assessment & Severity ────────────────────────────────────────
        "{{ TECHNICAL_NOTES }}":                        clean(row.get("Technical Notes")),
        "{{ PRIORITY }}":                               clean(row.get("Priority")),
        "{{ EVALUATION_SCORE }}":                       clean(row.get("Evaluation score")),

        # ── 04. Field Photo / Evidence ───────────────────────────────────────
        "{{ PHOTO }}":                                  build_photo_html(door_id),
        "{{ LOGO }}":                                   build_photo_html(logo),

        # ── 05. Door ─────────────────────────────────────────────────────────
        "{{ DOOR_CURRENT_STATUS }}":                    clean(row.get("Door - Current Status")),
        "{{ DOOR_RECOMMENDED_ACTION }}":                clean(row.get("Door - Recommended Action")),

        # ── 06. Frame ────────────────────────────────────────────────────────
        "{{ FRAME_CURRENT_STATUS }}":                   clean(row.get("Frame - Current Status")),
        "{{ FRAME_RECOMMENDED_ACTION }}":               clean(row.get("Frame - Recommended Action")),

        # ── 07. Hinges ───────────────────────────────────────────────────────
        "{{ HINGES_CURRENT_STATUS }}":                  clean(row.get("Hinges - Current Status")),
        "{{ HINGES_RECOMMENDED_ACTION }}":              clean(row.get("Hinges - Recommended Action")),

        # ── 08. Transom ──────────────────────────────────────────────────────
        "{{ TRANSOM_CURRENT_STATUS }}":                 clean(row.get("Transom - Current Status")),
        "{{ TRANSOM_RECOMMENDED_ACTION }}":             clean(row.get("Transom - Recommended Action")),
        "{{ TRANSOM_FUNCTION }}":                       clean(row.get("Transom - Function")),

        # ── 09. Door Handle ──────────────────────────────────────────────────
        "{{ DOOR_HANDLE_CURRENT_STATUS }}":             clean(row.get("Door handle - Current Status")),
        "{{ DOOR_HANDLE_RECOMMENDED_ACTION }}":         clean(row.get("Door handle - Recommended Action")),

        # ── 10. Automatic Closing Arm ────────────────────────────────────────
        "{{ AUTOMATIC_CLOSING_ARM_CURRENT_STATUS }}":   clean(row.get("Automatic closing arm - Current Status")),
    }

    html = template
    for key, val in replacements.items():
        html = html.replace(key, val)

    output_path = Path("html_cards") / f"{door_id}_card.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"✓  {output_path}")

print("\nDone.")