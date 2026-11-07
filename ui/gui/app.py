"""
Main ATM Kiosk Graphical User Interface application.
"""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from config import (
    BANK_NAME,
    DEFAULT_CASSETTE_INVENTORY,
    TERMINAL_ID,
    TERMINAL_LOCATION,
)
from core.atm_controller import ATMController, ATMState
from core.exceptions import BankingError
from ui.gui.components.card_slot import ATMHardwareBay
from ui.gui.components.keypad import ATMKeypad
from ui.gui.components.receipt_modal import ReceiptModal
from ui.gui.components.screen import ATMScreen
from ui.gui.screens.account_view import AccountSelectView
from ui.gui.screens.admin_view import AdminView
from ui.gui.screens.balance_view import BalanceView
from ui.gui.screens.deposit_view import DepositView
from ui.gui.screens.dispensing_view import DispensingView
from ui.gui.screens.menu_view import MainMenuView
from ui.gui.screens.pin_change_view import PINChangeView
from ui.gui.screens.pin_view import PINView
from ui.gui.screens.statement_view import StatementView
from ui.gui.screens.welcome_view import WelcomeView
from ui.gui.screens.withdraw_view import WithdrawView
from ui.theme import (
    COLOR_FRAME_BEZEL,
    COLOR_FRAME_BORDER,
    COLOR_FRAME_OUTER,
    COLOR_KEYPAD_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
)


