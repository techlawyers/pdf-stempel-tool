import os
import shlex
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tkinter as tk
from tkinter import filedialog, messagebox

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

    return output_path

def process_files(files):
    processed_files = []
    for file in files:
        if file.lower().endswith(".pdf") and os.path.isfile(file):
            output_path = process_pdf(file)
            processed_files.append(output_path)
    
    return processed_files

def browse_files():
    files = filedialog.askopenfilenames(
        title="PDFs auswählen",
        filetypes=[("PDF Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
    )
    
    if files:
        status_label.config(text="Verarbeite Dateien...")
        root.update()
        
        processed = process_files(files)
        
        if processed:
            messagebox.showinfo(
                "Fertig", 
                f"{len(processed)} PDF(s) wurden gestempelt und im Ordner 'stamped_pdfs' gespeichert."
            )
            status_label.config(text=f"{len(processed)} PDF(s) gestempelt")
        else:
            status_label.config(text="Keine PDFs verarbeitet")

def create_gui():
    global root, status_label
    
    root = tk.Tk()
    root.title("PDF Stempel Tool")
    root.geometry("400x200")
    
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True, fill="both")
    
    title_label = tk.Label(frame, text="PDF Stempel Tool", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    browse_button = tk.Button(frame, text="PDFs auswählen", command=browse_files, font=("Helvetica", 12))
    browse_button.pack(pady=10)
    
    status_label = tk.Label(frame, text="Bereit", font=("Helvetica", 10))
    status_label.pack(pady=10)
    
    info_label = tk.Label(frame, text="Wähle PDF-Dateien aus, um sie mit dem Dateinamen zu stempeln", font=("Helvetica", 9))
    info_label.pack(pady=(20, 0))
    
    root.mainloop()

def main():
    create_gui()

if __name__ == "__main__":
    main()