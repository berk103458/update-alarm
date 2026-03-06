"""
UpdateAlarm - Online guncelleme modulu
GitHub latest.json -> versiyon karsilastir -> indir -> kur
"""
import json
import os
import subprocess
import tempfile
import threading
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import ttk
from typing import Callable, Optional

from version import APP_NAME, APP_VERSION, UPDATE_CHECK_URL


# ──────────────── Versiyon karsilastirma ──────────────────────────────────────
def _vtuple(v: str):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except Exception:
        return (0, 0, 0)


def check_update() -> Optional[dict]:
    """
    Returns:
        dict with {version, download_url, changelog} if update available.
        None if up-to-date or check failed.
    """
    if "YOUR_USERNAME" in UPDATE_CHECK_URL:
        return None  # henuz yapilandirilmamis
    try:
        req = urllib.request.Request(
            UPDATE_CHECK_URL,
            headers={"User-Agent": f"UpdateAlarm/{APP_VERSION}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if _vtuple(data.get("version", "0")) > _vtuple(APP_VERSION):
            return data
    except Exception:
        pass
    return None


# ──────────────── Guncelleme diyalogu ────────────────────────────────────────
def _bg_color(): return "#1e1e2e"
def _fg():       return "#cdd6f4"
def _accent():   return "#89b4fa"
def _green():    return "#a6e3a1"
def _sep():      return "#45475a"


class UpdateDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, info: dict, on_confirm: Callable):
        super().__init__(parent)
        self.title("Guncelleme Mevcut")
        self.configure(bg=_bg_color())
        self.geometry("480x320")
        self.resizable(False, False)
        self.grab_set()

        self._info = info
        self._on_confirm = on_confirm
        self._progress_var = tk.DoubleVar(value=0)
        self._status_var = tk.StringVar(value="")
        self._downloading = False

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build(self):
        pad = dict(padx=20, pady=6)

        tk.Label(self, text="Yeni Surum Mevcut!", bg=_bg_color(),
                 fg=_accent(), font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", padx=20, pady=(18, 4))

        ver_frame = tk.Frame(self, bg=_bg_color()); ver_frame.pack(fill="x", **pad)
        tk.Label(ver_frame, text=f"Mevcut:  {APP_VERSION}", bg=_bg_color(), fg="#888", font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(ver_frame, text=f"Yeni:       {self._info.get('version', '?')}",
                 bg=_bg_color(), fg=_green(), font=("Segoe UI", 10, "bold")).pack(anchor="w")

        tk.Frame(self, bg=_sep(), height=1).pack(fill="x", padx=20, pady=6)

        clog = self._info.get("changelog", "")
        if clog:
            tk.Label(self, text="Degisiklikler:", bg=_bg_color(), fg="#aaa", font=("Segoe UI", 8)).pack(anchor="w", padx=20)
            txt = tk.Text(self, height=4, bg="#2a2a3e", fg=_fg(),
                          font=("Segoe UI", 9), borderwidth=0, highlightthickness=0, wrap="word")
            txt.pack(fill="x", padx=20, pady=(2, 8))
            txt.insert("1.0", clog)
            txt.configure(state="disabled")

        self._progress_bar = ttk.Progressbar(self, variable=self._progress_var, maximum=100, length=440)
        self._progress_bar.pack(padx=20, pady=(0, 4))
        self._progress_bar.pack_forget()

        tk.Label(self, textvariable=self._status_var, bg=_bg_color(),
                 fg="#aaa", font=("Segoe UI", 8)).pack(anchor="w", padx=20)

        btn_frame = tk.Frame(self, bg=_bg_color()); btn_frame.pack(pady=(8, 18))
        self._update_btn = tk.Button(btn_frame, text="Simdi Guncelle", bg=_accent(), fg=_bg_color(),
                                     font=("Segoe UI", 10, "bold"), padx=18, pady=6,
                                     relief="flat", cursor="hand2", command=self._start_download)
        self._update_btn.pack(side="left", padx=(0, 10))
        tk.Button(btn_frame, text="Sonra Hatirlatma", bg="#313145", fg=_fg(),
                  font=("Segoe UI", 9), padx=12, pady=6, relief="flat",
                  command=self.destroy).pack(side="left")

    def _start_download(self):
        if self._downloading:
            return
        self._downloading = True
        self._update_btn.configure(state="disabled", text="Indiriliyor...")
        self._progress_bar.pack(padx=20, pady=(0, 4))
        url = self._info.get("download_url", "")
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url: str):
        try:
            self._status_var.set("Baglaniyor...")
            suffix = Path(url).suffix or ".exe"
            tmp = tempfile.mktemp(suffix=suffix, prefix="UpdateAlarm_Setup_")

            def hook(count, block, total):
                if total > 0:
                    pct = min(100, count * block * 100 / total)
                    self._progress_var.set(pct)
                    mb_done = count * block / 1_048_576
                    mb_total = total / 1_048_576
                    self._status_var.set(f"Indiriliyor... {mb_done:.1f} / {mb_total:.1f} MB")

            urllib.request.urlretrieve(url, tmp, hook)
            self._status_var.set("Yukleniyor...")
            self._progress_var.set(100)
            self.after(500, lambda: self._run_installer(tmp))

        except Exception as ex:
            self._status_var.set(f"Hata: {ex}")
            self._update_btn.configure(state="normal", text="Tekrar Dene")
            self._downloading = False

    def _run_installer(self, path: str):
        self._on_confirm()  # ana uygulamanin kapanmasi icin callback
        subprocess.Popen(
            [path, "/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self.destroy()

    def _on_close(self):
        if not self._downloading:
            self.destroy()


# ──────────────── Arka planda kontrol ─────────────────────────────────────────
def check_async(callback: Callable[[Optional[dict]], None]):
    """Arka planda guncelleme kontrolu. callback(info_dict | None) ile sonuc bildirir."""
    def _run():
        result = check_update()
        callback(result)
    threading.Thread(target=_run, daemon=True).start()
