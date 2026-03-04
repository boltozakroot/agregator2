import unittest

from src.ecotech_parser.parser import EcotechParser


class ParserTests(unittest.TestCase):
    def test_map_card_timber_house(self):
        parser = EcotechParser()
        house = parser.map_card(
            {
                "id": "abc",
                "title": "Дом Тест",
                "area": 100,
                "price": 9000000,
                "floors": 2,
                "isVisible": True,
                "options": {"isTimberHouse": True},
            }
        )

        self.assertIsNotNone(house)
        assert house is not None
        self.assertEqual(house.material, "клеёный брус")
        self.assertTrue(house.card_url.endswith("/catalog/kleeny-brus/abc"))

    def test_map_card_filters_hidden(self):
        parser = EcotechParser()
        house = parser.map_card(
            {
                "id": "abc",
                "title": "Дом Тест",
                "isVisible": False,
                "options": {"isTimberHouse": True},
            }
        )
        self.assertIsNone(house)

    def test_map_card_default_material(self):
        parser = EcotechParser()
        house = parser.map_card(
            {
                "id": "abc",
                "title": "Дом Тест",
                "area": 50,
                "price": 1,
                "floors": 1,
                "options": {},
            }
        )
        self.assertIsNotNone(house)
        assert house is not None
        self.assertEqual(house.material, "не указан")
        self.assertTrue(house.card_url.endswith("/catalog/catalog/abc"))


if __name__ == "__main__":
    unittest.main()
