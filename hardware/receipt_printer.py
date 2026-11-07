"""
Thermal receipt formatting and generation for Apex Federal Bank ATM.
"""

from datetime import datetime
from typing import Dict, List, Optional

from config import (
    BANK_NAME,
    BANK_TAGLINE,
    CURRENCY_SYMBOL,
    SUPPORT_PHONE,
    TERMINAL_ID,
    TERMINAL_LOCATION,
)
from core.models import Account, Transaction, TransactionType
from core.security import mask_card_number


class ReceiptPrinter:
    """Emulates a 40-column thermal receipt printer."""

    WIDTH = 42

    @classmethod
    def _header(cls, tx_title: str) -> List[str]:
        lines = [
            "=" * cls.WIDTH,
            f"{BANK_NAME:^{cls.WIDTH}}",
            f"{BANK_TAGLINE:^{cls.WIDTH}}",
            "-" * cls.WIDTH,
            f"TERMINAL: {TERMINAL_ID:<16} DATE: {datetime.now().strftime('%Y-%m-%d')}",
            f"LOCATION: {TERMINAL_LOCATION[:20]:<16} TIME: {datetime.now().strftime('%H:%M:%S')}",
            "=" * cls.WIDTH,
            f"{tx_title:^{cls.WIDTH}}",
            "-" * cls.WIDTH,
        ]
        return lines

    @classmethod
    def _footer(cls) -> List[str]:
        return [
            "=" * cls.WIDTH,
            f"{'THANK YOU FOR BANKING WITH US!':^{cls.WIDTH}}",
            f"{'24/7 CUSTOMER CARE':^{cls.WIDTH}}",
            f"{SUPPORT_PHONE:^{cls.WIDTH}}",
            f"{'WWW.APEXBANK.COM':^{cls.WIDTH}}",
            "=" * cls.WIDTH,
        ]

    @classmethod
    def format_withdrawal(
        cls,
        tx: Transaction,
        account: Account,
        dispensed_bills: Optional[Dict[int, int]] = None
    ) -> str:
        lines = cls._header("CASH WITHDRAWAL RECEIPT")
        lines.extend([
            f"REF NUMBER:       {tx.tx_id}",
            f"CARD:             {mask_card_number(tx.card_number)}",
            f"ACCOUNT:          {account.account_type.value} ({account.account_number})",
            "-" * cls.WIDTH,
            f"AMOUNT DISPENSED: {CURRENCY_SYMBOL + f'{tx.amount:,.2f}':>18}",
        ])

        if dispensed_bills:
            lines.append("DISPENSED BILLS:")
            for denom in sorted(dispensed_bills.keys(), reverse=True):
                count = dispensed_bills[denom]
                if count > 0:
                    val = denom * count
                    val_str = CURRENCY_SYMBOL + f"{val:,.2f}"
                    lines.append(f"  {count} x {CURRENCY_SYMBOL}{denom:<4} = {val_str:>16}")

        lines.extend([
            f"ATM SURCHARGE:    {CURRENCY_SYMBOL + f'{tx.fee:,.2f}':>18}",
            "-" * cls.WIDTH,
            f"AVAILABLE BAL:    {CURRENCY_SYMBOL + f'{tx.balance_after:,.2f}':>18}",
            f"LEDGER BAL:       {CURRENCY_SYMBOL + f'{tx.balance_after:,.2f}':>18}",
        ])
        lines.extend(cls._footer())
        return "\n".join(lines)

    @classmethod
    def format_deposit(cls, tx: Transaction, account: Account) -> str:
        lines = cls._header("CASH DEPOSIT RECEIPT")
        lines.extend([
            f"REF NUMBER:       {tx.tx_id}",
            f"CARD:             {mask_card_number(tx.card_number)}",
            f"ACCOUNT:          {account.account_type.value} ({account.account_number})",
            "-" * cls.WIDTH,
            f"AMOUNT CREDITED:  {CURRENCY_SYMBOL + f'{tx.amount:,.2f}':>18}",
            f"AVAILABLE BAL:    {CURRENCY_SYMBOL + f'{tx.balance_after:,.2f}':>18}",
            "-" * cls.WIDTH,
            "FUNDS SUBJECT TO VERIFICATION.",
        ])
        lines.extend(cls._footer())
        return "\n".join(lines)

    @classmethod
    def format_transfer(
        cls,
        tx: Transaction,
        source_account: Account,
        target_account_number: str
    ) -> str:
        lines = cls._header("FUNDS TRANSFER RECEIPT")
        lines.extend([
            f"REF NUMBER:       {tx.tx_id}",
            f"CARD:             {mask_card_number(tx.card_number)}",
            f"FROM ACCOUNT:     {source_account.account_type.value} ({source_account.account_number})",
            f"TO ACCOUNT:       {target_account_number}",
            "-" * cls.WIDTH,
            f"TRANSFER AMOUNT:  {CURRENCY_SYMBOL + f'{tx.amount:,.2f}':>18}",
            f"FEE:              {CURRENCY_SYMBOL + f'{tx.fee:,.2f}':>18}",
            "-" * cls.WIDTH,
            f"AVAILABLE BAL:    {CURRENCY_SYMBOL + f'{tx.balance_after:,.2f}':>18}",
        ])
        lines.extend(cls._footer())
        return "\n".join(lines)

    @classmethod
    def format_balance_inquiry(cls, card_number: str, account: Account) -> str:
        lines = cls._header("BALANCE INQUIRY RECEIPT")
        lines.extend([
            f"CARD:             {mask_card_number(card_number)}",
            f"ACCOUNT:          {account.account_type.value} ({account.account_number})",
            f"ACCOUNT HOLDER:   {account.holder_name}",
            "-" * cls.WIDTH,
            f"AVAILABLE BAL:    {CURRENCY_SYMBOL + f'{account.balance:,.2f}':>18}",
            f"LEDGER BAL:       {CURRENCY_SYMBOL + f'{account.balance:,.2f}':>18}",
            f"TODAY WITHDRAWN:  {CURRENCY_SYMBOL + f'{account.daily_withdrawn_today:,.2f}':>18}",
        ])
        lines.extend(cls._footer())
        return "\n".join(lines)

    @classmethod
    def format_mini_statement(
        cls,
        card_number: str,
        account: Account,
        transactions: List[Transaction]
    ) -> str:
        lines = cls._header("MINI-STATEMENT RECEIPT")
        lines.extend([
            f"CARD:             {mask_card_number(card_number)}",
            f"ACCOUNT:          {account.account_type.value} ({account.account_number})",
            f"CURRENT BAL:      {CURRENCY_SYMBOL}{account.balance:>16,.2f}",
            "-" * cls.WIDTH,
            f"{'DATE':<10} {'TX TYPE':<16} {'AMOUNT':>14}",
            "-" * cls.WIDTH,
        ])
        if not transactions:
            lines.append(f"{'NO RECENT TRANSACTIONS FOUND':^{cls.WIDTH}}")
        else:
            for t in transactions[:8]:
                dt = t.timestamp.strftime("%m/%d %H:%M")
                type_abbr = t.tx_type.value[:14]
                sign = "+" if t.tx_type in (TransactionType.DEPOSIT, TransactionType.TRANSFER_IN) else "-"
                amt_str = f"{sign}{CURRENCY_SYMBOL}{t.amount:,.2f}"
                lines.append(f"{dt:<11} {type_abbr:<15} {amt_str:>14}")

        lines.extend(cls._footer())
        return "\n".join(lines)
