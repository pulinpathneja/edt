# POI Attributes Schema for Persona-Driven Itineraries

## Overview

This document defines all attributes required for POIs to support:
- Group-specific pros/cons analysis
- Instagram/photography suitability
- Accessibility requirements
- Time-based recommendations
- Budget planning

---

## 1. Core Identification (Required)

| Attribute | Type | Source | Example |
|-----------|------|--------|---------|
| `id` | UUID | System | `uuid-v4` |
| `name` | string | Overture/Google | "Colosseum" |
| `latitude` | decimal | Overture | 41.8902 |
| `longitude` | decimal | Overture | 12.4922 |
| `category` | enum | Overture | attraction, restaurant, cafe |
| `subcategory` | string | Enriched | museum, trattoria, gelateria |

---

## 2. Group Type Suitability Scores (0.0 - 1.0)

### Scores
| Attribute | Description | High Score If... |
|-----------|-------------|------------------|
| `score_family` | Family with kids | Safe, facilities, engaging |
| `score_kids` | Specifically for children | Interactive, fun, short duration |
| `score_couple` | Romantic couples | Intimate, conversation-friendly |
| `score_honeymoon` | Newlyweds | Luxury, special, private |
| `score_solo` | Solo travelers | Safe alone, social opportunities |
| `score_friends` | Friend groups | Fun, shareable, group-friendly |
| `score_seniors` | Elderly travelers | Accessible, comfortable pace |
| `score_business` | Business travelers | Efficient, professional |

### Pros/Cons Text (for each group)
```json
{
  "family": {
    "pros": ["Stroller accessible", "Kids eat free", "Play area available"],
    "cons": ["Can get crowded", "Limited high chairs"]
  },
  "couple": {
    "pros": ["Romantic ambiance", "Quiet corners available"],
    "cons": ["Can be noisy on weekends"]
  }
}
```

---

## 3. Vibe/Experience Scores (0.0 - 1.0)

| Attribute | Description | High Score If... |
|-----------|-------------|------------------|
| `score_cultural` | Historical/artistic value | Museums, monuments, traditions |
| `score_foodie` | Culinary experience | Local cuisine, food tours |
| `score_romantic` | Romance factor | Sunset views, intimate settings |
| `score_adventure` | Thrill/excitement | Outdoor, physical, unique |
| `score_relaxation` | Peace/calm | Spa, gardens, slow-paced |
| `score_nightlife` | Evening entertainment | Bars, clubs, late hours |
| `score_shopping` | Retail experience | Markets, boutiques |
| `score_nature` | Natural beauty | Parks, gardens, views |
| `score_photography` | Photo opportunities | Iconic, scenic, beautiful |
| `score_wellness` | Health/fitness | Yoga, spa, healthy options |
| `score_local_authentic` | Non-touristy | Hidden gems, local favorites |

---

## 4. Instagram/Photography Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_instagram_worthy` | boolean | Highly photogenic spot |
| `best_photo_spots` | array[string] | ["Main entrance", "Rooftop terrace"] |
| `golden_hour_rating` | int (1-5) | How good at sunset/sunrise |
| `night_photography` | boolean | Good for night shots |
| `selfie_friendly` | boolean | Easy self-portraits |
| `drone_allowed` | boolean | Aerial photography permitted |
| `tripod_allowed` | boolean | Can use tripod |
| `photo_restrictions` | string | "No flash", "No interior photos" |
| `iconic_shot_description` | string | "View through the arch at sunset" |
| `crowd_for_photos` | enum | empty, moderate, crowded |
| `best_photo_time` | string | "Early morning before 9am" |

---

## 5. Accessibility Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `wheelchair_accessible` | boolean | Full wheelchair access |
| `wheelchair_partial` | boolean | Partial access |
| `elevator_available` | boolean | Has elevator/lift |
| `accessible_restroom` | boolean | Accessible toilets |
| `braille_signage` | boolean | For visually impaired |
| `audio_guide` | boolean | Audio descriptions available |
| `sign_language` | boolean | Sign language tours |
| `stroller_friendly` | boolean | Easy with strollers |
| `accessible_parking` | boolean | Disabled parking nearby |
| `service_animals` | boolean | Service animals allowed |
| `sensory_friendly` | boolean | Low sensory environment |
| `accessibility_notes` | string | Additional details |

