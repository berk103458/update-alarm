"""
UpdateAlarm - Ana dashboard penceresi
Sekmeler: Yaklasan | Cycle'lar | Istatistik | Ayarlar
"""
import datetime as dt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Dict, List, Optional

from reader import AppData, CycleGroup, UpdateEvent, TR_WEEKDAY_NAMES

# ──────────────── Renkler ────────────────────────────────────────────────────
BG         = "#1e1e2e"
BG2        = "#2a2a3e"
BG3        = "#313145"
FG         = "#cdd6f4"
FG2        = "#a6adc8"
ACCENT     = "#89b4fa"
RED        = "#f38ba8"
ORANGE     = "#fab387"
YELLOW     = "#f9e2af"
GREEN      = "#a6e3a1"
TEAL       = "#94e2d5"
PURPLE     = "#cba6f7"
SEP        = "#45475a"

URGENCY_COLORS = {
    "today":  RED,
    "soon":   ORANGE,
    "week":   YELLOW,
    "month":  GREEN,
    "future": FG2,
    "past":   SEP,
}

URGENCY_LABELS = {
    "today":  "BUGUN",
    "soon":   "YARIN/OBURGÜN",
    "week":   "BU HAFTA",
    "month":  "BU AY",
    "future": "GELECEK",
    "past":   "GECTI",
}

# ──────────────── Yardimci fonksiyonlar ──────────────────────────────────────
def _style(root: tk.Tk):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".",              background=BG,  foreground=FG,   font=("Segoe UI", 9))
    style.configure("TFrame",        background=BG)
    style.configure("TLabelframe",   background=BG,  foreground=ACCENT)
    style.configure("TLabelframe.Label", background=BG, foreground=ACCENT, font=("Segoe UI", 9, "bold"))
    style.configure("TNotebook",     background=BG2, borderwidth=0)
    style.configure("TNotebook.Tab", background=BG2, foreground=FG2,   padding=[14, 6], font=("Segoe UI", 9))
    style.map("TNotebook.Tab",       background=[("selected", BG3)],   foreground=[("selected", ACCENT)])
    style.configure("TScrollbar",    background=BG3, troughcolor=BG2,  arrowcolor=FG2)
    style.configure("Treeview",      background=BG2, foreground=FG,    fieldbackground=BG2,
                    rowheight=22, borderwidth=0, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background=BG3, foreground=ACCENT,
                    font=("Segoe UI", 9, "bold"), borderwidth=0)
    style.map("Treeview",            background=[("selected", ACCENT)], foreground=[("selected", BG)])
    style.configure("TEntry",        fieldbackground=BG3, foreground=FG, insertcolor=FG, borderwidth=0)
    style.configure("TCombobox",     fieldbackground=BG3, foreground=FG, selectbackground=ACCENT)
    style.configure("TButton",       background=BG3, foreground=FG,    padding=[10, 5], borderwidth=0)
    style.map("TButton",             background=[("active", ACCENT)],  foreground=[("active", BG)])
    style.configure("Accent.TButton",background=ACCENT, foreground=BG, font=("Segoe UI", 9, "bold"), padding=[10,5])
    style.map("Accent.TButton",      background=[("active", PURPLE)])
    style.configure("TSeparator",    background=SEP)
    style.configure("TLabel",        background=BG, foreground=FG)
    style.configure("Header.TLabel", background=BG, foreground=ACCENT, font=("Segoe UI", 14, "bold"))
    style.configure("Sub.TLabel",    background=BG, foreground=FG2,   font=("Segoe UI", 9))
    style.configure("Stat.TLabel",   background=BG2, foreground=FG,   font=("Segoe UI", 11, "bold"), padding=8)
    style.configure("StatTitle.TLabel", background=BG2, foreground=FG2, font=("Segoe UI", 8), padding=[8,2])


