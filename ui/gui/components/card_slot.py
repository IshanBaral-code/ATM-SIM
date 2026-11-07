"""
Physical card reader slot, card ejector, and cash shutter module.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from config import CURRENCY_SYMBOL
from core.security import format_card_number
from ui.theme import (
    COLOR_ACCENT_CYAN,
    COLOR_FRAME_BEZEL,
    COLOR_FRAME_BORDER,
    COLOR_KEYPAD_BG,
    COLOR_LED_ACTIVE,
    COLOR_LED_IDLE,
    COLOR_SUCCESS,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
)


class ATMHardwareBay(tk.Frame):
    """Encapsulates the card insertion slot, demo card selector, and cash shutter tray."""

    DEMO_PROFILES = [
        ("4532015011223341", "Alexander Vance (Standard: $4,850)", "1234"),
        ("4532882011223344", "Eleanor Sterling (HNW: $85,400)", "9999"),
        ("4532009111223343", "Marcus Brody (Low Bal: $45)", "0000"),
        ("4000123411223342", "System Administrator (Vault)", "7777"),
    ]

    def __init__(self, parent, on_insert_card: Callable[[str], None], on_eject_card: Callable[[], None], **kwargs):
        super().__init__(parent, bg=COLOR_FRAME_BEZEL, highlightbackground=COLOR_FRAME_BORDER, highlightthickness=2, padx=16, pady=14, **kwargs)
        self.on_insert_card = on_insert_card
        self.on_eject_card = on_eject_card
        self.card_inserted = False

        self._build_card_slot()
        self._build_cash_shutter()

    def _build_card_slot(self) -> None:
        title_frame = tk.Frame(self, bg=COLOR_FRAME_BEZEL)
        title_frame.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            title_frame,
            text="💳 CARD READER / DIP SLOT",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_FRAME_BEZEL
        ).pack(side=tk.LEFT)

        self.led_indicator = tk.Label(
            title_frame,
            text="● ACTIVE",
            font=FONT_SMALL,
            fg=COLOR_LED_ACTIVE,
            bg=COLOR_FRAME_BEZEL
        )
        self.led_indicator.pack(side=tk.RIGHT)

        # Slot visual graphic
        slot_visual = tk.Frame(self, bg="#0A0C10", height=14, highlightbackground="#334155", highlightthickness=1)
        slot_visual.pack(fill=tk.X, pady=(0, 10))

        # Demo Card Quick Select Dropdown
        tk.Label(
            self,
            text="Select Demo Account / Card:",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_FRAME_BEZEL
        ).pack(anchor="w")

        self.selected_profile_var = tk.StringVar(value=self.DEMO_PROFILES[0][1])
        profile_options = [p[1] for p in self.DEMO_PROFILES]
        self.profile_dropdown = ttk.Combobox(
            self,
            textvariable=self.selected_profile_var,
            values=profile_options,
            state="readonly",
            font=FONT_BODY
        )
        self.profile_dropdown.pack(fill=tk.X, pady=(2, 8))
        self.profile_dropdown.bind("<<ComboboxSelected>>", self._on_profile_picked)

        # Manual Card Input Frame
        tk.Label(
            self,
            text="Card Number (16 Digits):",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_FRAME_BEZEL
        ).pack(anchor="w")

        input_frame = tk.Frame(self, bg=COLOR_FRAME_BEZEL)
        input_frame.pack(fill=tk.X, pady=(2, 10))

        self.card_num_entry = tk.Entry(
            input_frame,
            font=FONT_BODY,
            bg="#0F172A",
            fg="#F8FAFC",
            insertbackground="#38BDF8",
            relief=tk.FLAT,
            highlightbackground="#334155",
            highlightthickness=1
        )
        self.card_num_entry.pack(fill=tk.X, side=tk.LEFT, expand=True, ipady=4, padx=(0, 6))
        self.card_num_entry.insert(0, format_card_number(self.DEMO_PROFILES[0][0]))

        # Insert / Eject Buttons
        btn_frame = tk.Frame(self, bg=COLOR_FRAME_BEZEL)
        btn_frame.pack(fill=tk.X, pady=(0, 14))

        self.insert_btn = tk.Button(
            btn_frame,
            text="INSERT CARD ▶",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg=COLOR_SUCCESS,
            activebackground="#059669",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._handle_insert
        )
        self.insert_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.eject_btn = tk.Button(
            btn_frame,
            text="EJECT ⏏",
            font=FONT_BODY_BOLD,
            fg="#94A3B8",
            bg="#1E293B",
            activebackground="#334155",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._handle_eject
        )
        self.eject_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    def _build_cash_shutter(self) -> None:
        divider = tk.Frame(self, bg=COLOR_FRAME_BORDER, height=1)
        divider.pack(fill=tk.X, pady=(4, 12))

        header_frame = tk.Frame(self, bg=COLOR_FRAME_BEZEL)
        header_frame.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header_frame,
            text="💵 CASH DISPENSER SHUTTER",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_FRAME_BEZEL
        ).pack(side=tk.LEFT)

        self.shutter_led = tk.Label(
            header_frame,
            text="CLOSED",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_FRAME_BEZEL
        )
        self.shutter_led.pack(side=tk.RIGHT)

        # Physical Cash Shutter Box
        self.shutter_box = tk.Frame(
            self,
            bg="#0B0F19",
            height=60,
            highlightbackground="#222B3E",
            highlightthickness=2
        )
        self.shutter_box.pack(fill=tk.X, pady=(2, 6))
        self.shutter_box.pack_propagate(False)

        self.shutter_label = tk.Label(
            self.shutter_box,
            text="[ CASH DISPENSER CLOSED ]",
            font=FONT_SMALL,
            fg="#475569",
            bg="#0B0F19"
        )
        self.shutter_label.pack(expand=True)

    def _on_profile_picked(self, event=None) -> None:
        selected_text = self.selected_profile_var.get()
        for num, label, pin in self.DEMO_PROFILES:
            if label == selected_text:
                self.card_num_entry.delete(0, tk.END)
                self.card_num_entry.insert(0, format_card_number(num))
                break

    def _handle_insert(self) -> None:
        card_text = self.card_num_entry.get().strip()
        if card_text:
            self.card_inserted = True
            self.insert_btn.config(state=tk.DISABLED, bg="#334155")
            self.eject_btn.config(state=tk.NORMAL, bg="#EF4444", fg="#FFFFFF")
            self.led_indicator.config(text="● CARD IN", fg="#38BDF8")
            self.profile_dropdown.config(state=tk.DISABLED)
            self.card_num_entry.config(state=tk.DISABLED)
            self.on_insert_card(card_text)

    def _handle_eject(self) -> None:
        self.card_inserted = False
        self.insert_btn.config(state=tk.NORMAL, bg=COLOR_SUCCESS)
        self.eject_btn.config(state=tk.DISABLED, bg="#1E293B", fg="#94A3B8")
        self.led_indicator.config(text="● ACTIVE", fg=COLOR_LED_ACTIVE)
        self.profile_dropdown.config(state="readonly")
        self.card_num_entry.config(state=tk.NORMAL)
        self.on_eject_card()

    def set_dispensing_state(self, is_dispensing: bool, notes_info: str = "") -> None:
        """Animates the shutter to open with cash ready."""
        if is_dispensing:
            self.shutter_box.config(bg="#064E3B", highlightbackground="#10B981")
            self.shutter_label.config(
                text=f"💵 CASH DISPENSED - TAKE NOTES!\n{notes_info}",
                fg="#6EE7B7",
                bg="#064E3B"
            )
            self.shutter_led.config(text="OPEN", fg="#10B981")
        else:
            self.shutter_box.config(bg="#0B0F19", highlightbackground="#222B3E")
            self.shutter_label.config(
                text="[ CASH DISPENSER CLOSED ]",
                fg="#475569",
                bg="#0B0F19"
            )
            self.shutter_led.config(text="CLOSED", fg=COLOR_TEXT_MUTED)
