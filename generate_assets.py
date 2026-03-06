"""
logo.png'den tum uygulama varlıklarini uretir:
  - icon.ico          (6 boyut: 16..256)
  - wizard_main.bmp   (164x314 - Inno Setup sol panel)
  - wizard_small.bmp  (55x58  - Inno Setup sag ust)
  - logo_header.png   (40x40  - dashboard header)
"""
from PIL import Image, ImageDraw
from pathlib import Path

BASE = Path(__file__).parent
SRC  = BASE / "logo.png"

if not SRC.exists():
    print("HATA: logo.png bulunamadi.")
    raise SystemExit(1)

orig = Image.open(SRC).convert("RGBA")
print(f"Logo yuklendi: {orig.size[0]}x{orig.size[1]} {orig.mode}")


# ── Yardimci: belirtilen boyuta seffaf kareye yerles ─────────────────────────
def fit(img: Image.Image, size: int) -> Image.Image:
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    tmp = img.copy()
    tmp.thumbnail((size, size), Image.LANCZOS)
    ox = (size - tmp.width)  // 2
    oy = (size - tmp.height) // 2
    out.paste(tmp, (ox, oy), tmp)
    return out


# ── 1. icon.ico ──────────────────────────────────────────────────────────────
ico_sizes = [16, 32, 48, 64, 128, 256]
frames = [fit(orig, s).convert("RGBA") for s in ico_sizes]

ico_path = BASE / "icon.ico"
# Her boyutu ayri RGBA JPEG degil PNG olarak embed et
frames[0].save(
    str(ico_path),
    format="ICO",
    sizes=[(s, s) for s in ico_sizes],
    append_images=frames[1:],
)
size_kb = ico_path.stat().st_size // 1024
print(f"icon.ico olusturuldu: {size_kb} KB ({len(frames)} boyut)")
if size_kb < 5:
    print("  UYARI: ICO cok kucuk, alternatif yontem deneniyor...")
    # Alternatif: her boyutu ayri kaydet, sonra birlestir
    import struct, io
    def _ico_entry(img):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()
        w, h = img.size
        w8 = w if w < 256 else 0
        h8 = h if h < 256 else 0
        return data, w8, h8

    entries = [_ico_entry(f) for f in frames]
    n = len(entries)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + n * 16
    directory = b""
    image_data = b""
    for data, w, h in entries:
        size = len(data)
        directory += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, size, offset)
        offset += size
        image_data += data
    with open(str(ico_path), "wb") as f:
        f.write(header + directory + image_data)
    size_kb2 = ico_path.stat().st_size // 1024
    print(f"  icon.ico yeniden olusturuldu: {size_kb2} KB")


# ── 2. logo_header.png (40x40 dashboard) ─────────────────────────────────────
fit(orig, 40).save(BASE / "logo_header.png", format="PNG")
print("logo_header.png olusturuldu (40x40)")


# ── 3. wizard_main.bmp (164x314 Inno Setup sol panel) ────────────────────────
W, H = 164, 314
canvas = Image.new("RGB", (W, H), (18, 20, 38))
draw = ImageDraw.Draw(canvas)

# Degrade
for y in range(H):
    t = y / H
    r = int(18  + (35  - 18)  * t)
    g = int(20  + (40  - 20)  * t)
    b = int(38  + (70  - 38)  * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Logo: max 130px genislik, yukarida ortali
logo_w = min(W - 24, 130)
logo_resized = orig.copy()
logo_resized.thumbnail((logo_w, logo_w), Image.LANCZOS)
lx = (W - logo_resized.width)  // 2
ly = 28
canvas.paste(logo_resized, (lx, ly), logo_resized)

# Alt ince cizgi
draw.line([(12, H - 24), (W - 12, H - 24)], fill=(60, 65, 100), width=1)

canvas.save(BASE / "wizard_main.bmp", format="BMP")
print("wizard_main.bmp olusturuldu (164x314)")


# ── 4. wizard_small.bmp (55x58 Inno Setup sag ust) ───────────────────────────
small_canvas = Image.new("RGB", (55, 58), (18, 20, 38))
logo_s = orig.copy()
logo_s.thumbnail((50, 50), Image.LANCZOS)
sx = (55 - logo_s.width)  // 2
sy = (58 - logo_s.height) // 2
small_canvas.paste(logo_s, (sx, sy), logo_s)
small_canvas.save(BASE / "wizard_small.bmp", format="BMP")
print("wizard_small.bmp olusturuldu (55x58)")


print("\nTum varlıklar basariyla olusturuldu.")
