#!/usr/bin/env python3
"""
Scryfall Manabox Importer

Takes an exported CSV file from Manabox, queries Scryfall for metadata,
and creates a new JSON file containing data from both sources.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from manabox import ManaboxError
from scryfall import enrich_manabox_csv_with_scryfall, save_enriched_data_to_json

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def create_concise_output(enriched_cards: list[dict[str, Any]], flatten_legalities: bool = False) -> list[dict[str, Any]]:
    """Create concise output with only game-mechanics related fields."""
    concise_cards = []

    for card in enriched_cards:
        # Start with key manabox fields
        concise_card = {
            "name": card.get("name"),
            "quantity": card.get("quantity"),
            "set_name": card.get("set_name"),
            "collector_number": card.get("collector_number"),
            "rarity": card.get("rarity"),
            "scryfall_id": card.get("scryfall_id"),
            "mana_box_id": card.get("mana_box_id"),
        }

        # Add game-mechanics fields from scryfall_data
        scryfall_data = card.get("scryfall_data")
        if scryfall_data:
            # Core game mechanics fields (excluding legalities for now)
            game_mechanics_fields = ["mana_cost", "cmc", "type_line", "oracle_text", "power", "toughness", "colors", "color_identity", "keywords"]

            for field in game_mechanics_fields:
                if field in scryfall_data:
                    concise_card[field] = scryfall_data[field]

            # Handle legalities based on flatten_legalities flag
            if "legalities" in scryfall_data:
                legalities = scryfall_data["legalities"]
                if flatten_legalities:
                    # Flatten to boolean fields for common formats
                    concise_card["commander_legal"] = legalities.get("commander") == "legal"
                    concise_card["standard_legal"] = legalities.get("standard") == "legal"
                    concise_card["modern_legal"] = legalities.get("modern") == "legal"
                else:
                    # Include full legalities object
                    concise_card["legalities"] = legalities

        concise_cards.append(concise_card)

    return concise_cards


def process_manabox_csv(input_path: Path, output_path: Path, delay_ms: int = 100, concise: bool = False, flatten_legalities: bool = False) -> None:
    """
    Main processing function: read Manabox CSV, enrich with Scryfall, save JSON.

    Args:
        input_path: Path to input Manabox CSV file
        output_path: Path for output JSON file
        delay_ms: Delay between Scryfall API requests in milliseconds
        concise: Whether to output only game-mechanics related fields
        flatten_legalities: Whether to flatten legalities to simple boolean fields
    """
    logger.info("Starting Scryfall Manabox import process")
    logger.info("Input: %s", input_path)
    logger.info("Output: %s", output_path)
    if concise:
        logger.info("Using concise output (game-mechanics fields only)")
    if flatten_legalities:
        logger.info("Using flattened legalities (commander/standard/modern boolean fields)")

    # Validate input file exists
    if not input_path.exists():
        msg = f"Input file not found: {input_path}"
        raise FileNotFoundError(msg)

    try:
        # Enrich cards with Scryfall data
        enriched_cards = enrich_manabox_csv_with_scryfall(input_path, delay_ms)

        # Filter to concise output if requested
        if concise:
            enriched_cards = create_concise_output(enriched_cards, flatten_legalities)

        # Save to JSON format
        save_enriched_data_to_json(enriched_cards, output_path)

        logger.info("Process completed successfully!")

    except ManaboxError as e:
        logger.exception("Manabox processing error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import Manabox CSV and enrich with Scryfall data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --input cards.csv --output enriched_cards.json
    python main.py -i input.csv -o output.json --delay 200 --verbose
    python main.py -i input.csv -o concise.json --concise
    python main.py -i input.csv -o concise.json --concise --flatten-legalities
        """,
    )

    parser.add_argument("--input", "-i", type=Path, required=True, help="Path to input Manabox CSV file")

    parser.add_argument("--output", "-o", type=Path, required=True, help="Path for output JSON file with Scryfall data")

    parser.add_argument("--delay", type=int, default=100, help="Delay between Scryfall API requests in milliseconds (default: 100)")

    parser.add_argument("--concise", "-c", action="store_true", help="Output only game-mechanics related fields (mana cost, type, power/toughness, colors, legalities, etc.)")

    parser.add_argument(
        "--flatten-legalities", "-f", action="store_true", help="Flatten legalities to boolean fields: commander_legal, standard_legal, modern_legal (only works with --concise)"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_arguments()

    # Setup logging
    setup_logging(args.verbose)

    # Process the files
    process_manabox_csv(args.input, args.output, args.delay, args.concise, args.flatten_legalities)


if __name__ == "__main__":
    main()
