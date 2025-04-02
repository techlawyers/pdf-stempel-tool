import os
import shlex
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

def create_stamp(text, page_width, page_height):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    can.setFont("Helvetica-Bold", 14)

    # Ersetze Unterstriche durch Leerzeichen
    text = text.replace("_", " ")

    text_width = can.stringWidth(text, "Helvetica-Bold", 14)
    x_pos = page_width - text_width - 40
    y_pos = page_height - 40

    can.drawString(x_pos, y_pos, text)
    can.save()
    packet.seek(0)
    return PdfReader(packet)

def process_pdf(file_path):
    name_without_ext = os.path.splitext(os.path.basename(file_path))[0]

    reader = PdfReader(file_path)
    writer = PdfWriter()

    # Format der ersten Seite ermitteln
    first_page = reader.pages[0]
    page_width = float(first_page.mediabox.width)
    page_height = float(first_page.mediabox.height)

    # Stempel für Format erstellen
    stamp_pdf = create_stamp(name_without_ext, page_width, page_height)
    stamp_page = stamp_pdf.pages[0]

    for i, page in enumerate(reader.pages):
        if i == 0:
            page.merge_page(stamp_page)
        writer.add_page(page)

    output_folder = "stamped_pdfs"
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, os.path.basename(file_path))
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"PDF gestempelt: {output_path}")

def on_drop(event):
    raw = event.data

    # Beispiel: '{C:/Pfad 1/datei.pdf} {C:/Pfad 2/datei mit leerzeichen.pdf}'
    cleaned = raw.replace("{", "").replace("}", "")
    files = cleaned.split()

    merged_files = []
    buffer = ""

    for part in files:
        if os.path.isfile(buffer + " " + part):
            merged_files.append(buffer + " " + part)
            buffer = ""
        elif os.path.isfile(part):
            merged_files.append(part)
        else:
            buffer = part if not buffer else buffer + " " + part

    for file in merged_files:
        print("Verarbeite:", file)
        if file.lower().endswith(".pdf") and os.path.isfile(file):
            process_pdf(file)

def create_gui():
    root = TkinterDnD.Tk()
    root.title("PDF Stempel Tool – Drag & Drop")

    label = tk.Label(root, text="Ziehe deine PDFs hierher", font=("Helvetica", 16))
    label.pack(padx=20, pady=40)

    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    root.geometry("400x200")
    root.mainloop()

if __name__ == "__main__":
    create_gui()