class ATMApplication:
    """Top-level Tkinter window controller for the Apex Federal Bank ATM kiosk."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{BANK_NAME} - ATM KIOSK [{TERMINAL_ID}]")
        self.root.geometry("1100x780")
        self.root.minsize(1000, 720)
        self.root.configure(bg=COLOR_FRAME_OUTER)

        # Initialize ATM backend controller
        self.controller = ATMController()

        # Build kiosk hardware chassis
        self._build_chassis()

        # Keyboard bindings
        self._bind_keys()

        # Show initial screen
        self._render_current_state()

    def _build_chassis(self) -> None:
        """Constructs the physical kiosk bezel frame, monitor, and lower hardware consoles."""
        # Top Machine Marquee
        top_marquee = tk.Frame(self.root, bg="#0B0E14", pady=8, padx=20)
        top_marquee.pack(fill=tk.X)

        tk.Label(
            top_marquee,
            text=f"🏛 {BANK_NAME}  •  ATM TERMINAL #{TERMINAL_ID}",
            font=FONT_HEADING,
            fg="#60A5FA",
            bg="#0B0E14"
        ).pack(side=tk.LEFT)

        tk.Label(
            top_marquee,
            text=f"LOCATION: {TERMINAL_LOCATION}",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg="#0B0E14"
        ).pack(side=tk.RIGHT)

        # Upper Deck (Screen + Card Reader Bay)
        upper_deck = tk.Frame(self.root, bg=COLOR_FRAME_OUTER, padx=16, pady=10)
        upper_deck.pack(fill=tk.BOTH, expand=True)

        # Screen (Left, ~70% width)
        self.screen = ATMScreen(
            upper_deck,
            on_toggle_audio=self.controller.speaker.toggle_mute
        )
        self.screen.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Hardware Bay (Right, ~30% width)
        self.hardware_bay = ATMHardwareBay(
            upper_deck,
            on_insert_card=self._handle_card_insert,
            on_eject_card=self._handle_card_eject,
            width=320
        )
        self.hardware_bay.pack(side=tk.LEFT, fill=tk.Y)
        self.hardware_bay.pack_propagate(False)

        # Lower Deck (Physical Keypad + Hardware Guidance)
        lower_deck = tk.Frame(self.root, bg=COLOR_FRAME_BEZEL, padx=20, pady=8, highlightbackground=COLOR_FRAME_BORDER, highlightthickness=1)
        lower_deck.pack(fill=tk.X)

        # Keypad on Left
        self.keypad = ATMKeypad(
            lower_deck,
            on_digit=self._on_keypad_digit,
            on_clear=self._on_keypad_clear,
            on_cancel=self._on_keypad_cancel,
            on_enter=self._on_keypad_enter
        )
        self.keypad.pack(side=tk.LEFT, padx=(40, 20))

        # Hardware Guidance Card on Right
        help_card = tk.Frame(lower_deck, bg="#131926", padx=16, pady=12, highlightbackground="#222B3E", highlightthickness=1)
        help_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            help_card,
            text="🛡️ SECURE TRANSACTION CONTROLS",
            font=FONT_BODY_BOLD,
            fg="#38BDF8",
            bg="#131926"
        ).pack(anchor="w")

        tk.Label(
            help_card,
            text="• Keyboard Shortcuts Enabled: Digits [0-9], [Enter], [Backspace] (Clear), [Escape] (Cancel).\n"
                 "• Audio Guidance: Click 'AUDIO ON' at the top right to toggle voice assistance prompts.\n"
                 "• Thermal Receipts: Generated upon cash withdrawal, deposit, transfer, or balance inquiry.",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg="#131926",
            justify=tk.LEFT
        ).pack(anchor="w", pady=(4, 0))

    def _bind_keys(self) -> None:
        """Maps physical computer keyboard to the ATM hardware keypad."""
        self.root.bind("<Key>", self._handle_physical_key)

    def _handle_physical_key(self, event: tk.Event) -> None:
        char = event.char
        keysym = event.keysym

        if char.isdigit():
            self._on_keypad_digit(char)
        elif keysym in ("Return", "KP_Enter"):
            self._on_keypad_enter()
        elif keysym == "BackSpace":
            self._on_keypad_clear()
        elif keysym == "Escape":
            self._on_keypad_cancel()

    # Hardware Handlers
    def _handle_card_insert(self, card_number: str) -> None:
        try:
            self.controller.insert_card(card_number)
            self._render_current_state()
        except BankingError as e:
            self.screen.set_status(e.user_friendly_message, is_error=True)
            self.hardware_bay._handle_eject()

    def _handle_card_eject(self) -> None:
        self.controller.eject_and_reset()
        self.hardware_bay.set_dispensing_state(False)
        self._render_current_state()

    # Keypad Event Handlers
    def _on_keypad_digit(self, char: str) -> None:
        self.controller.speaker.play_key_beep()
        # Route to active screen view if it accepts digits
        if isinstance(self.current_view, PINView):
            self.current_view.append_digit(char)
        elif isinstance(self.current_view, (WithdrawView, DepositView, TransferView)):
            self.current_view.append_digit(char)

    def _on_keypad_clear(self) -> None:
        self.controller.speaker.play_key_beep()
        if isinstance(self.current_view, PINView):
            self.current_view.clear()
        elif isinstance(self.current_view, (WithdrawView, DepositView, TransferView)):
            self.current_view.clear()

    def _on_keypad_cancel(self) -> None:
        self.controller.speaker.play_key_beep()
        if self.controller.state == ATMState.PIN_ENTRY:
            self._handle_card_eject()
        elif self.controller.state in (ATMState.WITHDRAW_SELECT, ATMState.DEPOSIT_INPUT, ATMState.TRANSFER_INPUT, ATMState.PIN_CHANGE_INPUT, ATMState.BALANCE_DISPLAY, ATMState.STATEMENT_DISPLAY):
            self.controller.state = ATMState.MAIN_MENU
            self._render_current_state()
        elif self.controller.state == ATMState.MAIN_MENU:
            self._handle_card_eject()

    def _on_keypad_enter(self) -> None:
        self.controller.speaker.play_key_beep()
        if isinstance(self.current_view, PINView):
            pin = self.current_view.get_pin()
            if not pin:
                self.screen.set_status("Please enter your 4-digit PIN first.", is_error=True)
                return
            try:
                self.controller.enter_pin(pin)
                self._render_current_state()
            except BankingError as e:
                self.screen.set_status(e.user_friendly_message, is_error=True)
                if self.controller.state == ATMState.IDLE:
                    self.hardware_bay._handle_eject()
                elif isinstance(self.current_view, PINView):
                    self.current_view.clear()

        elif isinstance(self.current_view, WithdrawView):
            self.current_view._handle_custom_dispense()
        elif isinstance(self.current_view, DepositView):
            self.current_view._handle_confirm()
        elif isinstance(self.current_view, TransferView):
            self.current_view._handle_confirm()

    # View Router & Screen Rendering
    def _render_current_state(self) -> None:
        self.screen.clear_content()
        self.screen.set_status(self.controller.status_message)
        state = self.controller.state

        if state == ATMState.IDLE:
            self.current_view = WelcomeView(self.screen.content_container)
            self.hardware_bay.set_dispensing_state(False)

        elif state == ATMState.PIN_ENTRY:
            card = self.controller.current_card
            self.current_view = PINView(
                self.screen.content_container,
                holder_name=card.holder_name if card else "Cardholder",
                card_number=card.card_number if card else "4532000000000000"
            )

        elif state == ATMState.ACCOUNT_SELECTION:
            self.current_view = AccountSelectView(
                self.screen.content_container,
                accounts=self.controller.available_accounts,
                on_select_account=self._handle_select_account
            )

        elif state == ATMState.MAIN_MENU:
            self.current_view = MainMenuView(
                self.screen.content_container,
                account=self.controller.current_account,
                on_action=self._handle_menu_action
            )

        elif state == ATMState.WITHDRAW_SELECT:
            self.current_view = WithdrawView(
                self.screen.content_container,
                available_balance=self.controller.current_account.balance,
                on_withdraw=self._handle_withdraw,
                on_back=self._back_to_menu
            )

        elif state == ATMState.DEPOSIT_INPUT:
            self.current_view = DepositView(
                self.screen.content_container,
                account_number=self.controller.current_account.account_number,
                on_deposit=self._handle_deposit,
                on_back=self._back_to_menu
            )

        elif state == ATMState.TRANSFER_INPUT:
            self.current_view = TransferView(
                self.screen.content_container,
                source_account=self.controller.current_account,
                on_transfer=self._handle_transfer,
                on_back=self._back_to_menu
            )

        elif state == ATMState.BALANCE_DISPLAY:
            self.current_view = BalanceView(
                self.screen.content_container,
                account=self.controller.current_account,
                on_print_receipt=self._show_receipt_modal,
                on_back=self._back_to_menu,
                on_eject=self._handle_card_eject
            )

        elif state == ATMState.STATEMENT_DISPLAY:
            history = self.controller.bank_service.get_statement(self.controller.current_card.card_number)
            self.current_view = StatementView(
                self.screen.content_container,
                transactions=history,
                on_print_receipt=self._show_receipt_modal,
                on_back=self._back_to_menu
            )

        elif state == ATMState.DISPENSING:
            bills = self.controller.last_dispense.bills if self.controller.last_dispense else {}
            amount = self.controller.last_dispense.amount if self.controller.last_dispense else 0.0

            # Update hardware shutter
            bill_desc = ", ".join(f"{c}x${d}" for d, c in sorted(bills.items(), reverse=True))
            self.hardware_bay.set_dispensing_state(True, notes_info=bill_desc)

            self.current_view = DispensingView(
                self.screen.content_container,
                amount=amount,
                bills=bills,
                on_print_receipt=self._show_receipt_modal,
                on_finish=self._finish_dispensing
            )

        elif state == ATMState.PIN_CHANGE_INPUT:
            self.current_view = PINChangeView(
                self.screen.content_container,
                on_change_pin=self._handle_pin_change,
                on_back=self._back_to_menu
            )

        elif state == ATMState.ADMIN_MENU:
            cassettes = self.controller.cash_dispenser.inventory
            logs = self.controller.repo.get_audit_logs(limit=25)
            self.current_view = AdminView(
                self.screen.content_container,
                cassettes=cassettes,
                audit_logs=logs,
                on_refill_vault=self._handle_refill_vault,
                on_exit=self._handle_card_eject
            )

        self.current_view.pack(fill=tk.BOTH, expand=True)

    # Transition Callbacks
    def _handle_select_account(self, account_number: str) -> None:
        self.controller.select_account(account_number)
        self._render_current_state()

    def _handle_menu_action(self, action: str) -> None:
        self.controller.speaker.play_key_beep()
        if action == "fast_cash_100":
            self._handle_withdraw(100.0, is_fast_cash=True)
        elif action == "withdraw":
            self.controller.state = ATMState.WITHDRAW_SELECT
            self.controller.status_message = "Select Fast Cash or enter custom amount."
            self._render_current_state()
        elif action == "deposit":
            self.controller.state = ATMState.DEPOSIT_INPUT
            self.controller.status_message = "Enter or select cash deposit amount."
            self._render_current_state()
        elif action == "transfer":
            self.controller.state = ATMState.TRANSFER_INPUT
            self.controller.status_message = "Select destination and amount to transfer."
            self._render_current_state()
        elif action == "balance":
            self.controller.view_balance()
            self._render_current_state()
        elif action == "statement":
            self.controller.view_statement()
            self._render_current_state()
        elif action == "change_pin":
            self.controller.state = ATMState.PIN_CHANGE_INPUT
            self.controller.status_message = "Update card PIN."
            self._render_current_state()
        elif action == "eject":
            self._handle_card_eject()

    def _handle_withdraw(self, amount: float, is_fast_cash: bool = False) -> None:
        try:
            self.controller.process_withdrawal(amount, is_fast_cash=is_fast_cash)
            self._render_current_state()
        except BankingError as e:
            self.screen.set_status(e.user_friendly_message, is_error=True)
            self.controller.speaker.play_error_tone()

    def _handle_deposit(self, amount: float) -> None:
        try:
            self.controller.process_deposit(amount)
            self.screen.set_status(f"Successfully deposited ${amount:,.2f}.", is_success=True)
            self._show_receipt_modal()
            self.controller.state = ATMState.MAIN_MENU
            self._render_current_state()
        except BankingError as e:
            self.screen.set_status(e.user_friendly_message, is_error=True)
            self.controller.speaker.play_error_tone()

    def _handle_transfer(self, target_account: str, amount: float) -> None:
        try:
            self.controller.process_transfer(target_account, amount)
            self.screen.set_status(f"Transferred ${amount:,.2f} to {target_account}.", is_success=True)
            self._show_receipt_modal()
            self.controller.state = ATMState.MAIN_MENU
            self._render_current_state()
        except BankingError as e:
            self.screen.set_status(e.user_friendly_message, is_error=True)
            self.controller.speaker.play_error_tone()

    def _handle_pin_change(self, old_pin: str, new_pin: str) -> None:
        try:
            self.controller.process_pin_change(old_pin, new_pin)
            self.screen.set_status("PIN updated successfully.", is_success=True)
            self._render_current_state()
        except BankingError as e:
            self.screen.set_status(e.user_friendly_message, is_error=True)
            self.controller.speaker.play_error_tone()

    def _handle_refill_vault(self) -> None:
        self.controller.cash_dispenser.reload_cassettes(DEFAULT_CASSETTE_INVENTORY)
        self.controller.audit.log_event("VAULT_REFILLED", None, "All cassettes refilled to full stock.", "ADMIN")
        self.controller.speaker.play_success_chime()
        self.screen.set_status("All cassettes refilled to full capacity.", is_success=True)
        self._render_current_state()

    def _finish_dispensing(self) -> None:
        self.hardware_bay.set_dispensing_state(False)
        self.controller.state = ATMState.MAIN_MENU
        self.controller.status_message = "Transaction complete. Select next operation or eject card."
        self._render_current_state()

    def _back_to_menu(self) -> None:
        self.controller.state = ATMState.MAIN_MENU
        self.controller.status_message = "Select an operation from the menu."
        self._render_current_state()

    def _show_receipt_modal(self) -> None:
        if self.controller.last_receipt:
            ReceiptModal(self.root, self.controller.last_receipt)
        else:
            messagebox.showinfo("Receipt", "No receipt available for current action.", parent=self.root)
