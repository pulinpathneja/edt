# 🌍 City Expansion Guide

## How to Add a New City to the Itinerary System

---

## Overview

Adding a new city takes approximately **8-12 days** and follows a 4-phase process:

| Phase | Duration | Key Output |
|-------|----------|------------|
| 1. Data Collection | 2-3 days | Raw POI data |
| 2. Persona Scoring | 3-5 days | Scored & tagged POIs |
| 3. Embedding & Indexing | 1 day | Searchable database |
| 4. Validation | 2 days | Quality-assured city |

---

## Phase 1: Data Collection

### Minimum Requirements

| Category | Minimum | Recommended | Purpose |
|----------|---------|-------------|---------|
| Attractions | 15 | 30+ | Anchor activities |
| Restaurants | 30 | 60+ | Meal planning |
| Activities | 10 | 20+ | Fill itinerary gaps |
| Shopping | 5 | 15+ | Persona variety |
| Nightlife | 5 | 15+ | Evening options |
| **Neighborhoods** | 4 | 8+ | Geographic coverage |

### Required Fields per POI

```
MANDATORY:
├── name (string)
├── latitude (decimal)
├── longitude (decimal)
├── category (enum: attraction, restaurant, activity, shopping, nightlife)
├── neighborhood (string)
└── description (text, min 50 characters)

RECOMMENDED:
├── subcategory (e.g., museum, trattoria, walking_tour)
├── cost_level (1-5)
├── avg_cost_per_person (decimal)
├── typical_duration_minutes (int)
├── best_time_of_day (morning/afternoon/evening/night/any)
├── address (text)
└── opening_hours (structured)

OPTIONAL BUT VALUABLE:
├── phone
├── website
├── booking_url
├── image_url
└── source_id (for deduplication)
```

### Data Sources (by Priority)

| Source | Cost | Quality | Best For |
|--------|------|---------|----------|
| **Overture Maps** | Free | Good | Base POI data, coordinates |
| **Google Places API** | $17/1000 requests | Excellent | Rich descriptions, ratings |
| **Foursquare** | Free tier | Good | Categories, tips |
| **TripAdvisor** | Paid | Excellent | Tourist-focused data |
| **Local Tourism Board** | Free | Variable | Official attractions |
| **OpenStreetMap** | Free | Good | Addresses, hours |

### Collection Script Template

```python
# Example: Fetch from Overture Maps
import overturemaps as om

# Define bounding box for city
bbox = {
    'rome': (12.35, 41.80, 12.60, 42.00),
    'florence': (11.20, 43.75, 11.30, 43.80),
    'barcelona': (2.10, 41.35, 2.20, 41.45),
}

# Fetch POIs
pois = om.places(bbox=bbox['rome'], categories=['restaurant', 'attraction'])
```

---

## Phase 2: Persona Scoring

### Group Type Scores (0.0 - 1.0)

Score each POI for how well it fits each traveler type:

| Group Type | Scoring Criteria |
|------------|------------------|
| **Family** | Kid-friendly, safe, facilities, not too long |
| **Kids** | Interactive, educational-fun, engaging, short |
| **Couple** | Romantic ambiance, intimate, conversation-friendly |
| **Honeymoon** | Luxury feel, special experiences, private |
| **Solo** | Safe for singles, social opportunities, easy navigation |
| **Friends** | Fun activities, photo ops, shared experiences |
| **Seniors** | Accessible, not demanding, comfortable pacing |
| **Business** | Efficient, professional, quick options |

### Vibe Scores (0.0 - 1.0)

| Vibe | High Score If... |
|------|------------------|
| **Adventure** | Outdoor, physical activity, unique |
| **Relaxation** | Spa, slow-paced, peaceful |
| **Cultural** | Museums, history, local traditions |
| **Foodie** | Local cuisine, food tours, notable restaurants |
| **Nightlife** | Bars, clubs, late-night venues |
| **Nature** | Parks, gardens, natural beauty |
| **Shopping** | Markets, boutiques, unique finds |
| **Photography** | Scenic views, iconic spots |
| **Wellness** | Yoga, health-focused, meditation |
| **Romantic** | Sunset spots, fine dining, couples activities |

### Practical Attributes (Boolean)

```
□ is_kid_friendly
□ is_wheelchair_accessible
□ is_pet_friendly
□ requires_reservation
□ is_indoor
□ is_outdoor
□ is_must_see
□ is_hidden_gem
□ instagram_worthy
```

### Scoring Guidelines

**0.9 - 1.0**: Perfect fit, specifically designed for this persona
**0.7 - 0.8**: Great fit, highly recommended
**0.5 - 0.6**: Neutral, works for most
**0.3 - 0.4**: Not ideal, but acceptable
**0.0 - 0.2**: Poor fit, avoid for this persona

### Example: Scoring "Colosseum"

```json
{
  "name": "Colosseum",
  "persona_scores": {
    "score_family": 0.85,      // Educational, manageable duration
    "score_kids": 0.75,        // Interesting but can be tiring
    "score_couple": 0.90,      // Romantic, iconic
    "score_honeymoon": 0.85,   // Must-see but crowded
    "score_solo": 0.95,        // Easy to visit alone
    "score_friends": 0.90,     // Great group photos
    "score_seniors": 0.70,     // Lots of walking/stairs
    "score_business": 0.60,    // Time-consuming

    "score_cultural": 0.98,    // Peak cultural experience
    "score_photography": 0.95, // Iconic shots
    "score_adventure": 0.50,   // Not adventurous
    "score_foodie": 0.20,      // No food relevance
    "score_romantic": 0.75     // Romantic but crowded
  }
}
```

