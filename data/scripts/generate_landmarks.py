"""
Script to pre-generate famous landmark files for all cities.
This enables scalable itinerary generation across 100+ cities.

Usage:
    python -m data.scripts.generate_landmarks                    # All cities
    python -m data.scripts.generate_landmarks paris             # Single city
    python -m data.scripts.generate_landmarks --method wikidata  # Use Wikidata
    python -m data.scripts.generate_landmarks --method llm       # Use Gemini LLM
"""

import json
import os
import sys
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional


# City database with coordinates for queries
CITY_DATABASE = {
    "paris": {"name": "Paris", "country": "France"},
    "rome": {"name": "Rome", "country": "Italy"},
    "barcelona": {"name": "Barcelona", "country": "Spain"},
    "tokyo": {"name": "Tokyo", "country": "Japan"},
    "london": {"name": "London", "country": "United Kingdom"},
    "new_york": {"name": "New York City", "country": "United States"},
    "amsterdam": {"name": "Amsterdam", "country": "Netherlands"},
    "prague": {"name": "Prague", "country": "Czech Republic"},
    "vienna": {"name": "Vienna", "country": "Austria"},
    "berlin": {"name": "Berlin", "country": "Germany"},
    "lisbon": {"name": "Lisbon", "country": "Portugal"},
    "florence": {"name": "Florence", "country": "Italy"},
    "venice": {"name": "Venice", "country": "Italy"},
    "madrid": {"name": "Madrid", "country": "Spain"},
    "athens": {"name": "Athens", "country": "Greece"},
    "istanbul": {"name": "Istanbul", "country": "Turkey"},
    "dubai": {"name": "Dubai", "country": "UAE"},
    "singapore": {"name": "Singapore", "country": "Singapore"},
    "bangkok": {"name": "Bangkok", "country": "Thailand"},
    "sydney": {"name": "Sydney", "country": "Australia"},
}


