"""
Customer Dashboard routes for Apex Federal Bank Web Portal.
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash
from core.models import TransactionType
from core.security import format_card_number, mask_card_number
from web.routes.auth import get_services, login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def overview():
    repo, service, audit = get_services()
    card_number = session["card_number"]

    # Retrieve customer's card & linked accounts
    card = repo.get_card(card_number)
    if not card:
        session.clear()
        return redirect(url_for("auth.login"))

    accounts = service.get_accounts_for_card(card_number)
    total_net_worth = sum(acc.balance for acc in accounts)

    # Recent transactions
    transactions = service.get_statement(card_number, limit=12)

    # Analytics breakdown for spending chart
    withdrawals_total = sum(t.amount for t in transactions if t.tx_type in (TransactionType.WITHDRAWAL, TransactionType.FAST_CASH))
    deposits_total = sum(t.amount for t in transactions if t.tx_type == TransactionType.DEPOSIT)
    transfers_total = sum(t.amount for t in transactions if t.tx_type == TransactionType.TRANSFER_OUT)

    return render_template(
        "dashboard.html",
        card=card,
        masked_card=mask_card_number(card.card_number),
        formatted_card=format_card_number(card.card_number),
        accounts=accounts,
        total_net_worth=total_net_worth,
        transactions=transactions,
        stats={
            "withdrawals": withdrawals_total,
            "deposits": deposits_total,
            "transfers": transfers_total,
        }
    )
