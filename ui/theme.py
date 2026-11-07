"""
Visual design system and theme tokens for the Apex Federal Bank ATM Kiosk.
"""

# Color Palette - Modern Banking & Kiosk Hardware
COLOR_FRAME_OUTER = "#11141C"       # Outer kiosk chassis
COLOR_FRAME_BEZEL = "#1E2433"       # Bezel around screen & hardware
COLOR_FRAME_BORDER = "#2E384D"      # Subtle hardware seams

# Display Colors
COLOR_SCREEN_BG = "#0A0F1D"         # Deep sapphire terminal display
COLOR_SCREEN_SURFACE = "#121A2F"    # Elevated UI panels on screen
COLOR_SCREEN_SURFACE_ALT = "#192442"# Interactive card panels
COLOR_SCREEN_BORDER = "#1E2C4F"     # Glass screen borders

# Typography & Accents
COLOR_TEXT_PRIMARY = "#F8FAFC"      # Crisp white
COLOR_TEXT_SECONDARY = "#94A3B8"    # Slate grey
COLOR_TEXT_MUTED = "#64748B"        # Low contrast info
COLOR_ACCENT_CYAN = "#38BDF8"       # Apex Cyan (brand primary)
COLOR_ACCENT_BLUE = "#2563EB"       # Classic banking royal blue
COLOR_ACCENT_HOVER = "#60A5FA"

# Status & Hardware Signals
COLOR_SUCCESS = "#10B981"           # Emerald green (Enter / Dispense)
COLOR_SUCCESS_HOVER = "#059669"
COLOR_WARNING = "#F59E0B"           # Amber (Clear / Attention)
COLOR_WARNING_HOVER = "#D97706"
COLOR_DANGER = "#EF4444"            # Rose red (Cancel / Lockout)
COLOR_DANGER_HOVER = "#DC2626"
COLOR_LED_ACTIVE = "#22C55E"        # Glowing card slot indicator
COLOR_LED_IDLE = "#EAB308"

# Thermal Paper Receipt Palette
COLOR_RECEIPT_BG = "#FAF8F5"        # Warm thermal paper
COLOR_RECEIPT_TEXT = "#1E293B"      # Dark thermal ink
COLOR_RECEIPT_BORDER = "#E2DCD5"
COLOR_RECEIPT_HEADER = "#0F172A"

# Hardware Keypad Colors
COLOR_KEYPAD_BG = "#151B28"
COLOR_KEYPAD_BTN = "#252E42"
COLOR_KEYPAD_BTN_HOVER = "#343F5A"
COLOR_KEYPAD_TEXT = "#E2E8F0"

# Typography
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

# Font Specs (Family, Size, Weight)
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13, "normal")
FONT_HEADING = (FONT_FAMILY, 15, "bold")
FONT_BODY = (FONT_FAMILY, 11, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 9, "normal")
FONT_KEYPAD = (FONT_FAMILY, 14, "bold")
FONT_KEYPAD_FN = (FONT_FAMILY, 10, "bold")
FONT_RECEIPT = (FONT_MONO, 9, "normal")
FONT_RECEIPT_BOLD = (FONT_MONO, 9, "bold")
