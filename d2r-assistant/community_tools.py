"""
D2R Inventory Assistant - Community Tools

Provides build guides, calculators, valuable item checklists,
and other community resources for D2R players.
"""

# ── Popular Build Guides ──────────────────────────────────────────────

BUILD_GUIDES = {
    "Lightning Sorceress": {
        "class": "Sorceress",
        "type": "Caster",
        "tier": "S",
        "difficulty": "Medium",
        "description": "Top-tier farming build. Clears most content with Lightning/Chain Lightning. Requires Infinity merc to break immunities.",
        "skills": {
            "Lightning": 20,
            "Chain Lightning": 20,
            "Lightning Mastery": 20,
            "Charged Bolt": 20,
            "Telekinesis": 1,
            "Teleport": 1,
            "Static Field": 1,
            "Warmth": 1,
        },
        "gear": {
            "helm": {"best": "Griffon's Eye", "budget": "Shako"},
            "body_armor": {"best": "Chains of Honor", "budget": "Vipermagi"},
            "weapon": {"best": "HOTO / Eschuta's", "budget": "Spirit Sword"},
            "shield": {"best": "Spirit Monarch (35 FCR)", "budget": "Spirit Monarch"},
            "gloves": {"best": "Magefist", "budget": "Magefist"},
            "boots": {"best": "War Traveler", "budget": "Sandstorm Trek"},
            "belt": {"best": "Arachnid Mesh", "budget": "Goldwrap"},
            "amulet": {"best": "Mara's 30", "budget": "Mara's / +2 Sorc Ammy"},
            "ring1": {"best": "Stone of Jordan", "budget": "FCR Ring w/ Res"},
            "ring2": {"best": "Stone of Jordan", "budget": "FCR Ring w/ Res"},
        },
        "merc": {
            "type": "Act 2 Nightmare (Holy Freeze)",
            "weapon": "Infinity (Eth Thresher/GT)",
            "armor": "Fortitude (Eth)",
            "helm": "Andariel's Visage (w/ Ral)",
        },
        "breakpoints": {
            "FCR": {"frames": [63, 105, 200], "target": "105 or 200"},
            "FHR": {"frames": [60, 86], "target": "86"},
        },
        "farm_spots": ["Chaos Sanctuary", "Baal Waves", "Cows", "Arcane Sanctuary"],
    },
    "Hammerdin": {
        "class": "Paladin",
        "type": "Caster",
        "tier": "S",
        "difficulty": "Medium",
        "description": "Versatile and powerful. Blessed Hammer deals magic damage which very few monsters are immune to.",
        "skills": {
            "Blessed Hammer": 20,
            "Vigor": 20,
            "Blessed Aim": 20,
            "Concentration": 20,
            "Holy Shield": 1,
            "Redemption": 1,
        },
        "gear": {
            "helm": {"best": "Shako", "budget": "Lore RW"},
            "body_armor": {"best": "Enigma", "budget": "Vipermagi"},
            "weapon": {"best": "Heart of the Oak", "budget": "Spirit Sword"},
            "shield": {"best": "Herald of Zakarum", "budget": "Spirit Paladin Shield"},
            "gloves": {"best": "Magefist / Trang-Oul's", "budget": "Magefist"},
            "boots": {"best": "War Traveler", "budget": "Sandstorm Trek"},
            "belt": {"best": "Arachnid Mesh", "budget": "Goldwrap"},
            "amulet": {"best": "Mara's 30", "budget": "Any +2 Pally Ammy"},
            "ring1": {"best": "Stone of Jordan", "budget": "FCR Ring w/ Res"},
            "ring2": {"best": "Stone of Jordan", "budget": "BK Ring"},
        },
        "merc": {
            "type": "Act 2 Nightmare (Holy Freeze)",
            "weapon": "Insight (Eth Thresher)",
            "armor": "Fortitude / Treachery",
            "helm": "Andariel's Visage / Tal Rasha's Mask",
        },
        "breakpoints": {
            "FCR": {"frames": [75, 125], "target": "125"},
            "FHR": {"frames": [48, 86], "target": "86"},
        },
        "farm_spots": ["Chaos Sanctuary", "Baal Waves", "Worldstone Keep", "Travincal"],
    },
    "Javazon": {
        "class": "Amazon",
        "type": "Hybrid",
        "tier": "S",
        "difficulty": "Easy",
        "description": "Lightning Fury is the best area-of-effect skill in the game. Destroys cow level and large mob packs.",
        "skills": {
            "Lightning Fury": 20,
            "Charged Strike": 20,
            "Lightning Strike": 1,
            "Power Strike": 20,
            "Pierce": 1,
            "Valkyrie": 1,
            "Decoy": 1,
            "Dodge": 1,
            "Avoid": 1,
            "Evade": 1,
        },
        "gear": {
            "helm": {"best": "Griffon's Eye", "budget": "Shako"},
            "body_armor": {"best": "Enigma", "budget": "Peace RW / Treachery"},
            "weapon": {"best": "Titan's Revenge (Eth)", "budget": "Titan's Revenge"},
            "shield": {"best": "Spirit Monarch (35 FCR)", "budget": "Spirit Monarch"},
            "gloves": {"best": "Java Gloves +2/20 IAS", "budget": "+2 Java Gloves"},
            "boots": {"best": "War Traveler", "budget": "Aldur's Boots"},
            "belt": {"best": "Razortail", "budget": "Razortail"},
            "amulet": {"best": "Highlord's Wrath", "budget": "Cat's Eye"},
            "ring1": {"best": "Raven Frost", "budget": "Raven Frost"},
            "ring2": {"best": "BK Ring / Rare Ring", "budget": "Res Ring"},
        },
        "merc": {
            "type": "Act 2 Nightmare (Holy Freeze)",
            "weapon": "Infinity (Eth Thresher/GT)",
            "armor": "Fortitude (Eth)",
            "helm": "Andariel's Visage",
        },
        "breakpoints": {
            "IAS": {"note": "Depends on weapon speed. Titan's needs IAS from gear."},
            "FHR": {"frames": [52, 86], "target": "86"},
        },
        "farm_spots": ["Cow Level", "Chaos Sanctuary", "Worldstone Keep"],
    },
    "Blizzard Sorceress": {
        "class": "Sorceress",
        "type": "Caster",
        "tier": "A",
        "difficulty": "Easy",
        "description": "Excellent starter build. High single-target and AoE damage. Struggles with Cold Immunes without merc.",
        "skills": {
            "Blizzard": 20,
            "Glacial Spike": 20,
            "Ice Blast": 20,
            "Cold Mastery": 20,
            "Ice Bolt": 1,
            "Telekinesis": 1,
            "Teleport": 1,
            "Static Field": 1,
            "Warmth": 1,
        },
        "gear": {
            "helm": {"best": "Nightwing's Veil", "budget": "Shako"},
            "body_armor": {"best": "Chains of Honor", "budget": "Vipermagi / Skullder's"},
            "weapon": {"best": "Death's Fathom", "budget": "Oculus / HOTO"},
            "shield": {"best": "Spirit Monarch (35 FCR)", "budget": "Spirit Monarch"},
            "gloves": {"best": "Magefist", "budget": "Magefist"},
            "boots": {"best": "War Traveler", "budget": "Aldur's Boots"},
            "belt": {"best": "Arachnid Mesh", "budget": "Goldwrap"},
            "amulet": {"best": "Mara's 30", "budget": "Any +2 Sorc Ammy"},
            "ring1": {"best": "Stone of Jordan", "budget": "FCR Ring"},
            "ring2": {"best": "Stone of Jordan", "budget": "Nagel Ring (MF)"},
        },
        "merc": {
            "type": "Act 2 Nightmare (Holy Freeze)",
            "weapon": "Insight (Eth Thresher)",
            "armor": "Fortitude (Eth) / Treachery",
            "helm": "Andariel's Visage / Tal Rasha's Mask",
        },
        "breakpoints": {
            "FCR": {"frames": [63, 105], "target": "105"},
            "FHR": {"frames": [60, 86], "target": "86"},
        },
        "farm_spots": ["Ancient Tunnels", "Mephisto", "Andariel", "Pindle"],
    },
    "Smiter": {
        "class": "Paladin",
        "type": "Melee",
        "tier": "A",
        "difficulty": "Medium",
        "description": "Dedicated Uber Tristram killer. Smite always hits and applies Crushing Blow reliably.",
        "skills": {
            "Smite": 20,
            "Holy Shield": 20,
            "Fanaticism": 20,
            "Resist Lightning": 10,
            "Resist Fire": 10,
            "Salvation": 1,
        },
        "gear": {
            "helm": {"best": "Guillaume's Face", "budget": "Guillaume's Face"},
            "body_armor": {"best": "Enigma", "budget": "Treachery (prebuff Fade)"},
            "weapon": {"best": "Grief (Phase Blade)", "budget": "Black RW Flail"},
            "shield": {"best": "Herald of Zakarum (Um'd)", "budget": "Herald of Zakarum"},
            "gloves": {"best": "Dracul's Grasp", "budget": "Crafted CB Gloves"},
            "boots": {"best": "Gore Rider", "budget": "Gore Rider"},
            "belt": {"best": "Thundergod's Vigor", "budget": "Verdungo's"},
            "amulet": {"best": "Highlord's Wrath", "budget": "Highlord's Wrath"},
            "ring1": {"best": "Raven Frost", "budget": "Raven Frost"},
            "ring2": {"best": "Dwarf Star", "budget": "Res Ring + Life"},
        },
        "merc": {
            "type": "Not typically used for Ubers",
            "weapon": "N/A",
            "armor": "N/A",
            "helm": "N/A",
        },
        "breakpoints": {
            "IAS": {"note": "Grief PB with Fanaticism reaches max Smite speed easily"},
        },
        "farm_spots": ["Uber Tristram", "Dclone"],
    },
    "Summon Necromancer": {
        "class": "Necromancer",
        "type": "Summoner",
        "tier": "A",
        "difficulty": "Easy",
        "description": "Safe, relaxed playstyle. Army of skeletons and revives do the work. Great for hardcore.",
        "skills": {
            "Raise Skeleton": 20,
            "Skeleton Mastery": 20,
            "Corpse Explosion": 20,
            "Amplify Damage": 1,
            "Decrepify": 1,
            "Dim Vision": 1,
            "Revive": 1,
            "Summon Resist": 1,
            "Clay Golem": 1,
            "Golem Mastery": 1,
        },
        "gear": {
            "helm": {"best": "Shako", "budget": "Lore RW"},
            "body_armor": {"best": "Enigma", "budget": "Smoke RW"},
            "weapon": {"best": "Beast / HOTO", "budget": "Spirit Sword"},
            "shield": {"best": "Homunculus", "budget": "Spirit Monarch"},
            "gloves": {"best": "Trang-Oul's Claws", "budget": "Magefist"},
            "boots": {"best": "Marrowwalk / War Traveler", "budget": "Aldur's Boots"},
            "belt": {"best": "Arachnid Mesh", "budget": "Goldwrap"},
            "amulet": {"best": "Mara's 30", "budget": "+2 Necro Ammy"},
            "ring1": {"best": "Stone of Jordan", "budget": "FCR Ring"},
            "ring2": {"best": "Stone of Jordan", "budget": "BK Ring"},
        },
        "merc": {
            "type": "Act 2 Nightmare (Might)",
            "weapon": "Infinity (Eth Thresher)",
            "armor": "Fortitude (Eth)",
            "helm": "Andariel's Visage",
        },
        "breakpoints": {
            "FCR": {"frames": [75, 125], "target": "75"},
            "FHR": {"frames": [56, 86], "target": "56"},
        },
        "farm_spots": ["Chaos Sanctuary", "Baal", "Cows", "Worldstone Keep"],
    },
}

