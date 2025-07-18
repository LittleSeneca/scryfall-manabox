"""ManaBox card management."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class ManaboxError(Exception):
    """Base exception for Manabox operations."""


class InvalidCSVFormatError(ManaboxError):
    """Raised when CSV format is invalid."""

    def __init__(self, details: str = "Invalid CSV format"):
        super().__init__(details)


class MissingColumnsError(ManaboxError):
    """Raised when required CSV columns are missing."""

    def __init__(self):
        super().__init__("Required columns missing")


class InvalidRowDataError(ManaboxError):
    """Raised when a CSV row contains invalid data."""

    def __init__(self, row_num: int, details: str):
        super().__init__(f"Row {row_num}: {details}")
        self.row_num = row_num


@dataclass
class ManaboxCard:
    """Represents a Magic: The Gathering card from ManaBox with all relevant data."""

    name: str
    quantity: int
    price: float
    total_price: float
    set_code: str
    set_name: str
    collector_number: str
    foil: bool
    rarity: str
    mana_box_id: str
    scryfall_id: str
    purchase_price: float | None = None
    misprint: bool = False
    altered: bool = False
    condition: str = "Near Mint"
    language: str = "English"
    purchase_price_currency: str = "USD"

    def to_dict(self) -> dict[str, Any]:
        """Convert the card to a dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self, indent: int | None = None) -> str:
        """Convert the card to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> ManaboxCard:
        """Create a ManaboxCard instance from a CSV row dictionary."""
        return cls(
            name=row["Name"],
            quantity=int(row["Quantity"]) if row["Quantity"] else 0,
            price=float(row.get("Price", "0")) if row.get("Price") else 0.0,
            total_price=float(row.get("Total price", "0")) if row.get("Total price") else 0.0,
            set_code=row["Set code"],
            set_name=row["Set name"],
            collector_number=row["Collector number"],
            foil=row["Foil"].lower() in ("true", "1", "yes") if row["Foil"] else False,
            rarity=row["Rarity"],
            mana_box_id=row["ManaBox ID"],
            scryfall_id=row["Scryfall ID"],
            purchase_price=float(row["Purchase price"]) if row.get("Purchase price") else None,
            misprint=row.get("Misprint", "").lower() in ("true", "1", "yes"),
            altered=row.get("Altered", "").lower() in ("true", "1", "yes"),
            condition=row.get("Condition", "Near Mint"),
            language=row.get("Language", "English"),
            purchase_price_currency=row.get("Purchase price currency", "USD"),
        )


def _validate_csv_columns(reader: csv.DictReader) -> None:
    """Validate that all required columns are present in the CSV."""
    required_columns = {"Name", "Quantity", "Set code", "Set name", "Collector number", "Foil", "Rarity", "ManaBox ID", "Scryfall ID"}

    fieldnames = set(reader.fieldnames or [])
    if not required_columns.issubset(fieldnames):
        raise MissingColumnsError


def _process_csv_row(row: dict[str, str], row_num: int) -> ManaboxCard:
    """Process a single CSV row into a ManaboxCard."""
    try:
        return ManaboxCard.from_csv_row(row)
    except (ValueError, TypeError) as e:
        raise InvalidRowDataError(row_num, str(e)) from e


def _read_csv_file(file_path: Path, encoding: str) -> list[ManaboxCard]:
    """Read and process the CSV file."""
    cards = []

    with file_path.open("r", encoding=encoding) as file:
        reader = csv.DictReader(file)
        _validate_csv_columns(reader)

        for row_num, row in enumerate(reader, start=2):
            card = _process_csv_row(row, row_num)
            cards.append(card)

    return cards


def import_from_csv(file_path: str | Path, encoding: str = "utf-8") -> list[ManaboxCard]:
    """
    Import ManaBox cards from a CSV file.

    Args:
        file_path: Path to the CSV file
        encoding: File encoding (default: utf-8)

    Returns:
        List of ManaboxCard instances

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        MissingColumnsError: If required CSV columns are missing
        InvalidRowDataError: If CSV row contains invalid data
        InvalidCSVFormatError: If CSV format is invalid
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError

    try:
        return _read_csv_file(file_path, encoding)
    except csv.Error as e:
        raise InvalidCSVFormatError(str(e)) from e


def _convert_cards_to_dict_list(cards: list[ManaboxCard]) -> list[dict[str, Any]]:
    """Convert a list of ManaboxCard instances to a list of dictionaries."""
    return [card.to_dict() for card in cards]


def export_to_json(cards: list[ManaboxCard], output_path: str | Path, indent: int = 2, encoding: str = "utf-8") -> None:
    """
    Export ManaBox cards to a JSON file.

    Args:
        cards: List of ManaboxCard instances
        output_path: Path for the output JSON file
        indent: JSON indentation (default: 2)
        encoding: File encoding (default: utf-8)
    """
    output_path = Path(output_path)
    cards_data = _convert_cards_to_dict_list(cards)

    with output_path.open("w", encoding=encoding) as file:
        json.dump(cards_data, file, indent=indent, ensure_ascii=False)


def csv_to_json(csv_path: str | Path, json_path: str | Path, encoding: str = "utf-8", indent: int = 2) -> int:
    """
    Convert a ManaBox CSV file directly to JSON.

    Args:
        csv_path: Path to the input CSV file
        json_path: Path for the output JSON file
        encoding: File encoding (default: utf-8)
        indent: JSON indentation (default: 2)

    Returns:
        Number of cards processed

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        MissingColumnsError: If required CSV columns are missing
        InvalidRowDataError: If CSV row contains invalid data
        InvalidCSVFormatError: If CSV format is invalid
    """
    cards = import_from_csv(csv_path, encoding=encoding)
    export_to_json(cards, json_path, indent=indent, encoding=encoding)
    return len(cards)
