"""
D2R Inventory Assistant - Trade Integration

Handles posting items to D2JSP and Traderie, generating trade posts,
and fetching recent sales data.
"""
import json
import os
import re
import time
from datetime import datetime


class TradeIntegration:
    """Manages trade posting and market data for D2JSP and Traderie."""

    def __init__(self, config=None):
        if config is None:
            from config import Config
            config = Config
        self.config = config

        # D2JSP Forum IDs for D2R sections
        self.d2jsp_forums = {
            "sc_ladder_iso": 149,   # Softcore Ladder - ISO (In Search Of)
            "sc_ladder_ft": 150,    # Softcore Ladder - FT (For Trade)
            "hc_ladder_iso": 151,   # Hardcore Ladder - ISO
            "hc_ladder_ft": 152,    # Hardcore Ladder - FT
            "sc_nl_iso": 153,       # Softcore Non-Ladder - ISO
            "sc_nl_ft": 154,        # Softcore Non-Ladder - FT
        }

        # Trade post history
        self.post_history_path = os.path.join(
            config.DATA_DIR, "trade_history.json"
        )
        self.post_history = self._load_history()

    def _load_history(self):
        """Load trade post history."""
        if os.path.exists(self.post_history_path):
            try:
                with open(self.post_history_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"posts": [], "purchases": []}
        return {"posts": [], "purchases": []}

    def _save_history(self):
        """Save trade post history."""
        os.makedirs(os.path.dirname(self.post_history_path), exist_ok=True)
        with open(self.post_history_path, "w") as f:
            json.dump(self.post_history, f, indent=2)

    # ── D2JSP Trade Post Generation ───────────────────────────────────

    def generate_d2jsp_post(self, items, mode="ft", price_engine=None):
        """
        Generate a formatted D2JSP trade post.

        Args:
            items: List of item dicts (name, mods, ethereal, etc.)
            mode: "ft" (For Trade) or "iso" (In Search Of)
            price_engine: Optional PriceEngine instance for pricing

        Returns:
            dict with title and body text ready to paste into D2JSP
        """
        if mode == "ft":
            return self._generate_ft_post(items, price_engine)
        elif mode == "iso":
            return self._generate_iso_post(items, price_engine)
        else:
            return {"error": f"Invalid mode: {mode}. Use 'ft' or 'iso'."}

    def _generate_ft_post(self, items, price_engine=None):
        """Generate a 'For Trade' post for D2JSP."""
        if not items:
            return {"error": "No items provided"}

        # Build title
        item_names = [i.get("name", "Unknown") for i in items[:3]]
        title = "FT: " + ", ".join(item_names)
        if len(items) > 3:
            title += f" + {len(items) - 3} more"
        title = title[:80]  # D2JSP title limit

        # Build body
        body_lines = []
        body_lines.append("[b]Items For Trade[/b]")
        body_lines.append("")

        for item in items:
            item_line = self._format_item_for_post(item, price_engine)
            body_lines.append(item_line)
            body_lines.append("")

        body_lines.append("[b]Payment:[/b] FG preferred. Also accepting runes.")
        body_lines.append("")
        body_lines.append("[i]Post here or PM with offers.[/i]")

        body = "\n".join(body_lines)

        # Record in history
        self.post_history["posts"].append({
            "platform": "d2jsp",
            "mode": "ft",
            "title": title,
            "items": [i.get("name", "Unknown") for i in items],
            "created_at": datetime.now().isoformat(),
        })
        self._save_history()

        return {
            "platform": "d2jsp",
            "title": title,
            "body": body,
            "forum_id": self.d2jsp_forums.get("sc_ladder_ft"),
        }

    def _generate_iso_post(self, items, price_engine=None):
        """Generate an 'In Search Of' post for D2JSP."""
        if not items:
            return {"error": "No items provided"}

        item_names = [i.get("name", "Unknown") for i in items[:3]]
        title = "ISO: " + ", ".join(item_names)
        if len(items) > 3:
            title += f" + {len(items) - 3} more"
        title = title[:80]

        body_lines = []
        body_lines.append("[b]Looking to Buy[/b]")
        body_lines.append("")

        for item in items:
            name = item.get("name", "Unknown")
            specs = item.get("specs", "")
            budget = ""

            if price_engine:
                price = price_engine.get_price(name)
                if price.get("fg_estimated"):
                    budget = f" | Budget: ~{price['fg_estimated']} FG"

            line = f"[*] [b]{name}[/b]"
            if specs:
                line += f" - {specs}"
            if budget:
                line += budget

            body_lines.append(line)

        body_lines.append("")
        body_lines.append("[b]Paying in FG.[/b] PM or post with what you have.")

        body = "\n".join(body_lines)

        self.post_history["posts"].append({
            "platform": "d2jsp",
            "mode": "iso",
            "title": title,
            "items": [i.get("name", "Unknown") for i in items],
            "created_at": datetime.now().isoformat(),
        })
        self._save_history()

        return {
            "platform": "d2jsp",
            "title": title,
            "body": body,
            "forum_id": self.d2jsp_forums.get("sc_ladder_iso"),
        }

    def _format_item_for_post(self, item, price_engine=None):
        """Format a single item for a trade post."""
        parts = []

        # Item header
        eth_tag = "[color=green]ETH[/color] " if item.get("ethereal") else ""
        name = item.get("name", "Unknown")
        parts.append(f"[b]{eth_tag}{name}[/b]")

        # Socket info
        if item.get("sockets"):
            parts[0] += f" ({item['sockets']}os)"

        # Mods
        if item.get("mods"):
            for mod_name, mod_value in item["mods"].items():
                parts.append(f"  • {mod_name}: {mod_value}")

        # Roll quality if analyzed
        if item.get("overall_quality_pct") is not None:
            pct = item["overall_quality_pct"]
            quality = item.get("overall_quality", "")
            parts.append(f"  [i]Roll Quality: {pct}% ({quality})[/i]")

        # Price
        if price_engine:
            price = price_engine.get_price(name, item.get("overall_quality_pct"))
            if price.get("fg_estimated"):
                parts.append(f"  [b]Asking: {price['fg_estimated']} FG[/b]")

        return "\n".join(parts)

    # ── Traderie Post Generation ──────────────────────────────────────

    def generate_traderie_post(self, items, price_engine=None):
        """
        Generate listing data formatted for Traderie.

        Args:
            items: List of item dicts
            price_engine: Optional PriceEngine for pricing

        Returns:
            List of Traderie-formatted listing dicts
        """
        listings = []

        for item in items:
            name = item.get("name", "Unknown")
            listing = {
                "item_name": name,
                "description": self._build_traderie_description(item),
                "looking_for": [],
                "platform": "traderie",
            }

            if price_engine:
                price = price_engine.get_price(name, item.get("overall_quality_pct"))
                if price.get("hr_equivalent"):
                    listing["looking_for"].append(price["hr_equivalent"])
                if price.get("fg_estimated"):
                    listing["fg_value"] = price["fg_estimated"]

            listings.append(listing)

        self.post_history["posts"].append({
            "platform": "traderie",
            "mode": "ft",
            "items": [i.get("name", "Unknown") for i in items],
            "created_at": datetime.now().isoformat(),
        })
        self._save_history()

        return listings

    def _build_traderie_description(self, item):
        """Build a description string for Traderie listings."""
        parts = []

        if item.get("ethereal"):
            parts.append("ETHEREAL")

        if item.get("sockets"):
            parts.append(f"{item['sockets']} sockets")

        if item.get("mods"):
            for mod_name, mod_value in item["mods"].items():
                parts.append(f"{mod_name}: {mod_value}")

        if item.get("overall_quality_pct") is not None:
            parts.append(f"Roll Quality: {item['overall_quality_pct']}%")

        return " | ".join(parts)

    # ── Sales Pitch Generator ─────────────────────────────────────────

    def generate_sales_pitch(self, item, analysis=None, price_data=None):
        """
        Generate a compelling sales pitch for an item.

        Args:
            item: Item dict
            analysis: ItemAnalyzer result (optional)
            price_data: PriceEngine result (optional)

        Returns:
            str with formatted sales pitch
        """
        name = item.get("name", "Unknown")
        lines = []

        # Header
        eth = "ETH " if item.get("ethereal") else ""
        lines.append(f"━━━ {eth}{name} ━━━")

        # Highlight key stats
        if analysis and analysis.get("mod_analysis"):
            high_rolls = []
            for mod in analysis["mod_analysis"]:
                if mod.get("quality_pct") and mod["quality_pct"] >= 80:
                    high_rolls.append(mod)

            if high_rolls:
                lines.append("")
                lines.append("★ Notable Rolls:")
                for mod in high_rolls:
                    pct = mod["quality_pct"]
                    label = mod["quality_label"].upper()
                    actual = mod.get("actual", "?")
                    range_str = f"[{mod.get('min', '?')}-{mod.get('max', '?')}]"
                    lines.append(
                        f"  • {mod['name']}: {actual} {range_str} — {pct}% ({label})"
                    )

        # Overall quality
        if analysis and analysis.get("overall_quality_pct"):
            lines.append("")
            overall = analysis["overall_quality_pct"]
            label = analysis["overall_quality"]
            lines.append(f"Overall Quality: {overall}% ({label})")

        # Pricing
        if price_data and price_data.get("fg_estimated"):
            lines.append("")
            lines.append(f"Market Value: {price_data['fg_low']}-{price_data['fg_high']} FG")
            lines.append(f"Estimated: {price_data['fg_estimated']} FG")
            if price_data.get("hr_equivalent"):
                lines.append(f"HR Equiv: {price_data['hr_equivalent']}")

        # Note
        if price_data and price_data.get("note"):
            lines.append(f"ℹ {price_data['note']}")

        return "\n".join(lines)

    # ── Trade History ─────────────────────────────────────────────────

    def get_post_history(self, platform=None, limit=20):
        """Get recent trade post history."""
        posts = self.post_history.get("posts", [])
        if platform:
            posts = [p for p in posts if p.get("platform") == platform]
        return posts[-limit:]

    def record_sale(self, item_name, price_fg, platform, buyer=None):
        """Record a completed sale."""
        sale = {
            "item": item_name,
            "price_fg": price_fg,
            "platform": platform,
            "buyer": buyer,
            "sold_at": datetime.now().isoformat(),
        }
        if "sales" not in self.post_history:
            self.post_history["sales"] = []
        self.post_history["sales"].append(sale)
        self._save_history()
        return sale

    def record_purchase(self, item_name, price_fg, platform, seller=None):
        """Record a completed purchase."""
        purchase = {
            "item": item_name,
            "price_fg": price_fg,
            "platform": platform,
            "seller": seller,
            "bought_at": datetime.now().isoformat(),
        }
        self.post_history["purchases"].append(purchase)
        self._save_history()
        return purchase

    def get_trade_summary(self):
        """Get a summary of all trades (buys and sells)."""
        sales = self.post_history.get("sales", [])
        purchases = self.post_history.get("purchases", [])

        total_sold_fg = sum(s.get("price_fg", 0) for s in sales)
        total_bought_fg = sum(p.get("price_fg", 0) for p in purchases)

        return {
            "total_sales": len(sales),
            "total_purchases": len(purchases),
            "total_sold_fg": total_sold_fg,
            "total_bought_fg": total_bought_fg,
            "net_fg": total_sold_fg - total_bought_fg,
            "recent_sales": sales[-5:],
            "recent_purchases": purchases[-5:],
        }