# ── FCR/IAS Breakpoint Tables ─────────────────────────────────────────

BREAKPOINT_TABLES = {
    "Sorceress": {
        "FCR": {
            "description": "Faster Cast Rate frames",
            "breakpoints": [
                {"fcr": 0, "frames": 13},
                {"fcr": 9, "frames": 12},
                {"fcr": 20, "frames": 11},
                {"fcr": 37, "frames": 10},
                {"fcr": 63, "frames": 9},
                {"fcr": 105, "frames": 8},
                {"fcr": 200, "frames": 7},
            ],
        },
        "FHR": {
            "description": "Faster Hit Recovery frames",
            "breakpoints": [
                {"fhr": 0, "frames": 15},
                {"fhr": 5, "frames": 14},
                {"fhr": 9, "frames": 13},
                {"fhr": 14, "frames": 12},
                {"fhr": 20, "frames": 11},
                {"fhr": 30, "frames": 10},
                {"fhr": 42, "frames": 9},
                {"fhr": 60, "frames": 8},
                {"fhr": 86, "frames": 7},
                {"fhr": 142, "frames": 6},
                {"fhr": 280, "frames": 5},
            ],
        },
    },
    "Paladin": {
        "FCR": {
            "breakpoints": [
                {"fcr": 0, "frames": 15},
                {"fcr": 9, "frames": 14},
                {"fcr": 18, "frames": 13},
                {"fcr": 30, "frames": 12},
                {"fcr": 48, "frames": 11},
                {"fcr": 75, "frames": 10},
                {"fcr": 125, "frames": 9},
            ],
        },
        "FHR": {
            "breakpoints": [
                {"fhr": 0, "frames": 9},
                {"fhr": 7, "frames": 8},
                {"fhr": 15, "frames": 7},
                {"fhr": 27, "frames": 6},
                {"fhr": 48, "frames": 5},
                {"fhr": 86, "frames": 4},
                {"fhr": 200, "frames": 3},
            ],
        },
    },
    "Amazon": {
        "FCR": {
            "breakpoints": [
                {"fcr": 0, "frames": 19},
                {"fcr": 7, "frames": 18},
                {"fcr": 14, "frames": 17},
                {"fcr": 22, "frames": 16},
                {"fcr": 32, "frames": 15},
                {"fcr": 48, "frames": 14},
                {"fcr": 68, "frames": 13},
                {"fcr": 99, "frames": 12},
                {"fcr": 152, "frames": 11},
            ],
        },
        "FHR": {
            "breakpoints": [
                {"fhr": 0, "frames": 11},
                {"fhr": 6, "frames": 10},
                {"fhr": 13, "frames": 9},
                {"fhr": 20, "frames": 8},
                {"fhr": 32, "frames": 7},
                {"fhr": 52, "frames": 6},
                {"fhr": 86, "frames": 5},
                {"fhr": 174, "frames": 4},
                {"fhr": 600, "frames": 3},
            ],
        },
    },
    "Necromancer": {
        "FCR": {
            "breakpoints": [
                {"fcr": 0, "frames": 15},
                {"fcr": 9, "frames": 14},
                {"fcr": 18, "frames": 13},
                {"fcr": 30, "frames": 12},
                {"fcr": 48, "frames": 11},
                {"fcr": 75, "frames": 10},
                {"fcr": 125, "frames": 9},
            ],
        },
    },
    "Barbarian": {
        "FCR": {
            "breakpoints": [
                {"fcr": 0, "frames": 13},
                {"fcr": 9, "frames": 12},
                {"fcr": 20, "frames": 11},
                {"fcr": 37, "frames": 10},
                {"fcr": 63, "frames": 9},
                {"fcr": 105, "frames": 8},
                {"fcr": 200, "frames": 7},
            ],
        },
    },
    "Druid": {
        "FCR": {
            "breakpoints": [
                {"fcr": 0, "frames": 18},
                {"fcr": 4, "frames": 17},
                {"fcr": 10, "frames": 16},
                {"fcr": 19, "frames": 15},
                {"fcr": 30, "frames": 14},
                {"fcr": 46, "frames": 13},
                {"fcr": 68, "frames": 12},
                {"fcr": 99, "frames": 11},
                {"fcr": 163, "frames": 10},
            ],
        },
    },
    "Assassin": {
        "FCR": {
            "breakpoints": [
                {"fcr": 0, "frames": 16},
                {"fcr": 8, "frames": 15},
                {"fcr": 16, "frames": 14},
                {"fcr": 27, "frames": 13},
                {"fcr": 42, "frames": 12},
                {"fcr": 65, "frames": 11},
                {"fcr": 102, "frames": 10},
                {"fcr": 174, "frames": 9},
            ],
        },
    },
}

