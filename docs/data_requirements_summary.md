# 📊 Data Requirements Summary

## Quick Reference for City Data

---

## Minimum POI Requirements

```
┌─────────────────────────────────────────────────────────────┐
│                    MINIMUM PER CITY                         │
├─────────────────────────────────────────────────────────────┤
│  📍 Attractions      │  15 POIs   │  Core sightseeing       │
│  🍽️  Restaurants      │  30 POIs   │  Lunch + dinner options │
│  🎯 Activities       │  10 POIs   │  Tours, classes, etc.   │
│  🛍️  Shopping         │   5 POIs   │  Markets, boutiques     │
│  🌙 Nightlife        │   5 POIs   │  Bars, evening venues   │
│  📍 Neighborhoods    │   4 areas  │  Geographic coverage    │
├─────────────────────────────────────────────────────────────┤
│  TOTAL MINIMUM      │  65+ POIs  │  For viable itineraries │
│  RECOMMENDED        │ 120+ POIs  │  For quality experience │
└─────────────────────────────────────────────────────────────┘
```

---

## Required Data Fields

### Must Have (100% coverage required)

| Field | Type | Example |
|-------|------|---------|
| `name` | string | "Colosseum" |
| `latitude` | decimal | 41.8902 |
| `longitude` | decimal | 12.4922 |
| `category` | enum | attraction, restaurant, activity, shopping, nightlife |
| `neighborhood` | string | "Centro Storico" |
| `description` | text (50+ chars) | "Ancient Roman amphitheater..." |

### Should Have (80%+ coverage target)

| Field | Type | Example |
|-------|------|---------|
| `subcategory` | string | museum, trattoria, walking_tour |
| `cost_level` | int (1-5) | 3 |
| `typical_duration_minutes` | int | 120 |
| `best_time_of_day` | enum | morning, afternoon, evening |

### Nice to Have

| Field | Type | Example |
|-------|------|---------|
| `avg_cost_per_person` | decimal | 18.00 |
| `address` | text | "Piazza del Colosseo, 1" |
| `opening_hours` | json | {"mon": "9:00-19:00"} |
| `requires_reservation` | boolean | true |
| `booking_url` | url | "https://..." |

---

## Persona Scores Required

### 8 Group Types
```
□ Family    □ Kids      □ Couple    □ Honeymoon
□ Solo      □ Friends   □ Seniors   □ Business
```

### 10 Vibe Categories
```
□ Adventure    □ Relaxation   □ Cultural     □ Foodie
□ Nightlife    □ Nature       □ Shopping     □ Photography
□ Wellness     □ Romantic
```

### Scoring Scale
```
0.9-1.0  →  Perfect fit (specifically for this persona)
0.7-0.8  →  Great fit (highly recommended)
0.5-0.6  →  Neutral (works for most)
0.3-0.4  →  Not ideal (but acceptable)
0.0-0.2  →  Poor fit (avoid for this persona)
```

---

## Quality Thresholds

```
DATA COMPLETENESS SCORE
├── 100% coordinates         → Required
├── 100% descriptions        → Required
├── 80%+ cost_level          → Target
├── 70%+ duration            → Target
└── 50%+ opening_hours       → Nice to have

PERSONA COVERAGE SCORE
├── Avg group score > 0.60   → Required
├── Avg vibe score > 0.50    → Required
├── Min 5 POIs @ 0.8+ each   → Required
└── All personas viable      → Required

GEOGRAPHIC COVERAGE SCORE
├── All major areas covered  → Required
├── Min 3 POIs/neighborhood  → Required
├── Restaurant within 500m   → Required
└── 3+ walkable zones        → Target
```

---

## Data Source Priority

| Priority | Source | Cost | Use For |
|----------|--------|------|---------|
| 1 | **Overture Maps** | Free | Base data, coordinates |
| 2 | **Google Places** | ~$5/city | Rich descriptions |
| 3 | **Manual Curation** | Labor | Persona scores |
| 4 | **Foursquare** | Free tier | Categories, tips |
| 5 | **Local Sources** | Variable | Hidden gems |

---

## Timeline per City

```
Week 1
├── Day 1-2: Data collection (Overture + Google)
├── Day 3-5: Persona scoring (manual)
└── Review checkpoint

Week 2
├── Day 1: Embedding generation
├── Day 2-3: Validation & testing
├── Day 4: Gap filling
└── Day 5: Final review & launch
```

---

## Validation Checklist

```
□ Generate test itinerary: 3-day couple/cultural
□ Generate test itinerary: 3-day family/relaxation
□ Generate test itinerary: 1-day solo/foodie
□ All itineraries have lunch + dinner
□ No walking distance > 2km between consecutive items
□ Every attraction has 2+ restaurants within 500m
□ Every neighborhood has 5+ POIs
□ Embedding search returns 50+ results
```

---

## Red Flags to Avoid

❌ **Data Issues**
- POIs without coordinates
- Duplicate entries
- Descriptions < 50 characters
- Missing category assignments

❌ **Coverage Issues**
- Neighborhood with < 3 POIs
- Attraction without nearby restaurant
- Zero nightlife options
- Missing must-see landmarks

❌ **Scoring Issues**
- All scores at 0.5 (not curated)
- Extreme scores without justification
- Missing persona for major POI
