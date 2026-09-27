from pathlib import Path
import tkinter as tk
import unittest
from unittest.mock import patch

import stempel_tool


class GuiLayoutTests(unittest.TestCase):
    def test_drop_paths_preserve_spaces_and_multiple_files(self) -> None:
        interpreter = tk.Tcl()
        raw_data = (
            r"{C:\Users\Lena Mustermann\Akte 1.pdf} "
            r"{D:\Andere Akte\Bericht.pdf}"
        )

        self.assertEqual(
            stempel_tool.split_drop_files(interpreter, raw_data),
            [
                r"C:\Users\Lena Mustermann\Akte 1.pdf",
                r"D:\Andere Akte\Bericht.pdf",
            ],
        )

    def test_window_is_fixed_and_fits_its_requested_layout(self) -> None:
        root = stempel_tool.TkinterDnD.Tk()
        root.withdraw()
        root.mainloop = lambda: None

        try:
            selected_icons = []
            root.iconbitmap = lambda icon_path: selected_icons.append(icon_path)
            with patch.object(stempel_tool.TkinterDnD, "Tk", return_value=root):
                stempel_tool.create_gui()

            root.update_idletasks()
            width, height = map(int, root.geometry().split("+")[0].split("x"))
            self.assertEqual((width, height), (600, 420))
            self.assertEqual(root.resizable(), (0, 0))
            self.assertLessEqual(root.winfo_reqwidth(), width)
            self.assertLessEqual(root.winfo_reqheight(), height)

            drop_zone = root.winfo_children()[0]
            self.assertEqual(root.logo_image.width(), 104)
            self.assertEqual(drop_zone.cget("highlightbackground"), stempel_tool.UI_BORDER)
            self.assertEqual(len(selected_icons), 1)
            self.assertEqual(Path(selected_icons[0]).name, "stempel_icon.ico")
            self.assertTrue(Path(selected_icons[0]).is_file())
        finally:
            root.destroy()

    def test_successful_stamping_has_no_confirmation(self) -> None:
        successful_result = stempel_tool.FileResult(
            Path("beispiel.pdf"),
            output=Path("beispiel_gestempelt.pdf"),
        )
        with (
            patch.object(
                stempel_tool, "process_files", return_value=[successful_result]
            ),
            patch.object(stempel_tool, "show_results") as show_results,
        ):
            stempel_tool.process_and_report(["beispiel.pdf"], root=object())

        show_results.assert_not_called()

    def test_show_results_does_not_show_a_success_popup(self) -> None:
        successful_result = stempel_tool.FileResult(
            Path("beispiel.pdf"),
            output=Path("beispiel_gestempelt.pdf"),
        )
        with patch.object(stempel_tool.messagebox, "showinfo") as showinfo:
            stempel_tool.show_results([successful_result])

        showinfo.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
