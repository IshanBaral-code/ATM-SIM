"""
PIN Change interface view.
"""

from typing import Callable
import tkinter as tk

from ui.theme import (
    COLOR_ACCENT_CYAN,
    COLOR_SCREEN_BG,
    COLOR_SCREEN_SURFACE,
    COLOR_SCREEN_SURFACE_ALT,
    COLOR_SUCCESS,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
)


class PINChangeView(tk.Frame):
    """View allowing secure update of the card PIN."""

    def __init__(
        self,
        parent,
        on_change_pin: Callable[[str, str], None],
        on_back: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.on_change_pin = on_change_pin
        self.on_back = on_back

        self._build_view()

    def _build_view(self) -> None:
        center_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        center_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=10)

        tk.Label(
            center_frame,
            text="CHANGE CARD PIN",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 4))

        tk.Label(
            center_frame,
            text="Enter your current PIN followed by your new 4-digit PIN:",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 14))

        form = tk.Frame(center_frame, bg=COLOR_SCREEN_SURFACE, padx=20, pady=16)
        form.pack(fill=tk.X, pady=(0, 16))

        # Current PIN
        tk.Label(form, text="Current PIN:", font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=COLOR_SCREEN_SURFACE).pack(anchor="w")
        self.old_pin_entry = tk.Entry(form, show="●", font=("Segoe UI", 14), bg="#0F172A", fg="#FFFFFF", bd=0, insertbackground="#38BDF8")
        self.old_pin_entry.pack(fill=tk.X, pady=(2, 10), ipady=4)

        # New PIN
        tk.Label(form, text="New 4-Digit PIN:", font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=COLOR_SCREEN_SURFACE).pack(anchor="w")
        self.new_pin_entry = tk.Entry(form, show="●", font=("Segoe UI", 14), bg="#0F172A", fg="#FFFFFF", bd=0, insertbackground="#38BDF8")
        self.new_pin_entry.pack(fill=tk.X, pady=(2, 10), ipady=4)

        # Confirm PIN
        tk.Label(form, text="Confirm New PIN:", font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=COLOR_SCREEN_SURFACE).pack(anchor="w")
        self.confirm_pin_entry = tk.Entry(form, show="●", font=("Segoe UI", 14), bg="#0F172A", fg="#FFFFFF", bd=0, insertbackground="#38BDF8")
        self.confirm_pin_entry.pack(fill=tk.X, pady=(2, 6), ipady=4)

        self.error_label = tk.Label(form, text="", font=FONT_SMALL, fg="#F87171", bg=COLOR_SCREEN_SURFACE)
        self.error_label.pack(anchor="w")

        # Buttons
        btn_bar = tk.Frame(center_frame, bg=COLOR_SCREEN_BG)
        btn_bar.pack(fill=tk.X)

        submit_btn = tk.Button(
            btn_bar,
            text="UPDATE PIN ▶",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg=COLOR_SUCCESS,
            activebackground="#059669",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_submit
        )
        submit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        back_btn = tk.Button(
            btn_bar,
            text="◀ Cancel",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg="#1E293B",
            activebackground="#334155",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_back
        )
        back_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

    def _handle_submit(self) -> None:
        old_p = self.old_pin_entry.get().strip()
        new_p = self.new_pin_entry.get().strip()
        conf_p = self.confirm_pin_entry.get().strip()

        if not old_p or not new_p or not conf_p:
            self.error_label.config(text="Please fill in all PIN fields.")
            return

        if new_p != conf_p:
            self.error_label.config(text="New PIN and confirmation do not match.")
            return

        self.on_change_pin(old_p, new_p)
