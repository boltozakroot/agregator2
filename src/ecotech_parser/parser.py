from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://ecotechstroy.ru"
CARDS_ENDPOINT = f"{BASE_URL}/apiback/cards"


@dataclass(slots=True)
class House:
    name: str
    area_m2: float
    material: str
    price_rub: int
    floors: int
    card_url: str


class EcotechParser:
    """Parses house data from ecotechstroy.ru backend endpoint."""

    _CATEGORY_RULES: tuple[tuple[str, tuple[str, str]], ...] = (
        ("hasBathhouse", ("bani", "баня")),
        ("isTimberHouse", ("kleeny-brus", "клеёный брус")),
        ("isFrameHouses", ("karkasny", "каркасный дом")),
        ("isRoundedLogs", ("ocilindrovannoe-brevno", "оцилиндрованное бревно")),
        ("isHandCutHouses", ("ruchnaya-rubka", "ручная рубка")),
    )

    def __init__(self, retries: int = 3, retry_delay_s: float = 1.0, timeout_s: int = 30):
        self.retries = retries
        self.retry_delay_s = retry_delay_s
        self.timeout_s = timeout_s

    def fetch_raw_cards(self) -> list[dict[str, Any]]:
        last_error: Exception | None = None
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; EcotechParser/1.0; +https://ecotechstroy.ru)",
            "Accept": "application/json,text/plain,*/*",
        }

        for attempt in range(1, self.retries + 1):
            try:
                request = Request(CARDS_ENDPOINT, headers=headers)
                with urlopen(request, timeout=self.timeout_s) as response:
                    payload = response.read().decode("utf-8")
                data = json.loads(payload)
                if not isinstance(data, list):
                    raise ValueError("Unexpected response format: cards payload is not a list")
                return data
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.retry_delay_s * attempt)

        raise RuntimeError(f"Unable to fetch cards from {CARDS_ENDPOINT}") from last_error

    @classmethod
    def _resolve_category(cls, options: dict[str, Any]) -> tuple[str, str]:
        for option_key, (slug, material) in cls._CATEGORY_RULES:
            if bool(options.get(option_key)):
                return slug, material
        return "catalog", "не указан"

    def map_card(self, card: dict[str, Any]) -> House | None:
        if not card.get("isVisible", True):
            return None

        options = card.get("options") or {}
        slug, material = self._resolve_category(options)
        card_id = str(card.get("id", "")).strip()
        if not card_id:
            return None

        price = int(card.get("price") or 0)
        floors = int(card.get("floors") or 0)
        area = float(card.get("area") or 0)
        name = str(card.get("title") or "").strip()

        if not name:
            return None

        return House(
            name=name,
            area_m2=area,
            material=material,
            price_rub=price,
            floors=floors,
            card_url=f"{BASE_URL}/catalog/{slug}/{card_id}",
        )

    def parse(self) -> list[House]:
        raw_cards = self.fetch_raw_cards()
        houses: list[House] = []
        seen_urls: set[str] = set()

        for raw in raw_cards:
            house = self.map_card(raw)
            if house is None:
                continue
            if house.card_url in seen_urls:
                continue
            seen_urls.add(house.card_url)
            houses.append(house)

        return houses

    @staticmethod
    def export_json(houses: list[House], output_file: Path) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        result = {
            "source": "ecotechstroy.ru",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
            "houses": [asdict(item) for item in houses],
        }
        output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def export_csv(houses: list[House], output_file: Path) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = ["name", "area_m2", "material", "price_rub", "floors", "card_url"]

        with output_file.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            for house in houses:
                writer.writerow(asdict(house))
