"""
D2R Inventory Assistant - Inventory Manager

Manages character inventory, stash, and equipped gear.
Supports multiple characters and shared stash.
"""
import json
import os
import copy
from datetime import datetime


DEFAULT_INVENTORY = {
    "characters": {},
    "shared_stash": {"tabs": {"tab1": [], "tab2": [], "tab3": []}},
    "last_updated": None,
}

DEFAULT_CHARACTER = {
    "name": "",
    "class": "",
    "level": 1,
    "equipped": {
        "helm": None,
        "body_armor": None,
        "weapon": None,
        "shield": None,
        "gloves": None,
        "boots": None,
        "belt": None,
        "amulet": None,
        "ring1": None,
        "ring2": None,
        "weapon_swap": None,
        "shield_swap": None,
    },
    "inventory": [],
    "personal_stash": {"tabs": {"tab1": [], "tab2": [], "tab3": []}},
    "created_at": None,
    "last_updated": None,
}

VALID_SLOTS = [
    "helm", "body_armor", "weapon", "shield", "gloves", "boots",
    "belt", "amulet", "ring1", "ring2", "weapon_swap", "shield_swap",
]

CHARACTER_CLASSES = [
    "Amazon", "Necromancer", "Barbarian", "Sorceress",
    "Paladin", "Druid", "Assassin",
]