def _scrolled_tree(parent, columns, headings, weights, height=18):
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    for col, head, w in zip(columns, headings, weights):
        tree.heading(col, text=head, command=lambda c=col: _sort_tree(tree, c, False))
        tree.column(col, width=w, minwidth=40, anchor="w")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    tree.grid(row=0, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return frame, tree


def _sort_tree(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    data.sort(reverse=reverse)
    for i, (_, k) in enumerate(data):
        tree.move(k, "", i)
    tree.heading(col, command=lambda: _sort_tree(tree, col, not reverse))


# ──────────────── Detail popup ───────────────────────────────────────────────
def _show_detail(parent, events: List[UpdateEvent], cycle: CycleGroup):
    win = tk.Toplevel(parent)
    win.title("Update Detayi")
    win.configure(bg=BG)
    win.geometry("640x520")
    win.resizable(True, True)

    pad = {"padx": 14, "pady": 4}

    def lbl(frame, text, fg=FG, font=("Segoe UI", 9), **kw):
        tk.Label(frame, text=text, bg=BG, fg=fg, font=font, anchor="w", justify="left", **kw).pack(fill="x", **pad)

    if not events:
        lbl(win, "Veri yok.")
        return

    e = events[0]
    tk.Label(win, text=e.cycle, bg=BG, fg=ACCENT, font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", padx=14, pady=(14, 2))

    info = ttk.Frame(win); info.pack(fill="x", padx=14, pady=6)

    def row(label, value, color=FG):
        r = ttk.Frame(info); r.pack(fill="x", pady=1)
        tk.Label(r, text=f"{label:<18}", bg=BG, fg=FG2, font=("Segoe UI", 9), width=18, anchor="w").pack(side="left")
        tk.Label(r, text=value, bg=BG, fg=color, font=("Segoe UI", 9, "bold"), anchor="w").pack(side="left")

    row("Tarih", f"{TR_WEEKDAY_NAMES[e.when.weekday()]}  {e.when:%d.%m.%Y}", YELLOW)
    row("Saat Penceresi", e.window, TEAL)
    row("Kural", e.rule)
    row("Kalan Sure", e.time_remaining, ORANGE)
    row("Urgency", URGENCY_LABELS.get(e.urgency, ""), URGENCY_COLORS.get(e.urgency, FG))

    ttk.Separator(win, orient="horizontal").pack(fill="x", padx=14, pady=6)

    # Sunucular
    srv_frame = ttk.LabelFrame(win, text=f"  Sunucular ({len(events)} adet)  ")
    srv_frame.pack(fill="both", expand=True, padx=14, pady=(0, 6))
    srv_box = tk.Listbox(srv_frame, bg=BG2, fg=FG, selectbackground=ACCENT, font=("Consolas", 9),
                         borderwidth=0, highlightthickness=0)
    srv_sb = ttk.Scrollbar(srv_frame, command=srv_box.yview)
    srv_box.configure(yscrollcommand=srv_sb.set)
    srv_sb.pack(side="right", fill="y")
    srv_box.pack(fill="both", expand=True, padx=4, pady=4)
    for ev in sorted(events, key=lambda x: x.server.lower()):
        srv_box.insert("end", ev.server)

    # Mail
    mail_frame = ttk.Frame(win); mail_frame.pack(fill="x", padx=14, pady=(0, 14))

    def mail_section(parent, title, mails, color):
        f = ttk.LabelFrame(parent, text=f"  {title}  ")
        f.pack(side="left", fill="both", expand=True, padx=(0, 6))
        lb = tk.Listbox(f, bg=BG2, fg=color, font=("Segoe UI", 8),
                        borderwidth=0, highlightthickness=0, height=4)
        lb.pack(fill="both", expand=True, padx=4, pady=4)
        for m in mails:
            lb.insert("end", m)
        if not mails:
            lb.insert("end", "(bos)")

    mail_section(mail_frame, "Oncesi Mail", e.pre_mails, GREEN)
    mail_section(mail_frame, "Sonrasi Mail", e.post_mails, ORANGE)

    ttk.Button(win, text="Kapat", command=win.destroy, style="Accent.TButton").pack(pady=(0, 12))


# ──────────────── Dashboard penceresi ────────────────────────────────────────
class DashboardWindow:
    def __init__(self, root: tk.Tk, settings: dict, save_fn: Callable):
        self.root = root
        self.settings = settings
        self.save_fn = save_fn
        self.data: Optional[AppData] = None
        self._filter_after: Optional[str] = None

        self.win = tk.Toplevel(root)
        self.win.title("OYYA1UPDATE ALARM - Dashboard")
        self.win.configure(bg=BG)
        self.win.geometry("1100x680")
        self.win.resizable(True, True)
        self.win.protocol("WM_DELETE_WINDOW", self.hide)

        _style(root)
        self._build_ui()
        self.win.withdraw()

    # ── Gorunurluk ────────────────────────────────────────────────────────────
    def show(self):
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()
        if self.data is None:
            self.reload()

    def hide(self):
        self.win.withdraw()

    # ── Veri yukleme ──────────────────────────────────────────────────────────
    def reload(self):
        from reader import load_excel
        path = self.settings.get("excel_path", "")
        self.data = load_excel(path)
        self._refresh_all()

    def refresh_data(self, data: AppData):
        self.data = data
        self._refresh_all()

    def _refresh_all(self):
        if not self.data:
            return
        if self.data.error:
            self._status_var.set(f"HATA: {self.data.error}")
        else:
            self._status_var.set(
                f"Yuklendi: {self.data.load_time:%H:%M:%S}  |  "
                f"{len(self.data.events)} event  |  {len(self.data.cycles)} cycle  |  "
                f"Kaynak: {self.data.source_file}"
            )
        self._populate_upcoming()
        self._populate_cycles()
        self._populate_stats()

    # ── UI insasi ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Baslik + durum cubugu
        top = ttk.Frame(self.win); top.pack(fill="x", padx=16, pady=(12, 4))

        # Logo (varsa goster)
        try:
            from PIL import Image, ImageTk
            from pathlib import Path
            logo_path = Path(__file__).parent / "logo_header.png"
            if logo_path.exists():
                _logo_img = Image.open(logo_path).resize((40, 40), Image.LANCZOS)
                self._logo_tk = ImageTk.PhotoImage(_logo_img)
                tk.Label(top, image=self._logo_tk, bg=BG).pack(side="left", padx=(0, 8))
        except Exception:
            pass

        ttk.Label(top, text="OYYA1UPDATE ALARM", style="Header.TLabel").pack(side="left")
        ttk.Button(top, text="Yenile", command=self.reload, style="Accent.TButton").pack(side="right", padx=(6, 0))
        ttk.Button(top, text="Excel Degistir", command=self._browse_excel).pack(side="right")

        self._status_var = tk.StringVar(value="Bekleniyor...")
        ttk.Label(self.win, textvariable=self._status_var, style="Sub.TLabel").pack(fill="x", padx=16, pady=(0, 6))

        ttk.Separator(self.win, orient="horizontal").pack(fill="x", padx=0)

        # Notebook
        self.nb = ttk.Notebook(self.win)
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._tab_upcoming = ttk.Frame(self.nb)
        self._tab_cycles   = ttk.Frame(self.nb)
        self._tab_stats    = ttk.Frame(self.nb)
        self._tab_settings = ttk.Frame(self.nb)

        self.nb.add(self._tab_upcoming, text="  Yaklasan Updateler  ")
        self.nb.add(self._tab_cycles,   text="  Cycle'lar  ")
        self.nb.add(self._tab_stats,    text="  Istatistik  ")
        self.nb.add(self._tab_settings, text="  Ayarlar  ")

        self._build_upcoming_tab(self._tab_upcoming)
        self._build_cycles_tab(self._tab_cycles)
        self._build_stats_tab(self._tab_stats)
        self._build_settings_tab(self._tab_settings)

    # ── Tab 1: Yaklasan ────────────────────────────────────────────────────────
    def _build_upcoming_tab(self, parent):
        # Filtre satiri
        fbar = ttk.Frame(parent); fbar.pack(fill="x", padx=10, pady=8)

        ttk.Label(fbar, text="Arama:").pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._schedule_filter())
        ttk.Entry(fbar, textvariable=self._search_var, width=22).pack(side="left", padx=(0, 12))

        ttk.Label(fbar, text="Cycle:").pack(side="left", padx=(0, 4))
        self._cycle_filter = tk.StringVar(value="Tumu")
        self._cycle_combo = ttk.Combobox(fbar, textvariable=self._cycle_filter, width=28, state="readonly")
        self._cycle_combo.pack(side="left", padx=(0, 12))
        self._cycle_combo.bind("<<ComboboxSelected>>", lambda *_: self._populate_upcoming())

        ttk.Label(fbar, text="Sure:").pack(side="left", padx=(0, 4))
        self._range_filter = tk.StringVar(value="30 Gun")
        ttk.Combobox(fbar, textvariable=self._range_filter, width=12, state="readonly",
                     values=["7 Gun", "14 Gun", "30 Gun", "90 Gun", "365 Gun", "Tumu"]).pack(side="left", padx=(0, 12))
        self._range_filter.trace_add("write", lambda *_: self._populate_upcoming())

        ttk.Label(fbar, text="Urgency:").pack(side="left", padx=(0, 4))
        self._urg_filter = tk.StringVar(value="Tumu")
        ttk.Combobox(fbar, textvariable=self._urg_filter, width=14, state="readonly",
                     values=["Tumu", "BUGUN", "YARIN/OBURGÜN", "BU HAFTA", "BU AY", "GELECEK"]).pack(side="left")

        self._urg_filter.trace_add("write", lambda *_: self._populate_upcoming())

        # Ozet etiketleri
        sumf = ttk.Frame(parent); sumf.pack(fill="x", padx=10, pady=(0, 4))
        self._sum_vars = {}
        for key, label, color in [
            ("today", "Bugun", RED), ("week", "Bu Hafta", YELLOW), ("month", "Bu Ay", GREEN), ("total", "Toplam", TEAL)
        ]:
            f = tk.Frame(sumf, bg=BG2, padx=10, pady=6); f.pack(side="left", padx=(0, 8))
            tk.Label(f, text=label, bg=BG2, fg=FG2, font=("Segoe UI", 8)).pack()
            var = tk.StringVar(value="0")
            self._sum_vars[key] = var
            tk.Label(f, textvariable=var, bg=BG2, fg=color, font=("Segoe UI", 14, "bold")).pack()

        # Treeview
        cols = ("kalan", "tarih", "gun", "saat", "cycle", "sunucu", "kural")
        heads = ("Kalan", "Tarih", "Gun", "Saat Penceresi", "Cycle", "Sunucu", "Kural")
        widths = (80, 90, 90, 110, 200, 150, 260)
        frame, self._upcoming_tree = _scrolled_tree(parent, cols, heads, widths)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for urg, color in URGENCY_COLORS.items():
            self._upcoming_tree.tag_configure(urg, foreground=color)

        self._upcoming_tree.bind("<Double-1>", self._on_upcoming_dbl)
        self._upcoming_tree.bind("<Return>",   self._on_upcoming_dbl)

    def _schedule_filter(self):
        if self._filter_after:
            self.win.after_cancel(self._filter_after)
        self._filter_after = self.win.after(300, self._populate_upcoming)

    def _populate_upcoming(self):
        if not self.data:
            return
        tree = self._upcoming_tree
        tree.delete(*tree.get_children())

        search = self._search_var.get().lower().strip()
        cycle_f = self._cycle_filter.get()
        range_f = self._range_filter.get()
        urg_f = self._urg_filter.get()

        # Zaman siniri
        now = dt.datetime.now()
        range_map = {"7 Gun": 7, "14 Gun": 14, "30 Gun": 30, "90 Gun": 90, "365 Gun": 365, "Tumu": 9999}
        days = range_map.get(range_f, 30)
        cutoff = now + dt.timedelta(days=days)

        # Cycle combo guncelle
        cycle_names = sorted(set(e.cycle for e in self.data.events))
        self._cycle_combo["values"] = ["Tumu"] + cycle_names
        if cycle_f not in ["Tumu"] + cycle_names:
            self._cycle_filter.set("Tumu")
            cycle_f = "Tumu"

        urg_reverse = {v: k for k, v in URGENCY_LABELS.items()}
        urg_key = urg_reverse.get(urg_f)

        count = today_cnt = week_cnt = month_cnt = 0
        for e in self.data.events:
            if e.when > cutoff or e.when < now:
                continue
            if cycle_f != "Tumu" and e.cycle != cycle_f:
                continue
            if urg_key and e.urgency != urg_key:
                continue
            if search and search not in e.server.lower() and search not in e.cycle.lower() and search not in e.rule.lower():
                continue

            count += 1
            delta = (e.when.date() - dt.date.today()).days
            if delta == 0: today_cnt += 1
            if delta <= 7: week_cnt += 1
            if delta <= 30: month_cnt += 1

            tree.insert("", "end", tags=(e.urgency,), values=(
                e.time_remaining,
                e.when.strftime("%d.%m.%Y"),
                e.day_tr,
                e.window,
                e.cycle,
                e.server,
                e.rule,
            ))

        self._sum_vars["today"].set(str(today_cnt))
        self._sum_vars["week"].set(str(week_cnt))
        self._sum_vars["month"].set(str(month_cnt))
        self._sum_vars["total"].set(str(count))

    def _on_upcoming_dbl(self, _event=None):
        sel = self._upcoming_tree.selection()
        if not sel or not self.data:
            return
        vals = self._upcoming_tree.item(sel[0], "values")
        target_cycle = vals[4]
        target_date  = vals[1]
        target_win   = vals[3]
        related = [
            e for e in self.data.events
            if e.cycle == target_cycle
            and e.when.strftime("%d.%m.%Y") == target_date
            and e.window == target_win
        ]
        cg = next((c for c in self.data.cycles if c.name == target_cycle), None)
        if cg:
            _show_detail(self.win, related, cg)

    # ── Tab 2: Cycle'lar ───────────────────────────────────────────────────────
    def _build_cycles_tab(self, parent):
        # Usteki treeview: cycle listesi
        top = ttk.Frame(parent); top.pack(fill="both", expand=True, padx=10, pady=10)

        lf = ttk.LabelFrame(top, text="  Cycle Listesi  ")
        lf.pack(side="left", fill="both", expand=True, padx=(0, 6))

        cols = ("num", "name", "sunucular", "kural", "sonraki", "kalan")
        heads = ("#", "Cycle Adi", "Sunucu", "Kural", "Sonraki Update", "Kalan")
        widths = (35, 200, 60, 220, 140, 80)
        cf, self._cycles_tree = _scrolled_tree(lf, cols, heads, widths, height=22)
        cf.pack(fill="both", expand=True, padx=4, pady=4)
        self._cycles_tree.bind("<<TreeviewSelect>>", self._on_cycle_select)

        # Sagdaki detay paneli
        rf = ttk.LabelFrame(top, text="  Cycle Detayi  "); rf.pack(side="right", fill="both", padx=(0, 0))
        self._cycle_detail_text = tk.Text(
            rf, width=36, bg=BG2, fg=FG, font=("Segoe UI", 9),
            borderwidth=0, highlightthickness=0, wrap="word", state="disabled"
        )
        sb = ttk.Scrollbar(rf, command=self._cycle_detail_text.yview)
        self._cycle_detail_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._cycle_detail_text.pack(fill="both", expand=True, padx=4, pady=4)

    def _populate_cycles(self):
        if not self.data:
            return
        tree = self._cycles_tree
        tree.delete(*tree.get_children())
        for cg in self.data.cycles:
            ne = cg.next_event
            sonraki = f"{TR_WEEKDAY_NAMES[ne.when.weekday()]} {ne.when:%d.%m.%Y %H:%M}" if ne else "-"
            kalan   = ne.time_remaining if ne else "-"
            tree.insert("", "end", iid=cg.name, values=(
                cg.num or "-",
                cg.name,
                cg.server_count,
                "; ".join(cg.rules)[:60],
                sonraki,
                kalan,
            ))

    def _on_cycle_select(self, _event=None):
        sel = self._cycles_tree.selection()
        if not sel or not self.data:
            return
        cname = sel[0]
        cg = next((c for c in self.data.cycles if c.name == cname), None)
        if not cg:
            return

        txt = self._cycle_detail_text
        txt.configure(state="normal")
        txt.delete("1.0", "end")

        def line(text, tag=None):
            if tag:
                txt.insert("end", text + "\n", tag)
            else:
                txt.insert("end", text + "\n")

        txt.tag_configure("h", foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        txt.tag_configure("k", foreground=FG2, font=("Segoe UI", 8))
        txt.tag_configure("v", foreground=FG)
        txt.tag_configure("srv", foreground=TEAL, font=("Consolas", 9))
        txt.tag_configure("mail_pre", foreground=GREEN, font=("Segoe UI", 8))
        txt.tag_configure("mail_post", foreground=ORANGE, font=("Segoe UI", 8))

        line(cg.name, "h")
        line("")

        ne = cg.next_event
        if ne:
            line("Sonraki Update", "k")
            line(f"  {TR_WEEKDAY_NAMES[ne.when.weekday()]} {ne.when:%d.%m.%Y %H:%M}  ({ne.time_remaining})", "v")
            line(f"  Pencere: {ne.window}", "v")
            line("")

        line("Kurallar", "k")
        for r in cg.rules:
            line(f"  {r}", "v")
        line("")

        line(f"Sunucular ({cg.server_count} adet)", "k")
        for s in sorted(cg.servers):
            line(f"  {s}", "srv")
        line("")

        line("Oncesi Mail (Pre)", "k")
        for m in cg.pre_mails:
            line(f"  {m}", "mail_pre")
        if not cg.pre_mails:
            line("  (bos)", "k")
        line("")

        line("Sonrasi Mail (Post)", "k")
        for m in cg.post_mails:
            line(f"  {m}", "mail_post")
        if not cg.post_mails:
            line("  (bos)", "k")

        line("")
        # Gelecek eventler
        now = dt.datetime.now()
        fut_events = sorted([e for e in cg.events if e.when >= now], key=lambda x: x.when)[:10]
        if fut_events:
            line(f"Gelecek {len(fut_events)} Event", "k")
            for ev in fut_events:
                line(f"  {ev.when:%d.%m.%Y %H:%M}  {ev.server}", "v")

        txt.configure(state="disabled")

    # ── Tab 3: Istatistik ──────────────────────────────────────────────────────
    def _build_stats_tab(self, parent):
        self._stats_frame = ttk.Frame(parent)
        self._stats_frame.pack(fill="both", expand=True, padx=14, pady=14)

    def _populate_stats(self):
        if not self.data:
            return
        for w in self._stats_frame.winfo_children():
            w.destroy()

        d = self.data
        now = dt.datetime.now()
        today_evs = d.upcoming_today
        week_evs  = d.upcoming_week
        month_evs = d.upcoming_month

        # Istatistik kartlari
        card_frame = ttk.Frame(self._stats_frame)
        card_frame.pack(fill="x", pady=(0, 14))

        def stat_card(parent, title, value, color=TEAL, sub=""):
            f = tk.Frame(parent, bg=BG2, padx=16, pady=10); f.pack(side="left", padx=(0, 10))
            tk.Label(f, text=title, bg=BG2, fg=FG2, font=("Segoe UI", 8)).pack(anchor="w")
            tk.Label(f, text=str(value), bg=BG2, fg=color, font=("Segoe UI", 20, "bold")).pack(anchor="w")
            if sub:
                tk.Label(f, text=sub, bg=BG2, fg=FG2, font=("Segoe UI", 8)).pack(anchor="w")

        stat_card(card_frame, "Toplam Cycle",       len(d.cycles), PURPLE)
        stat_card(card_frame, "Toplam Sunucu",       len(set(e.server for e in d.events)), ACCENT)
        stat_card(card_frame, "Bugun Update",        len(today_evs), RED, f"{len(set(e.server for e in today_evs))} sunucu")
        stat_card(card_frame, "Bu Hafta Update",     len(week_evs),  YELLOW, f"{len(set(e.server for e in week_evs))} sunucu")
        stat_card(card_frame, "Bu Ay Update",        len(month_evs), GREEN, f"{len(set(e.server for e in month_evs))} sunucu")
        stat_card(card_frame, "Toplam Event (365g)", len(d.events), TEAL)

        # Sonraki update
        ne_frame = ttk.LabelFrame(self._stats_frame, text="  Sonraki Update  ")
        ne_frame.pack(fill="x", pady=(0, 14))
        next_ev = min((e for e in d.events if e.when >= now), key=lambda x: x.when, default=None)
        if next_ev:
            txt = (f"{next_ev.cycle}   |   "
                   f"{TR_WEEKDAY_NAMES[next_ev.when.weekday()]} {next_ev.when:%d.%m.%Y %H:%M}   |   "
                   f"Pencere: {next_ev.window}   |   "
                   f"Kalan: {next_ev.time_remaining}")
            tk.Label(ne_frame, text=txt, bg=BG, fg=YELLOW, font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=10, pady=8)
        else:
            tk.Label(ne_frame, text="Planlanan event bulunamadi.", bg=BG, fg=FG2).pack(padx=10, pady=8)

        # Cycle ozeti tablosu
        tbl_frame = ttk.LabelFrame(self._stats_frame, text="  Cycle Ozeti  ")
        tbl_frame.pack(fill="both", expand=True)

        cols = ("num", "cycle", "sunucu", "bugun", "hafta", "ay", "toplam", "sonraki")
        heads = ("#", "Cycle Adi", "Sunucu", "Bugun", "Hafta", "Ay", "Toplam", "Sonraki Update")
        widths = (35, 210, 60, 60, 60, 60, 70, 160)
        cf, stree = _scrolled_tree(tbl_frame, cols, heads, widths, height=14)
        cf.pack(fill="both", expand=True, padx=4, pady=4)

        cycle_evs: Dict[str, List[UpdateEvent]] = {}
        for e in d.events:
            cycle_evs.setdefault(e.cycle, []).append(e)

        for cg in d.cycles:
            evs = cycle_evs.get(cg.name, [])
            bugun  = sum(1 for e in evs if e.when.date() == dt.date.today() and e.when >= now)
            hafta  = sum(1 for e in evs if now <= e.when <= now + dt.timedelta(days=7))
            ay     = sum(1 for e in evs if now <= e.when <= now + dt.timedelta(days=30))
            toplam = len(evs)
            ne_ev  = cg.next_event
            sonraki = f"{ne_ev.when:%d.%m.%Y %H:%M}" if ne_ev else "-"
            stree.insert("", "end", values=(
                cg.num or "-", cg.name, cg.server_count,
                bugun or "-", hafta or "-", ay or "-", toplam, sonraki
            ))

    # ── Tab 4: Ayarlar ─────────────────────────────────────────────────────────
    def _build_settings_tab(self, parent):
        pad = {"padx": 14, "pady": 6}

        ttk.Label(parent, text="Uygulama Ayarlari", style="Header.TLabel").pack(anchor="w", padx=14, pady=(14, 8))

        # Excel dosyasi
        ef = ttk.LabelFrame(parent, text="  Excel Dosyasi  "); ef.pack(fill="x", padx=14, pady=(0, 10))
        er = ttk.Frame(ef); er.pack(fill="x", **pad)
        self._excel_path_var = tk.StringVar(value=self.settings.get("excel_path", ""))
        ttk.Entry(er, textvariable=self._excel_path_var, width=60).pack(side="left", fill="x", expand=True)
        ttk.Button(er, text="Goz At", command=self._browse_excel).pack(side="left", padx=(6, 0))

        # Bildirim saati
        nf = ttk.LabelFrame(parent, text="  Gunluk Bildirim Saati  "); nf.pack(fill="x", padx=14, pady=(0, 10))
        nr = ttk.Frame(nf); nr.pack(fill="x", **pad)
        ttk.Label(nr, text="Saat:").pack(side="left")
        self._notify_hour = tk.IntVar(value=self.settings.get("notify_hour", 9))
        ttk.Spinbox(nr, textvariable=self._notify_hour, from_=0, to=23, width=5).pack(side="left", padx=4)
        ttk.Label(nr, text="Dakika:").pack(side="left", padx=(12, 0))
        self._notify_min = tk.IntVar(value=self.settings.get("notify_minute", 0))
        ttk.Spinbox(nr, textvariable=self._notify_min, from_=0, to=59, width=5).pack(side="left", padx=4)
        ttk.Label(nr, text=FG2).pack(side="left", padx=(10, 0))
        tk.Label(nr, text="(Her gun bu saatte Windows bildirimi gonderilir)", bg=BG, fg=FG2, font=("Segoe UI", 8)).pack(side="left", padx=(6, 0))

        # Bildirim penceresi (kac gun)
        lf = ttk.LabelFrame(parent, text="  Bildirim Ufku (Kac Gun Oncesinde Uyar)  "); lf.pack(fill="x", padx=14, pady=(0, 10))
        lr = ttk.Frame(lf); lr.pack(fill="x", **pad)
        self._lead_days_var = tk.IntVar(value=self.settings.get("lead_days", 7))
        ttk.Spinbox(lr, textvariable=self._lead_days_var, from_=1, to=90, width=5).pack(side="left")
        tk.Label(lr, text="gun icindeki eventleri bildirimde goster", bg=BG, fg=FG2, font=("Segoe UI", 8)).pack(side="left", padx=(8, 0))

        # Baslangicta bildirim
        sf = ttk.Frame(parent); sf.pack(fill="x", padx=14, pady=(0, 10))
        self._startup_notify = tk.BooleanVar(value=self.settings.get("startup_notify", True))
        ttk.Checkbutton(sf, text="Uygulama acilisinda bildirim gonder", variable=self._startup_notify).pack(anchor="w")

        # Butonlar
        bf = ttk.Frame(parent); bf.pack(fill="x", padx=14, pady=(6, 0))
        ttk.Button(bf, text="Kaydet", command=self._save_settings, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(bf, text="Test Bildirimi Gonder", command=self._test_notify).pack(side="left")

    def _browse_excel(self):
        path = filedialog.askopenfilename(
            title="Excel Dosyasini Sec",
            filetypes=[("Excel Dosyalari", "*.xlsx *.xls"), ("Tum Dosyalar", "*.*")]
        )
        if path:
            self._excel_path_var.set(path)
            self.settings["excel_path"] = path
            self.save_fn(self.settings)
            self.reload()

    def _save_settings(self):
        self.settings["excel_path"]     = self._excel_path_var.get()
        self.settings["notify_hour"]    = int(self._notify_hour.get())
        self.settings["notify_minute"]  = int(self._notify_min.get())
        self.settings["lead_days"]      = int(self._lead_days_var.get())
        self.settings["startup_notify"] = bool(self._startup_notify.get())
        self.save_fn(self.settings)
        messagebox.showinfo("Kaydedildi", "Ayarlar kaydedildi.", parent=self.win)

    def _test_notify(self):
        import notifier
        notifier.notify(
            "OYYA1UPDATE ALARM - Test",
            "Bildirim sistemi calisıyor! Bu bir test mesajidir."
        )
