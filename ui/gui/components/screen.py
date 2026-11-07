"""
ATM Digital Screen component with header status, dynamic content view, and bottom prompt bar.
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk

from config import BANK_NAME, TERMINAL_ID
from ui.theme import (
    COLOR_ACCENT_CYAN,
    COLOR_SCREEN_BG,
    COLOR_SCREEN_BORDER,
    COLOR_SCREEN_SURFACE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
)


class ATMScreen(tk.Frame):
    """Encapsulates the digital kiosk LCD monitor display."""

    def __init__(self, parent, on_toggle_audio=None, **kwargs):
        super().__init__(parent, bg=COLOR_SCREEN_BG, highlightbackground=COLOR_SCREEN_BORDER, highlightthickness=3, **kwargs)
        self.on_toggle_audio = on_toggle_audio
        self.audio_muted = False

        self._build_header()
        self._build_content_area()
        self._build_status_bar()
        self._update_clock()

    def _build_header(self) -> None:
        self.header_frame = tk.Frame(self, bg=COLOR_SCREEN_SURFACE, height=48, pady=6, padx=16)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)

        # Bank Branding
        brand_frame = tk.Frame(self.header_frame, bg=COLOR_SCREEN_SURFACE)
        brand_frame.pack(side=tk.LEFT)

        tk.Label(
            brand_frame,
            text="⛨ " + BANK_NAME,
            font=FONT_HEADING,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_SURFACE
        ).pack(side=tk.LEFT)

        tk.Label(
            brand_frame,
            text=f" [{TERMINAL_ID}]",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SCREEN_SURFACE
        ).pack(side=tk.LEFT, padx=(6, 0))

        # Status & Controls on Right
        right_frame = tk.Frame(self.header_frame, bg=COLOR_SCREEN_SURFACE)
        right_frame.pack(side=tk.RIGHT)

        # Encryption Indicator
        tk.Label(
            right_frame,
            text="🔒 256-BIT ENCRYPTED",
            font=FONT_SMALL,
            fg="#34D399",
            bg=COLOR_SCREEN_SURFACE
        ).pack(side=tk.LEFT, padx=10)

        # Audio Toggle Button
        self.audio_btn = tk.Button(
            right_frame,
            text="🔊 AUDIO ON",
            font=FONT_SMALL,
            fg=COLOR_TEXT_PRIMARY,
            bg="#1E293B",
            activebackground="#334155",
            activeforeground=COLOR_TEXT_PRIMARY,
            bd=0,
            padx=8,
            pady=2,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._handle_audio_toggle
        )
        self.audio_btn.pack(side=tk.LEFT, padx=6)

        # Live Clock
        self.clock_label = tk.Label(
            right_frame,
            text="",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_SURFACE
        )
        self.clock_label.pack(side=tk.LEFT, padx=(10, 0))

    def _build_content_area(self) -> None:
        self.content_container = tk.Frame(self, bg=COLOR_SCREEN_BG)
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

    def _build_status_bar(self) -> None:
        self.status_bar = tk.Frame(self, bg=COLOR_SCREEN_SURFACE, height=36, padx=16, pady=6)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_icon = tk.Label(
            self.status_bar,
            text="ℹ",
            font=FONT_BODY,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_SURFACE
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, 8))

        self.status_text = tk.Label(
            self.status_bar,
            text="Ready.",
            font=FONT_BODY,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_SURFACE,
            anchor="w"
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _handle_audio_toggle(self) -> None:
        if self.on_toggle_audio:
            is_muted = self.on_toggle_audio()
            self.audio_muted = is_muted
            if is_muted:
                self.audio_btn.config(text="🔇 MUTED", fg=COLOR_TEXT_MUTED)
            else:
                self.audio_btn.config(text="🔊 AUDIO ON", fg=COLOR_TEXT_PRIMARY)

    def set_status(self, text: str, is_error: bool = False, is_success: bool = False) -> None:
        fg_color = COLOR_TEXT_PRIMARY
        icon = "ℹ"
        if is_error:
            fg_color = "#F87171"
            icon = "⚠"
        elif is_success:
            fg_color = "#34D399"
            icon = "✔"

        self.status_icon.config(text=icon, fg=fg_color)
        self.status_text.config(text=text, fg=fg_color)

    def clear_content(self) -> None:
        for child in self.content_container.winfo_children():
            child.destroy()

    def _update_clock(self) -> None:
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.clock_label.config(text=now_str)
        self.after(1000, self._update_clock)
