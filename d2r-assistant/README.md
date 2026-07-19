# D2R Inventory Assistant

An all-in-one inventory organizer and trading assistant for Diablo II: Resurrected. Track your gear across characters, analyze item rolls, get pricing data, generate trade posts for D2JSP and Traderie, and access community tools like build guides and breakpoint calculators.

## Features

### Inventory Management
- Track multiple characters with full gear loadouts
- Manage equipped gear across 12 slots (including weapon swap)
- Personal and shared stash with 3 tabs each
- Search across all characters, inventories, and stashes
- Item tallying and breakdown by quality

### Item Analysis
- Roll quality analysis for all variable modifiers (% rating from low to perfect)
- Color-coded quality indicators (red/orange/yellow/green/gold)
- Complete modifier range database for runewords and popular uniques
- Auto-fill mod templates from the database for quick analysis

### Pricing Engine
- Forum Gold (FG) price estimates for 60+ items
- Price ranges adjusted by roll quality
- FG to High Rune conversion calculator
- HR to FG conversion with current rates
- Bulk pricing for multiple items

### Trade Integration
- **D2JSP**: Generate formatted FT (For Trade) and ISO (In Search Of) posts with BBCode
- **Traderie**: Generate listing descriptions with stat summaries
- Sales pitch generator that highlights high rolls and provides pricing
- Transaction history tracking (sales and purchases)
- Net profit/loss dashboard

### Community Tools
- **Build Guides**: 6 popular builds (Lightning Sorc, Hammerdin, Javazon, Blizzard Sorc, Smiter, Summon Necro)
  - Skill point allocation, gear recommendations (BIS and budget), merc setup, farm spots
- **Breakpoint Calculator**: FCR and FHR tables for all 7 classes with "what's my next breakpoint" checker
- **Valuable Items Watchlist**: What to always pick up, and which common items have premium rolls
- **Cube Recipes**: Rune upgrades, useful crafting recipes
- **Rune Upgrade Calculator**: How many lower runes you need to cube up to a target rune

## Quick Start

```bash
cd d2r-assistant

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Run the application
python app.py
```

Open `http://localhost:5000` in your browser.

## Project Structure

```
d2r-assistant/
  app.py                 - Flask web application (routes + API)
  config.py              - Configuration and HR/FG rates
  inventory_manager.py   - Character/inventory/stash management
  item_analyzer.py       - Item roll quality analysis engine
  price_engine.py        - Pricing, FG/HR conversion, market data
  trade_integration.py   - D2JSP/Traderie post generation
  community_tools.py     - Build guides, breakpoints, calculators
  requirements.txt       - Python dependencies
  data/
    item_database.json   - Comprehensive D2R item/runeword database
    inventory.json       - Your inventory data (auto-created)
    price_cache.json     - Cached price lookups (auto-created)
    trade_history.json   - Trade post/transaction history (auto-created)
  templates/
    base.html            - Base template with nav and shared layout
    index.html           - Dashboard with characters and stash
    character.html       - Character detail with gear grid
    analyzer.html        - Item analyzer with roll quality display
    prices.html          - Full price guide with converter
    trade.html           - Trade post generator and history
    guides.html          - Build guides and community tools
  static/
    css/style.css        - Dark theme D2R-styled CSS
    js/app.js            - Global JavaScript (search, toasts, utils)
```

## API Endpoints

### Characters
- `GET /api/characters` - List all characters
- `POST /api/characters` - Create character
- `GET /api/characters/<name>` - Get character details
- `DELETE /api/characters/<name>` - Delete character
- `POST /api/characters/<name>/equip` - Equip item to slot
- `POST /api/characters/<name>/unequip/<slot>` - Unequip item
- `POST /api/characters/<name>/inventory` - Add to inventory

### Analysis
- `POST /api/analyze` - Analyze item roll quality
- `GET /api/search?q=<query>` - Search items across inventory and database
- `GET /api/runewords` - List all runewords
- `GET /api/runeword/<name>` - Get runeword details
- `GET /api/uniques` - List all unique items
- `GET /api/bases` - List valuable bases

### Pricing
- `GET /api/price/<item_name>` - Get item price estimate
- `GET /api/prices` - Full price guide
- `POST /api/price/bulk` - Price multiple items
- `GET /api/convert/fg-to-hr?fg=<amount>` - Convert FG to HR
- `GET /api/convert/hr-to-fg?rune=<name>&qty=<n>` - Convert HR to FG

### Trading
- `POST /api/trade/generate` - Generate trade post
- `POST /api/trade/pitch` - Generate sales pitch
- `POST /api/trade/record-sale` - Record a sale
- `POST /api/trade/record-purchase` - Record a purchase
- `GET /api/trade/summary` - Get trade profit/loss summary

### Community
- `GET /api/builds` - List build guides
- `GET /api/builds/<name>` - Get full build guide
- `GET /api/breakpoints/<class>` - Get breakpoint tables
- `GET /api/breakpoints/<class>/check?fcr=<n>` - Check current breakpoint
- `GET /api/cube-recipes` - Cube recipes
- `GET /api/rune-calc?target=<rune>&start=<rune>` - Rune upgrade calculator

## Configuration

Edit `.env` to configure:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key |
| `DEBUG` | Enable debug mode (true/false) |
| `D2JSP_USERNAME` | D2JSP username for trade posting |
| `D2JSP_SESSION_ID` | D2JSP session cookie |
| `TRADERIE_API_KEY` | Traderie API key |

HR/FG conversion rates can be updated in `config.py` under `HR_TO_FG`.

## Tech Stack

- **Backend**: Python 3, Flask
- **Frontend**: Bootstrap 5 (dark theme), vanilla JavaScript
- **Data**: JSON file storage (no database required)
- **Styling**: Custom D2R-themed dark UI with item quality colors

## Notes

- This is a standalone tool. It does not read game memory or interact with D2R directly.
- All inventory data is entered manually through the web UI.
- Price estimates are baseline values and should be verified against current market conditions.
- D2JSP and Traderie integration generates formatted text for copy/paste - it does not post directly to those platforms.
