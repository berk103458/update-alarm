"""
logo.png'den tum uygulama varlıklarini uretir:
  - icon.ico          (6 boyut: 16..256)
  - wizard_main.bmp   (164x314 - Inno Setup sol panel)
  - wizard_small.bmp  (55x58  - Inno Setup sag ust)
  - logo_header.png   (200x200 - dashboard header)
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

BASE = Path(__file__).parent
SRC  = BASE / "logo.png"

if not SRC.exists():
    print("HATA: logo.png bulunamadi.")
    raise SystemExit(1)

logo = Image.open(SRC).convert("RGBA")
print(f"Logo yuklendi: {logo.size[0]}x{logo.size[1]}")


# ── 1. icon.ico ──────────────────────────────────────────────────────────────
def _make_square(img: Image.Image, size: int) -> Image.Image:
    """Orantili kucult, kare yap, seffaf arka plan."""
    img = img.copy()
    img.thumbnail((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    out.paste(img, offset, img if img.mode == "RGBA" else None)
    return out

ico_sizes = [16, 32, 48, 64, 128, 256]
ico_images = [_make_square(logo, s) for s in ico_sizes]
ico_images[0].save(
    BASE / "icon.ico",
    format="ICO",
    sizes=[(s, s) for s in ico_sizes],
    append_images=ico_images[1:],
)
print("icon.ico olusturuldu")


# ── 2. logo_header.png (dashboard) ───────────────────────────────────────────
header_img = _make_square(logo, 64)
header_img.save(BASE / "logo_header.png", format="PNG")
print("logo_header.png olusturuldu")


# ── 3. wizard_main.bmp (Inno Setup sol panel 164x314) ────────────────────────
def _wizard_main(logo_img: Image.Image, w=164, h=314) -> Image.Image:
    bg_color = (20, 20, 40)          # koyu lacivert arka plan
    accent   = (30, 30, 55)

    out = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(out)

    # Degrade efekt (ustden alta)
    for y in range(h):
        ratio = y / h
        r = int(bg_color[0] + (accent[0] - bg_color[0]) * ratio)
        g = int(bg_color[1] + (accent[1] - bg_color[1]) * ratio)
        b = int(bg_color[2] + (accent[2] - bg_color[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Logo ortaya, ust bolume
    logo_sz = min(w - 20, 120)
    logo_resized = logo_img.copy()
    logo_resized.thumbnail((logo_sz, logo_sz), Image.LANCZOS)
    lx = (w - logo_resized.width) // 2
    ly = 30
    out.paste(logo_resized, (lx, ly), logo_resized)

    # Alt cizgi
    draw.line([(10, h - 30), (w - 10, h - 30)], fill=(80, 80, 120), width=1)

    return out

wiz_main = _wizard_main(logo)
wiz_main.save(BASE / "wizard_main.bmp", format="BMP")
print("wizard_main.bmp olusturuldu")


# ── 4. wizard_small.bmp (Inno Setup sag ust 55x58) ───────────────────────────
wiz_small = logo.copy()
wiz_small.thumbnail((55, 55), Image.LANCZOS)
out_small = Image.new("RGBA", (55, 58), (20, 20, 40, 255))
offset = ((55 - wiz_small.width) // 2, (58 - wiz_small.height) // 2)
out_small.paste(wiz_small, offset, wiz_small)
out_small.convert("RGB").save(BASE / "wizard_small.bmp", format="BMP")
print("wizard_small.bmp olusturuldu")


print("\nTum varlıklar basariyla olusturuldu.")
