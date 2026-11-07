"""
Funds transfer routes for Apex Federal Bank Web Portal.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from core.exceptions import BankingError
from web.routes.auth import get_services, login_required

transfers_bp = Blueprint("transfers", __name__)


@transfers_bp.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    repo, service, audit = get_services()
    card_number = session["card_number"]
    user_accounts = service.get_accounts_for_card(card_number)

    if request.method == "POST":
        source_acc = request.form.get("source_account", "").strip()
        target_acc = request.form.get("target_account", "").strip()
        amount_str = request.form.get("amount", "").strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise BankingError("Transfer amount must be greater than zero.")

            tx = service.transfer(card_number, source_acc, target_acc, amount)
            flash(f"Successfully transferred ${amount:,.2f} to {target_acc}. Transaction Ref: {tx.tx_id}", "success")
            return redirect(url_for("dashboard.overview"))

        except ValueError:
            flash("Please enter a valid numeric transfer amount.", "danger")
        except BankingError as e:
            flash(e.user_friendly_message, "danger")

    # Sample destination contacts for convenient university testing
    sample_recipients = [
        {"account": "ACT-1002-SAV", "name": "Personal High-Yield Savings"},
        {"account": "ACT-2001-CHK", "name": "Eleanor Sterling (Checking)"},
        {"account": "ACT-3001-CHK", "name": "Marcus Brody (Checking)"},
    ]

    return render_template(
        "transfer.html",
        user_accounts=user_accounts,
        sample_recipients=sample_recipients
    )
