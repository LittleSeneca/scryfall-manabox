# Scryfall Manabox Importer

## Introduction
This project helps Magic The Gathering players by taking an exported CSV file from Manabox, querying Scryfall for all of the metadata and primary data for each card, and creating a new JSON file containing all of the contents from both Manabox and Scryfall.

## Requirements
1. You must have a modern version of Python 3.8+ installed locally
2. You must have pip installed locally
3. You must have git installed locally

## Installation
1. Pull down the project repository with the command: `git clone git@github.com:LittleSeneca/scryfall-manabox.git`
2. CD to the project directory with the following command: `cd scryfall-manabox`
3. Create a python environment with the following command: `python -m venv .venv`
4. Initialize the python environment with the following command: `source .venv/bin/activate`
5. Install dependencies with the following command: `pip install -r requirements.txt`
6. Run the project with the following command: `python main.py --input /path/to/your/manabox.csv --output /path/to/where/you/want/the/export.json`

## Usage Examples
```bash
# Basic usage (full data output)
python main.py --input "Red Green Dragons.csv" --output "enriched_cards.json"

# Concise output with only game-mechanics fields
python main.py --input "Red Green Dragons.csv" --output "concise_cards.json" --concise

# Concise output with flattened legalities (boolean fields)
python main.py --input "Red Green Dragons.csv" --output "concise_flat.json" --concise --flatten-legalities

# With custom delay and verbose logging
python main.py -i input.csv -o output.json --delay 200 --verbose

# Using short arguments with concise output and flattened legalities
python main.py -i cards.csv -o enriched.json -c -f -v
```

## Output Formats

### Full Output (default)
Contains complete data from both Manabox and Scryfall, including:
- All Manabox fields (name, quantity, set info, pricing, condition, etc.)
- Complete Scryfall API response nested under `scryfall_data`
- All metadata, images, pricing, related URIs, etc.

### Concise Output (`--concise` flag)
Contains only game-mechanics related fields for deck building and gameplay:

**Manabox Fields:**
- `name` - Card name
- `quantity` - Number of copies
- `set_name` - Set name
- `collector_number` - Collector number
- `rarity` - Card rarity
- `scryfall_id` - Scryfall UUID
- `mana_box_id` - ManaBox ID

**Scryfall Game Mechanics Fields:**
- `mana_cost` - Mana cost (e.g., "{2}{R}")
- `cmc` - Converted mana cost
- `type_line` - Full type line (e.g., "Creature — Dragon")
- `oracle_text` - Current rules text
- `power` - Power (for creatures)
- `toughness` - Toughness (for creatures)
- `colors` - Color identity array
- `color_identity` - Commander color identity
- `keywords` - Keyword abilities
- `legalities` - Format legality status (full object)

### Concise Output with Flattened Legalities (`--concise --flatten-legalities`)
Same as concise output, but replaces the full `legalities` object with simple boolean fields:

**Flattened Legality Fields:**
- `commander_legal` - Boolean: true if legal in Commander
- `standard_legal` - Boolean: true if legal in Standard
- `modern_legal` - Boolean: true if legal in Modern

This is useful for deck builders who only care about the most common formats and want simpler data structures.

## Features
- Imports Manabox CSV files with proper validation
- Enriches each card with comprehensive Scryfall API data
- Rate-limited API requests (100ms delay by default)
- Robust error handling and logging
- Three output modes: full data, concise game-mechanics, or concise with flattened legalities
- Outputs enriched data in JSON format with complete Scryfall data nested under `scryfall_data`
