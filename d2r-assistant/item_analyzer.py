"""
D2R Inventory Assistant - Item Analysis Engine

Analyzes item modifiers, determines roll quality (high/low),
and provides value assessment for D2R items.
"""
import json
import os
import math


class ItemAnalyzer:
    """Analyzes D2R items for roll quality, value, and modifier ranges."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__), "data", "item_database.json"
            )
        with open(db_path, "r") as f:
            self.db = json.load(f)

    def analyze_item(self, item):
        """
        Analyze an item and return detailed roll quality information.

        Args:
            item: dict with keys:
                - name: str (item name, e.g. "Griffon's Eye", "Enigma")
                - type: str ("unique", "runeword", "set", "rare", "magic", "base")
                - mods: dict mapping mod_name -> actual_value
                - ethereal: bool (optional)
                - sockets: int (optional)

        Returns:
            dict with roll analysis for each modifier
        """
        result = {
            "name": item.get("name", "Unknown"),
            "type": item.get("type", "unknown"),
            "ethereal": item.get("ethereal", False),
            "overall_quality": "unknown",
            "mod_analysis": [],
            "estimated_value": None,
            "tier": None,
        }

        db_entry = self._find_item_in_db(item["name"], item.get("type", ""))

        if not db_entry:
            result["mod_analysis"] = self._analyze_unknown_item(item)
            return result

        mods_db = db_entry.get("mods", {})
        result["tier"] = db_entry.get("tier", "?")

        total_quality = 0
        variable_count = 0

        for mod_name, mod_info in mods_db.items():
            actual_value = item.get("mods", {}).get(mod_name)
            analysis = self._analyze_single_mod(mod_name, mod_info, actual_value)
            result["mod_analysis"].append(analysis)

            if analysis["variable"] and analysis["quality_pct"] is not None:
                total_quality += analysis["quality_pct"]
                variable_count += 1

        if variable_count > 0:
            avg_quality = total_quality / variable_count
            result["overall_quality"] = self._quality_label(avg_quality)
            result["overall_quality_pct"] = round(avg_quality, 1)
        else:
            result["overall_quality"] = "fixed"
            result["overall_quality_pct"] = None

        result["estimated_value"] = db_entry.get("est_fg")

        return result

    def _find_item_in_db(self, name, item_type):
        """Look up an item in the database by name."""
        # Check runewords
        if name in self.db.get("runewords", {}):
            return self.db["runewords"][name]

        # Check unique items (nested under categories)
        for category, items in self.db.get("unique_items", {}).items():
            if name in items:
                return items[name]

        # Fuzzy match - check if item name is contained
        name_lower = name.lower()

        for rw_name, rw_data in self.db.get("runewords", {}).items():
            if rw_name.lower() in name_lower or name_lower in rw_name.lower():
                return rw_data

        for category, items in self.db.get("unique_items", {}).items():
            for item_name, item_data in items.items():
                if (
                    item_name.lower() in name_lower
                    or name_lower in item_name.lower()
                ):
                    return item_data

        return None

    def _analyze_single_mod(self, mod_name, mod_info, actual_value):
        """Analyze a single modifier's roll quality."""
        analysis = {
            "name": mod_name,
            "min": mod_info.get("min"),
            "max": mod_info.get("max"),
            "actual": actual_value,
            "variable": mod_info.get("variable", False),
            "per_level": mod_info.get("per_level", False),
            "quality_pct": None,
            "quality_label": None,
            "quality_color": None,
        }

        if not mod_info.get("variable", False):
            analysis["quality_label"] = "fixed"
            analysis["quality_color"] = "#888888"
            return analysis

        if actual_value is None:
            analysis["quality_label"] = "not set"
            analysis["quality_color"] = "#888888"
            return analysis

        min_val = mod_info["min"]
        max_val = mod_info["max"]

        if mod_info.get("per_level"):
            # Per-level mods: value depends on character level, skip quality calc
            analysis["quality_label"] = "per level"
            analysis["quality_color"] = "#888888"
            return analysis

        if max_val == min_val:
            analysis["quality_pct"] = 100.0
            analysis["quality_label"] = "perfect"
            analysis["quality_color"] = "#FFD700"
            return analysis

        raw_pct = ((actual_value - min_val) / (max_val - min_val)) * 100
        quality_pct = max(0, min(100, raw_pct))
        analysis["quality_pct"] = round(quality_pct, 1)
        analysis["quality_label"] = self._quality_label(quality_pct)
        analysis["quality_color"] = self._quality_color(quality_pct)

        return analysis

    def _analyze_unknown_item(self, item):
        """Provide basic analysis for items not in the database."""
        results = []
        for mod_name, mod_value in item.get("mods", {}).items():
            results.append({
                "name": mod_name,
                "actual": mod_value,
                "variable": True,
                "quality_pct": None,
                "quality_label": "unknown range",
                "quality_color": "#888888",
            })
        return results

    @staticmethod
    def _quality_label(pct):
        """Return a human-readable quality label based on roll percentage."""
        if pct >= 95:
            return "perfect"
        elif pct >= 80:
            return "high"
        elif pct >= 60:
            return "above avg"
        elif pct >= 40:
            return "average"
        elif pct >= 20:
            return "below avg"
        else:
            return "low"

    @staticmethod
    def _quality_color(pct):
        """Return a hex color for the roll quality percentage."""
        if pct >= 95:
            return "#FFD700"  # Gold
        elif pct >= 80:
            return "#00FF00"  # Green
        elif pct >= 60:
            return "#90EE90"  # Light green
        elif pct >= 40:
            return "#FFFF00"  # Yellow
        elif pct >= 20:
            return "#FFA500"  # Orange
        else:
            return "#FF4444"  # Red

    def get_runeword_info(self, name):
        """Get full information about a runeword including runes needed."""
        rw = self.db.get("runewords", {}).get(name)
        if not rw:
            return None

        rune_cost_fg = 0
        for rune in rw.get("runes", []):
            from config import Config
            rune_cost_fg += Config.HR_TO_FG.get(rune, 0)

        return {
            "name": name,
            "runes": rw["runes"],
            "bases": rw["bases"],
            "level_req": rw["level_req"],
            "mods": rw["mods"],
            "tier": rw.get("tier", "?"),
            "popular_bases": rw.get("popular_bases", []),
            "rune_cost_fg": rune_cost_fg,
        }

    def get_valuable_bases(self):
        """Return information about valuable item bases."""
        return self.db.get("valuable_bases", {})

    def get_all_runewords(self):
        """Return all runewords with their data."""
        return self.db.get("runewords", {})

    def get_all_uniques(self):
        """Return all unique items with their data."""
        return self.db.get("unique_items", {})

    def search_items(self, query):
        """Search for items by name across all categories."""
        query_lower = query.lower()
        results = []

        # Search runewords
        for name, data in self.db.get("runewords", {}).items():
            if query_lower in name.lower():
                results.append({"name": name, "category": "runeword", "data": data})

        # Search uniques
        for category, items in self.db.get("unique_items", {}).items():
            for name, data in items.items():
                if query_lower in name.lower():
                    results.append({
                        "name": name,
                        "category": f"unique ({category})",
                        "data": data,
                    })

        # Search bases
        for base_type in ["eth_bases", "non_eth_bases"]:
            bases = self.db.get("valuable_bases", {}).get(base_type, {})
            if isinstance(bases, dict):
                for sub_type, base_list in bases.items():
                    if isinstance(base_list, list):
                        for base in base_list:
                            if query_lower in base.get("name", "").lower():
                                results.append({
                                    "name": base["name"],
                                    "category": f"base ({sub_type})",
                                    "data": base,
                                })
            elif isinstance(bases, list):
                for base in bases:
                    if query_lower in base.get("name", "").lower():
                        results.append({
                            "name": base["name"],
                            "category": "base (non-eth)",
                            "data": base,
                        })

        return results
