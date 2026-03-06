"""
Cok cozunurluklu icon.ico olusturur.
Build oncesinde calistirilmali: python create_icon.py
"""
from PIL import Image, ImageDraw


def _draw(size: int) -> Image.Image:
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    m = max(1, s // 32)          # kenar payı

    # Arka plan daire – mavi degrade etkisi icin iki katman
    d.ellipse([m, m, s - m, s - m], fill=(33, 150, 243))
    d.ellipse([m + 2, m + 2, s - m - 2, s - m - 2], fill=(50, 160, 250))

    # Saat yuzu
    pad = s // 6
    d.ellipse([pad, pad, s - pad, s - pad], fill=(245, 248, 255), outline=(200, 210, 230), width=max(1, m))

    cx, cy = s // 2, s // 2

    # Saat 10:00 – akrep
    import math
    def hand(angle_deg, length_frac, width):
        angle = math.radians(angle_deg - 90)
        r = (s // 2 - pad) * length_frac
        x2 = cx + r * math.cos(angle)
        y2 = cy + r * math.sin(angle)
        d.line([cx, cy, x2, y2], fill=(30, 40, 90), width=max(1, width))

    hand(300, 0.52, max(2, m * 2))   # akrep
    hand(0,   0.65, max(1, m + 1))   # yelkovan

    # Merkez
    r = max(2, s // 16)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(33, 150, 243))

    # Zil (alt)
    bw = s // 5
    bx1, by1 = cx - bw // 2, s - pad - bw // 2
    bx2, by2 = bx1 + bw, by1 + bw * 3 // 4
    d.polygon([
        (bx1, by2), (bx2, by2),
        (bx2 - bw // 6, by1), (bx1 + bw // 6, by1)
    ], fill=(255, 193, 7))
    # zil top
    r2 = max(1, bw // 5)
    d.ellipse([cx - r2, by1 - r2, cx + r2, by1 + r2], fill=(255, 193, 7))

    return img


def create_ico(out_path: str = "icon.ico"):
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [_draw(s) for s in sizes]
    images[0].save(
        out_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )
    print(f"Ikon olusturuldu: {out_path}")


if __name__ == "__main__":
    create_ico()
