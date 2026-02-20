"""
D2R Inventory Assistant - Flask Application

Main web application that ties together all modules:
- Inventory management
- Item analysis
- Price engine
- Trade integration
- Community tools
"""
import json
import os
import sys
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS

from config import Config
from inventory_manager import InventoryManager
from item_analyzer import ItemAnalyzer
from price_engine import PriceEngine
from trade_integration import TradeIntegration
from community_tools import CommunityTools

# Set template and static dirs for PyInstaller bundle
template_dir = os.path.join(Config.BASE_DIR, "templates")
static_dir = os.path.join(Config.BASE_DIR, "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(Config)
CORS(app)

# Initialize modules
inventory = InventoryManager()
analyzer = ItemAnalyzer()
pricer = PriceEngine()
trader = TradeIntegration()
community = CommunityTools()


# ══════════════════════════════════════════════════════════════════════
# Page Routes
# ══════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Main dashboard."""
    chars = inventory.list_characters()
    tally = inventory.tally_items()
    return render_template("index.html", characters=chars, tally=tally)


@app.route("/character/<name>")
def character_page(name):
    """Character detail page."""
    char = inventory.get_character(name)
    if isinstance(char, dict) and "error" in char:
        return redirect(url_for("index"))
    return render_template("character.html", character=char)


@app.route("/analyzer")
def analyzer_page():
    """Item analyzer page."""
    return render_template("analyzer.html")


@app.route("/prices")
def prices_page():
    """Price guide page."""
    all_prices = pricer.get_all_prices()
    hr_rates = pricer.get_hr_rates()
    return render_template("prices.html", prices=all_prices, hr_rates=hr_rates)


@app.route("/trade")
def trade_page():
    """Trade posting page."""
    history = trader.get_post_history(limit=10)
    summary = trader.get_trade_summary()
    return render_template("trade.html", history=history, summary=summary)


@app.route("/guides")
def guides_page():
    """Community guides and tools."""
    builds = community.list_build_guides()
    watchlist = community.get_valuable_watchlist()
    return render_template("guides.html", builds=builds, watchlist=watchlist)


# ══════════════════════════════════════════════════════════════════════
# API Routes - Characters
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/characters", methods=["GET"])
def api_list_characters():
    return jsonify(inventory.list_characters())


@app.route("/api/characters", methods=["POST"])
def api_create_character():
    data = request.get_json()
    result = inventory.create_character(
        data.get("name", ""),
        data.get("class", ""),
        data.get("level", 1),
    )
    return jsonify(result)


@app.route("/api/characters/<name>", methods=["GET"])
def api_get_character(name):
    return jsonify(inventory.get_character(name))


@app.route("/api/characters/<name>", methods=["DELETE"])
def api_delete_character(name):
    return jsonify(inventory.delete_character(name))


@app.route("/api/characters/<name>/level", methods=["PUT"])
def api_update_level(name):
    data = request.get_json()
    return jsonify(inventory.update_character_level(name, data.get("level", 1)))


# ══════════════════════════════════════════════════════════════════════
# API Routes - Equipment
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/characters/<name>/equip", methods=["POST"])
def api_equip_item(name):
    data = request.get_json()
    return jsonify(inventory.equip_item(name, data.get("slot", ""), data.get("item", {})))


@app.route("/api/characters/<name>/unequip/<slot>", methods=["POST"])
def api_unequip_item(name, slot):
    return jsonify(inventory.unequip_item(name, slot))


@app.route("/api/characters/<name>/equipped", methods=["GET"])
def api_get_equipped(name):
    return jsonify(inventory.get_equipped(name))


# ══════════════════════════════════════════════════════════════════════
# API Routes - Inventory
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/characters/<name>/inventory", methods=["GET"])
def api_get_inventory(name):
    return jsonify(inventory.get_inventory(name))


@app.route("/api/characters/<name>/inventory", methods=["POST"])
def api_add_to_inventory(name):
    data = request.get_json()
    return jsonify(inventory.add_to_inventory(name, data))


@app.route("/api/characters/<name>/inventory/<item_id>", methods=["DELETE"])
def api_remove_from_inventory(name, item_id):
    return jsonify(inventory.remove_from_inventory(name, item_id))


# ══════════════════════════════════════════════════════════════════════
# API Routes - Stash
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/stash", methods=["GET"])
def api_get_stash():
    stash_type = request.args.get("type", "shared")
    char_name = request.args.get("character")
    return jsonify(inventory.get_stash(stash_type, char_name))


@app.route("/api/stash", methods=["POST"])
def api_add_to_stash():
    data = request.get_json()
    return jsonify(inventory.add_to_stash(
        data.get("item", {}),
        data.get("stash_type", "shared"),
        data.get("tab", "tab1"),
        data.get("character"),
    ))


@app.route("/api/stash/<item_id>", methods=["DELETE"])
def api_remove_from_stash(item_id):
    stash_type = request.args.get("type", "shared")
    char_name = request.args.get("character")
    tab = request.args.get("tab")
    return jsonify(inventory.remove_from_stash(item_id, stash_type, tab, char_name))


# ══════════════════════════════════════════════════════════════════════
# API Routes - Search
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/search", methods=["GET"])
def api_search():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"})

    # Search both inventory and item database
    inventory_results = inventory.search_all_items(query)
    db_results = analyzer.search_items(query)

    return jsonify({
        "query": query,
        "inventory_matches": inventory_results,
        "database_matches": db_results,
    })


@app.route("/api/tally", methods=["GET"])
def api_tally():
    return jsonify(inventory.tally_items())


# ══════════════════════════════════════════════════════════════════════
# API Routes - Item Analysis
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/analyze", methods=["POST"])
def api_analyze_item():
    """Analyze an item's roll quality."""
    data = request.get_json()
    result = analyzer.analyze_item(data)
    return jsonify(result)


@app.route("/api/runeword/<name>", methods=["GET"])
def api_runeword_info(name):
    """Get runeword details."""
    result = analyzer.get_runeword_info(name)
    if result:
        return jsonify(result)
    return jsonify({"error": f"Runeword '{name}' not found"}), 404


@app.route("/api/runewords", methods=["GET"])
def api_all_runewords():
    return jsonify(analyzer.get_all_runewords())


@app.route("/api/uniques", methods=["GET"])
def api_all_uniques():
    return jsonify(analyzer.get_all_uniques())


@app.route("/api/bases", methods=["GET"])
def api_valuable_bases():
    return jsonify(analyzer.get_valuable_bases())


# ══════════════════════════════════════════════════════════════════════
# API Routes - Pricing
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/price/<item_name>", methods=["GET"])
def api_get_price(item_name):
    quality = request.args.get("quality", type=float)
    return jsonify(pricer.get_price(item_name, quality))


@app.route("/api/prices", methods=["GET"])
def api_all_prices():
    return jsonify(pricer.get_all_prices())


@app.route("/api/price/bulk", methods=["POST"])
def api_bulk_price():
    data = request.get_json()
    return jsonify(pricer.bulk_price(data.get("items", [])))


@app.route("/api/hr-rates", methods=["GET"])
def api_hr_rates():
    return jsonify(pricer.get_hr_rates())


@app.route("/api/convert/hr-to-fg", methods=["GET"])
def api_hr_to_fg():
    rune = request.args.get("rune", "")
    qty = request.args.get("qty", 1, type=int)
    return jsonify(pricer.hr_to_fg_convert(rune, qty))


@app.route("/api/convert/fg-to-hr", methods=["GET"])
def api_fg_to_hr():
    fg = request.args.get("fg", 0, type=int)
    return jsonify({"fg": fg, "hr": pricer.fg_to_hr(fg)})


# ══════════════════════════════════════════════════════════════════════
# API Routes - Trade
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/trade/generate", methods=["POST"])
def api_generate_trade_post():
    """Generate a trade post for D2JSP or Traderie."""
    data = request.get_json()
    platform = data.get("platform", "d2jsp")
    mode = data.get("mode", "ft")
    items = data.get("items", [])

    if platform == "d2jsp":
        result = trader.generate_d2jsp_post(items, mode, pricer)
    elif platform == "traderie":
        result = trader.generate_traderie_post(items, pricer)
    else:
        result = {"error": f"Unknown platform: {platform}"}

    return jsonify(result)


@app.route("/api/trade/pitch", methods=["POST"])
def api_sales_pitch():
    """Generate a sales pitch for an item."""
    data = request.get_json()
    item = data.get("item", {})
    analysis = analyzer.analyze_item(item) if item.get("name") else None
    price_data = pricer.get_price(item.get("name", "")) if item.get("name") else None
    pitch = trader.generate_sales_pitch(item, analysis, price_data)
    return jsonify({"pitch": pitch})


@app.route("/api/trade/history", methods=["GET"])
def api_trade_history():
    platform = request.args.get("platform")
    limit = request.args.get("limit", 20, type=int)
    return jsonify(trader.get_post_history(platform, limit))


@app.route("/api/trade/record-sale", methods=["POST"])
def api_record_sale():
    data = request.get_json()
    return jsonify(trader.record_sale(
        data.get("item", ""),
        data.get("price_fg", 0),
        data.get("platform", ""),
        data.get("buyer"),
    ))


@app.route("/api/trade/record-purchase", methods=["POST"])
def api_record_purchase():
    data = request.get_json()
    return jsonify(trader.record_purchase(
        data.get("item", ""),
        data.get("price_fg", 0),
        data.get("platform", ""),
        data.get("seller"),
    ))


@app.route("/api/trade/summary", methods=["GET"])
def api_trade_summary():
    return jsonify(trader.get_trade_summary())


# ══════════════════════════════════════════════════════════════════════
# API Routes - Community Tools
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/builds", methods=["GET"])
def api_list_builds():
    return jsonify(community.list_build_guides())


@app.route("/api/builds/<name>", methods=["GET"])
def api_get_build(name):
    guide = community.get_build_guide(name)
    if guide:
        return jsonify(guide)
    return jsonify({"error": "Build guide not found"}), 404


@app.route("/api/breakpoints/<char_class>", methods=["GET"])
def api_breakpoints(char_class):
    result = community.get_all_breakpoints(char_class)
    if result:
        return jsonify(result)
    return jsonify({"error": f"No data for class: {char_class}"}), 404


@app.route("/api/breakpoints/<char_class>/check", methods=["GET"])
def api_check_breakpoint(char_class):
    fcr = request.args.get("fcr", 0, type=int)
    return jsonify(community.check_fcr_breakpoint(char_class, fcr))


@app.route("/api/cube-recipes", methods=["GET"])
def api_cube_recipes():
    return jsonify(community.get_cube_recipes())


@app.route("/api/watchlist", methods=["GET"])
def api_watchlist():
    return jsonify(community.get_valuable_watchlist())


@app.route("/api/rune-calc", methods=["GET"])
def api_rune_calc():
    target = request.args.get("target", "")
    start = request.args.get("start", "El")
    return jsonify(community.calculate_rune_upgrade_cost(target, start))


# ══════════════════════════════════════════════════════════════════════
# Error Handlers
# ══════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("index.html"), 500


if __name__ == "__main__":
    os.makedirs(Config.DATA_DIR, exist_ok=True)

    port = 5000
    is_frozen = getattr(sys, 'frozen', False)

    if is_frozen:
        # When running as exe, auto-open browser after a short delay
        def open_browser():
            webbrowser.open(f"http://localhost:{port}")
        threading.Timer(1.5, open_browser).start()
        print(f"D2R Inventory Assistant starting on http://localhost:{port}")
        print("Close this window to stop the server.")

    app.run(debug=Config.DEBUG, host="0.0.0.0", port=port, use_reloader=not is_frozen)
