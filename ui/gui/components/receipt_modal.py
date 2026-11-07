"""
Modal window displaying the simulated thermal printed receipt.
"""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from ui.theme import (
    COLOR_RECEIPT_BG,
    COLOR_RECEIPT_BORDER,
    COLOR_RECEIPT_TEXT,
    COLOR_TEXT_PRIMARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_RECEIPT,
)


class ReceiptModal(tk.Toplevel):
    """Pop-up modal emulating an authentic printed thermal receipt slip."""

    def __init__(self, parent, receipt_text: str):
        super().__init__(parent)
        self.title("Transaction Receipt - Apex Federal Bank")
        self.geometry("450x640")
        self.configure(bg="#0F172A")
        self.receipt_text = receipt_text

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self) -> None:
        # Title bar
        title_frame = tk.Frame(self, bg="#0F172A", pady=10)
        title_frame.pack(fill=tk.X)
        tk.Label(
            title_frame,
            text="🖨 THERMAL RECEIPT DISPENSED",
            font=FONT_BODY_BOLD,
            fg="#38BDF8",
            bg="#0F172A"
        ).pack()

        # Paper Container Frame (Paper effect)
        paper_outer = tk.Frame(self, bg="#E2DCD5", padx=2, pady=2)
        paper_outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        paper_frame = tk.Frame(paper_outer, bg=COLOR_RECEIPT_BG, padx=16, pady=16)
        paper_frame.pack(fill=tk.BOTH, expand=True)

        # Monospace Text Widget
        text_widget = tk.Text(
            paper_frame,
            wrap=tk.NONE,
            font=FONT_RECEIPT,
            bg=COLOR_RECEIPT_BG,
            fg=COLOR_RECEIPT_TEXT,
            bd=0,
            padx=8,
            pady=8,
            relief=tk.FLAT
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", self.receipt_text)
        text_widget.config(state=tk.DISABLED)

        # Action Buttons
        btn_bar = tk.Frame(self, bg="#0F172A", pady=12)
        btn_bar.pack(fill=tk.X)

        save_btn = tk.Button(
            btn_bar,
            text="💾 Save Receipt (.txt)",
            font=FONT_BODY,
            fg="#FFFFFF",
            bg="#2563EB",
            activebackground="#1D4ED8",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._save_file
        )
        save_btn.pack(side=tk.LEFT, padx=(20, 10))

        close_btn = tk.Button(
            btn_bar,
            text="Close Slip ✕",
            font=FONT_BODY,
            fg="#FFFFFF",
            bg="#334155",
            activebackground="#475569",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=(0, 20))

    def _save_file(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All Files", "*.*")],
            title="Save Transaction Receipt"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.receipt_text)
                messagebox.showinfo("Receipt Saved", f"Receipt successfully saved to:\n{file_path}", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save receipt:\n{e}", parent=self)
