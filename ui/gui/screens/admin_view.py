"""
Administrator diagnostic and vault management console.
"""

from typing import Callable, Dict, List
import tkinter as tk
from tkinter import messagebox

from config import CURRENCY_SYMBOL
from ui.theme import (
    COLOR_ACCENT_CYAN,
    COLOR_DANGER,
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


class AdminView(tk.Frame):
    """Diagnostic console for bank technicians and administrators."""

    def __init__(
        self,
        parent,
        cassettes: Dict[int, int],
        audit_logs: List[dict],
        on_refill_vault: Callable[[], None],
        on_exit: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.cassettes = cassettes
        self.audit_logs = audit_logs
        self.on_refill_vault = on_refill_vault
        self.on_exit = on_exit

        self._build_view()

    def _build_view(self) -> None:
        header_bar = tk.Frame(self, bg="#311B92", padx=16, pady=8)
        header_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            header_bar,
            text="🛠 ATM DIAGNOSTIC & VAULT CONSOLE",
            font=FONT_HEADING,
            fg="#E0E7FF",
            bg="#311B92"
        ).pack(side=tk.LEFT)

        tk.Label(
            header_bar,
            text="SECURITY CLEARANCE: LEVEL 5 (ADMIN)",
            font=FONT_SMALL,
            fg="#A5B4FC",
            bg="#311B92"
        ).pack(side=tk.RIGHT)

        # Main content
        main_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=14)

        # Top section: Cassette Inventory
        vault_box = tk.LabelFrame(
            main_frame,
            text=" Hardware Cassette Inventory ",
            font=FONT_SMALL,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_BG,
            padx=12,
            pady=8
        )
        vault_box.pack(fill=tk.X, pady=(0, 10))

        inv_grid = tk.Frame(vault_box, bg=COLOR_SCREEN_BG)
        inv_grid.pack(fill=tk.X)

        total_vault = 0
        for i, (denom, count) in enumerate(sorted(self.cassettes.items(), reverse=True)):
            val = denom * count
            total_vault += val

            cell = tk.Frame(inv_grid, bg=COLOR_SCREEN_SURFACE, padx=10, pady=6)
            cell.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

            tk.Label(cell, text=f"{CURRENCY_SYMBOL}{denom} Cassette", font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=COLOR_SCREEN_SURFACE).pack()
            tk.Label(cell, text=f"{count} Notes", font=FONT_BODY_BOLD, fg=COLOR_TEXT_PRIMARY, bg=COLOR_SCREEN_SURFACE).pack()
            tk.Label(cell, text=f"{CURRENCY_SYMBOL}{val:,.0f}", font=FONT_SMALL, fg="#34D399", bg=COLOR_SCREEN_SURFACE).pack()

        # Vault Total & Refill Row
        sub_row = tk.Frame(vault_box, bg=COLOR_SCREEN_BG, pady=6)
        sub_row.pack(fill=tk.X)

        tk.Label(
            sub_row,
            text=f"Total Vault Cash Available: {CURRENCY_SYMBOL}{total_vault:,.2f}",
            font=FONT_BODY_BOLD,
            fg="#38BDF8",
            bg=COLOR_SCREEN_BG
        ).pack(side=tk.LEFT)

        refill_btn = tk.Button(
            sub_row,
            text="🔄 Refill All Cassettes to Full",
            font=FONT_SMALL,
            fg="#FFFFFF",
            bg="#059669",
            activebackground="#047857",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.on_refill_vault
        )
        refill_btn.pack(side=tk.RIGHT)

        # Bottom section: Audit Trail
        audit_box = tk.LabelFrame(
            main_frame,
            text=" Regulatory Security & Transaction Audit Trail ",
            font=FONT_SMALL,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_BG,
            padx=10,
            pady=6
        )
        audit_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Text/list box for logs
        text_widget = tk.Text(
            audit_box,
            wrap=tk.NONE,
            font=("Consolas", 8),
            bg="#0B0F19",
            fg="#CBD5E1",
            bd=0,
            padx=6,
            pady=4,
            height=6
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        for log in self.audit_logs[:15]:
            ts = log.get("timestamp", "")
            evt = log.get("event_type", "")
            card = log.get("card_masked", "") or "N/A"
            dtl = log.get("details", "")
            sev = log.get("severity", "INFO")
            text_widget.insert(tk.END, f"[{ts}] [{sev:5}] [{evt:16}] Card: {card:<19} | {dtl}\n")
        text_widget.config(state=tk.DISABLED)

        # Exit Button
        exit_btn = tk.Button(
            self,
            text="⏏ Exit Diagnostic Mode & Eject Admin Card",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg="#DC2626",
            activebackground="#B91C1C",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_exit
        )
        exit_btn.pack(fill=tk.X, padx=14, pady=(0, 10))
