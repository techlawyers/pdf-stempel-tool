from pathlib import Path
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ICON_PATH = ROOT / "stempel_icon.ico"
ICON_SIZES = {(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)}


class IconAssetTests(unittest.TestCase):
    def test_icon_has_all_sizes_and_transparent_corners(self) -> None:
        with Image.open(ICON_PATH) as icon:
            self.assertEqual(icon.ico.sizes(), ICON_SIZES)

            for width, height in sorted(ICON_SIZES):
                frame = icon.ico.getimage((width, height))
                alpha = frame.getchannel("A")
                self.assertEqual(alpha.getextrema()[1], 255)
                self.assertEqual(
                    [
                        alpha.getpixel((0, 0)),
                        alpha.getpixel((width - 1, 0)),
                        alpha.getpixel((0, height - 1)),
                        alpha.getpixel((width - 1, height - 1)),
                    ],
                    [0, 0, 0, 0],
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
