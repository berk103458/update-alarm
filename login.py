"""
OYYA1UPDATE ALARM - Login ekrani
"""
import hashlib
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import sys

from version import APP_NAME

# Kimlik bilgileri (SHA-256 hash)
_USER = "ngtech"
_PASS_HASH = hashlib.sha256("Ngt1071!".encode()).hexdigest()


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class LoginWindow:
    """Modal login penceresi. show() True döndürürse giriş başarılı."""

    BG     = "#1e1e2e"
    BG2    = "#2a2a3e"
    FG     = "#cdd6f4"
    FG2    = "#a6adc8"
    ACCENT = "#89b4fa"
    RED    = "#f38ba8"
    SEP    = "#45475a"

    def __init__(self, root: tk.Tk):
        self.root = root
        self._result = False

        self.win = tk.Toplevel(root)
        self.win.title(APP_NAME)
        self.win.resizable(False, False)
        self.win.configure(bg=self.BG)
        self.win.grab_set()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build()
        self._center()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build(self):
        win = self.win

        # Logo / başlık alanı
        top = tk.Frame(win, bg=self.ACCENT, height=4)
        top.pack(fill="x")

        # Logo resmi (varsa)
        try:
            from PIL import Image, ImageTk
            _logo_path = None
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                _logo_path = Path(sys._MEIPASS) / "logo_header.png"
            else:
                _logo_path = Path(__file__).parent / "logo_header.png"

            if _logo_path and _logo_path.exists():
                img = Image.open(str(_logo_path)).resize((48, 48), Image.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(win, image=self._logo_img, bg=self.BG)
                lbl_logo.pack(pady=(18, 0))
        except Exception:
            pass

        # Başlık
        tk.Label(win, text=APP_NAME, bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(10, 2))
        tk.Label(win, text="Sisteme giriş yapın", bg=self.BG, fg=self.FG2,
                 font=("Segoe UI", 9)).pack(pady=(0, 16))

        # Form çerçevesi
        form = tk.Frame(win, bg=self.BG2, padx=24, pady=20)
        form.pack(padx=32, pady=(0, 8), fill="x")

        tk.Label(form, text="Kullanıcı Adı", bg=self.BG2, fg=self.FG2,
                 font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self._user_var = tk.StringVar()
        user_entry = tk.Entry(form, textvariable=self._user_var, width=24,
                              bg=self.BG, fg=self.FG, insertbackground=self.FG,
                              relief="flat", font=("Segoe UI", 10), bd=1,
                              highlightthickness=1, highlightbackground=self.SEP,
                              highlightcolor=self.ACCENT)
        user_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10), ipady=4)

        tk.Label(form, text="Şifre", bg=self.BG2, fg=self.FG2,
                 font=("Segoe UI", 8)).grid(row=2, column=0, sticky="w", pady=(0, 2))
        self._pass_var = tk.StringVar()
        pass_entry = tk.Entry(form, textvariable=self._pass_var, show="●", width=24,
                              bg=self.BG, fg=self.FG, insertbackground=self.FG,
                              relief="flat", font=("Segoe UI", 10), bd=1,
                              highlightthickness=1, highlightbackground=self.SEP,
                              highlightcolor=self.ACCENT)
        pass_entry.grid(row=3, column=0, sticky="ew", pady=(0, 4), ipady=4)

        form.columnconfigure(0, weight=1)

        # Hata mesajı
        self._err_var = tk.StringVar()
        tk.Label(win, textvariable=self._err_var, bg=self.BG, fg=self.RED,
                 font=("Segoe UI", 8)).pack(pady=(2, 6))

        # Giriş butonu
        btn = tk.Button(win, text="Giriş Yap", command=self._login,
                        bg=self.ACCENT, fg=self.BG, activebackground="#74a8e8",
                        activeforeground=self.BG, relief="flat",
                        font=("Segoe UI", 10, "bold"), cursor="hand2",
                        padx=20, pady=6)
        btn.pack(pady=(0, 24))

        # Enter ile giriş
        user_entry.bind("<Return>", lambda _: pass_entry.focus())
        pass_entry.bind("<Return>", lambda _: self._login())
        user_entry.focus()

    def _center(self):
        self.win.update_idletasks()
        w, h = self.win.winfo_width(), self.win.winfo_height()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.win.geometry(f"{w}x{h}+{x}+{y}")

    # ── Eylemler ──────────────────────────────────────────────────────────────
    def _login(self):
        user = self._user_var.get().strip()
        pwd  = self._pass_var.get()

        if user.lower() == _USER and _hash(pwd) == _PASS_HASH:
            self._result = True
            self.win.destroy()
        else:
            self._err_var.set("Kullanıcı adı veya şifre hatalı.")
            self._pass_var.set("")

    def _on_close(self):
        self._result = False
        self.win.destroy()

    # ── Açma ──────────────────────────────────────────────────────────────────
    def show(self) -> bool:
        """Pencereyi gösterir, True=başarılı giriş, False=iptal/hata."""
        self.root.wait_window(self.win)
        return self._result
