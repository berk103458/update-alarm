"""
OYYA1UPDATE ALARM Desktop App
Sistem tepsisi + gunluk bildirim + dashboard + otomatik guncelleme
"""
import datetime as dt
import json
import sys
import threading
import time
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageDraw
import pystray

import notifier
import updater
from dashboard import DashboardWindow
from reader import load_excel, TR_WEEKDAY_NAMES
from version import APP_NAME, APP_VERSION

# ──────────────── Ayar dosyasi ────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
SETTINGS_FILE = BASE_DIR / "settings.json"

# PyInstaller ile paketlendiginde exe'nin yanindaki klasore bak,
# gelistirme ortaminda ust klasore bak
def _find_default_excel() -> Path:
    # PyInstaller ile paketlenmisse exe icine gomulu Excel'i kullan
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        p = Path(sys._MEIPASS) / "Update Cycle.xlsx"
        if p.exists():
            return p
    # Gelistirme ortami
    for p in [BASE_DIR / "Update Cycle.xlsx", BASE_DIR.parent / "Update Cycle.xlsx"]:
        if p.exists():
            return p
    return BASE_DIR / "Update Cycle.xlsx"

DEFAULT_EXCEL = _find_default_excel()

DEFAULT_SETTINGS: dict = {
    "excel_path":     str(DEFAULT_EXCEL),
    "notify_hour":    9,
    "notify_minute":  0,
    "lead_days":      7,
    "startup_notify": True,
}


def load_settings() -> dict:
    s = DEFAULT_SETTINGS.copy()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                saved.setdefault(k, v)
            s = saved
        except Exception:
            pass

    # Kaydedilmis Excel yolu artik mevcut degilse gomulu Excel'e don
    excel_path = s.get("excel_path", "")
    if not excel_path or not Path(excel_path).exists():
        s["excel_path"] = str(DEFAULT_EXCEL)

    return s


