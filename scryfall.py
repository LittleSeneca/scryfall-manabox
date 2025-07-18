"""Scryfall API integration for ManaBox cards."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

import requests

from manabox import ManaboxCard, import_from_csv

logger = logging.getLogger(__name__)


def get_card_data(card_id: str) -> dict[str, Any]:
    """Get card data from Scryfall API."""
    url = f"https://api.scryfall.com/cards/{card_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def enrich_card_with_scryfall_data(card: ManaboxCard) -> dict[str, Any]:
    """Enrich a manabox card with Scryfall API data."""
    card_dict = card.to_dict()

    try:
        # Use scryfall_id if available, otherwise skip API call
        if card.scryfall_id:
            scryfall_data = get_card_data(card.scryfall_id)
            card_dict["scryfall_data"] = scryfall_data
        else:
            card_dict["scryfall_data"] = None

    except requests.RequestException as e:
        logger.warning("Failed to fetch Scryfall data for %s: %s", card.name, e)
        card_dict["scryfall_data"] = None

    return card_dict


def enrich_manabox_csv_with_scryfall(csv_path: str | Path, delay_ms: int = 100) -> list[dict[str, Any]]:
    """
    Read manabox CSV and enrich each card with Scryfall API data.

    Args:
        csv_path: Path to the manabox CSV file
        delay_ms: Delay between API requests in milliseconds (default: 100)

    Returns:
        List of enriched card dictionaries with scryfall_data added
    """
    # Import cards from CSV
    cards = import_from_csv(csv_path)
    enriched_cards = []

    total_cards = len(cards)
    logger.info("Enriching %d unique cards with Scryfall data...", total_cards)

    for i, card in enumerate(cards, 1):
        logger.info("Processing card %d/%d: %s", i, total_cards, card.name)

        # Enrich with Scryfall data
        enriched_card = enrich_card_with_scryfall_data(card)
        enriched_cards.append(enriched_card)

        # Add delay between requests (except for last card)
        if i < total_cards:
            time.sleep(delay_ms / 1000.0)

    logger.info("Completed enriching %d cards", total_cards)
    return enriched_cards


def save_enriched_data_to_json(enriched_cards: list[dict[str, Any]], output_path: str | Path) -> None:
    """Save enriched card data to JSON file."""

    output_path = Path(output_path)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(enriched_cards, file, indent=2, ensure_ascii=False)

    logger.info("Saved enriched data to %s", output_path)


def process_manabox_csv_with_scryfall(csv_path: str | Path, output_path: str | Path, delay_ms: int = 100) -> None:
    """
    Complete workflow: read CSV, enrich with Scryfall, save to JSON.

    Args:
        csv_path: Path to the manabox CSV file
        output_path: Path for the output JSON file
        delay_ms: Delay between API requests in milliseconds
    """
    enriched_cards = enrich_manabox_csv_with_scryfall(csv_path, delay_ms)
    save_enriched_data_to_json(enriched_cards, output_path)