# ── Runeword Calculator Data ─────────────────────────────────────────

CUBE_RECIPES = {
    "rune_upgrades": {
        "El + El + El": "Eld",
        "Eld + Eld + Eld": "Tir",
        "Tir + Tir + Tir": "Nef",
        "Nef + Nef + Nef": "Eth",
        "Eth + Eth + Eth": "Ith",
        "Ith + Ith + Ith": "Tal",
        "Tal + Tal + Tal": "Ral",
        "Ral + Ral + Ral": "Ort",
        "Ort + Ort + Ort": "Thul",
        "Thul + Thul + Thul + Chipped Topaz": "Amn",
        "Amn + Amn + Amn + Chipped Amethyst": "Sol",
        "Sol + Sol + Sol + Chipped Sapphire": "Shael",
        "Shael + Shael + Shael + Chipped Ruby": "Dol",
        "Dol + Dol + Dol + Chipped Emerald": "Hel",
        "Hel + Hel + Hel + Chipped Diamond": "Io",
        "Io + Io + Io + Flawed Topaz": "Lum",
        "Lum + Lum + Lum + Flawed Amethyst": "Ko",
        "Ko + Ko + Ko + Flawed Sapphire": "Fal",
        "Fal + Fal + Fal + Flawed Ruby": "Lem",
        "Lem + Lem + Lem + Flawed Emerald": "Pul",
        "Pul + Pul + Flawed Diamond": "Um",
        "Um + Um + Topaz": "Mal",
        "Mal + Mal + Amethyst": "Ist",
        "Ist + Ist + Sapphire": "Gul",
        "Gul + Gul + Ruby": "Vex",
        "Vex + Vex + Emerald": "Ohm",
        "Ohm + Ohm + Diamond": "Lo",
        "Lo + Lo + Flawless Topaz": "Sur",
        "Sur + Sur + Flawless Amethyst": "Ber",
        "Ber + Ber + Flawless Sapphire": "Jah",
        "Jah + Jah + Flawless Ruby": "Cham",
        "Cham + Cham + Flawless Emerald": "Zod",
    },
    "useful_recipes": {
        "Socket Quest": "Larzuk quest gives max sockets based on item level and type",
        "Unsocket Items": "Hel + TP Scroll + Socketed Item = Remove all gems/runes (destroys gems/runes)",
        "Upgrade Unique Armor": "Ko + Lem + Perfect Diamond + Unique Armor",
        "Upgrade Unique Weapon": "Lum + Pul + Perfect Emerald + Unique Weapon",
        "Reroll Grand Charm": "3 Perfect Gems + Magic Grand Charm (from specific area for +skills)",
        "Craft Caster Amulet": "Ral + Perfect Amethyst + Jewel + Magic Amulet",
        "Craft Blood Ring": "Sol + Perfect Ruby + Jewel + Magic Ring",
        "Token of Absolution": "Twisted Essence + Charged Essence + Burning Essence + Festering Essence",
    },
}

