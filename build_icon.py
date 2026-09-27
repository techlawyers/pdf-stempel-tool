from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "stempel_icon_source.png"
OUTPUT = ROOT / "stempel_icon.ico"
PREVIEW = ROOT / "stempel_icon_preview.png"
ICON_SIZE = 256
ICON_SIZES = [16, 24, 32, 48, 64, 128, 256]


def create_icon() -> Image.Image:
    artwork = Image.open(SOURCE).convert("RGBA")

    # Ignore only the nearly invisible outer glow when finding the crop.
    visible = artwork.getchannel("A").point(
        lambda alpha: 255 if alpha > 1 else 0
    )
    bounds = visible.getbbox()
    if bounds is None:
        raise ValueError(f"Das Icon enthält keine sichtbaren Pixel: {SOURCE}")

    margin = 10
    left, top, right, bottom = bounds
    bounds = (
        max(0, left - margin),
        max(0, top - margin),
        min(artwork.width, right + margin),
        min(artwork.height, bottom + margin),
    )
    artwork = artwork.crop(bounds)

    available_size = ICON_SIZE - 20
    scale = min(available_size / artwork.width, available_size / artwork.height)
    resized = artwork.resize(
        (round(artwork.width * scale), round(artwork.height * scale)),
        Image.Resampling.LANCZOS,
    )

    icon = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    position = (
        (ICON_SIZE - resized.width) // 2,
        (ICON_SIZE - resized.height) // 2,
    )
    icon.alpha_composite(resized, position)
    return icon


def main() -> None:
    icon = create_icon()
    icon.save(OUTPUT, format="ICO", sizes=[(size, size) for size in ICON_SIZES])

    preview_size = 512
    preview_background = Image.new(
        "RGBA", (preview_size, preview_size), (244, 246, 250, 255)
    )
    enlarged = icon.resize(
        (preview_size, preview_size), Image.Resampling.LANCZOS
    )
    preview_background.alpha_composite(enlarged)
    preview_background.convert("RGB").save(PREVIEW, format="PNG")
    print(f"Icon gespeichert: {OUTPUT}")
    print(f"Vorschau gespeichert: {PREVIEW}")


if __name__ == "__main__":
    main()
