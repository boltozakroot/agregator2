from __future__ import annotations

import argparse
from pathlib import Path

from src.ecotech_parser import EcotechParser


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ecotechstroy houses parser")
    parser.add_argument("--json", default="output/houses.json", help="Path to JSON output")
    parser.add_argument("--csv", default="output/houses.csv", help="Path to CSV output")
    return parser


def main() -> None:
    args = build_cli().parse_args()

    parser = EcotechParser()
    houses = parser.parse()

    parser.export_json(houses, Path(args.json))
    parser.export_csv(houses, Path(args.csv))

    print(f"Parsed houses: {len(houses)}")
    print(f"JSON: {args.json}")
    print(f"CSV: {args.csv}")


if __name__ == "__main__":
    main()
