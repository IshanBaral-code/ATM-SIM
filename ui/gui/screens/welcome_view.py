"""
Welcome and standby screen for Apex Federal Bank ATM.
"""

import tkinter as tk
from config import BANK_NAME, BANK_TAGLINE, TERMINAL_ID
from ui.theme import (
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_CYAN,
    COLOR_SCREEN_BG,
    COLOR_SCREEN_SURFACE,
    COLOR_SCREEN_SURFACE_ALT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
)


class WelcomeView(tk.Frame):
    """Standby display inviting user to insert card."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self._build_view()

    def _build_view(self) -> None:
        center_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        center_frame.pack(expand=True)

        # Graphic Bank Shield
        tk.Label(
            center_frame,
            text="🏛️",
            font=("Segoe UI", 48),
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 10))

        tk.Label(
            center_frame,
            text=BANK_NAME,
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack()

        tk.Label(
            center_frame,
            text=BANK_TAGLINE,
            font=FONT_BODY,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(4, 24))

        # Card Insertion Prompt Card
        card_box = tk.Frame(
            center_frame,
            bg=COLOR_SCREEN_SURFACE,
            highlightbackground="#2A3859",
            highlightthickness=1,
            padx=30,
            pady=20
        )
        card_box.pack(fill=tk.X, padx=20)

        tk.Label(
            card_box,
            text="💳 PLEASE INSERT YOUR CARD",
            font=FONT_HEADING,
            fg="#60A5FA",
            bg=COLOR_SCREEN_SURFACE
        ).pack()

        tk.Label(
            card_box,
            text="Insert chip card into reader on the right, or pick a demo profile.\nEnsure your PIN remains confidential at all times.",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_SURFACE,
            justify=tk.CENTER
        ).pack(pady=(8, 14))

        # Status Pill
        pill = tk.Frame(card_box, bg="#1E293B", padx=16, pady=4)
        pill.pack()

        tk.Label(
            pill,
            text="● SYSTEM READY - STANDBY MODE",
            font=FONT_SMALL,
            fg="#34D399",
            bg="#1E293B"
        ).pack()

        # Supported Payment Networks Footer
        network_frame = tk.Frame(center_frame, bg=COLOR_SCREEN_BG)
        network_frame.pack(pady=(26, 0))

        tk.Label(
            network_frame,
            text="ACCEPTED NETWORKS:   VISA  |  MasterCard  |  PLUS  |  Cirrus  |  Interac",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SCREEN_BG
        ).pack()
