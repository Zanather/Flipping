"""
D2R Inventory Assistant - Configuration
"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required for bundled exe


def _get_base_dir():
    """Get the base directory for bundled resources (read-only)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _get_user_data_dir():
    """Get the writable data directory for user files (inventory, trade history, cache).
    When running as a bundled exe, stores data next to the executable so it persists."""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "d2r_data")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "d2r-assistant-dev-key")
    DEBUG = os.getenv("DEBUG", "false" if getattr(sys, 'frozen', False) else "true").lower() == "true"

    # D2JSP Integration
    D2JSP_USERNAME = os.getenv("D2JSP_USERNAME", "")
    D2JSP_SESSION_ID = os.getenv("D2JSP_SESSION_ID", "")

    # Traderie Integration
    TRADERIE_API_KEY = os.getenv("TRADERIE_API_KEY", "")

    # Base directory for bundled resources (templates, static, item_database)
    BASE_DIR = _get_base_dir()

    # Writable data directory for user files
    DATA_DIR = _get_user_data_dir()
    INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
    PRICE_CACHE_FILE = os.path.join(DATA_DIR, "price_cache.json")

    # Read-only bundled data (item database)
    BUNDLED_DATA_DIR = os.path.join(BASE_DIR, "data")

    # Price cache duration in seconds (30 minutes)
    PRICE_CACHE_TTL = 1800

    # Default currency (fg = Forum Gold, hr = High Runes)
    DEFAULT_CURRENCY = "fg"

    # HR to FG conversion rates (approximate, updated from market data)
    HR_TO_FG = {
        "Ber": 3500,
        "Jah": 3200,
        "Lo": 1200,
        "Sur": 1700,
        "Ohm": 600,
        "Vex": 350,
        "Gul": 175,
        "Ist": 100,
        "Mal": 55,
        "Um": 30,
        "Pul": 15,
        "Lem": 8,
        "Fal": 4,
        "Ko": 3,
        "Lum": 2,
        "Io": 1,
        "Hel": 1,
        "Dol": 1,
        "Sol": 1,
        "Shael": 2,
        "Amn": 1,
        "Thul": 1,
        "Ort": 1,
        "Ral": 1,
        "Tal": 1,
        "Ith": 1,
        "Eth": 1,
        "Nef": 1,
        "Tir": 1,
        "Eld": 1,
        "El": 1,
        "Zod": 800,
        "Cham": 400,
    }
