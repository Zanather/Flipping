"""
D2R Inventory Assistant - Pricing Engine

Provides market pricing, FG/HR conversion, and price estimation
for D2R items across D2JSP and Traderie markets.
"""
import json
import os
import time
from datetime import datetime


class PriceEngine:
    """Handles D2R item pricing, market data, and currency conversion."""

    def __init__(self, config=None):
        if config is None:
            from config import Config
            config = Config

        self.config = config
        self.cache_path = config.PRICE_CACHE_FILE
        self.cache = self._load_cache()

        # HR to FG conversion rates
        self.hr_to_fg = config.HR_TO_FG

        # Comprehensive price guide (FG values, Softcore Ladder typical)
        self.price_guide = self._build_price_guide()

    def _load_cache(self):
        """Load cached price data."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        """Save price cache to disk."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f, indent=2)

    def _build_price_guide(self):
        """
        Build a comprehensive price guide for common D2R items.
        Prices are in Forum Gold (FG), representing typical Softcore Ladder values.
        These are baseline estimates that can be refined with live market data.
        """
        return {
            # ── High Runes ──
            "Zod": {"fg_low": 600, "fg_high": 1000, "category": "rune", "tier": "S"},
            "Cham": {"fg_low": 300, "fg_high": 500, "category": "rune", "tier": "A"},
            "Jah": {"fg_low": 2500, "fg_high": 4000, "category": "rune", "tier": "S"},
            "Ber": {"fg_low": 2800, "fg_high": 4500, "category": "rune", "tier": "S"},
            "Sur": {"fg_low": 1300, "fg_high": 2000, "category": "rune", "tier": "A"},
            "Lo": {"fg_low": 900, "fg_high": 1500, "category": "rune", "tier": "A"},
            "Ohm": {"fg_low": 450, "fg_high": 750, "category": "rune", "tier": "A"},
            "Vex": {"fg_low": 250, "fg_high": 450, "category": "rune", "tier": "B"},
            "Gul": {"fg_low": 125, "fg_high": 225, "category": "rune", "tier": "B"},
            "Ist": {"fg_low": 70, "fg_high": 130, "category": "rune", "tier": "B"},
            "Mal": {"fg_low": 35, "fg_high": 70, "category": "rune", "tier": "C"},
            "Um": {"fg_low": 20, "fg_high": 40, "category": "rune", "tier": "C"},
            "Pul": {"fg_low": 10, "fg_high": 20, "category": "rune", "tier": "C"},

            # ── Popular Runewords ──
            "Enigma": {"fg_low": 8000, "fg_high": 12000, "category": "runeword", "tier": "S", "note": "Price heavily depends on base and defense roll"},
            "Infinity": {"fg_low": 8000, "fg_high": 14000, "category": "runeword", "tier": "S", "note": "ED and -ELR rolls matter most"},
            "Grief": {"fg_low": 1800, "fg_high": 4000, "category": "runeword", "tier": "S", "note": "+damage and IAS are key rolls"},
            "Heart of the Oak": {"fg_low": 500, "fg_high": 800, "category": "runeword", "tier": "S", "note": "Resist roll is the variable"},
            "Call to Arms": {"fg_low": 1200, "fg_high": 5000, "category": "runeword", "tier": "S", "note": "BO roll is everything: +6 BO = premium"},
            "Chains of Honor": {"fg_low": 5000, "fg_high": 7000, "category": "runeword", "tier": "S"},
            "Fortitude": {"fg_low": 1500, "fg_high": 3000, "category": "runeword", "tier": "S", "note": "Base and res roll matter"},
            "Spirit (sword)": {"fg_low": 5, "fg_high": 50, "category": "runeword", "tier": "A", "note": "35 FCR is premium"},
            "Spirit (shield)": {"fg_low": 5, "fg_high": 100, "category": "runeword", "tier": "A", "note": "35 FCR + high res = premium"},
            "Insight": {"fg_low": 5, "fg_high": 50, "category": "runeword", "tier": "A", "note": "Meditation level and base matter"},
            "Last Wish": {"fg_low": 15000, "fg_high": 25000, "category": "runeword", "tier": "S"},
            "Faith": {"fg_low": 4000, "fg_high": 8000, "category": "runeword", "tier": "S", "note": "Fanat level is key: 15 = premium"},
            "Breath of the Dying": {"fg_low": 3000, "fg_high": 6000, "category": "runeword", "tier": "S"},
            "Bramble": {"fg_low": 2500, "fg_high": 4000, "category": "runeword", "tier": "A"},

            # ── Unique Items ──
            "Shako": {"fg_low": 150, "fg_high": 400, "category": "unique", "tier": "S"},
            "Arachnid Mesh": {"fg_low": 250, "fg_high": 600, "category": "unique", "tier": "S"},
            "Mara's Kaleidoscope": {"fg_low": 80, "fg_high": 500, "category": "unique", "tier": "S", "note": "+30 res = premium"},
            "Stone of Jordan": {"fg_low": 150, "fg_high": 400, "category": "unique", "tier": "S"},
            "Bul-Kathos Wedding Band": {"fg_low": 80, "fg_high": 200, "category": "unique", "tier": "A"},
            "Griffon's Eye": {"fg_low": 2500, "fg_high": 15000, "category": "unique", "tier": "S", "note": "-20/+15 = max premium"},
            "Death's Fathom": {"fg_low": 1500, "fg_high": 10000, "category": "unique", "tier": "S", "note": "30% cold = max premium"},
            "War Traveler": {"fg_low": 30, "fg_high": 500, "category": "unique", "tier": "A", "note": "50 MF = premium"},
            "Chance Guards": {"fg_low": 3, "fg_high": 40, "category": "unique", "tier": "B", "note": "40 MF = premium"},
            "Gheeds Fortune": {"fg_low": 3, "fg_high": 100, "category": "unique", "tier": "B", "note": "40 MF + 15% vendor = premium"},
            "Titan's Revenge": {"fg_low": 30, "fg_high": 200, "category": "unique", "tier": "A", "note": "Eth is 2-5x more valuable"},
            "Annihilus": {"fg_low": 150, "fg_high": 2000, "category": "unique", "tier": "S", "note": "20/20/10 = max premium"},
            "Torch (Sorc)": {"fg_low": 500, "fg_high": 3000, "category": "unique", "tier": "S", "note": "20/20 = premium"},
            "Torch (Pally)": {"fg_low": 400, "fg_high": 2500, "category": "unique", "tier": "S"},
            "Torch (Necro)": {"fg_low": 100, "fg_high": 500, "category": "unique", "tier": "A"},
            "Torch (Zon)": {"fg_low": 200, "fg_high": 1000, "category": "unique", "tier": "A"},
            "Torch (Barb)": {"fg_low": 100, "fg_high": 500, "category": "unique", "tier": "A"},
            "Torch (Druid)": {"fg_low": 80, "fg_high": 400, "category": "unique", "tier": "B"},
            "Torch (Sin)": {"fg_low": 80, "fg_high": 400, "category": "unique", "tier": "B"},
            "Tal Rasha's Guardianship": {"fg_low": 250, "fg_high": 600, "category": "unique", "tier": "A"},
            "Tal Rasha's Adjudication": {"fg_low": 100, "fg_high": 200, "category": "unique", "tier": "A"},
            "Tal Rasha's Lidless Eye": {"fg_low": 30, "fg_high": 80, "category": "unique", "tier": "B"},

            # ── Valuable Bases ──
            "Eth Thresher 4os": {"fg_low": 80, "fg_high": 500, "category": "base", "tier": "A"},
            "Eth Giant Thresher 4os": {"fg_low": 150, "fg_high": 800, "category": "base", "tier": "S"},
            "Eth Berserker Axe 5os": {"fg_low": 150, "fg_high": 1000, "category": "base", "tier": "S"},
            "Eth Archon Plate 4os": {"fg_low": 40, "fg_high": 500, "category": "base", "tier": "A"},
            "Eth Archon Plate 3os": {"fg_low": 40, "fg_high": 500, "category": "base", "tier": "A"},
            "Monarch 4os": {"fg_low": 1, "fg_high": 5, "category": "base", "tier": "C"},
            "Phase Blade 5os": {"fg_low": 5, "fg_high": 20, "category": "base", "tier": "B"},
            "45@ Sacred Targe 4os": {"fg_low": 200, "fg_high": 1500, "category": "base", "tier": "S"},
            "45@ Vortex Shield 4os": {"fg_low": 150, "fg_high": 1000, "category": "base", "tier": "S"},
            "GMB +3 Bow 4os": {"fg_low": 80, "fg_high": 500, "category": "base", "tier": "A"},
        }

    def get_price(self, item_name, quality_pct=None):
        """
        Get estimated price for an item.

        Args:
            item_name: Name of the item
            quality_pct: Overall roll quality percentage (0-100) to adjust price

        Returns:
            dict with pricing info in both FG and HR equivalent
        """
        # Check cache first
        cache_key = item_name.lower().strip()
        cached = self.cache.get(cache_key)
        if cached and (time.time() - cached.get("timestamp", 0)) < self.config.PRICE_CACHE_TTL:
            return cached["data"]

        # Look up in price guide
        guide_entry = self._lookup_price_guide(item_name)
        if not guide_entry:
            return {
                "item": item_name,
                "fg_low": None,
                "fg_high": None,
                "fg_estimated": None,
                "hr_equivalent": None,
                "source": "not found",
                "note": "Item not in price guide. Check D2JSP or Traderie manually.",
            }

        fg_low = guide_entry["fg_low"]
        fg_high = guide_entry["fg_high"]

        # Adjust based on roll quality
        if quality_pct is not None:
            quality_factor = quality_pct / 100.0
            fg_estimated = fg_low + (fg_high - fg_low) * quality_factor
        else:
            fg_estimated = (fg_low + fg_high) / 2

        fg_estimated = round(fg_estimated)
        hr_equiv = self.fg_to_hr(fg_estimated)

        result = {
            "item": item_name,
            "fg_low": fg_low,
            "fg_high": fg_high,
            "fg_estimated": fg_estimated,
            "hr_equivalent": hr_equiv,
            "category": guide_entry.get("category"),
            "tier": guide_entry.get("tier"),
            "note": guide_entry.get("note", ""),
            "source": "price_guide",
            "quality_pct": quality_pct,
        }

        # Cache it
        self.cache[cache_key] = {
            "data": result,
            "timestamp": time.time(),
        }
        self._save_cache()

        return result

    def _lookup_price_guide(self, item_name):
        """Find an item in the price guide with fuzzy matching."""
        name_lower = item_name.lower().strip()

        # Exact match
        for guide_name, data in self.price_guide.items():
            if guide_name.lower() == name_lower:
                return data

        # Partial match
        for guide_name, data in self.price_guide.items():
            if name_lower in guide_name.lower() or guide_name.lower() in name_lower:
                return data

        return None

    def fg_to_hr(self, fg_amount):
        """
        Convert Forum Gold amount to High Rune equivalent.

        Returns the most human-readable HR breakdown.
        """
        if fg_amount <= 0:
            return "< 1 Pul"

        result = []
        remaining = fg_amount

        # Sort runes by value descending
        sorted_runes = sorted(
            self.hr_to_fg.items(), key=lambda x: x[1], reverse=True
        )

        for rune, fg_value in sorted_runes:
            if fg_value <= 0:
                continue
            count = remaining // fg_value
            if count > 0:
                remaining -= count * fg_value
                if count == 1:
                    result.append(rune)
                else:
                    result.append(f"{count}x {rune}")

            if remaining <= 0:
                break

        if not result:
            return "< 1 El"

        return " + ".join(result[:4])  # Cap at 4 runes for readability

    def hr_to_fg_convert(self, rune_name, quantity=1):
        """Convert a high rune (or any rune) to FG value."""
        fg_per = self.hr_to_fg.get(rune_name, 0)
        return {
            "rune": rune_name,
            "quantity": quantity,
            "fg_per_rune": fg_per,
            "fg_total": fg_per * quantity,
        }

    def bulk_price(self, items):
        """
        Price multiple items at once.

        Args:
            items: List of dicts with 'name' and optional 'quality_pct'

        Returns:
            List of price results with total
        """
        results = []
        total_fg = 0

        for item in items:
            price = self.get_price(
                item.get("name", ""),
                item.get("quality_pct"),
            )
            results.append(price)
            if price.get("fg_estimated"):
                total_fg += price["fg_estimated"]

        return {
            "items": results,
            "total_fg": total_fg,
            "total_hr": self.fg_to_hr(total_fg),
        }

    def get_all_prices(self):
        """Return the full price guide."""
        result = {}
        for name, data in self.price_guide.items():
            result[name] = {
                **data,
                "fg_mid": (data["fg_low"] + data["fg_high"]) // 2,
                "hr_equivalent": self.fg_to_hr(
                    (data["fg_low"] + data["fg_high"]) // 2
                ),
            }
        return result

    def get_hr_rates(self):
        """Return current HR to FG conversion rates."""
        return dict(
            sorted(self.hr_to_fg.items(), key=lambda x: x[1], reverse=True)
        )

    def generate_trade_price_text(self, item_name, quality_pct=None):
        """Generate a human-readable price summary for trade posts."""
        price = self.get_price(item_name, quality_pct)
        if not price.get("fg_estimated"):
            return f"{item_name}: Price unknown - check market"

        lines = [
            f"**{item_name}**",
            f"Estimated: {price['fg_estimated']} FG",
            f"Range: {price['fg_low']} - {price['fg_high']} FG",
            f"HR Equiv: {price['hr_equivalent']}",
        ]
        if price.get("note"):
            lines.append(f"Note: {price['note']}")

        return "\n".join(lines)
