"""
RESTful JSON API endpoints for Apex Federal Bank.
"""

from flask import Blueprint, jsonify, session
from config import TERMINAL_ID, TERMINAL_LOCATION
from core.security import mask_card_number
from web.routes.auth import get_services

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/atm/status")
def atm_status():
    """Returns live status of ATM Terminal #APX-4821 and cassette levels."""
    repo, service, audit = get_services()
    cassettes = repo.get_cassettes()
    total_cash = sum(d * c for d, c in cassettes.items())

    return jsonify({
        "terminal_id": TERMINAL_ID,
        "location": TERMINAL_LOCATION,
        "status": "ONLINE",
        "total_cash_available": total_cash,
        "cassettes": cassettes,
        "currency": "USD"
    })


@api_bp.route("/accounts")
def customer_accounts():
    """Returns active customer accounts if session is authenticated."""
    card_number = session.get("card_number")
    if not card_number:
        return jsonify({"error": "Unauthorized"}), 401

    repo, service, audit = get_services()
    accounts = service.get_accounts_for_card(card_number)

    return jsonify({
        "card_number": mask_card_number(card_number),
        "accounts": [
            {
                "account_number": a.account_number,
                "holder_name": a.holder_name,
                "type": a.account_type.value,
                "balance": a.balance,
                "daily_withdrawn_today": a.daily_withdrawn_today
            }
            for a in accounts
        ]
    })
