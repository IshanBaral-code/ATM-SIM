"""
Web Portal Runner for Apex Federal Bank Online Banking.
Run with: python run_web.py [--port 5000]
"""

import argparse
import sys
from web.app import create_app


def main():
    parser = argparse.ArgumentParser(description="Apex Federal Bank - Web Portal")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    app = create_app()

    print("\n" + "=" * 68)
    print("      🏛  APEX FEDERAL BANK - ONLINE BANKING PORTAL  🏛")
    print("=" * 68)
    print(f" ▶ Server running at: http://{args.host}:{args.port}")
    print(" ▶ Live ATM Fleet Status: http://{args.host}:{args.port}/atms")
    print(" ▶ Telemetry API: http://{args.host}:{args.port}/api/v1/atm/status")
    print("-" * 68)
    print(" University Project Quick Demo Logins:")
    print("   • Alexander Vance:  Card: 4532-0150-1122-3341 | PIN: 1234 ($4,850)")
    print("   • Eleanor Sterling: Card: 4532-8820-1122-3344 | PIN: 9999 ($85,400)")
    print("   • Marcus Brody:     Card: 4532-0091-1122-3343 | PIN: 0000 ($45)")
    print("   • System Admin:     Card: 4000-1234-1122-3342 | PIN: 7777 (Vault Admin)")
    print("=" * 68 + "\n")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