# ── Valuable Item Watchlist ───────────────────────────────────────────

VALUABLE_WATCHLIST = {
    "always_pick_up": {
        "runes": {
            "description": "High runes are always valuable",
            "items": [
                "Ber", "Jah", "Lo", "Sur", "Ohm", "Vex", "Gul", "Ist",
                "Mal", "Um", "Pul",
            ],
        },
        "uniques": {
            "description": "These uniques are almost always worth selling",
            "items": [
                "Shako (Harlequin Crest)",
                "Arachnid Mesh",
                "Mara's Kaleidoscope",
                "Stone of Jordan",
                "Griffon's Eye",
                "Death's Fathom",
                "Crown of Ages",
                "Bul-Kathos Wedding Band",
                "Highlord's Wrath",
                "War Traveler",
                "Herald of Zakarum",
                "Arreat's Face",
                "Andariel's Visage",
                "Nightwing's Veil",
                "Dracul's Grasp",
                "Gore Rider",
                "Verdungo's Hearty Cord",
                "Titan's Revenge",
                "Thunderstroke",
                "Eschuta's Temper",
                "Jalal's Mane",
                "Homunculus",
                "Stormshield",
            ],
        },
        "sets": {
            "description": "Valuable set pieces",
            "items": [
                "Tal Rasha's Guardianship (Armor)",
                "Tal Rasha's Adjudication (Amulet)",
                "IK Armor (Immortal King's Soul Cage)",
                "Trang-Oul's Claws (Gloves)",
            ],
        },
        "charms": {
            "description": "Always ID Grand Charms (Skillers), Small Charms, Annihilus, Torch",
            "items": [
                "Any Grand Charm from Hell (potential skiller)",
                "Small Charms with life/resist/FHR/MF",
                "Annihilus",
                "Hellfire Torch",
                "Gheeds Fortune",
            ],
        },
        "bases": {
            "description": "Valuable socketed bases for runewords",
            "items": [
                "4os Monarch (Spirit)",
                "5os Phase Blade (Grief)",
                "4os Flail (HOTO)",
                "3os Mage Plate / Dusk Shroud / Archon Plate",
                "4os Eth Thresher / Giant Thresher / Cryptic Axe",
                "5/6os Eth Berserker Axe / Colossus Blade",
                "4os 35+ Res Paladin Shield",
                "3os Eth Archon Plate / Sacred Armor",
                "4os Grand Matron Bow +3 skills",
            ],
        },
    },
    "check_rolls": {
        "description": "These items are common but high rolls can be very valuable",
        "items": [
            {"name": "Chance Guards", "check": "MF% (25-40)", "valuable_if": "40 MF"},
            {"name": "Gheeds Fortune", "check": "MF% (20-40)", "valuable_if": "35+ MF"},
            {"name": "War Traveler", "check": "MF% (30-50)", "valuable_if": "45+ MF"},
            {"name": "Mara's Kaleidoscope", "check": "Res (20-30)", "valuable_if": "28+ Res"},
            {"name": "Annihilus", "check": "Stats/Res/Exp", "valuable_if": "18+/18+/10 or 20/20/10"},
            {"name": "Torch", "check": "Stats/Res + Class", "valuable_if": "18+/18+ Sorc/Pally"},
            {"name": "Call to Arms", "check": "BO level (1-6)", "valuable_if": "+5 or +6 BO"},
            {"name": "Grief", "check": "Damage (340-400) / IAS (30-40)", "valuable_if": "390+ dmg, 40 IAS"},
            {"name": "Infinity", "check": "ED (255-325) / -ELR (45-55)", "valuable_if": "-55 ELR"},
            {"name": "Griffon's Eye", "check": "-ELR (15-20) / +Light (10-15)", "valuable_if": "-20/+15"},
            {"name": "Death's Fathom", "check": "Cold% (15-30)", "valuable_if": "25%+ cold"},
        ],
    },
}


