import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None


STAMP_FONT = "Helvetica-Bold"
STAMP_FONT_SIZE = 14
OUTPUT_FOLDER_NAME = "stamped_pdfs"


@dataclass
class FileResult:
    source: Path
    output: Path | None = None
    status: str = "processed"
    message: str = ""


def get_app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_output_folder() -> Path:
    return get_app_base_dir() / OUTPUT_FOLDER_NAME


def create_unique_output_path(output_folder: Path, file_name: str) -> Path:
    candidate = output_folder / file_name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        numbered = output_folder / f"{stem} ({counter}){suffix}"
        if not numbered.exists():
            return numbered
        counter += 1


def create_stamp(text: str, page_width: float, page_height: float) -> PdfReader:
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    can.setFont(STAMP_FONT, STAMP_FONT_SIZE)

    text = text.replace("_", " ")
    text_width = can.stringWidth(text, STAMP_FONT, STAMP_FONT_SIZE)
    x_pos = page_width - text_width - 40
    y_pos = page_height - 40

    can.drawString(x_pos, y_pos, text)
    can.save()
    packet.seek(0)
    return PdfReader(packet)


def process_pdf(file_path: Path, output_folder: Path) -> Path:
    reader = PdfReader(str(file_path))

    if reader.is_encrypted:
        try:
            decrypt_result = reader.decrypt("")
        except Exception as exc:
            raise ValueError("PDF ist verschluesselt und konnte nicht geoeffnet werden.") from exc
        if decrypt_result == 0:
            raise ValueError("PDF ist verschluesselt und konnte nicht geoeffnet werden.")

    if len(reader.pages) == 0:
        raise ValueError("PDF enthaelt keine Seiten.")

    writer = PdfWriter()
    first_page = reader.pages[0]
    if first_page.rotation:
        first_page.transfer_rotation_to_content()

    page_width = float(first_page.mediabox.width)
    page_height = float(first_page.mediabox.height)

    stamp_pdf = create_stamp(file_path.stem, page_width, page_height)
    stamp_page = stamp_pdf.pages[0]

    for index, page in enumerate(reader.pages):
        if index == 0:
            page.merge_page(stamp_page)
        writer.add_page(page)

    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = create_unique_output_path(output_folder, file_path.name)
    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return output_path


def process_files(files) -> list[FileResult]:
    output_folder = get_output_folder()
    results: list[FileResult] = []

    for raw_file in files:
        file_path = Path(raw_file).expanduser()

        if not file_path.exists() or not file_path.is_file():
            results.append(
                FileResult(file_path, status="failed", message="Datei wurde nicht gefunden.")
            )
            continue

        if file_path.suffix.lower() != ".pdf":
            results.append(
                FileResult(file_path, status="skipped", message="Keine PDF-Datei.")
            )
            continue

        try:
            output_path = process_pdf(file_path, output_folder)
        except Exception as exc:
            results.append(FileResult(file_path, status="failed", message=str(exc)))
        else:
            results.append(FileResult(file_path, output=output_path))

    return results


def summarize_results(results: list[FileResult]) -> tuple[str, str]:
    processed = [result for result in results if result.status == "processed"]
    skipped = [result for result in results if result.status == "skipped"]
    failed = [result for result in results if result.status == "failed"]

    title = "Fertig" if not failed else "Verarbeitung abgeschlossen"
    lines = [
        f"Erfolgreich gestempelt: {len(processed)}",
        f"Uebersprungen: {len(skipped)}",
        f"Fehlgeschlagen: {len(failed)}",
        f"Zielordner: {get_output_folder()}",
    ]

    if skipped or failed:
        lines.append("")
        lines.append("Details:")
        for result in skipped + failed:
            lines.append(f"- {result.source.name}: {result.message}")

    return title, "\n".join(lines)


def show_results(results: list[FileResult], parent=None) -> None:
    title, message = summarize_results(results)
    has_failures = any(result.status == "failed" for result in results)
    if has_failures:
        messagebox.showwarning(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent)


def parse_drop_data(root, data: str) -> tuple[str, ...]:
    return tuple(root.tk.splitlist(data))


def browse_files(root, status_label) -> None:
    files = filedialog.askopenfilenames(
        title="PDFs auswaehlen",
        filetypes=[("PDF Dateien", "*.pdf"), ("Alle Dateien", "*.*")],
        parent=root,
    )

    if not files:
        return

    status_label.config(text="Verarbeite Dateien...")
    root.update_idletasks()

    results = process_files(files)
    show_results(results, parent=root)

    processed_count = sum(1 for result in results if result.status == "processed")
    failed_count = sum(1 for result in results if result.status == "failed")
    status_label.config(
        text=f"{processed_count} gestempelt, {failed_count} fehlgeschlagen"
    )


def handle_drop(root, status_label, event) -> None:
    files = parse_drop_data(root, event.data)
    if not files:
        return

    status_label.config(text="Verarbeite Dateien...")
    root.update_idletasks()

    results = process_files(files)
    show_results(results, parent=root)

    processed_count = sum(1 for result in results if result.status == "processed")
    failed_count = sum(1 for result in results if result.status == "failed")
    status_label.config(
        text=f"{processed_count} gestempelt, {failed_count} fehlgeschlagen"
    )


def create_gui() -> None:
    if TkinterDnD is not None:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    root.title("PDF Stempel Tool")
    root.geometry("460x280")
    root.minsize(420, 250)

    frame = tk.Frame(root, padx=24, pady=24)
    frame.pack(expand=True, fill="both")

    title_label = tk.Label(frame, text="PDF Stempel Tool", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 16))

    drop_text = "PDFs hier ablegen oder ueber den Button auswaehlen"
    if TkinterDnD is None:
        drop_text = "PDFs ueber den Button auswaehlen"

    drop_label = tk.Label(
        frame,
        text=drop_text,
        relief="groove",
        borderwidth=2,
        width=48,
        height=4,
        font=("Helvetica", 10),
    )
    drop_label.pack(fill="x", pady=(0, 14))

    browse_button = tk.Button(
        frame,
        text="PDFs auswaehlen",
        command=lambda: browse_files(root, status_label),
        font=("Helvetica", 12),
    )
    browse_button.pack(pady=8)

    status_label = tk.Label(frame, text="Bereit", font=("Helvetica", 10))
    status_label.pack(pady=8)

    info_label = tk.Label(
        frame,
        text=f"Ausgabeordner: {get_output_folder()}",
        font=("Helvetica", 9),
        wraplength=390,
        justify="center",
    )
    info_label.pack(pady=(10, 0))

    if TkinterDnD is not None:
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind("<<Drop>>", lambda event: handle_drop(root, status_label, event))
        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<Drop>>", lambda event: handle_drop(root, status_label, event))

    root.mainloop()


def run_cli(files: list[str]) -> None:
    results = process_files(files)
    root = tk.Tk()
    root.withdraw()
    show_results(results, parent=root)
    root.destroy()


def main() -> None:
    files = sys.argv[1:]
    if files:
        run_cli(files)
    else:
        create_gui()


if __name__ == "__main__":
    main()