def fetch_landmarks_from_wikidata(city_name: str, country: str, limit: int = 20) -> List[Dict]:
    """
    Fetch famous landmarks from Wikidata SPARQL endpoint.
    Free and covers most major cities worldwide.
    """

    # SPARQL query for tourist attractions in a city
    query = f"""
    SELECT DISTINCT ?place ?placeLabel ?placeDescription
           (SAMPLE(?coord) AS ?coordinate)
           (SAMPLE(?image) AS ?img)
    WHERE {{
      # Tourist attractions, landmarks, monuments, museums
      VALUES ?type {{ wd:Q570116 wd:Q839954 wd:Q4989906 wd:Q33506 wd:Q811979 wd:Q16970 wd:Q57821 }}
      ?place wdt:P31/wdt:P279* ?type.

      # Located in the city or its administrative territory
      ?place wdt:P131* ?location.
      ?location rdfs:label "{city_name}"@en.

      # Must have coordinates
      ?place wdt:P625 ?coord.

      # Optional image
      OPTIONAL {{ ?place wdt:P18 ?image. }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    GROUP BY ?place ?placeLabel ?placeDescription
    LIMIT {limit}
    """

    url = "https://query.wikidata.org/sparql"
    headers = {'User-Agent': 'TravelItineraryBot/1.0 (contact@example.com)'}

    try:
        response = requests.get(
            url,
            params={'query': query, 'format': 'json'},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        landmarks = []
        for i, item in enumerate(data.get('results', {}).get('bindings', [])):
            name = item.get('placeLabel', {}).get('value', '')
            coord = item.get('coordinate', {}).get('value', '')
            desc = item.get('placeDescription', {}).get('value', '')

            # Parse coordinates from "Point(lon lat)" format
            if coord and name:
                try:
                    coord = coord.replace('Point(', '').replace(')', '')
                    lon, lat = map(float, coord.split())

                    # Determine category from description
                    category = 'attraction'
                    desc_lower = desc.lower()
                    if any(x in desc_lower for x in ['museum', 'gallery']):
                        category = 'museum'
                    elif any(x in desc_lower for x in ['church', 'cathedral', 'basilica', 'temple']):
                        category = 'church'
                    elif any(x in desc_lower for x in ['palace', 'castle']):
                        category = 'palace'
                    elif any(x in desc_lower for x in ['park', 'garden']):
                        category = 'park'
                    elif any(x in desc_lower for x in ['tower', 'monument', 'memorial']):
                        category = 'monument'

                    landmarks.append({
                        'id': f'wikidata_{i}',
                        'name': name,
                        'category': category,
                        'latitude': lat,
                        'longitude': lon,
                        'description': desc[:200] if desc else f"Famous landmark in {city_name}",
                        'duration_minutes': 90,
                        'must_see': True,
                        'family_friendly': True
                    })
                except (ValueError, IndexError):
                    pass

        return landmarks
    except Exception as e:
        print(f"  Wikidata error: {e}")
        return []


def generate_landmarks_with_llm(city: str, country: str, api_key: Optional[str] = None) -> List[Dict]:
    """
    Use Gemini to generate famous landmarks for any city.
    Most flexible but requires API key.
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("  No Gemini API key found (set GEMINI_API_KEY or GOOGLE_API_KEY)")
        return []

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        List the top 15 must-visit tourist attractions in {city}, {country}.

        Return ONLY a valid JSON array (no markdown, no explanation) with objects containing:
        - id: unique identifier (e.g., "landmark_1")
        - name: Official name of the attraction
        - category: One of: monument, museum, church, park, attraction, palace
        - latitude: Decimal latitude (be accurate!)
        - longitude: Decimal longitude (be accurate!)
        - duration_minutes: Typical visit duration in minutes
        - description: One sentence about why it's famous
        - must_see: true if it's absolutely unmissable, false otherwise
        - family_friendly: true if good for kids

        Only include actual famous landmarks and attractions, not restaurants or hotels.
        Be accurate with coordinates - these will be used for mapping.
        """

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up response
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        landmarks = json.loads(text)

        # Ensure consistent format
        for i, lm in enumerate(landmarks):
            if 'id' not in lm:
                lm['id'] = f'llm_{i}'
            if 'must_see' not in lm:
                lm['must_see'] = True
            if 'family_friendly' not in lm:
                lm['family_friendly'] = True

        return landmarks
    except Exception as e:
        print(f"  LLM error: {e}")
        return []


def save_landmarks(city_key: str, landmarks: List[Dict], output_dir: Path):
    """Save landmarks to JSON file."""
    filename = f"{city_key}_landmarks.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(landmarks, f, indent=2, ensure_ascii=False)

    return filepath


def generate_for_city(
    city_key: str,
    city_info: Dict,
    output_dir: Path,
    method: str = 'auto',
    api_key: Optional[str] = None
) -> bool:
    """Generate landmarks for a single city."""
    city_name = city_info['name']
    country = city_info['country']

    print(f"\n{'='*60}")
    print(f"Generating landmarks for {city_name}, {country}")
    print(f"{'='*60}")

    landmarks = []

    # Try Wikidata first (free, no API key needed)
    if method in ['auto', 'wikidata']:
        print(f"  Trying Wikidata...")
        landmarks = fetch_landmarks_from_wikidata(city_name, country)
        if landmarks:
            print(f"  Found {len(landmarks)} landmarks from Wikidata")

    # Try LLM if Wikidata failed or method is llm
    if not landmarks and method in ['auto', 'llm']:
        print(f"  Trying LLM generation...")
        landmarks = generate_landmarks_with_llm(city_name, country, api_key)
        if landmarks:
            print(f"  Generated {len(landmarks)} landmarks from LLM")

    if not landmarks:
        print(f"  No landmarks found for {city_name}")
        return False

    # Save to file
    filepath = save_landmarks(city_key, landmarks, output_dir)
    print(f"  Saved to: {filepath}")

    # Show sample
    print(f"\n  Sample landmarks:")
    for lm in landmarks[:5]:
        print(f"    - {lm['name']} ({lm['category']})")

    return True


def main():
    parser = argparse.ArgumentParser(description='Generate landmark files for cities')
    parser.add_argument('city', nargs='?', help='City to generate (default: all cities)')
    parser.add_argument('--method', choices=['auto', 'wikidata', 'llm'], default='auto',
                        help='Method to use for fetching landmarks')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')

    args = parser.parse_args()

    # Output directory
    output_dir = Path(__file__).parent.parent / "landmarks"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("LANDMARK GENERATOR")
    print("="*60)
    print(f"Output directory: {output_dir}")
    print(f"Method: {args.method}")

    # Generate for specific city or all cities
    if args.city:
        city_key = args.city.lower().replace(' ', '_')
        if city_key in CITY_DATABASE:
            generate_for_city(city_key, CITY_DATABASE[city_key], output_dir, args.method, args.api_key)
        else:
            print(f"\nCity '{args.city}' not in database. Available cities:")
            for key in CITY_DATABASE:
                print(f"  - {key}")
            sys.exit(1)
    else:
        # Generate for all cities
        print(f"\nGenerating landmarks for {len(CITY_DATABASE)} cities...")

        success_count = 0
        for city_key, city_info in CITY_DATABASE.items():
            # Skip if file already exists
            existing_file = output_dir / f"{city_key}_landmarks.json"
            if existing_file.exists():
                print(f"\n  Skipping {city_info['name']} (file exists)")
                success_count += 1
                continue

            if generate_for_city(city_key, city_info, output_dir, args.method, args.api_key):
                success_count += 1

        print(f"\n{'='*60}")
        print(f"COMPLETE: Generated landmarks for {success_count}/{len(CITY_DATABASE)} cities")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