class CommunityTools:
    """Provides community tools, guides, and calculators for D2R."""

    def get_build_guide(self, build_name):
        """Get a specific build guide."""
        for name, guide in BUILD_GUIDES.items():
            if build_name.lower() in name.lower():
                return {"name": name, **guide}
        return None

    def list_build_guides(self):
        """List all available build guides with summary."""
        return [
            {
                "name": name,
                "class": guide["class"],
                "tier": guide["tier"],
                "type": guide["type"],
                "difficulty": guide["difficulty"],
                "description": guide["description"],
            }
            for name, guide in BUILD_GUIDES.items()
        ]

    def get_breakpoints(self, char_class, bp_type="FCR"):
        """Get breakpoint table for a class."""
        class_data = BREAKPOINT_TABLES.get(char_class)
        if not class_data:
            return None
        return class_data.get(bp_type)

    def get_all_breakpoints(self, char_class):
        """Get all breakpoint tables for a class."""
        return BREAKPOINT_TABLES.get(char_class)

    def get_cube_recipes(self):
        """Return all Horadric Cube recipes."""
        return CUBE_RECIPES

    def get_valuable_watchlist(self):
        """Return the valuable items watchlist."""
        return VALUABLE_WATCHLIST

    def calculate_rune_upgrade_cost(self, target_rune, starting_rune="El"):
        """Calculate how many of a starting rune you need to cube up to a target rune."""
        from config import Config

        rune_order = list(Config.HR_TO_FG.keys())
        # Reverse to go from low to high
        rune_order_low_to_high = list(reversed(rune_order))

        if target_rune not in rune_order_low_to_high:
            return {"error": f"Unknown rune: {target_rune}"}
        if starting_rune not in rune_order_low_to_high:
            return {"error": f"Unknown rune: {starting_rune}"}

        start_idx = rune_order_low_to_high.index(starting_rune)
        target_idx = rune_order_low_to_high.index(target_rune)

        if start_idx >= target_idx:
            return {"error": "Starting rune must be lower than target rune"}

        # Calculate: each upgrade requires 3 runes (or 2 for high runes)
        count = 1
        for i in range(start_idx, target_idx):
            if i < 20:  # Low runes: 3 to 1
                count *= 3
            else:  # High runes (Pul+): 2 to 1
                count *= 2

        return {
            "starting_rune": starting_rune,
            "target_rune": target_rune,
            "runes_needed": count,
            "fg_value_target": Config.HR_TO_FG.get(target_rune, 0),
        }

    def check_fcr_breakpoint(self, char_class, current_fcr):
        """Check which FCR breakpoint a character is at and what's next."""
        bp_data = self.get_breakpoints(char_class, "FCR")
        if not bp_data:
            return {"error": f"No FCR data for {char_class}"}

        breakpoints = bp_data["breakpoints"]
        current_bp = None
        next_bp = None

        for i, bp in enumerate(breakpoints):
            if current_fcr >= bp["fcr"]:
                current_bp = bp
                if i + 1 < len(breakpoints):
                    next_bp = breakpoints[i + 1]
            else:
                if next_bp is None:
                    next_bp = bp
                break

        result = {
            "class": char_class,
            "current_fcr": current_fcr,
            "current_frames": current_bp["frames"] if current_bp else breakpoints[0]["frames"],
        }

        if next_bp:
            result["next_breakpoint"] = next_bp["fcr"]
            result["fcr_needed"] = next_bp["fcr"] - current_fcr
            result["next_frames"] = next_bp["frames"]

        return result
