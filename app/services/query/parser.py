"""
Rule-based natural language query parser for travel POI search.

Decomposes queries like "romantic restaurant in rome" into structured
intent (city, category, vibes, attributes) + semantic residual for
vector embedding.
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from app.core.config import (
    GROUP_TYPES,
    POI_CATEGORIES,
    TIME_OF_DAY,
    VIBE_CATEGORIES,
)
from app.core.country_config import CITY_BBOXES, COUNTRY_DATABASE


@dataclass
class ParsedQuery:
    """Structured intent extracted from a natural language query."""

    raw_query: str
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    neighborhood: Optional[str] = None
    vibes: List[str] = field(default_factory=list)
    group_type: Optional[str] = None
    attributes: List[str] = field(default_factory=list)
    near_poi_name: Optional[str] = None
    cost_level: Optional[int] = None
    time_of_day: Optional[str] = None
    semantic_query: str = ""
    confidence: float = 0.0


# ---------- Synonym dictionaries ----------

CATEGORY_SYNONYMS: Dict[str, List[str]] = {
    "restaurant": [
        "restaurant", "restaurants", "eat", "eating", "food", "dine",
        "dining", "lunch", "dinner", "brunch", "eatery", "eateries",
        "trattoria", "trattorias", "bistro", "pizzeria",
    ],
    "attraction": [
        "attraction", "attractions", "sight", "sights", "sightseeing",
        "landmark", "landmarks", "monument", "monuments", "temple",
        "temples", "cathedral", "cathedrals", "basilica", "palace",
        "palaces", "castle", "castles", "ruin", "ruins", "church",
        "churches", "tower", "towers",
    ],
    "activity": [
        "activity", "activities", "things to do", "experience",
        "experiences", "tour", "tours", "class", "classes",
        "workshop", "workshops", "excursion", "walk", "walking tour",
    ],
    "shopping": [
        "shopping", "shop", "shops", "store", "stores", "market",
        "markets", "boutique", "boutiques", "mall",
    ],
    "nightlife": [
        "nightlife", "club", "clubs", "nightclub", "nightclubs",
        "lounge", "lounges", "disco",
    ],
}

SUBCATEGORY_SYNONYMS: Dict[str, List[str]] = {
    "museum": ["museum", "museums", "gallery", "galleries", "exhibit", "exhibition"],
    "cafe": ["cafe", "cafes", "coffee", "coffee shop", "coffeehouse"],
    "bar": ["bar", "bars", "pub", "pubs", "tavern", "wine bar", "cocktail bar"],
    "park": ["park", "parks"],
    "garden": ["garden", "gardens", "botanical"],
    "beach": ["beach", "beaches", "seaside", "shore", "coast", "coastal"],
    "church": ["church", "churches", "chapel", "basilica", "cathedral", "cathedrals"],
    "fine_dining": ["fine dining", "michelin", "gourmet", "upscale dining"],
    "street_food": ["street food", "street vendor", "food stall", "food cart"],
    "spa": ["spa", "spas", "thermal bath", "thermal baths", "onsen", "hammam"],
    "hiking": ["hiking", "hike", "hikes", "trek", "trekking", "trail", "trails"],
    "viewpoint": ["viewpoint", "viewpoints", "lookout", "overlook", "panoramic", "scenic view"],
}

VIBE_SYNONYMS: Dict[str, List[str]] = {
    "romantic": [
        "romantic", "romance", "love", "intimate", "couples", "date",
        "date night", "honeymoon", "candlelit",
    ],
    "cultural": [
        "cultural", "culture", "heritage", "historical", "history",
        "art", "artistic", "traditional", "ancient",
    ],
    "foodie": [
        "foodie", "culinary", "gastronomic", "gourmet", "cuisine",
        "tasting", "food lover",
    ],
    "adventure": [
        "adventure", "adventurous", "thrill", "thrilling", "exciting",
        "extreme", "adrenaline",
    ],
    "relaxation": [
        "relaxation", "relax", "relaxing", "chill", "calm", "peaceful",
        "quiet", "tranquil", "serene", "laid-back",
    ],
    "nature": [
        "nature", "natural", "outdoors", "outdoor", "scenic", "green",
        "wilderness", "wildlife",
    ],
    "nightlife": [
        "nightlife", "party", "partying", "clubbing", "drinks",
        "cocktails", "night out", "lively",
    ],
    "photography": [
        "photography", "photo", "photos", "photogenic", "instagram",
        "instagrammable", "scenic views", "picture", "picturesque",
    ],
    "wellness": [
        "wellness", "health", "yoga", "meditation", "thermal",
        "rejuvenation", "mindfulness",
    ],
    "shopping": [
        "shopping", "boutiques", "fashion", "vintage", "antiques",
        "souvenirs",
    ],
}

GROUP_TYPE_SYNONYMS: Dict[str, List[str]] = {
    "family": ["family", "families", "family-friendly"],
    "kids": ["kids", "children", "child", "toddler", "toddlers"],
    "couple": ["couple", "couples", "two of us", "partner"],
    "honeymoon": ["honeymoon", "honeymooners", "newlywed", "newlyweds"],
    "solo": ["solo", "alone", "by myself", "solo traveler"],
    "friends": ["friends", "friend group", "buddies", "group trip", "mates"],
    "seniors": ["seniors", "senior", "elderly", "retired", "retirees", "older adults"],
    "business": ["business", "corporate", "work trip", "conference"],
}

ATTRIBUTE_KEYWORDS: Dict[str, List[str]] = {
    "is_hidden_gem": [
        "hidden gem", "hidden gems", "off the beaten path", "secret",
        "local secret", "underrated", "lesser known", "lesser-known",
        "off-beat", "offbeat", "undiscovered",
    ],
    "is_must_see": [
        "must see", "must-see", "must visit", "must-visit", "iconic",
        "famous", "top rated", "top-rated", "best", "essential",
        "cannot miss", "can't miss", "don't miss", "bucket list",
    ],
    "is_kid_friendly": [
        "kid friendly", "kid-friendly", "child friendly", "child-friendly",
        "family friendly", "family-friendly", "for kids", "for children",
        "with kids", "with children",
    ],
    "instagram_worthy": [
        "instagram", "instagrammable", "photogenic", "photo spot",
        "photo spots", "photo worthy", "photo-worthy",
    ],
}

COST_KEYWORDS: Dict[int, List[str]] = {
    1: ["cheap", "budget", "free", "inexpensive", "affordable", "low cost", "low-cost", "backpacker"],
    2: ["moderate", "mid-range", "mid range", "reasonable", "value"],
    4: ["upscale", "fancy", "high-end", "high end", "premium", "splurge"],
    5: ["luxury", "luxurious", "expensive", "fine dining", "michelin", "exclusive", "5-star", "five star"],
}

TIME_KEYWORDS: Dict[str, List[str]] = {
    "morning": ["morning", "breakfast", "brunch", "early", "sunrise", "dawn"],
    "afternoon": ["afternoon", "lunch", "midday", "daytime"],
    "evening": ["evening", "dinner", "sunset", "dusk", "golden hour"],
    "night": ["night", "nighttime", "late night", "after dark", "midnight"],
}

# Prepositions that signal a city reference
_CITY_PREPOSITIONS = {"in", "at", "of", "around", "near", "from", "visit", "visiting"}

# Pattern for spatial modifier extraction
_SPATIAL_PATTERN = re.compile(
    r"\b(?:near|close to|next to|around|by|beside|nearby|walking distance from|walking distance to)\s+(.+)",
    re.IGNORECASE,
)


def _build_city_lookup() -> Dict[str, Tuple[str, str]]:
    """Build a normalized city name → (display_name, country) lookup."""
    lookup: Dict[str, Tuple[str, str]] = {}

    # From CITY_BBOXES
    for key, bbox in CITY_BBOXES.items():
        display = key.replace("_", " ").title()
        country = bbox.get("country", "")
        lookup[key] = (display, country)
        # Also add the display name lowercased
        lookup[display.lower()] = (display, country)

    # From COUNTRY_DATABASE cities
    for country_key, country_data in COUNTRY_DATABASE.items():
        country_name = country_data.get("name", country_key.title())
        for city_key, city_data in country_data.get("cities", {}).items():
            display = city_data.get("name", city_key.replace("_", " ").title())
            lookup[city_key] = (display, country_name)
            lookup[display.lower()] = (display, country_name)

    return lookup


def _build_reverse_lookup(synonyms: Dict[str, List[str]]) -> Dict[str, str]:
    """Build a reverse lookup: synonym → canonical key."""
    reverse: Dict[str, str] = {}
    for canonical, syns in synonyms.items():
        for syn in syns:
            reverse[syn.lower()] = canonical
    return reverse


class QueryParser:
    """Rule-based parser that decomposes natural language into structured query intent."""

    def __init__(self):
        self._city_lookup = _build_city_lookup()
        self._category_rev = _build_reverse_lookup(CATEGORY_SYNONYMS)
        self._subcategory_rev = _build_reverse_lookup(SUBCATEGORY_SYNONYMS)
        self._vibe_rev = _build_reverse_lookup(VIBE_SYNONYMS)
        self._group_rev = _build_reverse_lookup(GROUP_TYPE_SYNONYMS)

        # Build sorted phrase lists (longest first) for multi-word matching
        self._attribute_phrases = self._sorted_phrases(ATTRIBUTE_KEYWORDS)
        self._cost_phrases = self._sorted_phrases(COST_KEYWORDS)
        self._time_phrases = self._sorted_phrases(TIME_KEYWORDS)
        self._category_phrases = self._sorted_phrases(CATEGORY_SYNONYMS)
        self._subcategory_phrases = self._sorted_phrases(SUBCATEGORY_SYNONYMS)
        self._vibe_phrases = self._sorted_phrases(VIBE_SYNONYMS)
        self._group_phrases = self._sorted_phrases(GROUP_TYPE_SYNONYMS)

    @staticmethod
    def _sorted_phrases(mapping: Dict) -> List[Tuple[str, str]]:
        """Return (phrase, canonical_key) pairs sorted longest-first for greedy matching."""
        pairs = []
        for key, phrases in mapping.items():
            for phrase in phrases:
                pairs.append((phrase.lower(), str(key)))
        pairs.sort(key=lambda p: len(p[0]), reverse=True)
        return pairs

    def parse(self, raw_query: str) -> ParsedQuery:
        """Parse a natural language query into structured components."""
        result = ParsedQuery(raw_query=raw_query)
        normalized = raw_query.lower().strip()

        # Track consumed spans to avoid double-extraction
        consumed: Set[Tuple[int, int]] = set()

        # 1. Extract spatial modifier first ("near colosseum" etc.)
        result.near_poi_name, consumed = self._extract_spatial(normalized, consumed)

        # 2. Extract city (requires preposition context for ambiguous names)
        result.city, result.country, consumed = self._extract_city(normalized, consumed)

        # 3. Extract attributes (multi-word phrases, longest-first)
        result.attributes, consumed = self._extract_from_phrases(
            normalized, consumed, self._attribute_phrases
        )

        # 4. Extract cost level
        cost_matches, consumed = self._extract_from_phrases(
            normalized, consumed, self._cost_phrases
        )
        if cost_matches:
            result.cost_level = int(cost_matches[0])

        # 5. Extract time of day
        time_matches, consumed = self._extract_from_phrases(
            normalized, consumed, self._time_phrases
        )
        if time_matches:
            result.time_of_day = time_matches[0]

        # 6. Extract subcategory before category (more specific first)
        subcat_matches, consumed = self._extract_from_phrases(
            normalized, consumed, self._subcategory_phrases
        )
        if subcat_matches:
            result.subcategory = subcat_matches[0]

        # 7. Extract category
        cat_matches, consumed = self._extract_from_phrases(
            normalized, consumed, self._category_phrases
        )
        if cat_matches:
            result.category = cat_matches[0]

        # If subcategory found but no category, infer category
        if result.subcategory and not result.category:
            result.category = self._infer_category_from_subcategory(result.subcategory)

        # 8. Extract vibes
        vibe_matches, consumed = self._extract_from_phrases(
            normalized, consumed, self._vibe_phrases
        )
        result.vibes = list(dict.fromkeys(vibe_matches))  # dedupe preserving order

        # 9. Extract group type
        group_matches, consumed = self._extract_from_phrases(
            normalized, consumed, self._group_phrases
        )
        if group_matches:
            result.group_type = group_matches[0]

        # 10. Build semantic query from unconsumed tokens
        result.semantic_query = self._build_semantic_query(normalized, consumed)

        # 11. Calculate confidence
        result.confidence = self._calculate_confidence(result)

        return result

    def _extract_spatial(
        self, text: str, consumed: Set[Tuple[int, int]]
    ) -> Tuple[Optional[str], Set[Tuple[int, int]]]:
        """Extract 'near X' spatial modifier."""
        match = _SPATIAL_PATTERN.search(text)
        if not match:
            return None, consumed

        poi_ref = match.group(1).strip()
        # Clean up: remove trailing prepositions and common words
        poi_ref = re.sub(r"\s+(in|at|of|for|with)\s+.*$", "", poi_ref)
        # Remove trailing punctuation
        poi_ref = poi_ref.rstrip(".,;!?")

        if poi_ref:
            span = (match.start(), match.end())
            consumed = consumed | {span}
            return poi_ref, consumed

        return None, consumed

    def _extract_city(
        self, text: str, consumed: Set[Tuple[int, int]]
    ) -> Tuple[Optional[str], Optional[str], Set[Tuple[int, int]]]:
        """Extract city name, handling ambiguity (e.g., 'nice' as city vs adjective)."""
        words = text.split()

        # Strategy 1: look for "in/at/of <city>" patterns (highest confidence)
        for prep in _CITY_PREPOSITIONS:
            pattern = re.compile(rf"\b{re.escape(prep)}\s+(\w[\w\s]*)", re.IGNORECASE)
            for match in pattern.finditer(text):
                candidate = match.group(1).strip()
                # Try progressively shorter substrings
                candidate_words = candidate.split()
                for length in range(len(candidate_words), 0, -1):
                    attempt = " ".join(candidate_words[:length]).lower()
                    if attempt in self._city_lookup:
                        display, country = self._city_lookup[attempt]
                        span = (match.start(), match.start() + len(prep) + 1 + len(attempt))
                        consumed = consumed | {span}
                        return display, country, consumed

        # Strategy 2: check if any word matches a known city (but not for ambiguous short words)
        ambiguous_cities = {"nice", "bath", "split", "lima"}
        for i, word in enumerate(words):
            if self._is_consumed(text, word, i, consumed):
                continue
            w = word.lower().rstrip(".,;!?")
            if w in self._city_lookup and w not in ambiguous_cities:
                display, country = self._city_lookup[w]
                start = text.index(word)
                consumed = consumed | {(start, start + len(word))}
                return display, country, consumed

        return None, None, consumed

    def _extract_from_phrases(
        self,
        text: str,
        consumed: Set[Tuple[int, int]],
        phrases: List[Tuple[str, str]],
    ) -> Tuple[List[str], Set[Tuple[int, int]]]:
        """Extract all matching phrases from text, longest-first greedy."""
        matches: List[str] = []
        for phrase, canonical in phrases:
            idx = text.find(phrase)
            if idx == -1:
                continue
            span = (idx, idx + len(phrase))
            if self._overlaps(span, consumed):
                continue
            matches.append(canonical)
            consumed = consumed | {span}
        return matches, consumed

    def _build_semantic_query(self, text: str, consumed: Set[Tuple[int, int]]) -> str:
        """Build the semantic query from unconsumed portions of text."""
        # Mark consumed character positions
        consumed_chars = set()
        for start, end in consumed:
            for i in range(start, min(end, len(text))):
                consumed_chars.add(i)

        # Collect unconsumed characters
        parts = []
        current = []
        for i, ch in enumerate(text):
            if i in consumed_chars:
                if current:
                    parts.append("".join(current))
                    current = []
            else:
                current.append(ch)
        if current:
            parts.append("".join(current))

        # Clean up
        result = " ".join(parts)
        # Remove leftover prepositions and articles
        result = re.sub(r"\b(in|at|of|the|a|an|for|with|and|or)\b", " ", result)
        # Collapse whitespace
        result = re.sub(r"\s+", " ", result).strip()

        return result

    def _calculate_confidence(self, result: ParsedQuery) -> float:
        """Calculate a 0-1 confidence score based on how much structure was extracted."""
        score = 0.0
        if result.city:
            score += 0.25
        if result.category:
            score += 0.20
        if result.vibes:
            score += 0.15
        if result.subcategory:
            score += 0.10
        if result.group_type:
            score += 0.10
        if result.attributes:
            score += 0.10
        if result.cost_level:
            score += 0.05
        if result.time_of_day:
            score += 0.05
        return min(score, 1.0)

    @staticmethod
    def _infer_category_from_subcategory(subcategory: str) -> Optional[str]:
        """Infer the parent category from a subcategory."""
        mapping = {
            "museum": "attraction",
            "cafe": "restaurant",
            "bar": "restaurant",
            "park": "attraction",
            "garden": "attraction",
            "beach": "attraction",
            "church": "attraction",
            "fine_dining": "restaurant",
            "street_food": "restaurant",
            "spa": "activity",
            "hiking": "activity",
            "viewpoint": "attraction",
        }
        return mapping.get(subcategory)

    @staticmethod
    def _overlaps(span: Tuple[int, int], consumed: Set[Tuple[int, int]]) -> bool:
        """Check if a span overlaps with any consumed span."""
        for cs, ce in consumed:
            if span[0] < ce and span[1] > cs:
                return True
        return False

    @staticmethod
    def _is_consumed(text: str, word: str, word_index: int, consumed: Set[Tuple[int, int]]) -> bool:
        """Check if a word at a given index falls within a consumed span."""
        try:
            pos = 0
            for i in range(word_index):
                pos = text.index(text.split()[i], pos) + len(text.split()[i])
            start = text.index(word, pos if word_index > 0 else 0)
        except ValueError:
            return False

        for cs, ce in consumed:
            if cs <= start < ce:
                return True
        return False
