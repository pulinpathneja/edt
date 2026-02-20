"""
Unit tests for web_poi_crawler and auto_crawl_converter.

Pure unit tests — no network calls, no database.
"""
import pytest
from unittest.mock import patch

from app.services.data_ingestion.web_poi_crawler import (
    ExtractedPOI,
    POIEntityExtractor,
    _dedup_pois,
    _extract_rating,
    _extract_review_count,
    _normalize_name,
)
from app.services.data_ingestion.auto_crawl_converter import (
    convert_extracted_pois,
)


# ---------------------------------------------------------------------------
# POIEntityExtractor tests
# ---------------------------------------------------------------------------

class TestPOIEntityExtractor:

    def setup_method(self):
        self.extractor = POIEntityExtractor()

    def test_numbered_list_extraction(self):
        text = """
1. Colosseum - The iconic amphitheater of ancient Rome, a must-visit for history buffs and architecture lovers alike.
2. Trevi Fountain - A stunning baroque masterpiece where visitors traditionally toss coins to ensure a return to the eternal city.
3. Pantheon - One of the best preserved ancient Roman buildings, featuring a remarkable concrete dome with an oculus.
"""
        pois = self.extractor.extract_pois_from_text(text)
        names = [p.name for p in pois]
        assert "Colosseum" in names
        assert "Trevi Fountain" in names
        assert "Pantheon" in names

    def test_bold_entry_extraction(self):
        text = """
**Trattoria da Mario** - A beloved local spot serving traditional Florentine cuisine since 1953, known for their ribollita.
**Mercato Centrale** - The vibrant central market packed with food stalls offering fresh pasta, wine, and street food.
"""
        pois = self.extractor.extract_pois_from_text(text)
        names = [p.name for p in pois]
        assert "Trattoria da Mario" in names
        assert "Mercato Centrale" in names

    def test_heading_extraction(self):
        text = """## Uffizi Gallery
Home to masterpieces by Botticelli, Leonardo, and Michelangelo. One of the most important art museums in the world.

## Ponte Vecchio
The famous medieval bridge lined with jewelry shops spanning the Arno River.
"""
        pois = self.extractor.extract_pois_from_text(text)
        names = [p.name for p in pois]
        assert "Uffizi Gallery" in names
        assert "Ponte Vecchio" in names

    def test_category_guessing_restaurant(self):
        cat = self.extractor._guess_category(
            "Trattoria da Mario",
            "A beloved local trattoria serving traditional cuisine"
        )
        assert cat == "restaurant"

    def test_category_guessing_attraction(self):
        cat = self.extractor._guess_category(
            "British Museum",
            "A world-famous museum with free entry in London"
        )
        assert cat == "attraction"

    def test_category_guessing_shopping(self):
        cat = self.extractor._guess_category(
            "Grand Bazaar",
            "Historic covered market and bazaar with thousands of shops"
        )
        assert cat == "shopping"

    def test_category_guessing_cafe(self):
        cat = self.extractor._guess_category(
            "Cafe Florian",
            "A historic coffee house on St Marks Square"
        )
        assert cat == "cafe"

    def test_category_guessing_default(self):
        cat = self.extractor._guess_category(
            "Mysterious Place",
            "An interesting location to visit"
        )
        assert cat == "attraction"

    def test_dedup_within_text(self):
        text = """
1. Colosseum - The iconic amphitheater of ancient Rome and a marvel of engineering.
2. Trevi Fountain - Stunning baroque fountain in the heart of the city center.
3. Colosseum - The great Roman amphitheater, a UNESCO World Heritage site and symbol of Rome.
"""
        pois = self.extractor.extract_pois_from_text(text)
        names = [p.name for p in pois]
        assert names.count("Colosseum") == 1

    def test_empty_input(self):
        assert self.extractor.extract_pois_from_text("") == []
        assert self.extractor.extract_pois_from_text("   ") == []
        assert self.extractor.extract_pois_from_text("short") == []

    def test_snippet_extraction(self):
        pois = self.extractor.extract_pois_from_snippet(
            title="Colosseum - Rome, Italy - Tripadvisor",
            snippet="4.5 of 5 based on 12,345 reviews. The iconic amphitheater.",
            source_url="https://tripadvisor.com/Attraction-g123",
            source_domain="tripadvisor.com",
        )
        assert len(pois) == 1
        assert pois[0].name == "Colosseum"
        assert pois[0].rating == 4.5
        assert pois[0].review_count == 12345

    def test_snippet_skips_aggregate_pages(self):
        pois = self.extractor.extract_pois_from_snippet(
            title="THE 10 BEST Things to Do in Rome - Tripadvisor",
            snippet="some snippet",
        )
        assert len(pois) == 0

    def test_snippet_skips_empty_title(self):
        pois = self.extractor.extract_pois_from_snippet(title="", snippet="some text")
        assert len(pois) == 0

    def test_numbered_list_with_parenthesized_numbers(self):
        text = """
1) Vatican Museums - Home to one of the world's most extensive art collections including the Sistine Chapel.
2) St Peters Basilica - The largest church in the world with stunning Renaissance architecture.
"""
        pois = self.extractor.extract_pois_from_text(text)
        names = [p.name for p in pois]
        assert "Vatican Museums" in names
        assert "St Peters Basilica" in names


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------