---

## 6. Family/Kids Specific

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_kid_friendly` | boolean | Suitable for children |
| `min_recommended_age` | int | Minimum age suggestion |
| `max_recommended_age` | int | Maximum age suggestion |
| `has_play_area` | boolean | Playground/play zone |
| `kids_menu` | boolean | Children's menu available |
| `baby_changing` | boolean | Changing facilities |
| `high_chairs` | boolean | Available for restaurants |
| `kids_activities` | array[string] | ["Treasure hunt", "Art workshop"] |
| `educational_value` | int (1-5) | Learning potential |
| `stroller_parking` | boolean | Place to leave stroller |
| `family_restroom` | boolean | Family toilet available |
| `kid_attention_span` | int | Minutes kids stay engaged |

---

## 7. Time & Duration

| Attribute | Type | Description |
|-----------|------|-------------|
| `typical_duration_minutes` | int | Average visit time |
| `min_duration_minutes` | int | Quick visit |
| `max_duration_minutes` | int | Extended visit |
| `best_time_of_day` | enum | morning, afternoon, evening, night, any |
| `best_days` | array[string] | ["weekday", "saturday"] |
| `avoid_times` | array[string] | ["Sunday morning", "Lunch rush"] |
| `seasonal_best` | array[string] | ["spring", "fall"] |
| `seasonal_avoid` | array[string] | ["august"] |
| `golden_hour_relevant` | boolean | Worth visiting at sunset |
| `night_visit_possible` | boolean | Open/accessible at night |

---

## 8. Opening Hours & Availability

| Attribute | Type | Description |
|-----------|------|-------------|
| `opening_hours` | json | Structured hours by day |
| `last_entry_before_close` | int | Minutes before closing |
| `closed_days` | array[string] | ["Monday", "Jan 1"] |
| `seasonal_closures` | string | "Closed August" |
| `requires_reservation` | boolean | Booking needed |
| `reservation_lead_days` | int | Book X days ahead |
| `walk_in_possible` | boolean | Can visit without booking |
| `timed_entry` | boolean | Specific entry times |
| `capacity_limited` | boolean | Limited daily visitors |

---

## 9. Cost & Budget

| Attribute | Type | Description |
|-----------|------|-------------|
| `cost_level` | int (1-5) | 1=free, 5=luxury |
| `avg_cost_per_person` | decimal | Average spend |
| `cost_currency` | string | "EUR" |
| `entry_fee` | decimal | Admission cost |
| `entry_fee_child` | decimal | Child admission |
| `entry_fee_senior` | decimal | Senior admission |
| `free_entry_times` | string | "First Sunday of month" |
| `tips_expected` | boolean | Tipping culture |
| `tip_percentage` | int | Suggested tip % |
| `hidden_costs` | array[string] | ["Audio guide €6", "Lockers €2"] |
| `payment_methods` | array[string] | ["cash", "card", "mobile"] |
| `budget_tips` | string | "Free with Roma Pass" |

---

## 10. Crowd & Atmosphere

| Attribute | Type | Description |
|-----------|------|-------------|
| `typical_crowd_level` | int (1-5) | Average crowding |
| `peak_crowd_times` | array[string] | ["10am-12pm", "weekends"] |
| `quiet_times` | array[string] | ["Early morning", "Late afternoon"] |
| `atmosphere` | array[string] | ["lively", "quiet", "romantic"] |
| `noise_level` | int (1-5) | 1=silent, 5=loud |
| `dress_code` | string | "Smart casual", "Cover shoulders" |
| `tourist_ratio` | int (1-5) | 1=locals only, 5=all tourists |
| `is_hidden_gem` | boolean | Off the beaten path |
| `is_must_see` | boolean | Iconic must-visit |
| `is_tourist_trap` | boolean | Overrated/overpriced |
| `local_favorite` | boolean | Loved by locals |

---

## 11. Physical Requirements

| Attribute | Type | Description |
|-----------|------|-------------|
| `physical_intensity` | int (1-5) | 1=sedentary, 5=strenuous |
| `walking_required_meters` | int | Walking distance inside |
| `stairs_count` | int | Number of stairs |
| `elevation_gain_meters` | int | Climbing involved |
| `standing_time_minutes` | int | Time spent standing |
| `seating_available` | boolean | Places to rest |
| `shade_available` | boolean | Protection from sun |
| `indoor_outdoor` | enum | indoor, outdoor, both |
| `weather_dependent` | boolean | Affected by weather |
| `rain_alternative` | string | What to do if raining |

---

## 12. Amenities & Facilities

| Attribute | Type | Description |
|-----------|------|-------------|
| `has_restroom` | boolean | Toilets available |
| `has_wifi` | boolean | Free WiFi |
| `has_parking` | boolean | Parking available |
| `parking_cost` | decimal | Parking fee |
| `has_cloakroom` | boolean | Bag storage |
| `has_cafe` | boolean | On-site cafe |
| `has_restaurant` | boolean | On-site dining |
| `has_gift_shop` | boolean | Souvenir shop |
| `has_atm` | boolean | Cash machine |
| `has_water_fountain` | boolean | Free water |
| `has_charging` | boolean | Phone charging |
| `luggage_storage` | boolean | Store bags |

---

## 13. Food & Dining Specific (Restaurants)

| Attribute | Type | Description |
|-----------|------|-------------|
| `cuisine_type` | array[string] | ["Italian", "Roman", "Seafood"] |
| `meal_types` | array[string] | ["breakfast", "lunch", "dinner"] |
| `dietary_options` | array[string] | ["vegetarian", "vegan", "gluten-free"] |
| `halal_certified` | boolean | Halal food |
| `kosher_certified` | boolean | Kosher food |
| `outdoor_seating` | boolean | Al fresco dining |
| `reservation_difficulty` | int (1-5) | How hard to book |
| `wait_time_typical` | int | Minutes without reservation |
| `tasting_menu` | boolean | Multi-course option |
| `wine_pairing` | boolean | Wine pairing available |
| `local_specialty` | array[string] | ["Cacio e Pepe", "Carbonara"] |
| `michelin_stars` | int | 0-3 stars |
| `avg_meal_duration` | int | Minutes for full meal |

---

## 14. Reviews & Ratings (from external APIs)

| Attribute | Type | Source |
|-----------|------|--------|
| `google_rating` | decimal | Google Places |
| `google_review_count` | int | Google Places |
| `tripadvisor_rating` | decimal | TripAdvisor |
| `tripadvisor_rank` | int | City ranking |
| `yelp_rating` | decimal | Yelp |
| `aggregated_rating` | decimal | Weighted average |
| `sentiment_score` | decimal | NLP from reviews |
| `trending_score` | decimal | Recent popularity |
| `review_highlights` | array[string] | Top mentioned phrases |

---

## 15. Logistics & Connections

| Attribute | Type | Description |
|-----------|------|-------------|
| `nearest_metro` | string | Closest metro station |
| `metro_distance_meters` | int | Walking distance |
| `bus_lines` | array[string] | Nearby bus routes |
| `taxi_pickup_easy` | boolean | Easy to get taxi |
| `uber_available` | boolean | Rideshare works here |
| `nearby_parking` | string | Nearest parking |
| `best_approach` | string | "Walk from Termini" |
| `combines_well_with` | array[UUID] | Nearby POI IDs |
| `walking_route_from` | json | Routes from major points |

---

## 16. Seasonality & Weather

### Season Scores (0.0 - 1.0)
| Attribute | Type | Description |
|-----------|------|-------------|
| `score_spring` | decimal | March-May suitability |
| `score_summer` | decimal | June-August suitability |
| `score_fall` | decimal | September-November suitability |
| `score_winter` | decimal | December-February suitability |

### Monthly Breakdown
| Attribute | Type | Description |
|-----------|------|-------------|
| `best_months` | array[int] | [4, 5, 9, 10] = Apr, May, Sep, Oct |
| `avoid_months` | array[int] | [7, 8] = Jul, Aug |
| `peak_season` | array[int] | Busiest months |
| `off_season` | array[int] | Quietest months |
| `shoulder_season` | array[int] | Good balance months |

### Weather Sensitivity
| Attribute | Type | Description |
|-----------|------|-------------|
| `weather_dependent` | boolean | Experience affected by weather |
| `rain_suitable` | boolean | Good even when raining |
| `rain_alternative` | string | "Visit the indoor gallery section" |
| `heat_sensitive` | boolean | Avoid on very hot days |
| `cold_sensitive` | boolean | Avoid on very cold days |
| `wind_sensitive` | boolean | Affected by wind |
| `ideal_temp_min` | int | Minimum comfortable temp °C |
| `ideal_temp_max` | int | Maximum comfortable temp °C |
| `indoor_outdoor` | enum | indoor, outdoor, both |
| `covered_areas` | boolean | Has sheltered sections |

### Seasonal Variations
| Attribute | Type | Description |
|-----------|------|-------------|
| `seasonal_hours` | json | Different hours by season |
| `seasonal_pricing` | json | Price variations |
| `seasonal_crowd` | json | Crowd level by month |
| `seasonal_closures` | array[string] | ["August", "Christmas week"] |
| `seasonal_events` | array | Special seasonal activities |

### Daylight Considerations
| Attribute | Type | Description |
|-----------|------|-------------|
| `needs_daylight` | boolean | Best visited in daylight |
| `sunset_worthy` | boolean | Worth visiting at sunset |
| `sunrise_worthy` | boolean | Worth visiting at sunrise |
| `night_experience` | boolean | Special night experience |
| `golden_hour_rating` | int (1-5) | Quality at golden hour |

### Local Calendar
| Attribute | Type | Description |
|-----------|------|-------------|
| `local_holidays_closed` | array[string] | Closed on which holidays |
| `festival_relevant` | array[string] | Related festivals |
| `avoid_during_events` | array[string] | ["Football match days"] |
| `special_seasonal_experience` | json | Unique seasonal offerings |

### Example Seasonal Data
```json
{
  "Colosseum": {
    "season_scores": {
      "spring": 0.95,
      "summer": 0.60,
      "fall": 0.95,
      "winter": 0.75
    },
    "best_months": [4, 5, 9, 10],
    "avoid_months": [7, 8],
    "seasonal_notes": {
      "summer": "Extremely hot, visit early morning only",
      "winter": "Fewer crowds, pleasant temperatures",
      "spring": "Perfect weather, book ahead for Easter"
    },
    "weather": {
      "weather_dependent": true,
      "heat_sensitive": true,
      "rain_suitable": false,
      "rain_alternative": "Visit nearby Palazzo Valentini underground"
    }
  },
  "Trastevere Dinner": {
    "season_scores": {
      "spring": 0.95,
      "summer": 0.90,
      "fall": 0.95,
      "winter": 0.70
    },
    "seasonal_notes": {
      "summer": "Amazing outdoor dining, lively atmosphere",
      "winter": "Many outdoor spots closed, but cozy indoor trattorias"
    }
  }
}
```

---

## 17. Safety & Practical

| Attribute | Type | Description |
|-----------|------|-------------|
| `safety_rating` | int (1-5) | General safety |
| `safe_at_night` | boolean | Safe after dark |
| `pickpocket_risk` | int (1-5) | Theft risk level |
| `scam_warnings` | array[string] | Known scams |
| `emergency_nearby` | boolean | Hospital/police nearby |
| `first_aid` | boolean | First aid available |
| `covid_measures` | string | Health protocols |
| `insurance_recommended` | boolean | Travel insurance needed |

---

## Data Sources Mapping

| Attribute Category | Primary Source | Enrichment Source |
|--------------------|----------------|-------------------|
| Core (name, location) | Overture Maps | - |
| Categories | Overture Maps | Manual curation |
| Ratings/Reviews | Google Places | TripAdvisor, Yelp |
| Photos | Google Places | Instagram API |
| Hours/Availability | Google Places | Official websites |
| Accessibility | Manual | Google Maps |
| Persona Scores | **Manual Curation** | ML from reviews |
| Pros/Cons | **Manual Curation** | NLP from reviews |
| Instagram worthiness | **Manual Curation** | Instagram hashtag analysis |
| Family attributes | **Manual Curation** | Review NLP |
| Cost details | Google Places | Manual verification |

---

## Priority for MVP

### Must Have (Phase 1)
- Core identification
- Group type scores (8 scores)
- Vibe scores (10 scores)
- Basic timing (duration, best_time)
- Cost level
- is_kid_friendly, wheelchair_accessible

### Should Have (Phase 2)
- Instagram/photography attributes
- Detailed accessibility
- Family-specific attributes
- Crowd patterns
- Pros/cons text

### Nice to Have (Phase 3)
- Full amenities
- Detailed logistics
- Safety ratings
- Review integration

---

## Example Complete POI

```json
{
  "id": "poi_colosseum_001",
  "name": "Colosseum",
  "latitude": 41.8902,
  "longitude": 12.4922,
  "category": "attraction",
  "subcategory": "historical_site",

  "scores": {
    "family": 0.75,
    "kids": 0.65,
    "couple": 0.85,
    "honeymoon": 0.80,
    "solo": 0.90,
    "friends": 0.85,
    "seniors": 0.60,
    "business": 0.50,

    "cultural": 0.98,
    "photography": 0.95,
    "romantic": 0.70,
    "adventure": 0.40,
    "relaxation": 0.30
  },

  "group_insights": {
    "family": {
      "pros": ["Educational for kids", "Fascinating history", "Audio guides available"],
      "cons": ["Lots of walking", "Can be hot in summer", "Stroller difficult on cobblestones"]
    },
    "couple": {
      "pros": ["Romantic sunset views", "Iconic photo backdrop", "Night tours available"],
      "cons": ["Very crowded midday", "Not intimate"]
    },
    "seniors": {
      "pros": ["Historical significance", "Guided tours available"],
      "cons": ["Extensive walking", "Limited seating", "Steep stairs"]
    }
  },

  "instagram": {
    "is_instagram_worthy": true,
    "best_photo_spots": ["View from Palatine Hill", "Through the arches", "Night illumination"],
    "golden_hour_rating": 5,
    "best_photo_time": "Sunset or early morning before 9am",
    "iconic_shot": "Wide angle from Piazza del Colosseo"
  },

  "accessibility": {
    "wheelchair_accessible": true,
    "elevator_available": true,
    "accessible_path": "Ground floor and first tier accessible"
  },

  "timing": {
    "typical_duration_minutes": 90,
    "best_time_of_day": "morning",
    "avoid_times": ["11am-2pm weekends"],
    "requires_reservation": true,
    "reservation_lead_days": 7
  },

  "cost": {
    "cost_level": 3,
    "entry_fee": 16.00,
    "entry_fee_child": 2.00,
    "currency": "EUR",
    "free_entry": "First Sunday of month",
    "budget_tip": "Combined ticket with Roman Forum valid 2 days"
  },

  "crowd": {
    "typical_crowd_level": 5,
    "quiet_times": ["Early morning", "Late afternoon winter"],
    "is_must_see": true
  },

  "physical": {
    "physical_intensity": 3,
    "walking_required_meters": 800,
    "stairs_count": 150,
    "seating_available": false,
    "indoor_outdoor": "outdoor"
  }
}
```