class InventoryManager:
    """Manages D2R character inventories, stash, and equipped gear."""

    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(__file__), "data", "inventory.json"
            )
        self.data_path = data_path
        self.data = self._load()

    def _load(self):
        """Load inventory data from disk."""
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return copy.deepcopy(DEFAULT_INVENTORY)

    def _save(self):
        """Persist inventory data to disk."""
        self.data["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(self.data, f, indent=2)

    # ── Character Management ──────────────────────────────────────────

    def create_character(self, name, char_class, level=1):
        """Create a new character."""
        if not name or not name.strip():
            return {"error": "Character name is required"}
        if char_class not in CHARACTER_CLASSES:
            return {"error": f"Invalid class. Must be one of: {CHARACTER_CLASSES}"}
        if name in self.data["characters"]:
            return {"error": f"Character '{name}' already exists"}

        char = copy.deepcopy(DEFAULT_CHARACTER)
        char["name"] = name
        char["class"] = char_class
        char["level"] = max(1, min(99, level))
        char["created_at"] = datetime.now().isoformat()
        char["last_updated"] = datetime.now().isoformat()

        self.data["characters"][name] = char
        self._save()
        return {"success": True, "character": char}

    def delete_character(self, name):
        """Delete a character and all their gear."""
        if name not in self.data["characters"]:
            return {"error": f"Character '{name}' not found"}
        del self.data["characters"][name]
        self._save()
        return {"success": True}

    def get_character(self, name):
        """Get a character's full data."""
        char = self.data["characters"].get(name)
        if not char:
            return {"error": f"Character '{name}' not found"}
        return char

    def list_characters(self):
        """List all characters with summary info."""
        result = []
        for name, char in self.data["characters"].items():
            equipped_count = sum(
                1 for v in char["equipped"].values() if v is not None
            )
            inv_count = len(char["inventory"])
            stash_count = sum(
                len(tab) for tab in char["personal_stash"]["tabs"].values()
            )
            result.append({
                "name": name,
                "class": char["class"],
                "level": char["level"],
                "equipped_count": equipped_count,
                "inventory_count": inv_count,
                "stash_count": stash_count,
            })
        return result

    def update_character_level(self, name, level):
        """Update a character's level."""
        if name not in self.data["characters"]:
            return {"error": f"Character '{name}' not found"}
        self.data["characters"][name]["level"] = max(1, min(99, level))
        self.data["characters"][name]["last_updated"] = datetime.now().isoformat()
        self._save()
        return {"success": True}

    # ── Equipped Gear Management ──────────────────────────────────────

    def equip_item(self, char_name, slot, item):
        """
        Equip an item to a character's gear slot.

        Args:
            char_name: Character name
            slot: One of VALID_SLOTS
            item: dict with item data (name, type, mods, ethereal, sockets, etc.)

        Returns:
            dict with result, including previously equipped item if any
        """
        if char_name not in self.data["characters"]:
            return {"error": f"Character '{char_name}' not found"}
        if slot not in VALID_SLOTS:
            return {"error": f"Invalid slot '{slot}'. Must be one of: {VALID_SLOTS}"}

        char = self.data["characters"][char_name]
        previous = char["equipped"].get(slot)

        item["equipped_at"] = datetime.now().isoformat()
        char["equipped"][slot] = item
        char["last_updated"] = datetime.now().isoformat()
        self._save()

        return {"success": True, "previous_item": previous}

    def unequip_item(self, char_name, slot):
        """Remove an item from a gear slot, returning it."""
        if char_name not in self.data["characters"]:
            return {"error": f"Character '{char_name}' not found"}
        if slot not in VALID_SLOTS:
            return {"error": f"Invalid slot '{slot}'"}

        char = self.data["characters"][char_name]
        item = char["equipped"].get(slot)
        char["equipped"][slot] = None
        char["last_updated"] = datetime.now().isoformat()
        self._save()

        return {"success": True, "item": item}

    def get_equipped(self, char_name):
        """Get all equipped gear for a character."""
        if char_name not in self.data["characters"]:
            return {"error": f"Character '{char_name}' not found"}
        return self.data["characters"][char_name]["equipped"]

    # ── Inventory Management ──────────────────────────────────────────

    def add_to_inventory(self, char_name, item):
        """Add an item to a character's inventory."""
        if char_name not in self.data["characters"]:
            return {"error": f"Character '{char_name}' not found"}

        item["added_at"] = datetime.now().isoformat()
        item["id"] = self._generate_item_id()
        self.data["characters"][char_name]["inventory"].append(item)
        self.data["characters"][char_name]["last_updated"] = datetime.now().isoformat()
        self._save()
        return {"success": True, "item_id": item["id"]}

    def remove_from_inventory(self, char_name, item_id):
        """Remove an item from a character's inventory by ID."""
        if char_name not in self.data["characters"]:
            return {"error": f"Character '{char_name}' not found"}

        inv = self.data["characters"][char_name]["inventory"]
        for i, item in enumerate(inv):
            if item.get("id") == item_id:
                removed = inv.pop(i)
                self.data["characters"][char_name]["last_updated"] = (
                    datetime.now().isoformat()
                )
                self._save()
                return {"success": True, "item": removed}

        return {"error": f"Item '{item_id}' not found in inventory"}

    def get_inventory(self, char_name):
        """Get a character's inventory items."""
        if char_name not in self.data["characters"]:
            return {"error": f"Character '{char_name}' not found"}
        return self.data["characters"][char_name]["inventory"]

    # ── Stash Management ──────────────────────────────────────────────

    def add_to_stash(self, item, stash_type="shared", tab="tab1", char_name=None):
        """
        Add an item to stash.

        Args:
            item: Item data dict
            stash_type: "shared" or "personal"
            tab: "tab1", "tab2", or "tab3"
            char_name: Required if stash_type is "personal"
        """
        valid_tabs = ["tab1", "tab2", "tab3"]
        if tab not in valid_tabs:
            return {"error": f"Invalid tab. Must be one of: {valid_tabs}"}

        item["added_at"] = datetime.now().isoformat()
        item["id"] = self._generate_item_id()

        if stash_type == "shared":
            self.data["shared_stash"]["tabs"][tab].append(item)
        elif stash_type == "personal":
            if not char_name or char_name not in self.data["characters"]:
                return {"error": "Valid character name required for personal stash"}
            self.data["characters"][char_name]["personal_stash"]["tabs"][tab].append(
                item
            )
            self.data["characters"][char_name]["last_updated"] = (
                datetime.now().isoformat()
            )
        else:
            return {"error": "stash_type must be 'shared' or 'personal'"}

        self._save()
        return {"success": True, "item_id": item["id"]}

    def remove_from_stash(self, item_id, stash_type="shared", tab=None, char_name=None):
        """Remove an item from stash by ID."""
        if stash_type == "shared":
            stash = self.data["shared_stash"]["tabs"]
        elif stash_type == "personal" and char_name:
            if char_name not in self.data["characters"]:
                return {"error": f"Character '{char_name}' not found"}
            stash = self.data["characters"][char_name]["personal_stash"]["tabs"]
        else:
            return {"error": "Invalid stash type or missing character name"}

        tabs_to_search = [tab] if tab else stash.keys()
        for t in tabs_to_search:
            if t in stash:
                for i, item in enumerate(stash[t]):
                    if item.get("id") == item_id:
                        removed = stash[t].pop(i)
                        self._save()
                        return {"success": True, "item": removed}

        return {"error": f"Item '{item_id}' not found in stash"}

    def get_stash(self, stash_type="shared", char_name=None):
        """Get stash contents."""
        if stash_type == "shared":
            return self.data["shared_stash"]["tabs"]
        elif stash_type == "personal" and char_name:
            if char_name not in self.data["characters"]:
                return {"error": f"Character '{char_name}' not found"}
            return self.data["characters"][char_name]["personal_stash"]["tabs"]
        return {"error": "Invalid parameters"}

    # ── Search & Tally ────────────────────────────────────────────────

    def search_all_items(self, query):
        """Search across all characters' gear, inventory, and stash."""
        query_lower = query.lower()
        results = []

        for char_name, char in self.data["characters"].items():
            # Search equipped
            for slot, item in char["equipped"].items():
                if item and query_lower in item.get("name", "").lower():
                    results.append({
                        "location": f"{char_name} (equipped: {slot})",
                        "item": item,
                    })

            # Search inventory
            for item in char["inventory"]:
                if query_lower in item.get("name", "").lower():
                    results.append({
                        "location": f"{char_name} (inventory)",
                        "item": item,
                    })

            # Search personal stash
            for tab, items in char["personal_stash"]["tabs"].items():
                for item in items:
                    if query_lower in item.get("name", "").lower():
                        results.append({
                            "location": f"{char_name} (stash: {tab})",
                            "item": item,
                        })

        # Search shared stash
        for tab, items in self.data["shared_stash"]["tabs"].items():
            for item in items:
                if query_lower in item.get("name", "").lower():
                    results.append({
                        "location": f"Shared Stash ({tab})",
                        "item": item,
                    })

        return results

    def tally_items(self):
        """Get a summary count of all items across all storage."""
        tally = {
            "total_items": 0,
            "by_character": {},
            "shared_stash_count": 0,
            "by_quality": {},
            "by_slot": {},
        }

        # Count shared stash
        for tab, items in self.data["shared_stash"]["tabs"].items():
            tally["shared_stash_count"] += len(items)
            tally["total_items"] += len(items)
            for item in items:
                q = item.get("quality", "unknown")
                tally["by_quality"][q] = tally["by_quality"].get(q, 0) + 1

        # Count per character
        for char_name, char in self.data["characters"].items():
            char_tally = {"equipped": 0, "inventory": 0, "stash": 0}

            for slot, item in char["equipped"].items():
                if item:
                    char_tally["equipped"] += 1
                    tally["total_items"] += 1
                    tally["by_slot"][slot] = tally["by_slot"].get(slot, 0) + 1
                    q = item.get("quality", "unknown")
                    tally["by_quality"][q] = tally["by_quality"].get(q, 0) + 1

            char_tally["inventory"] = len(char["inventory"])
            tally["total_items"] += char_tally["inventory"]
            for item in char["inventory"]:
                q = item.get("quality", "unknown")
                tally["by_quality"][q] = tally["by_quality"].get(q, 0) + 1

            for tab, items in char["personal_stash"]["tabs"].items():
                char_tally["stash"] += len(items)
                tally["total_items"] += len(items)
                for item in items:
                    q = item.get("quality", "unknown")
                    tally["by_quality"][q] = tally["by_quality"].get(q, 0) + 1

            tally["by_character"][char_name] = char_tally

        return tally

    # ── Export ─────────────────────────────────────────────────────────

    def export_for_trade(self, char_name=None, items=None):
        """
        Export items formatted for trade posting.

        Args:
            char_name: If provided, export all items from this character
            items: If provided, export these specific items

        Returns:
            List of items formatted for trade posting
        """
        trade_items = []

        if items:
            for item in items:
                trade_items.append(self._format_for_trade(item))
        elif char_name and char_name in self.data["characters"]:
            char = self.data["characters"][char_name]
            for slot, item in char["equipped"].items():
                if item:
                    trade_items.append(self._format_for_trade(item, slot))
            for item in char["inventory"]:
                trade_items.append(self._format_for_trade(item))

        return trade_items

    def _format_for_trade(self, item, slot=None):
        """Format a single item for trade posting."""
        parts = []
        if item.get("ethereal"):
            parts.append("ETH")
        parts.append(item.get("name", "Unknown Item"))
        if item.get("sockets"):
            parts.append(f"({item['sockets']}os)")

        title = " ".join(parts)

        mods_str = ""
        if item.get("mods"):
            mod_lines = []
            for mod_name, mod_value in item["mods"].items():
                mod_lines.append(f"  {mod_name}: {mod_value}")
            mods_str = "\n".join(mod_lines)

        return {
            "title": title,
            "mods_text": mods_str,
            "raw_item": item,
            "slot": slot,
        }

    # ── Helpers ────────────────────────────────────────────────────────

    def _generate_item_id(self):
        """Generate a unique item ID."""
        import hashlib
        import time
        raw = f"{time.time()}-{id(self)}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
