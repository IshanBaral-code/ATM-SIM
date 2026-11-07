"""
Public marketing, landing page, and ATM locator routes.
"""

from flask import Blueprint, render_template, Response, session, redirect, url_for
from config import BANK_NAME, BANK_TAGLINE, TERMINAL_ID, TERMINAL_LOCATION
from core.security import mask_card_number
from web.routes.auth import get_services, login_required

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    if "card_number" in session:
        return redirect(url_for("dashboard.overview"))
    return render_template("index.html")


@public_bp.route("/atms")
def atm_locator():
    repo, service, audit = get_services()
    cassettes = repo.get_cassettes()
    total_cash = sum(d * c for d, c in cassettes.items())

    terminals = [
        {
            "id": TERMINAL_ID,
            "name": "Apex Flagship Terminal",
            "address": TERMINAL_LOCATION,
            "city": "New York, NY 10005",
            "status": "Online & Operational",
            "cash_available": f"${total_cash:,.2f}",
            "features": ["24/7 Access", "Cash Dispenser ($10-$100)", "Check/Cash Deposit", "Audio Guidance", "Touchscreen Display"],
            "is_primary": True
        },
        {
            "id": "APX-3019",
            "name": "Midtown Manhattan Branch",
            "address": "450 Lexington Ave, Concourse Level",
            "city": "New York, NY 10017",
            "status": "Online & Operational",
            "cash_available": "$18,500.00",
            "features": ["Drive-Up ATM", "High-Speed Cash Dispense", "Envelope-Free Deposit", "Multilingual"],
            "is_primary": False
        },
        {
            "id": "APX-5510",
            "name": "JFK International Airport - Terminal 4",
            "address": "Arrivals Hall Gate 12",
            "city": "Jamaica, NY 11430",
            "status": "Online & Operational",
            "cash_available": "$25,000.00",
            "features": ["Currency Exchange", "24/7 International Access", "Contactless Tap"],
            "is_primary": False
        }
    ]

    return render_template("atm_locator.html", terminals=terminals)


@public_bp.route("/statement")
@login_required
def statement():
    repo, service, audit = get_services()
    card_number = session["card_number"]
    card = repo.get_card(card_number)
    accounts = service.get_accounts_for_card(card_number)
    transactions = service.get_statement(card_number, limit=50)

    return render_template(
        "statement.html",
        card=card,
        masked_card=mask_card_number(card.card_number),
        accounts=accounts,
        transactions=transactions
    )


@public_bp.route("/statement/download-csv")
@login_required
def download_csv():
    repo, service, audit = get_services()
    card_number = session["card_number"]
    transactions = service.get_statement(card_number, limit=100)

    csv_lines = ["Transaction ID,Date/Time,Card Number,Account Number,Type,Amount,Balance After,Description\n"]
    for t in transactions:
        csv_lines.append(
            f'"{t.tx_id}","{t.timestamp.strftime("%Y-%m-%d %H:%M:%S")}","{mask_card_number(t.card_number)}","{t.account_number}","{t.tx_type.value}",{t.amount:.2f},{t.balance_after:.2f},"{t.description}"\n'
        )

    response = Response("".join(csv_lines), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=apex_statement.csv"
    return response
