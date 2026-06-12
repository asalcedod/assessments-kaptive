"""
Conversor masivo de HTML a PDF usando Playwright.
Lee todos los .html de una carpeta de entrada y guarda los PDF en una carpeta de salida.

Uso:
    python html_to_pdf_batch.py --input ./html_cards --output ./pdf_cards

Requisitos:
    pip install playwright
    playwright install chromium
"""

import os
import sys
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright


def html_to_pdf(page, html_path: Path, pdf_path: Path) -> bool:
    """
    Convierte un archivo HTML a PDF de una sola página, preservando todos los colores.
    Retorna True si fue exitoso, False si hubo un error.
    """
    try:
        # Cargar la página emulando pantalla (NO print) para preservar colores Tailwind
        page.emulate_media(media="screen")

        # Viewport amplio para que Tailwind renderice en modo desktop (max-w-5xl, etc.)
        page.set_viewport_size({"width": 1280, "height": 900})

        file_url = f"file://{html_path.resolve()}"
        # networkidle espera a que el CDN de Tailwind termine de procesar
        page.goto(file_url, wait_until="networkidle", timeout=30000)

        # Espera adicional para que Tailwind aplique todos los estilos JIT
        page.wait_for_timeout(1500)

        # Calcular el alto real del contenido para forzar una sola página
        content_height = page.evaluate("""
            () => {
                const body = document.body;
                const html = document.documentElement;
                return Math.max(
                    body.scrollHeight, body.offsetHeight,
                    html.clientHeight, html.scrollHeight, html.offsetHeight
                );
            }
        """)

        # Carta (Letter) en puntos: 612 x 792. Ancho del viewport: 1280px
        # 1pt = 1.3333px → Letter ancho = 612 * 1.3333 ≈ 816px
        letter_width_pt = 712
        letter_height_pt = 892
        margin_mm = 0
        margin_pt = margin_mm * 2.8346          # 8mm → ~22.7pt por lado
        usable_width_pt = letter_width_pt - (margin_pt * 2)   # ≈ 566pt
        usable_height_pt = letter_height_pt - (margin_pt * 2) # ≈ 746pt

        scale_by_width = (usable_width_pt * 1.3333) / 1280

        usable_height_px = usable_height_pt * 1.3333
        if content_height > 0:
            scale_by_height = usable_height_px / content_height
        else:
            scale_by_height = 1.0

        # El menor garantiza que todo cabe en una sola página
        scale = min(scale_by_width, scale_by_height)
        scale = max(0.1, min(scale, 1.0))

        page.pdf(
            path=str(pdf_path),
            format="Letter",
            print_background=True,       # Imprescindible para fondos de color
            scale=scale,                 # Escala para forzar una sola página
            margin={
                "top": f"{margin_mm}mm",
                "bottom": f"{margin_mm}mm",
                "left": f"{margin_mm}mm",
                "right": f"{margin_mm}mm",
            },
            display_header_footer=False,
        )
        return True

    except Exception as e:
        print(f"  ✗ Error procesando {html_path.name}: {e}")
        return False


def batch_convert(input_dir: str, output_dir: str):
    """
    Convierte todos los archivos .html de input_dir a PDF en output_dir.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: La carpeta de entrada '{input_dir}' no existe.")
        sys.exit(1)

    # Crear carpeta de salida si no existe
    output_path.mkdir(parents=True, exist_ok=True)

    html_files = sorted(input_path.glob("*.html"))

    if not html_files:
        print(f"No se encontraron archivos .html en '{input_dir}'.")
        sys.exit(0)

    print(f"Encontrados {len(html_files)} archivo(s) HTML en '{input_dir}'")
    print(f"Los PDF se guardarán en '{output_dir}'\n")

    ok_count = 0
    fail_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Una sola página/contexto reutilizada para todos los archivos (más eficiente)
        context = browser.new_context()
        page = context.new_page()

        for i, html_file in enumerate(html_files, start=1):
            pdf_file = output_path / (html_file.stem + ".pdf")
            print(f"[{i}/{len(html_files)}] {html_file.name} → {pdf_file.name} ...", end=" ")

            success = html_to_pdf(page, html_file, pdf_file)

            if success:
                ok_count += 1
                print("✓")
            else:
                fail_count += 1

        context.close()
        browser.close()

    print(f"\n--- Resumen ---")
    print(f"  Exitosos : {ok_count}")
    print(f"  Fallidos : {fail_count}")
    print(f"  Total    : {len(html_files)}")


if __name__ == "__main__":
    batch_convert("html_cards", "pdf_cards")