"""
Main entrypoint for the Apex Federal Bank ATM Simulation.
Launches the Graphical Kiosk UI by default, or Terminal CLI mode when --cli is passed.
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Apex Federal Bank - ATM Kiosk Simulation")
    parser.add_argument("--cli", action="store_true", help="Launch in Terminal CLI mode instead of Graphical Kiosk")
    args = parser.parse_args()

    if args.cli:
        from ui.cli.cli_kiosk import CLIKiosk
        kiosk = CLIKiosk()
        try:
            kiosk.run()
        except KeyboardInterrupt:
            print("\nATM Terminal shutdown.")
            sys.exit(0)
    else:
        import tkinter as tk
        from ui.gui.app import ATMApplication

        root = tk.Tk()
        app = ATMApplication(root)
        root.mainloop()


if __name__ == "__main__":
    main()
