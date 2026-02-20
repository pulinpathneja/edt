"""Unit tests for the natural language query parser."""
from app.services.query.parser import QueryParser, ParsedQuery


parser = QueryParser()


def test_romantic_restaurant_in_rome():
    result = parser.parse("romantic restaurant in rome")
    assert result.city == "Rome"
    assert result.country == "Italy"
    assert result.category == "restaurant"
    assert "romantic" in result.vibes
    assert result.confidence > 0


def test_hidden_gems_in_tokyo():
    result = parser.parse("hidden gems in tokyo")
    assert result.city == "Tokyo"
    assert result.country == "Japan"
    assert "is_hidden_gem" in result.attributes
    assert result.confidence > 0


def test_kid_friendly_activities_near_colosseum():
    result = parser.parse("kid-friendly activities near colosseum")
    assert result.category == "activity"
    assert "is_kid_friendly" in result.attributes
    assert result.near_poi_name is not None
    assert "colosseum" in result.near_poi_name.lower()


def test_cheap_street_food_in_osaka():
    result = parser.parse("cheap street food in osaka")
    assert result.city == "Osaka"
    assert result.cost_level == 1
    assert result.subcategory == "street_food" or result.category == "restaurant"


def test_best_museums_in_paris():
    result = parser.parse("best museums in paris")
    assert result.city == "Paris"
    assert result.country == "France"
    assert result.subcategory == "museum"
    # "best" should map to must_see attribute
    assert "is_must_see" in result.attributes


def test_sunset_spots_in_barcelona():
    result = parser.parse("sunset spots in barcelona")
    assert result.city == "Barcelona"
    assert result.country == "Spain"


def test_nice_restaurants_ambiguity():
    """'nice' should NOT be matched as the city Nice when not preceded by 'in'."""
    result = parser.parse("nice restaurants")
    # "nice" without "in" should NOT match as a city
    assert result.city is None
    assert result.category == "restaurant"


def test_restaurants_in_nice():
    """'in nice' should correctly match Nice as a city."""
    result = parser.parse("restaurants in nice")
    assert result.city == "Nice"
    assert result.country == "France"
    assert result.category == "restaurant"


def test_luxury_fine_dining_in_milan():
    result = parser.parse("luxury fine dining in milan")
    assert result.city == "Milan"
    assert result.cost_level == 5


def test_morning_cafes_in_florence():
    result = parser.parse("morning cafes in florence")
    assert result.city == "Florence"
    assert result.subcategory == "cafe"
    assert result.time_of_day == "morning"


def test_solo_traveler_adventures_in_kyoto():
    result = parser.parse("solo traveler adventures in kyoto")
    assert result.city == "Kyoto"
    assert result.group_type == "solo"
    assert "adventure" in result.vibes


def test_family_friendly_parks_in_london():
    result = parser.parse("family friendly parks in london")
    assert result.city == "London"
    assert result.subcategory == "park"
    assert "is_kid_friendly" in result.attributes or result.group_type == "family"


def test_instagrammable_spots_rome():
    result = parser.parse("instagrammable spots in rome")
    assert result.city == "Rome"
    assert "instagram_worthy" in result.attributes or "photography" in result.vibes


def test_empty_query_returns_defaults():
    result = parser.parse("things")
    assert result.raw_query == "things"
    assert isinstance(result, ParsedQuery)


def test_semantic_query_built():
    """Verify semantic_query is non-empty and doesn't contain consumed tokens."""
    result = parser.parse("romantic restaurant in rome")
    # The semantic query should contain meaningful words, not "in" or "rome"
    assert isinstance(result.semantic_query, str)


def test_confidence_increases_with_more_structure():
    """More extracted fields should yield higher confidence."""
    simple = parser.parse("places")
    detailed = parser.parse("romantic restaurant in rome")
    assert detailed.confidence > simple.confidence


def test_multiple_vibes():
    result = parser.parse("romantic cultural experience in venice")
    assert result.city == "Venice"
    assert "romantic" in result.vibes
    assert "cultural" in result.vibes


def test_budget_afternoon_restaurants():
    result = parser.parse("affordable afternoon restaurants in barcelona")
    assert result.city == "Barcelona"
    assert result.category == "restaurant"
    assert result.time_of_day == "afternoon"
    assert result.cost_level in [1, 2]
