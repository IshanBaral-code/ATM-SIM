"""
Rich Terminal Command Line Interface (CLI) for Apex Federal Bank ATM.
"""

import getpass
import os
import sys
import time

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

from config import (
    BANK_NAME,
    BANK_TAGLINE,
    CURRENCY_SYMBOL,
    FAST_CASH_AMOUNTS,
    TERMINAL_ID,
    TERMINAL_LOCATION,
)
from core.atm_controller import ATMController, ATMState
from core.exceptions import BankingError, CardBlockedError, InvalidPINError
from core.security import format_card_number, mask_card_number


class CLIKiosk:
    """Provides a terminal-based ATM kiosk experience with ANSI formatting."""

    def __init__(self):
        self.controller = ATMController(tts_enabled=False)

    def _c(self, color_code: str, text: str) -> str:
        if HAS_COLOR:
            return f"{color_code}{text}{Style.RESET_ALL}"
        return text

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def print_banner(self) -> None:
        width = 66
        print(self._c(Fore.CYAN, "╔" + "═" * (width - 2) + "╗"))
        print(self._c(Fore.CYAN, f"║{BANK_NAME:^{width - 2}}║"))
        print(self._c(Fore.BLUE, f"║{BANK_TAGLINE:^{width - 2}}║"))
        print(self._c(Fore.CYAN, f"║ TERMINAL: {TERMINAL_ID:<20} LOCATION: {TERMINAL_LOCATION[:25]:<22} ║"))
        print(self._c(Fore.CYAN, "╚" + "═" * (width - 2) + "╝"))

    def run(self) -> None:
        while True:
            self.clear()
            self.print_banner()

            if self.controller.state == ATMState.IDLE:
                if not self._idle_screen():
                    break
            elif self.controller.state == ATMState.PIN_ENTRY:
                self._pin_screen()
            elif self.controller.state == ATMState.ACCOUNT_SELECTION:
                self._account_select_screen()
            elif self.controller.state == ATMState.MAIN_MENU:
                self._main_menu_screen()
            elif self.controller.state == ATMState.ADMIN_MENU:
                self._admin_menu_screen()

    def _idle_screen(self) -> bool:
        print(self._c(Fore.YELLOW, "\n[ 💳 INSERT CARD / WELCOME SCREEN ]"))
        print("Available Demo Accounts for Testing:")
        print("  1. Alexander Vance   - Card: 4532-0150-1122-3341 (PIN: 1234) [Standard: $4,850]")
        print("  2. Eleanor Sterling  - Card: 4532-8820-1122-3344 (PIN: 9999) [HNW: $85,400]")
        print("  3. Marcus Brody      - Card: 4532-0091-1122-3343 (PIN: 0000) [Low Bal: $45]")
        print("  4. Administrator     - Card: 4000-1234-1122-3342 (PIN: 7777) [Tech Diagnostics]")
        print("  5. Manual 16-Digit Card Entry")
        print("  Q. Shut Down ATM Terminal")

        choice = input("\nSelect an option [1-5, Q]: ").strip().upper()
        if choice == "Q":
            print(self._c(Fore.YELLOW, "\nShutting down ATM terminal. Goodbye."))
            return False

        card_map = {
            "1": "4532015011223341",
            "2": "4532882011223344",
            "3": "4532009111223343",
            "4": "4000123411223342",
        }

        if choice in card_map:
            card_num = card_map[choice]
        elif choice == "5":
            card_num = input("Enter 16-digit card number: ").strip()
        else:
            input(self._c(Fore.RED, "Invalid option. Press Enter to retry..."))
            return True

        try:
            self.controller.insert_card(card_num)
        except BankingError as e:
            input(self._c(Fore.RED, f"\n{e.user_friendly_message}\nPress Enter to continue..."))
        return True

    def _pin_screen(self) -> None:
        card = self.controller.current_card
        print(self._c(Fore.CYAN, f"\nWelcome, {card.holder_name.upper()}"))
        print(f"Card Number: {mask_card_number(card.card_number)}")
        print(self._c(Fore.YELLOW, "Enter [C] to Cancel & Eject Card."))

        pin = getpass.getpass("Enter 4-digit PIN: ").strip()
        if pin.upper() == "C":
            self.controller.eject_and_reset()
            return

        try:
            self.controller.enter_pin(pin)
        except (InvalidPINError, CardBlockedError) as e:
            input(self._c(Fore.RED, f"\n{e.user_friendly_message}\nPress Enter to continue..."))

    def _account_select_screen(self) -> None:
        print(self._c(Fore.CYAN, "\n[ SELECT ACCOUNT FOR THIS SESSION ]"))
        for i, acc in enumerate(self.controller.available_accounts, 1):
            print(f"  {i}. {acc.account_type.value:<14} ({acc.account_number}) - Available: ${acc.balance:,.2f}")

        choice = input("\nSelect account number: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.controller.available_accounts):
                self.controller.select_account(self.controller.available_accounts[idx].account_number)
            else:
                input(self._c(Fore.RED, "Invalid selection. Press Enter..."))
        except ValueError:
            input(self._c(Fore.RED, "Invalid input. Press Enter..."))

    def _main_menu_screen(self) -> None:
        acc = self.controller.current_account
        print(self._c(Fore.GREEN, f"\nACTIVE ACCOUNT: {acc.account_type.value} ({acc.account_number}) | BALANCE: ${acc.balance:,.2f}"))
        print("\nTRANSACTION MENU:")
        print("  1. ⚡ Fast Cash ($100)")
        print("  2. 🏧 Custom Cash Withdrawal")
        print("  3. 📥 Cash Deposit")
        print("  4. 🔄 Transfer Funds")
        print("  5. 📊 Balance Inquiry")
        print("  6. 🧾 Mini-Statement")
        print("  7. 🔑 Change PIN")
        print("  8. ⏏ Finish & Eject Card")

        choice = input("\nSelect transaction [1-8]: ").strip()

        if choice == "1":
            self._do_withdraw(100.0, is_fast_cash=True)
        elif choice == "2":
            amt_str = input(f"Enter amount in multiples of $10: ").strip()
            try:
                amt = float(amt_str)
                self._do_withdraw(amt, is_fast_cash=False)
            except ValueError:
                input(self._c(Fore.RED, "Invalid amount. Press Enter..."))
        elif choice == "3":
            amt_str = input(f"Enter cash deposit amount: ").strip()
            try:
                amt = float(amt_str)
                tx = self.controller.process_deposit(amt)
                print(self._c(Fore.GREEN, f"\n✔ Deposited ${amt:,.2f}. New Balance: ${tx.balance_after:,.2f}"))
                self._offer_receipt()
            except BankingError as e:
                input(self._c(Fore.RED, f"\n{e.user_friendly_message}\nPress Enter..."))
        elif choice == "4":
            print("\nDestinations: [1] Personal Savings (ACT-1002-SAV), [2] Manual Account")
            t_choice = input("Choice: ").strip()
            target_acc = "ACT-1002-SAV" if t_choice == "1" else input("Enter Destination Account Number: ").strip()
            amt_str = input("Enter transfer amount: ").strip()
            try:
                amt = float(amt_str)
                tx = self.controller.process_transfer(target_acc, amt)
                print(self._c(Fore.GREEN, f"\n✔ Transferred ${amt:,.2f} to {target_acc}. New Balance: ${tx.balance_after:,.2f}"))
                self._offer_receipt()
            except BankingError as e:
                input(self._c(Fore.RED, f"\n{e.user_friendly_message}\nPress Enter..."))
        elif choice == "5":
            self.controller.view_balance()
            print("\n" + self.controller.last_receipt)
            input("\nPress Enter to return to menu...")
        elif choice == "6":
            self.controller.view_statement()
            print("\n" + self.controller.last_receipt)
            input("\nPress Enter to return to menu...")
        elif choice == "7":
            old_p = getpass.getpass("Enter current PIN: ").strip()
            new_p = getpass.getpass("Enter new 4-digit PIN: ").strip()
            try:
                self.controller.process_pin_change(old_p, new_p)
                input(self._c(Fore.GREEN, "\n✔ PIN updated successfully! Press Enter..."))
            except BankingError as e:
                input(self._c(Fore.RED, f"\n{e.user_friendly_message}\nPress Enter..."))
        elif choice == "8":
            self.controller.eject_and_reset()
            input(self._c(Fore.YELLOW, "\nCard ejected. Thank you for banking with us! Press Enter..."))

    def _do_withdraw(self, amount: float, is_fast_cash: bool) -> None:
        try:
            tx, dispense = self.controller.process_withdrawal(amount, is_fast_cash=is_fast_cash)
            print(self._c(Fore.GREEN, f"\n✔ DISPENSING ${amount:,.2f} CASH..."))
            for denom, count in sorted(dispense.bills.items(), reverse=True):
                print(f"  • {count} x ${denom} note(s)")
            print(self._c(Fore.GREEN, f"Remaining Balance: ${tx.balance_after:,.2f}"))
            self._offer_receipt()
        except BankingError as e:
            input(self._c(Fore.RED, f"\n{e.user_friendly_message}\nPress Enter..."))

    def _offer_receipt(self) -> None:
        want = input("\nWould you like a printed receipt? [Y/N]: ").strip().upper()
        if want == "Y" and self.controller.last_receipt:
            print("\n" + self.controller.last_receipt)
        input("\nPress Enter to continue...")

    def _admin_menu_screen(self) -> None:
        print(self._c(Fore.MAGENTA, "\n[ 🛠 ATM DIAGNOSTIC & VAULT CONSOLE ]"))
        cassettes = self.controller.cash_dispenser.inventory
        print("Cassette Inventory:")
        total = 0
        for denom, count in sorted(cassettes.items(), reverse=True):
            val = denom * count
            total += val
            print(f"  ${denom:<3} : {count:<4} notes  (${val:,.2f})")
        print(self._c(Fore.CYAN, f"Total Vault Cash: ${total:,.2f}"))

        print("\nAdmin Options:")
        print("  1. Refill Cassettes to Full Capacity")
        print("  2. View Recent Audit Trail")
        print("  3. Eject Admin Card & Exit")

        c = input("\nSelect [1-3]: ").strip()
        if c == "1":
            from config import DEFAULT_CASSETTE_INVENTORY
            self.controller.cash_dispenser.reload_cassettes(DEFAULT_CASSETTE_INVENTORY)
            input(self._c(Fore.GREEN, "\n✔ Cassettes refilled to full stock. Press Enter..."))
        elif c == "2":
            logs = self.controller.repo.get_audit_logs(limit=10)
            print("\nAudit Log Entries:")
            for l in logs:
                print(f"  [{l['timestamp']}] {l['event_type']:<15} {l['card_masked']:<19} {l['details']}")
            input("\nPress Enter...")
        elif c == "3":
            self.controller.eject_and_reset()
