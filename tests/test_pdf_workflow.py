import hashlib
import os
from io import BytesIO
from pathlib import Path
import shutil
import unittest

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

from stempel_tool import process_files, process_pdf


PORTRAIT = (595.28, 841.89)
LANDSCAPE = (841.89, 595.28)
TEMP_ROOT = Path(__file__).resolve().parents[1] / "tmp" / "pdfs"


def create_sample_pdf(file_path: Path, page_sizes: list[tuple[float, float]]) -> None:
    pdf_canvas = canvas.Canvas(str(file_path), pagesize=page_sizes[0])

    for index, (width, height) in enumerate(page_sizes, start=1):
        pdf_canvas.setPageSize((width, height))
        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.drawString(40, height - 60, f"Testinhalt Seite {index}")
        pdf_canvas.drawString(40, 40, f"Format {width:.0f} x {height:.0f}")
        pdf_canvas.showPage()

    pdf_canvas.save()


def pdf_text(file_path: Path, page_number: int = 0) -> str:
    return PdfReader(str(file_path)).pages[page_number].extract_text()


def rotate_first_page(file_path: Path, rotation: int) -> None:
    reader = PdfReader(BytesIO(file_path.read_bytes()))
    writer = PdfWriter()
    writer.add_page(reader.pages[0].rotate(rotation))
    output = BytesIO()
    writer.write(output)
    file_path.write_bytes(output.getvalue())


class PdfWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.folder = TEMP_ROOT / self._testMethodName
        if self.folder.exists():
            shutil.rmtree(self.folder)
        self.folder.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.folder)

    def test_stamped_copy_sits_beside_original_and_only_stamps_first_page(self) -> None:
        source = self.folder / "Mandat_2026.pdf"
        create_sample_pdf(source, [PORTRAIT, LANDSCAPE])
        original_bytes = source.read_bytes()

        results = process_files([source])

        self.assertEqual(results[0].status, "processed")
        output = results[0].output
        self.assertIsNotNone(output)
        self.assertEqual(output.parent, source.parent)
        self.assertEqual(output.name, "Mandat_2026_gestempelt.pdf")
        self.assertEqual(source.read_bytes(), original_bytes)

        reader = PdfReader(str(output))
        self.assertEqual(len(reader.pages), 2)
        self.assertIn("Mandat 2026", reader.pages[0].extract_text())
        self.assertNotIn("Mandat 2026", reader.pages[1].extract_text())
        self.assertLess(float(reader.pages[0].mediabox.width), float(reader.pages[0].mediabox.height))
        self.assertGreater(float(reader.pages[1].mediabox.width), float(reader.pages[1].mediabox.height))

    def test_landscape_first_page_gets_filename_stamp(self) -> None:
        source = self.folder / "Querschnitt_Fall.pdf"
        create_sample_pdf(source, [LANDSCAPE])

        output = process_pdf(source)

        page = PdfReader(str(output)).pages[0]
        self.assertGreater(float(page.mediabox.width), float(page.mediabox.height))
        self.assertIn("Querschnitt Fall", page.extract_text())

    def test_stamp_is_upright_on_pages_rotated_90_180_and_270_degrees(self) -> None:
        for rotation in (90, 180, 270):
            with self.subTest(rotation=rotation):
                source = self.folder / f"Drehung_{rotation}.pdf"
                create_sample_pdf(source, [PORTRAIT])
                rotate_first_page(source, rotation)
                original_bytes = source.read_bytes()

                output = process_pdf(source)

                page = PdfReader(str(output)).pages[0]
                self.assertIn(f"Drehung {rotation}", page.extract_text())
                self.assertEqual(page.get("/Rotate"), 0)
                self.assertEqual(
                    float(page.mediabox.width) > float(page.mediabox.height),
                    rotation in (90, 270),
                )
                self.assertEqual(source.read_bytes(), original_bytes)

    def test_existing_stamped_copy_is_not_overwritten(self) -> None:
        source = self.folder / "Fallakte.pdf"
        create_sample_pdf(source, [PORTRAIT])
        existing_output = self.folder / "Fallakte_gestempelt.pdf"
        existing_output.write_bytes(b"bestehende Testdatei")
        original_bytes = source.read_bytes()
        existing_bytes = existing_output.read_bytes()

        results = process_files([source])

        self.assertEqual(results[0].status, "processed")
        self.assertEqual(results[0].output.name, "Fallakte_gestempelt (2).pdf")
        self.assertEqual(source.read_bytes(), original_bytes)
        self.assertEqual(existing_output.read_bytes(), existing_bytes)
        self.assertIn("Fallakte", pdf_text(results[0].output))

    def test_invalid_input_does_not_change_original_or_create_output(self) -> None:
        source = self.folder / "beschädigt.pdf"
        source.write_bytes(b"not a PDF")
        original_bytes = source.read_bytes()

        results = process_files([source])

        self.assertEqual(results[0].status, "failed")
        self.assertEqual(source.read_bytes(), original_bytes)
        self.assertFalse((self.folder / "beschädigt_gestempelt.pdf").exists())

    def test_validated_copy_can_replace_the_same_path_in_a_disposable_probe(self) -> None:
        source = self.folder / "InPlaceProbe.pdf"
        create_sample_pdf(source, [PORTRAIT])
        original_hash = hashlib.sha256(source.read_bytes()).hexdigest()

        replacement = process_pdf(source)
        replacement_reader = PdfReader(str(replacement))
        self.assertIn("InPlaceProbe", replacement_reader.pages[0].extract_text())

        os.replace(replacement, source)

        self.assertTrue(source.exists())
        self.assertFalse(replacement.exists())
        self.assertNotEqual(hashlib.sha256(source.read_bytes()).hexdigest(), original_hash)
        self.assertIn("InPlaceProbe", pdf_text(source))


if __name__ == "__main__":
    unittest.main(verbosity=2)
