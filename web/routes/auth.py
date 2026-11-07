"""
Authentication routes for Apex Federal Bank Web Portal.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from core.bank_service import BankService
from core.exceptions import BankingError, CardBlockedError, InvalidPINError
from core.security import clean_card_number, format_card_number
from hardware.cash_dispenser import CashDispenser
from storage.audit_logger import AuditLogger
from storage.database import get_connection
from storage.repository import BankRepository

auth_bp = Blueprint("auth", __name__)


def get_services():
    conn = get_connection()
    repo = BankRepository(conn)
    audit = AuditLogger(conn)
    dispenser = CashDispenser(repo)
    service = BankService(repo, dispenser, audit)
    return repo, service, audit


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "card_number" not in session:
            flash("Please sign in to access your online banking dashboard.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Access denied. Administrator clearance required.", "danger")
            return redirect(url_for("dashboard.overview"))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "card_number" in session:
        return redirect(url_for("dashboard.overview"))

    repo, service, audit = get_services()

    if request.method == "POST":
        card_num_raw = request.form.get("card_number", "").strip()
        pin = request.form.get("pin", "").strip()
        card_num = clean_card_number(card_num_raw)

        if not card_num or not pin:
            flash("Please enter both card number and PIN.", "danger")
            return render_template("login.html")

        try:
            card = service.authenticate_card(card_num, pin)
            session["card_number"] = card.card_number
            session["holder_name"] = card.holder_name
            session["primary_account"] = card.primary_account_number
            session["is_admin"] = (card.card_number == "4000123411223342")

            audit.log_event("WEB_LOGIN_SUCCESS", card.card_number, "Customer signed into Web Portal", "INFO")
            flash(f"Welcome back, {card.holder_name}!", "success")

            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            if session.get("is_admin"):
                return redirect(url_for("admin.vault_dashboard"))
            return redirect(url_for("dashboard.overview"))

        except (InvalidPINError, CardBlockedError, BankingError) as e:
            flash(e.user_friendly_message, "danger")
            return render_template("login.html", card_number=format_card_number(card_num))

    # GET request - pass demo profiles for easy university presentation testing
    demo_profiles = [
        {"name": "Alexander Vance", "card": "4532-0150-1122-3341", "pin": "1234", "tier": "Standard Checking ($4,850)"},
        {"name": "Eleanor Sterling", "card": "4532-8820-1122-3344", "pin": "9999", "tier": "High Net Worth ($85,400)"},
        {"name": "Marcus Brody", "card": "4532-0091-1122-3343", "pin": "0000", "tier": "Student Checking ($45)"},
        {"name": "System Administrator", "card": "4000-1234-1122-3342", "pin": "7777", "tier": "Vault Management & Diagnostics"},
    ]
    return render_template("login.html", demo_profiles=demo_profiles)


@auth_bp.route("/fast-login/<card_number>/<pin>")
def fast_login(card_number: str, pin: str):
    """Convenience helper for university project live demonstrations."""
    repo, service, audit = get_services()
    clean_num = clean_card_number(card_number)
    try:
        card = service.authenticate_card(clean_num, pin)
        session["card_number"] = card.card_number
        session["holder_name"] = card.holder_name
        session["primary_account"] = card.primary_account_number
        session["is_admin"] = (card.card_number == "4000123411223342")
        flash(f"Signed in as {card.holder_name} (Demo Mode).", "success")
        if session.get("is_admin"):
            return redirect(url_for("admin.vault_dashboard"))
        return redirect(url_for("dashboard.overview"))
    except Exception as e:
        flash(f"Failed to sign in: {e}", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
def logout():
    card_num = session.get("card_number")
    if card_num:
        repo, service, audit = get_services()
        audit.log_event("WEB_LOGOUT", card_num, "Customer signed out of Web Portal", "INFO")
    session.clear()
    flash("You have been securely signed out. Thank you for banking with Apex Federal Bank.", "info")
    return redirect(url_for("public.index"))
