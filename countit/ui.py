"""CountIt GUI."""

from __future__ import annotations

import ctypes
import tkinter as tk
from tkinter import simpledialog

from . import __version__
from . import settings as cfg
from .instance import WINDOW_TITLE
from .stats import analyze

BG = "#111111"
FG = "#ffffff"
MUTED = "#999999"
CARD = "#1a1a1a"
ACCENT = "#93c5fd"


class CountItApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("720x560")
        self.minsize(520, 420)
        self.configure(bg=BG)
        self._after_id: str | None = None
        self._wpm = cfg.get_wpm()  # None = locked

        pad = tk.Frame(self, bg=BG)
        pad.pack(fill="both", expand=True, padx=22, pady=18)

        head = tk.Frame(pad, bg=BG)
        head.pack(fill="x")
        tk.Label(head, text="CountIt", bg=BG, fg=FG, font=("Segoe UI Semibold", 18)).pack(
            side="left"
        )
        tk.Label(
            head,
            text="неделя 6 · Текст · день 39",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right")

        tk.Label(
            pad,
            text="Сколько символов, слов и времени на чтение",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 12))

        self._footer = tk.Frame(pad, bg=BG)
        self._footer.pack(side="bottom", fill="x")

        row = tk.Frame(self._footer, bg=BG)
        row.pack(side="bottom", fill="x", pady=(10, 0))
        self._mk_btn(row, "Из буфера", self.from_clip).pack(side="left")
        self._mk_btn(row, "Очистить", self.clear_box).pack(side="left", padx=(8, 0))
        tk.Label(
            row,
            text=f"v{__version__} · darkshade",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right")

        board = tk.Frame(self._footer, bg=BG)
        board.pack(side="bottom", fill="x", pady=(8, 0))

        self._stat_labels: dict[str, tk.Label] = {}
        self._stat_titles: dict[str, tk.Label] = {}

        for key, title in (("chars", "символов"), ("words", "слов")):
            col = tk.Frame(board, bg=BG)
            col.pack(side="left", padx=(0, 36))
            val = tk.Label(col, text="0", bg=BG, fg=FG, font=("Segoe UI Semibold", 40))
            val.pack(anchor="w")
            cap = tk.Label(col, text=title, bg=BG, fg=MUTED, font=("Segoe UI", 11))
            cap.pack(anchor="w")
            self._stat_labels[key] = val
            self._stat_titles[key] = cap

        read_col = tk.Frame(board, bg=BG)
        read_col.pack(side="left", padx=(0, 36))
        self._read_val = tk.Label(
            read_col,
            text="🔒",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI Emoji", 36),
            cursor="hand2",
        )
        self._read_val.pack(anchor="w")
        self._read_cap = tk.Label(
            read_col,
            text="чтение · нажми замок",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
            cursor="hand2",
        )
        self._read_cap.pack(anchor="w")
        self._read_val.bind("<Button-1>", lambda _e: self.unlock_read())
        self._read_cap.bind("<Button-1>", lambda _e: self.unlock_read())
        self._stat_labels["read"] = self._read_val

        self._box = tk.Text(
            pad,
            height=14,
            bg=CARD,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=("Consolas", 12),
            wrap="word",
            padx=12,
            pady=10,
            undo=True,
        )
        self._box.pack(fill="both", expand=True)
        self._box.bind("<<Modified>>", self._on_modified)

        self.after(20, self._place)
        self.after(80, self._box.focus_set)
        self._refresh()

    def _mk_btn(self, parent, text, cmd) -> tk.Label:
        lbl = tk.Label(
            parent,
            text=text,
            bg="#333333",
            fg=FG,
            font=("Segoe UI", 10),
            padx=12,
            pady=7,
            cursor="hand2",
        )
        lbl.bind("<Button-1>", lambda _e: cmd())
        return lbl

    def _place(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width() or 720, self.winfo_height() or 560
        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 4}")

    def _text(self) -> str:
        return self._box.get("1.0", "end-1c")

    def _on_modified(self, _event=None) -> None:
        self._box.edit_modified(False)
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(40, self._refresh)

    def unlock_read(self) -> None:
        initial = self._wpm if self._wpm else 200
        value = simpledialog.askinteger(
            "Скорость чтения",
            "Слов в минуту (обычно 150–250):",
            parent=self,
            minvalue=50,
            maxvalue=1000,
            initialvalue=initial,
        )
        if value is None:
            return
        self._wpm = value
        cfg.set_wpm(value)
        self._refresh()

    def _refresh(self) -> None:
        self._after_id = None
        if self._wpm is None:
            s = analyze(self._text(), 200)
            self._stat_labels["chars"].configure(text=str(s.chars))
            self._stat_labels["words"].configure(text=str(s.words))
            self._read_val.configure(text="🔒", fg=MUTED, font=("Segoe UI Emoji", 36))
            self._read_cap.configure(text="чтение · нажми замок")
            return

        s = analyze(self._text(), self._wpm)
        self._stat_labels["chars"].configure(text=str(s.chars))
        self._stat_labels["words"].configure(text=str(s.words))
        self._read_val.configure(
            text=s.read_label(),
            fg=ACCENT if s.words else FG,
            font=("Segoe UI Semibold", 40),
        )
        self._read_cap.configure(text=f"чтение · {self._wpm} сл/мин")

    def from_clip(self) -> None:
        try:
            data = self.clipboard_get()
        except tk.TclError:
            return
        if not isinstance(data, str):
            data = str(data)
        self._box.delete("1.0", "end")
        self._box.insert("1.0", data)
        self._refresh()

    def clear_box(self) -> None:
        self._box.delete("1.0", "end")
        self._refresh()


def run() -> None:
    CountItApp().mainloop()