class TestHelperFunctions:

    def test_normalize_name(self):
        assert _normalize_name("Colosseum") == "colosseum"
        assert _normalize_name("Trevi Fountain!") == "trevifountain"
        assert _normalize_name("St. Peter's Basilica") == "stpetersbasilica"

    def test_extract_rating_of_5(self):
        assert _extract_rating("4.5 of 5") == 4.5

    def test_extract_rating_slash(self):
        assert _extract_rating("rating: 4.0/5") == 4.0

    def test_extract_rating_none(self):
        assert _extract_rating("no rating here") is None

    def test_extract_review_count(self):
        assert _extract_review_count("12,345 reviews") == 12345

    def test_extract_review_count_none(self):
        assert _extract_review_count("no reviews here") is None

    def test_dedup_pois(self):
        pois = [
            ExtractedPOI(name="Colosseum", description="Ancient", category="attraction"),
            ExtractedPOI(name="Trevi Fountain", description="Baroque", category="attraction"),
            ExtractedPOI(name="Colosseum", description="Different desc", category="attraction"),
        ]
        result = _dedup_pois(pois)
        assert len(result) == 2
        names = [p.name for p in result]
        assert "Colosseum" in names
        assert "Trevi Fountain" in names


# ---------------------------------------------------------------------------
# AutoCrawlConverter tests
# ---------------------------------------------------------------------------

class TestAutoCrawlConverter:

    def test_basic_conversion(self):
        pois = [
            ExtractedPOI(
                name="Colosseum",
                description="The iconic Roman amphitheater",
                category="attraction",
                source_url="https://example.com",
                source_domain="example.com",
            ),
            ExtractedPOI(
                name="Trattoria da Mario",
                description="Traditional Florentine trattoria",
                category="restaurant",
                source_url="https://example.com",
                source_domain="example.com",
            ),
        ]
        result = convert_extracted_pois(pois, "rome")
        assert len(result) == 2
        assert result[0]["name"] == "Colosseum"
        assert result[0]["category"] == "attraction"
        assert result[0]["city"] == "Rome"
        assert "persona_scores" in result[0]
        assert result[0]["source"].startswith("auto_crawl_")

    def test_rating_boost(self):
        pois = [
            ExtractedPOI(
                name="Amazing Place",
                description="A highly rated spot",
                category="attraction",
                rating=4.8,
            ),
        ]
        result_boosted = convert_extracted_pois(pois, "rome")

        pois_no_rating = [
            ExtractedPOI(
                name="Normal Place",
                description="A regular spot with similar text",
                category="attraction",
                rating=3.0,
            ),
        ]
        result_normal = convert_extracted_pois(pois_no_rating, "rome")

        # The boosted one should have higher scores
        boosted_cultural = result_boosted[0]["persona_scores"]["score_cultural"]
        normal_cultural = result_normal[0]["persona_scores"]["score_cultural"]
        assert boosted_cultural > normal_cultural

    def test_review_count_must_see(self):
        pois = [
            ExtractedPOI(
                name="Popular Place",
                description="Very popular spot",
                category="attraction",
                review_count=5000,
            ),
        ]
        result = convert_extracted_pois(pois, "rome")
        assert result[0]["attributes"].get("is_must_see") is True

    def test_review_count_not_must_see(self):
        pois = [
            ExtractedPOI(
                name="Less Popular",
                description="A decent spot",
                category="attraction",
                review_count=50,
            ),
        ]
        result = convert_extracted_pois(pois, "rome")
        assert result[0]["attributes"].get("is_must_see") is not True

    def test_source_boosts(self):
        pois_eater = [
            ExtractedPOI(
                name="Best Pizza",
                description="Amazing pizza restaurant",
                category="restaurant",
                source_domain="eater.com",
            ),
        ]
        pois_generic = [
            ExtractedPOI(
                name="Good Pizza",
                description="Good pizza restaurant nearby",
                category="restaurant",
                source_domain="randomsite.com",
            ),
        ]
        result_eater = convert_extracted_pois(pois_eater, "rome")
        result_generic = convert_extracted_pois(pois_generic, "rome")

        # Eater.com should boost foodie score
        eater_foodie = result_eater[0]["persona_scores"]["score_foodie"]
        generic_foodie = result_generic[0]["persona_scores"]["score_foodie"]
        assert eater_foodie > generic_foodie

    def test_dedup_in_converter(self):
        pois = [
            ExtractedPOI(name="Colosseum", description="Ancient", category="attraction"),
            ExtractedPOI(name="Colosseum", description="Different", category="attraction"),
            ExtractedPOI(name="Pantheon", description="Temple", category="attraction"),
        ]
        result = convert_extracted_pois(pois, "rome")
        assert len(result) == 2

    def test_url_crawl_source_tag(self):
        pois = [
            ExtractedPOI(
                name="Test Place",
                description="A test location",
                category="attraction",
                source_domain="timeout.com",
            ),
        ]
        result = convert_extracted_pois(pois, "rome", source_tag_prefix="url_crawl")
        assert result[0]["source"].startswith("url_crawl_")

    def test_empty_input(self):
        result = convert_extracted_pois([], "rome")
        assert result == []

    def test_skips_empty_names(self):
        pois = [
            ExtractedPOI(name="", description="No name", category="attraction"),
            ExtractedPOI(name="   ", description="Whitespace", category="attraction"),
        ]
        result = convert_extracted_pois(pois, "rome")
        assert len(result) == 0
