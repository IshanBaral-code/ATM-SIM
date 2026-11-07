# Apex Federal Bank - ATM & Online Banking Ecosystem

An enterprise-grade, full-stack financial ecosystem in Python combining an authentic **Automated Teller Machine (ATM) Kiosk Simulation** with a **Modern Online Banking Web Portal**.

Built specifically to meet the highest university academic and project evaluation criteria, featuring domain-driven layered architecture, ACID-compliant SQLite persistence, PBKDF2-HMAC-SHA256 salted cryptography, dynamic cash denomination dispensing algorithms, and real-time transaction synchronization between web and physical kiosk hardware.

---

## 🏛 System Architecture Overview

```
                                  APEX FEDERAL BANK ECOSYSTEM
                                
       ┌───────────────────────────────┐           ┌───────────────────────────────┐
       │     GRAPHICAL ATM KIOSK       │           │   ONLINE BANKING WEB PORTAL   │
       │   Tkinter / LCD Screen UI     │           │    Flask / Modern Responsive  │
       │  Physical PIN Pad & Shutter   │           │   Accounts, Transfers, Cards  │
       └──────────────┬────────────────┘           └──────────────┬────────────────┘
                      │                                           │
                      ▼                                           ▼
       ┌───────────────────────────────────────────────────────────────────────────┐
       │                        CORE BANKING SERVICE LAYER                         │
       │     PBKDF2-SHA256 PIN Security  •  Luhn Checksum  •  Daily Limit Engine    │
       │          Multi-Denomination Dispenser  •  Thermal Receipt Formatter        │
       └─────────────────────────────────────┬─────────────────────────────────────┘
                                             │
                                             ▼
       ┌───────────────────────────────────────────────────────────────────────────┐
       │                     SHARED PERSISTENCE & AUDIT LAYER                      │
       │           SQLite Database (ACID)  •  Regulatory Audit Log File            │
       └───────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Capabilities

### 1. Online Banking Web Portal (`run_web.py`)
- **Executive FinTech Interface**: Deep sapphire & neon emerald palette with translucent cards, custom CSS layout, and zero external npm dependencies.
- **Total Net Worth & Balance Analytics**: Real-time asset aggregation across Checking, Savings, and Money Market accounts.
- **Interactive 3D Virtual Debit Card**: Emulates a physical chip card with cardholder details, expiration, CVV, and live contactless indicator.
- **One-Touch Card Freeze / Lock**: Instantly freeze your debit card from the web browser to immediately prevent any physical ATM withdrawals.
- **Fast Inter-Account & Peer Transfers**: Atomic fund movement with instant balance validation and audit reference generation.
- **Electronic Statement & CSV Export**: Detailed transaction history with 1-click CSV download.
- **Fleet ATM Locator**: Real-time directory of all bank ATMs including live telemetry of Terminal `#APX-4821`.
- **Manager & Vault Admin Console**: Inspect live cassette banknote counts (\$100, \$50, \$20, \$10 notes) and trigger vault replenishment.

### 2. Physical ATM Kiosk Simulation (`main.py`)
- **Kiosk Hardware Frame**: Dark brushed metal chassis, 256-bit encrypted LCD monitor, audio toggle, and hardware status LEDs.
- **Tactile Keypad**: 3x4 numeric pad with color-coded **CANCEL** (Red), **CLEAR** (Yellow), and **ENTER** (Green) action keys. Supports physical computer keyboard keys (0-9, Enter, Backspace, Escape).
- **Cassette Bill Dispenser**: Greedily solves the optimal note combination across \$100, \$50, \$20, and \$10 bills while adjusting cassette stock.
- **Thermal Paper Receipts**: Authentic 42-column monospace thermal slip generator with export to `.txt`.
- **Audio Feedback**: Authentic mechanical beeps, dispense sound effects, success chimes, and optional voice assistance via `pyttsx3`.

---

## 💳 Pre-Seeded Academic Demo Profiles

The database (`data/atm_banking.db`) is automatically initialized and seeded with mathematically valid Luhn card numbers:

| Cardholder Profile | Card Number | PIN | Primary Account | Starting Balances | Demonstration Role |
|---|---|---|---|---|---|
| **Alexander Vance** | `4532-0150-1122-3341` | `1234` | Checking (`ACT-1001-CHK`) | Checking: **$4,850.00**<br>Savings: **$15,200.00** | Standard user (Multi-account transfers) |
| **Eleanor Sterling** | `4532-8820-1122-3344` | `9999` | Checking (`ACT-2001-CHK`) | Checking: **$85,400.00**<br>Money Market: **$150,000.00** | High-Net-Worth customer |
| **Marcus Brody** | `4532-0091-1122-3343` | `0000` | Checking (`ACT-3001-CHK`) | Checking: **$45.00** | Overdraft / Low-balance rejection |
| **System Administrator** | `4000-1234-1122-3342` | `7777` | System (`ACT-9999-SYS`) | Vault Reserves: **$1,000,000.00** | ATM Fleet & Cassette Vault Refill |

---

## 🚀 How to Run the Applications

### 1. Launch the Online Banking Web Portal
Open a terminal in `d:\atm_simulation`:
```powershell
python run_web.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
*Note*: Click on any of the **One-Click Demo Profiles** on the login page to sign in immediately without manual typing!

### 2. Launch the Graphical ATM Kiosk (Desktop App)
Open a second terminal window:
```powershell
python main.py
```
*Keyboard shortcuts supported*:
- **Numeric Keys [0-9]**: Press on your computer keyboard or click on screen.
- **Enter**: Confirm PIN, withdrawal, or action.
- **Backspace**: Clear entered digit.
- **Escape**: Cancel / abort operation.

### 3. Launch the Terminal CLI Mode (Headless / Console)
```powershell
python main.py --cli
```

### 4. Run the Complete Automated Test Suite (29 Tests)
```powershell
python -m unittest discover -s tests -v
```

---

## 📁 Directory Structure

```
d:\atm_simulation/
├── config.py                 # Banking configurations, limits, denominations
├── main.py                   # ATM application entrypoint (GUI / CLI)
├── run_web.py                # Web Portal entrypoint (Flask)
├── requirements.txt          # Python dependencies
├── README.md                 # Complete system documentation
├── core/
│   ├── models.py             # Data entities (Account, Card, Transaction)
│   ├── exceptions.py         # Custom domain exceptions
│   ├── security.py           # PBKDF2-SHA256 hashing, Luhn check, PII masking
│   ├── bank_service.py       # Core banking business logic & transaction handling
│   └── atm_controller.py     # State machine coordinating user session lifecycle
├── hardware/
│   ├── card_reader.py        # Motorized card reader emulation
│   ├── cash_dispenser.py     # Multi-denomination bill solver & cassette tracking
│   ├── receipt_printer.py    # Thermal paper receipt formatter
│   └── speaker.py            # Keypad audio beeps, chimes, and voice assistance
├── storage/
│   ├── database.py           # SQLite connection pool & automated demo seeding
│   ├── repository.py         # Data Access Object (DAO) for atomic transactions
│   └── audit_logger.py       # Regulatory event audit trail (DB + log file)
├── ui/
│   ├── theme.py              # Visual styling tokens & color palettes
│   ├── gui/                  # Modern Tkinter ATM Kiosk application
│   │   ├── app.py            # Main application window & event router
│   │   ├── components/       # Screen, tactile Keypad, Card Slot, Receipt Modal
│   │   └── screens/          # Screen views (PIN, Menu, Withdraw, Admin, etc.)
│   └── cli/
│       └── cli_kiosk.py      # Rich ANSI terminal interface
├── web/
│   ├── app.py                # Flask application factory
│   ├── routes/
│   │   ├── auth.py           # Authentication, sessions, fast-demo logins
│   │   ├── dashboard.py      # Customer net worth, balances, spending analytics
│   │   ├── transfers.py      # Account-to-account funds transfer
│   │   ├── cards.py          # 3D virtual card, freeze toggle, PIN update
│   │   ├── admin.py          # ATM vault diagnostics, fleet monitoring, audit log
│   │   ├── public.py         # Landing page, ATM locator, CSV export
│   │   └── api.py            # RESTful JSON telemetry API
│   ├── templates/            # Responsive Jinja2 HTML5 templates
│   └── static/               # FinTech CSS3 stylesheet & interactive JavaScript
└── tests/
    ├── test_security.py      # Cryptography, salt, Luhn, masking tests
    ├── test_cash_dispenser.py # Denomination optimization & inventory tests
    ├── test_bank_service.py  # Withdraw, deposit, transfer, lockout tests
    ├── test_integration.py   # Full user session journey end-to-end test
    └── test_web.py           # Web portal endpoints, login, transfers, CSV export
```
