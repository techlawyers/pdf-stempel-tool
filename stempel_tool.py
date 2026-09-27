import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from tkinterdnd2 import DND_FILES, TkinterDnD


STAMP_FONT = "Helvetica-Bold"
STAMP_FONT_SIZE = 14
STAMPED_SUFFIX = "_gestempelt"
UI_BACKGROUND = "#F4F6FA"
UI_SURFACE = "#FFFFFF"
UI_TEXT = "#172A45"
UI_BORDER = "#DCE4EF"
UI_BLUE = "#1769E0"
UI_BLUE_HOVER = "#0F55C4"


def resource_path(file_name: str) -> Path:
    app_folder = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return app_folder / file_name


@dataclass
class FileResult:
    source: Path
    output: Path | None = None
    status: str = "processed"
    message: str = ""


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
    pdf_canvas = canvas.Canvas(packet, pagesize=(page_width, page_height))
    pdf_canvas.setFont(STAMP_FONT, STAMP_FONT_SIZE)

    stamp_text = text.replace("_", " ")
    text_width = pdf_canvas.stringWidth(stamp_text, STAMP_FONT, STAMP_FONT_SIZE)
    x_pos = page_width - text_width - 40
    y_pos = page_height - 40

    pdf_canvas.drawString(x_pos, y_pos, stamp_text)
    pdf_canvas.save()
    packet.seek(0)
    return PdfReader(packet)


def process_pdf(file_path: Path) -> Path:
    reader = PdfReader(str(file_path))

    if reader.is_encrypted:
        try:
            decrypt_result = reader.decrypt("")
        except Exception as exc:
            raise ValueError("PDF ist verschlüsselt und konnte nicht geöffnet werden.") from exc
        if decrypt_result == 0:
            raise ValueError("PDF ist verschlüsselt und konnte nicht geöffnet werden.")

    if len(reader.pages) == 0:
        raise ValueError("PDF enthält keine Seiten.")

    first_page = reader.pages[0]
    if first_page.rotation:
        first_page.transfer_rotation_to_content()

    page_width = float(first_page.mediabox.width)
    page_height = float(first_page.mediabox.height)
    stamp_page = create_stamp(file_path.stem, page_width, page_height).pages[0]

    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        if index == 0:
            page.merge_page(stamp_page)
        writer.add_page(page)

    output_folder = file_path.parent
    stamped_name = f"{file_path.stem}{STAMPED_SUFFIX}{file_path.suffix}"
    output_path = create_unique_output_path(output_folder, stamped_name)
    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return output_path


def process_files(files: list[str | Path]) -> list[FileResult]:
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
            output_path = process_pdf(file_path)
        except Exception as exc:
            results.append(FileResult(file_path, status="failed", message=str(exc)))
        else:
            results.append(FileResult(file_path, output=output_path))

    return results


def split_drop_files(tk_interpreter, drop_data: str) -> list[str]:
    return list(tk_interpreter.splitlist(drop_data))


def summarize_results(results: list[FileResult]) -> tuple[str, str]:
    processed = [result for result in results if result.status == "processed"]
    failed = [result for result in results if result.status == "failed"]

    if failed:
        details = "\n".join(
            f"{result.source.name}: {result.message}" for result in failed
        )
        if processed:
            details = f"{len(processed)} PDF(s) gestempelt.\n\n{details}"
        return "PDF-Stempel", details
    if processed:
        return "PDF-Stempel", f"{len(processed)} PDF(s) gestempelt."
    return "PDF-Stempel", "Keine PDF-Datei erkannt."


def show_results(results: list[FileResult], parent=None) -> None:
    title, message = summarize_results(results)
    has_failures = any(result.status == "failed" for result in results)
    if has_failures:
        messagebox.showwarning(title, message, parent=parent)


def process_and_report(files: list[str | Path], root) -> None:
    results = process_files(files)
    failed = any(result.status == "failed" for result in results)

    if failed:
        show_results(results, parent=root)


def browse_files(root) -> None:
    files = filedialog.askopenfilenames(
        title="PDF-Dateien auswählen",
        filetypes=[("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*")],
        parent=root,
    )
    if files:
        process_and_report(list(files), root)


def create_gui() -> None:
    root = TkinterDnD.Tk()
    root.title("PDF-Stempel")
    root.geometry("600x420")
    root.resizable(False, False)
    root.configure(bg=UI_BACKGROUND)
    root.iconbitmap(str(resource_path("stempel_icon.ico")))

    drop_zone = tk.Frame(
        root,
        bg=UI_SURFACE,
        highlightbackground=UI_BORDER,
        highlightthickness=1,
        bd=0,
    )
    drop_zone.pack(expand=True, fill="both", padx=30, pady=28)

    center = tk.Frame(drop_zone, bg=UI_SURFACE)
    center.pack(expand=True)

    with Image.open(resource_path("stempel_icon.ico")) as icon_source:
        logo = ImageTk.PhotoImage(
            icon_source.resize((104, 104), Image.Resampling.LANCZOS), master=root
        )
    root.logo_image = logo

    logo_label = tk.Label(center, image=logo, bg=UI_SURFACE, bd=0)
    logo_label.pack(pady=(0, 8))
    drop_label = tk.Label(
        center,
        text="PDF hier ablegen",
        font=("Segoe UI", 14, "bold"),
        fg=UI_TEXT,
        bg=UI_SURFACE,
    )
    drop_label.pack()
    choose_button = tk.Button(
        center,
        text="Datei auswählen",
        font=("Segoe UI", 10, "bold"),
        fg="#FFFFFF",
        bg=UI_BLUE,
        activeforeground="#FFFFFF",
        activebackground=UI_BLUE_HOVER,
        relief="flat",
        borderwidth=0,
        padx=20,
        pady=10,
        cursor="hand2",
        command=lambda: browse_files(root),
    )
    choose_button.pack(pady=(20, 0))

    def set_drop_highlight(active: bool) -> None:
        drop_zone.configure(
            highlightbackground=UI_BLUE if active else UI_BORDER,
            highlightthickness=2 if active else 1,
        )

    def on_drop(event):
        files = split_drop_files(root.tk, event.data)
        if files:
            process_and_report(list(files), root)
        set_drop_highlight(False)
        return "break"

    def on_drag_enter(_event):
        set_drop_highlight(True)

    def on_drag_leave(_event):
        set_drop_highlight(False)

    for widget in (root, drop_zone, center, logo_label, drop_label, choose_button):
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<Drop>>", on_drop)
        widget.dnd_bind("<<DragEnter>>", on_drag_enter)
        widget.dnd_bind("<<DragLeave>>", on_drag_leave)

    root.mainloop()


def run_cli(files: list[str]) -> None:
    root = tk.Tk()
    root.withdraw()
    show_results(process_files(files), parent=root)
    root.destroy()


def main() -> None:
    files = sys.argv[1:]
    if files:
        run_cli(files)
    else:
        create_gui()


if __name__ == "__main__":
    main()
