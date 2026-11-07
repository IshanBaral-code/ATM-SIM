"""
Administrator and ATM Fleet Management routes for Web Portal.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import DEFAULT_CASSETTE_INVENTORY, TERMINAL_ID, TERMINAL_LOCATION
from web.routes.auth import admin_required, get_services, login_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_required
def vault_dashboard():
    repo, service, audit = get_services()

    # Cassette inventory
    cassettes = repo.get_cassettes()
    total_vault = sum(denom * count for denom, count in cassettes.items())

    # Demo accounts directory
    demo_cards = repo.get_all_demo_cards()

    # Security & transaction audit trail
    logs = repo.get_audit_logs(limit=40)

    # Max limits for cassette gauge calculation
    max_counts = {100: 100, 50: 100, 20: 300, 10: 300}
    cassette_stats = []
    for denom, count in sorted(cassettes.items(), reverse=True):
        m = max_counts.get(denom, 200)
        pct = min(100.0, (count / m) * 100.0)
        cassette_stats.append({
            "denomination": denom,
            "count": count,
            "value": denom * count,
            "max": m,
            "pct": round(pct, 1)
        })

    return render_template(
        "admin.html",
        terminal_id=TERMINAL_ID,
        terminal_location=TERMINAL_LOCATION,
        total_vault=total_vault,
        cassette_stats=cassette_stats,
        demo_cards=demo_cards,
        audit_logs=logs
    )


@admin_bp.route("/admin/refill-vault", methods=["POST"])
@login_required
@admin_required
def refill_vault():
    repo, service, audit = get_services()
    repo.update_cassettes(DEFAULT_CASSETTE_INVENTORY)
    audit.log_event("VAULT_REFILLED", None, "ATM Cassettes replenished to standard capacity via Web Portal", "ADMIN")
    flash("ATM Cassettes replenished to standard capacity ($20,000.00).", "success")
    return redirect(url_for("admin.vault_dashboard"))
