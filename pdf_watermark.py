from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pathlib import Path
from argparse import ArgumentParser
from io import BytesIO
from os import remove
from sys import exit


def parse_args():
    parser = ArgumentParser(
        description="Adds a watermark to every page of a PDF and overwrites the input file."
    )
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("watermark_text", help="Watermark text to draw on each page")
    return parser.parse_args()


def main():
    args = parse_args()
    input_pdf = args.input_pdf
    watermark_text = args.watermark_text

    # Input-Datei existiert?
    input_path = Path(input_pdf)
    if not input_path.exists():
        print(f"Error: Input file '{input_pdf}' does not exist")
        exit(1)

    # Output-Pfad mit Wasserzeichen-Text im Namen (Leerzeichen/Sonderzeichen durch _ ersetzen)
    watermark_text_safe = "".join(c if c.isalnum() else "_" for c in watermark_text).strip("_") or "watermark"
    output_path = input_path.parent / f"{input_path.stem}_{watermark_text_safe}{input_path.suffix}"
    output_pdf = str(output_path)

    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        packet = BytesIO()
        c = canvas.Canvas(packet)

        # Position unten rechts (anpassbar)
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        c.setFont("Times-Roman", 10)
        c.setFillColor(HexColor("#03468F"))
        c.drawRightString(width - 20, 20, watermark_text)

        c.save()
        packet.seek(0)

        overlay = PdfReader(packet)
        page.merge_page(overlay.pages[0])
        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)

    # Input-Datei löschen
    remove(input_pdf)
    print(f"✓ PDF verarbeitet: {output_pdf}")
    print(f"✓ Original-Datei gelöscht")


if __name__ == "__main__":
    main()