---

## Phase 3: Embedding & Indexing

### Generate Embeddings

```python
from app.core.embeddings import create_poi_description_embedding

for poi in pois:
    embedding = create_poi_description_embedding(
        name=poi.name,
        description=poi.description,
        category=poi.category,
        subcategory=poi.subcategory,
        neighborhood=poi.neighborhood
    )
    poi.description_embedding = embedding
```

### Build Relationships

```python
from app.services.knowledge_graph import RelationshipBuilder

builder = RelationshipBuilder(db)

# Auto-create proximity relationships (within 500m)
await builder.auto_create_proximity_relationships(
    city="Florence",
    max_distance_km=0.5
)
```

### Index in Database

```bash
# Run migration for new city data
alembic upgrade head

# Seed the data
python -m data.scripts.seed_data --city florence
```

---

## Phase 4: Validation

### Quality Checklist

```
DATA COMPLETENESS
□ All POIs have coordinates
□ All POIs have descriptions (50+ chars)
□ 90%+ POIs have cost_level
□ All attractions have typical_duration
□ All restaurants have subcategory

PERSONA COVERAGE
□ Average group scores > 0.6
□ Average vibe scores > 0.5
□ At least 5 POIs score > 0.8 for each persona
□ Must-see attractions marked (5-10)

GEOGRAPHIC COVERAGE
□ All major neighborhoods covered
□ No neighborhood has < 3 POIs
□ Restaurant within 500m of each attraction
□ At least 3 walkable zones identified

ITINERARY TESTING
□ Generate 3-day itinerary for "couple + cultural"
□ Generate 3-day itinerary for "family + relaxation"
□ Generate 1-day itinerary for "solo + foodie"
□ All itineraries have lunch + dinner
□ No impossible walking distances
```

### Test Queries

```python
# Test 1: Semantic search
results = await retriever.retrieve_candidates(
    TripRequestCreate(
        destination_city="Florence",
        group_type="honeymoon",
        vibes=["romantic", "cultural"],
        pacing="slow"
    )
)
assert len(results) >= 20

# Test 2: Restaurant accessibility
for attraction in attractions:
    nearby = await kg.find_nearby_restaurants(
        attraction.id, max_distance_meters=500
    )
    assert len(nearby) >= 2, f"No restaurants near {attraction.name}"

# Test 3: Full itinerary generation
itinerary = await generate_itinerary(
    destination="Florence",
    days=3,
    group_type="friends",
    vibes=["foodie", "cultural"]
)
assert len(itinerary.days) == 3
assert all(len(day.items) >= 3 for day in itinerary.days)
```

---

## Cost Estimation

### Per City Costs

| Item | Cost |
|------|------|
| Overture Maps data | $0 (free) |
| Google Places (100 POIs enrichment) | ~$5 |
| Embedding generation (local) | $0 |
| Manual curation (8-12 hours) | Labor |
| **Total data cost** | **~$5** |

### At Scale (50 cities)

| Item | Cost |
|------|------|
| Data collection & enrichment | ~$250 |
| Embedding storage (pgvector) | ~$50/month |
| Compute for embeddings | ~$20 |
| **Total for 50 cities** | **~$320 + $50/month** |

---

## City Priority Matrix

### How to Prioritize New Cities

| Factor | Weight | Metrics |
|--------|--------|---------|
| **Demand** | 40% | Search volume, booking requests |
| **Data Availability** | 25% | Overture coverage, API access |
| **Complexity** | 20% | City size, POI density |
| **Strategic Value** | 15% | Market expansion, partnerships |

### Recommended Expansion Order

**Tier 1 (High demand, Low complexity)**
- Florence, Venice, Amsterdam, Prague, Lisbon

**Tier 2 (High demand, Medium complexity)**
- Barcelona, Paris, London, Berlin, Vienna

**Tier 3 (Emerging markets)**
- Porto, Seville, Budapest, Krakow, Athens

**Tier 4 (Asia expansion)**
- Tokyo, Kyoto, Bangkok, Singapore, Bali

---

## Templates & Tools

### POI Data Template (CSV)

```csv
name,latitude,longitude,category,subcategory,neighborhood,description,cost_level,typical_duration_minutes
"Uffizi Gallery",43.7677,11.2553,attraction,museum,"Centro Storico","World-renowned art museum...",3,180
```

### Persona Scoring Template (JSON)

```json
{
  "poi_id": "uuid",
  "scores": {
    "group_types": {
      "family": 0.7,
      "couple": 0.9
    },
    "vibes": {
      "cultural": 0.95,
      "relaxation": 0.4
    }
  }
}
```

### Validation Report Template

```markdown
# City Validation Report: [CITY NAME]

## Summary
- Total POIs: X
- Categories: Y
- Neighborhoods: Z
- Data Quality Score: X/100

## Gaps Identified
1. [Gap 1]
2. [Gap 2]

## Recommendations
1. [Rec 1]
2. [Rec 2]

## Sign-off
- [ ] Data Lead
- [ ] QA Lead
- [ ] Product Owner
```

---

## Support & Resources

- **Data Team**: data@company.com
- **Technical Docs**: /docs/technical/
- **API Reference**: /docs/api/
- **Slack Channel**: #city-expansion