def save_settings(s: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


# ──────────────── Programatik tray ikonu ─────────────────────────────────────
def _make_icon(alert: bool = False) -> Image.Image:
    import math
    sz = 64
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = sz // 2

    # Arka daire
    color = (220, 80, 80) if alert else (33, 150, 243)
    d.ellipse([2, 2, sz - 2, sz - 2], fill=color, outline=(max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40)), width=2)
    d.ellipse([6, 6, sz - 6, sz - 6], fill=(245, 248, 255, 240))

    # Saat akrep / yelkovan
    def hand(deg, frac, width, fill=(30, 40, 90)):
        a = math.radians(deg - 90)
        r = (sz // 2 - 8) * frac
        d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)], fill=fill, width=width)

    hand(300, 0.52, 4)
    hand(0, 0.65, 3)
    r = 4
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # Zil
    bw = sz // 5
    bx1, by1 = cx - bw // 2, sz - 12 - bw // 2
    d.polygon([(bx1, by1 + bw // 2), (bx1 + bw, by1 + bw // 2),
               (bx1 + bw - 4, by1), (bx1 + 4, by1)], fill=(255, 193, 7))
    r2 = 3
    d.ellipse([cx - r2, by1 - r2, cx + r2, by1 + r2], fill=(255, 193, 7))

    # Alert rozeti (kirmizi nokta)
    if alert:
        d.ellipse([sz - 16, 0, sz, 16], fill=(255, 60, 60), outline=(255, 255, 255), width=1)

    return img


# ──────────────── Ana uygulama ────────────────────────────────────────────────
class UpdateAlarmApp:

    def __init__(self):
        self.settings = load_settings()
        self._update_info: dict | None = None
        self._last_notify_day = dt.date(2000, 1, 1)
        self._stop = threading.Event()

        # Tkinter root (gizli – popup/dialog icin parent)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title(APP_NAME)

        # Dashboard
        self.dashboard = DashboardWindow(self.root, self.settings, save_settings)

        # Tray
        self.tray = pystray.Icon(APP_NAME, _make_icon(), APP_NAME, self._build_menu())

    # ── Tray menu ─────────────────────────────────────────────────────────────
    def _build_menu(self) -> pystray.Menu:
        """Her menu acilisinda cagrilir – guncel durumu yansitir."""
        items = [
            pystray.MenuItem("Dashboard Ac",   self._open_dashboard, default=True),
            pystray.MenuItem("Simdi Bildir",   self._do_notify),
            pystray.MenuItem("Excel Yenile",   self._reload_data),
            pystray.Menu.SEPARATOR,
        ]

        if self._update_info:
            ver = self._update_info.get("version", "?")
            items.append(
                pystray.MenuItem(f"Guncelleme Mevcut: v{ver}  --  Indir",
                                 self._open_update_dialog)
            )
        else:
            items.append(pystray.MenuItem("Guncelleme Kontrol Et", self._check_update_manual))

        items += [
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Surum: {APP_VERSION}", None, enabled=False),
            pystray.MenuItem("Cikis", self._quit),
        ]
        return pystray.Menu(*items)

    def _refresh_tray(self, alert: bool = False):
        """Tray ikonu ve menusunu yenile."""
        self.tray.icon = _make_icon(alert=alert)
        self.tray.menu = self._build_menu()

    # ── Tray aksiyonlari ──────────────────────────────────────────────────────
    def _open_dashboard(self, *_):
        self.root.after(0, self.dashboard.show)

    def _do_notify(self, *_):
        threading.Thread(target=self._send_notification, daemon=True).start()

    def _reload_data(self, *_):
        self.root.after(0, self.dashboard.reload)

    def _check_update_manual(self, *_):
        def _run():
            info = updater.check_update()
            if info:
                self._on_update_found(info)
            else:
                notifier.notify(APP_NAME, f"Surum guncel: v{APP_VERSION}")
        threading.Thread(target=_run, daemon=True).start()

    def _open_update_dialog(self, *_):
        if self._update_info:
            self.root.after(0, lambda: updater.UpdateDialog(
                self.root, self._update_info, self._quit
            ))

    def _quit(self, *_):
        self._stop.set()
        self.tray.stop()
        self.root.after(0, self.root.destroy)

    # ── Guncelleme ────────────────────────────────────────────────────────────
    def _on_update_found(self, info: dict):
        self._update_info = info
        self._refresh_tray(alert=True)
        ver = info.get("version", "?")
        notifier.notify(
            f"{APP_NAME} - Guncelleme Mevcut",
            f"Yeni surum hazir: v{ver}\n"
            "Sistem tepsisindeki ikona tiklayin."
        )

    # ── Bildirim icerigi ──────────────────────────────────────────────────────
    def _send_notification(self):
        try:
            data = load_excel(self.settings.get("excel_path", ""))
            if data.error:
                notifier.notify(f"{APP_NAME} - Hata", f"Excel okunamadi:\n{data.error}")
                return

            lead = self.settings.get("lead_days", 7)
            now  = dt.datetime.now()
            cutoff = now + dt.timedelta(days=lead)
            upcoming = [e for e in data.events if now <= e.when <= cutoff]

            today_evs    = [e for e in upcoming if e.when.date() == dt.date.today()]
            tomorrow_evs = [e for e in upcoming if (e.when.date() - dt.date.today()).days == 1]

            if not upcoming:
                notifier.notify(APP_NAME, f"Onumuzdeki {lead} gunde planlanan update yok.")
                return

            cycles_ct  = len(set(e.cycle  for e in upcoming))
            servers_ct = len(set(e.server for e in upcoming))
            ne = min(upcoming, key=lambda x: x.when)

            lines = [
                f"Toplam: {len(upcoming)} event | {cycles_ct} cycle | {servers_ct} sunucu",
            ]
            if today_evs:
                lines.append(f"Bugun: {len(today_evs)} event ({len(set(e.server for e in today_evs))} sunucu)")
            if tomorrow_evs:
                lines.append(f"Yarin: {len(tomorrow_evs)} event ({len(set(e.server for e in tomorrow_evs))} sunucu)")
            lines.append(
                f"Sonraki: {ne.cycle} | "
                f"{TR_WEEKDAY_NAMES[ne.when.weekday()]} {ne.when:%d.%m %H:%M} ({ne.time_remaining})"
            )

            title = f"{APP_NAME} - {len(today_evs)} Bugun, {len(upcoming)} Toplam ({lead}g)"
            notifier.notify(title, "\n".join(lines))

            self.root.after(0, lambda: self.dashboard.refresh_data(data))

        except Exception as ex:
            notifier.notify(f"{APP_NAME} - Hata", str(ex))

    # ── Gunluk zamanlayici ────────────────────────────────────────────────────
    def _scheduler_loop(self):
        # Guncelleme kontrolu: baslangictan 10s sonra
        time.sleep(10)
        updater.check_async(lambda info: self._on_update_found(info) if info else None)

        while not self._stop.is_set():
            time.sleep(30)
            now = dt.datetime.now()
            h   = self.settings.get("notify_hour", 9)
            m   = self.settings.get("notify_minute", 0)

            if now.hour == h and now.minute == m and now.date() != self._last_notify_day:
                self._last_notify_day = now.date()
                self._send_notification()
                # Guncelleme kontrolu gunluk bildirimle birlikte
                updater.check_async(lambda info: self._on_update_found(info) if info else None)

    # ── Calistir ──────────────────────────────────────────────────────────────
    def run(self):
        # Zamanlayici thread
        threading.Thread(target=self._scheduler_loop, daemon=True).start()

        # Acilis bildirimi
        if self.settings.get("startup_notify", True):
            self.root.after(4000, lambda: threading.Thread(
                target=self._send_notification, daemon=True).start()
            )

        # Tray'i ayri thread'de baslat
        threading.Thread(target=self.tray.run, daemon=True).start()

        # Tkinter mainloop – ana thread
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._quit()


# ──────────────── Tek ornek koruması ─────────────────────────────────────────
def _already_running() -> bool:
    try:
        import ctypes
        ctypes.windll.kernel32.CreateMutexW(None, False, "UpdateAlarmApp_Mutex_v1")
        return ctypes.windll.kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
    except Exception:
        return False


if __name__ == "__main__":
    if _already_running():
        root = tk.Tk(); root.withdraw()
        tk.messagebox.showwarning(APP_NAME, "Uygulama zaten calisiyor!\nSistem tepsisine bakin.")
        sys.exit(0)

    UpdateAlarmApp().run()
