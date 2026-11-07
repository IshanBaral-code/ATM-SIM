"""
Card services, limits, freeze/unfreeze, and PIN updates for Web Portal.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import DAILY_WITHDRAWAL_LIMIT
from core.exceptions import BankingError
from core.security import format_card_number, mask_card_number
from web.routes.auth import get_services, login_required

cards_bp = Blueprint("cards", __name__)


@cards_bp.route("/cards", methods=["GET", "POST"])
@login_required
def manage():
    repo, service, audit = get_services()
    card_number = session["card_number"]
    card = repo.get_card(card_number)
    primary_acc = repo.get_account(card.primary_account_number)

    daily_spent = primary_acc.daily_withdrawn_today if primary_acc else 0.0
    limit_pct = min(100.0, (daily_spent / DAILY_WITHDRAWAL_LIMIT) * 100.0)

    return render_template(
        "cards.html",
        card=card,
        formatted_card=format_card_number(card.card_number),
        masked_card=mask_card_number(card.card_number),
        daily_spent=daily_spent,
        daily_limit=DAILY_WITHDRAWAL_LIMIT,
        limit_pct=round(limit_pct, 1)
    )


@cards_bp.route("/cards/toggle-freeze", methods=["POST"])
@login_required
def toggle_freeze():
    repo, service, audit = get_services()
    card_number = session["card_number"]
    card = repo.get_card(card_number)

    new_state = not card.is_blocked
    repo.update_card_security(card_number, card.failed_attempts, is_blocked=new_state)

    status_str = "frozen" if new_state else "unfrozen and active"
    audit.log_event("WEB_CARD_STATUS_CHANGE", card_number, f"Card {status_str} via Web Portal", "SECURITY")
    flash(f"Your debit card is now {status_str}.", "info" if new_state else "success")

    return redirect(url_for("cards.manage"))


@cards_bp.route("/cards/change-pin", methods=["POST"])
@login_required
def change_pin():
    repo, service, audit = get_services()
    card_number = session["card_number"]

    old_pin = request.form.get("old_pin", "").strip()
    new_pin = request.form.get("new_pin", "").strip()
    confirm_pin = request.form.get("confirm_pin", "").strip()

    if new_pin != confirm_pin:
        flash("New PIN and confirmation PIN do not match.", "danger")
        return redirect(url_for("cards.manage"))

    try:
        service.change_pin(card_number, old_pin, new_pin)
        flash("Your card PIN has been updated successfully.", "success")
    except BankingError as e:
        flash(e.user_friendly_message, "danger")

    return redirect(url_for("cards.manage"))
