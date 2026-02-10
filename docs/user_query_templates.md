# User Query Templates for Itinerary Generation

## Overview

These are sample natural language queries users might ask. The system should extract relevant parameters and generate personalized itineraries.

---

## Query Templates by Category

### 1. Honeymoon & Romance

```
Q1: "Plan a 5-day romantic getaway in Rome for our honeymoon in June"
```
| Extracted | Value |
|-----------|-------|
| group_type | honeymoon |
| vibes | romantic, foodie |
| pacing | slow |
| duration | 5 days |
| month | June (summer) |
| budget | luxury (assumed) |

```
Q2: "We're celebrating our 10th anniversary. Something special and intimate"
```
| Extracted | Value |
|-----------|-------|
| group_type | couple |
| vibes | romantic, relaxation |
| pacing | slow |
| special | anniversary celebration |

```
Q3: "Surprise trip for my partner. They love sunset views and wine"
```
| Extracted | Value |
|-----------|-------|
| group_type | couple |
| vibes | romantic, photography, foodie |
| preferences | sunset_worthy, wine_bars |

---

### 2. Family Travel

```
Q4: "Family trip with kids aged 5 and 8. They get bored easily!"
```
| Extracted | Value |
|-----------|-------|
| group_type | family |
| has_kids | true |
| kids_ages | [5, 8] |
| vibes | relaxation, cultural |
| pacing | moderate |
| constraints | kid_friendly, short_duration_activities |

```
Q5: "Multi-generational trip - grandparents, parents, and kids. Need something for everyone"
```
| Extracted | Value |
|-----------|-------|
| group_type | family |
| has_kids | true |
| has_seniors | true |
| constraints | accessible, mixed_interests |
| pacing | slow |

```
Q6: "Visiting Rome in August with toddlers. How do we survive the heat?"
```
| Extracted | Value |
|-----------|-------|
| group_type | family |
| has_kids | true |
| kids_ages | [1-3] |
| month | August |
| constraints | avoid_heat, indoor_activities, stroller_friendly |

---

### 3. Solo Travel

```
Q7: "Solo female traveler. Safe neighborhoods and social spots to meet people"
```
| Extracted | Value |
|-----------|-------|
| group_type | solo |
| safety_priority | high |
| vibes | social, cultural, foodie |
| preferences | safe_neighborhoods |

```
Q8: "Digital nomad spending a month in Rome. Best cafes to work from and local life"
```
| Extracted | Value |
|-----------|-------|
| group_type | solo |
| vibes | foodie, cultural, relaxation |
| duration | 30 days |
| preferences | wifi_cafes, local_authentic |

```
Q9: "Introvert's guide to Rome. Quiet spots, less crowded times"
```
| Extracted | Value |
|-----------|-------|
| group_type | solo |
| vibes | relaxation, cultural, photography |
| preferences | avoid_crowds, quiet_times |

---

### 4. Friends Trip

```
Q10: "Bachelorette party! Fun, Instagram-worthy, great nightlife"
```
| Extracted | Value |
|-----------|-------|
| group_type | friends |
| vibes | nightlife, photography, shopping |
| pacing | fast |
| preferences | instagram_worthy, fun |

```
Q11: "College reunion trip. 6 friends, we like food and wine"
```
| Extracted | Value |
|-----------|-------|
| group_type | friends |
| group_size | 6 |
| vibes | foodie, nightlife |
| preferences | group_friendly |

```
Q12: "Boys trip - adventure activities, good food, sports bars"
```
| Extracted | Value |
|-----------|-------|
| group_type | friends |
| vibes | adventure, foodie, nightlife |
| pacing | fast |

---

### 5. Senior Travel

```
Q13: "Retired couple, taking it slow. Accessibility is important"
```
| Extracted | Value |
|-----------|-------|
| group_type | seniors |
| vibes | cultural, relaxation |
| pacing | slow |
| constraints | wheelchair_accessible, limited_walking |

```
Q14: "70th birthday trip. Not too strenuous but want to see the highlights"
```
| Extracted | Value |
|-----------|-------|
| group_type | seniors |
| vibes | cultural, photography |
| pacing | slow |
| constraints | minimal_stairs, seating_available |

---

### 6. Budget Focused

```
Q15: "Backpacker budget. Free stuff and cheap eats only!"
```
| Extracted | Value |
|-----------|-------|
| group_type | solo |
| budget_level | 1 |
| vibes | cultural, adventure, foodie |
| constraints | free_attractions, budget_restaurants |

```
Q16: "How to see Rome on €50/day including food?"
```
| Extracted | Value |
|-----------|-------|
| daily_budget | 50 EUR |
| constraints | cost_conscious |

---

### 7. Luxury Focused

```
Q17: "Money is no object. Best of the best in Rome"
```
| Extracted | Value |
|-----------|-------|
| budget_level | 5 |
| vibes | foodie, relaxation |
| preferences | michelin_restaurants, exclusive_experiences |

```
Q18: "VIP experience. Skip the lines, private tours, best tables"
```
| Extracted | Value |
|-----------|-------|
| budget_level | 5 |
| preferences | skip_line, private_tours, reservations |

---

### 8. Special Interest

```
Q19: "I'm a photographer. Best golden hour spots and iconic shots"
```
| Extracted | Value |
|-----------|-------|
| vibes | photography |
| preferences | sunset_worthy, golden_hour, iconic_shots |
| timing | early_morning, sunset |

```
Q20: "Foodie trip - every local specialty, cooking classes, markets"
```
| Extracted | Value |
|-----------|-------|
| vibes | foodie, cultural |
| preferences | local_specialties, cooking_classes, markets |

```
Q21: "History buff. Ancient Rome, archaeological sites, in-depth"
```
| Extracted | Value |
|-----------|-------|
| vibes | cultural |
| subcategory_preference | historical_site, museum, ruins |

```
Q22: "Wine lover's Rome. Best enotecas, wine bars, day trips to vineyards"
```
| Extracted | Value |
|-----------|-------|
| vibes | foodie |
| preferences | wine_bars, wine_tasting |

---

### 9. Time Constrained

```
Q23: "Only 48 hours in Rome. Maximize my time!"
```
| Extracted | Value |
|-----------|-------|
| duration | 2 days |
| pacing | fast |
| preferences | must_see, efficient |

```
Q24: "Long layover - 8 hours. What can I realistically see?"
```
| Extracted | Value |
|-----------|-------|
| duration | 8 hours |
| pacing | fast |
| constraints | near_airport_accessible |

```
Q25: "One perfect day in Rome. If I could only have 24 hours"
```
| Extracted | Value |
|-----------|-------|
| duration | 1 day |
| pacing | moderate |
| preferences | must_see, highlights |

---

### 10. Seasonal & Weather

```
Q26: "Visiting in August. How to beat the heat?"
```
| Extracted | Value |
|-----------|-------|
| month | August |
| constraints | avoid_heat, indoor_activities, early_morning |
| timing_preference | morning, evening |

```
Q27: "Christmas in Rome. Festive markets and winter activities"
```
| Extracted | Value |
|-----------|-------|
| month | December |
| vibes | cultural, shopping, romantic |
| preferences | christmas_markets, winter_activities |

```
Q28: "Rainy day plan. What if weather doesn't cooperate?"
```
| Extracted | Value |
|-----------|-------|
| constraints | indoor_only, rain_suitable |

```
Q29: "Best time for outdoor dining and rooftop bars"
```
| Extracted | Value |
|-----------|-------|
| preferences | outdoor_seating, rooftop |
| season | summer (recommended) |

---

### 11. Dietary & Restrictions

```
Q30: "Vegan couple. Where can we actually eat well?"
```
| Extracted | Value |
|-----------|-------|
| dietary_restrictions | vegan |
| vibes | foodie |

```
Q31: "Gluten-free traveler. Best restaurants with real options"
```
| Extracted | Value |
|-----------|-------|
| dietary_restrictions | gluten_free |

```
Q32: "Halal food options in Rome. Recommendations?"
```
| Extracted | Value |
|-----------|-------|
| dietary_restrictions | halal |

---

### 12. Local Experience

```
Q33: "Skip the tourist traps. Where do Romans actually go?"
```
| Extracted | Value |
|-----------|-------|
| preferences | local_favorite, hidden_gem |
| anti_preferences | tourist_trap |

```
Q34: "Trastevere deep dive. Want to really know the neighborhood"
```
| Extracted | Value |
|-----------|-------|
| neighborhood_focus | Trastevere |
| vibes | foodie, cultural |

```
Q35: "Sunday in Rome like a local"
```
| Extracted | Value |
|-----------|-------|
| day_specific | Sunday |
| preferences | local_authentic |
| constraints | check_sunday_closures |

---

## Query Complexity Levels

### Level 1: Simple (Single Intent)
- "3-day Rome itinerary"
- "Best restaurants in Rome"
- "Rome for couples"

### Level 2: Moderate (Multiple Constraints)
- "Family trip with kids in summer, need AC"
- "Budget honeymoon, romantic but affordable"
- "Solo foodie, 5 days, avoid crowds"

### Level 3: Complex (Multiple Personas + Constraints)
- "Multi-gen trip: grandparents need wheelchairs, kids aged 5-10, parents want romantic dinner one night"
- "First 2 days cultural, last 2 days relaxation, medium budget"
- "Photographer by day, foodie by night, early riser"

---

## System Response Format

For each query, the system should return:

```json
{
  "parsed_intent": {
    "group_type": "family",
    "vibes": ["cultural", "relaxation"],
    "pacing": "moderate",
    "duration_days": 4,
    "budget_level": 3,
    "season": "summer",
    "constraints": ["kid_friendly", "avoid_heat"]
  },
  "clarifying_questions": [
    "What ages are your kids?",
    "Do you need wheelchair accessibility?"
  ],
  "itinerary_preview": {
    "day_1_theme": "Ancient Rome Highlights",
    "highlights": ["Colosseum", "Roman Forum"],
    "estimated_cost": "€150"
  }
}
```

---

## Parameter Extraction Rules

| User Says | Extract As |
|-----------|------------|
| "honeymoon", "anniversary", "romantic" | group_type: couple/honeymoon, vibe: romantic |
| "kids", "children", "family" | group_type: family, has_kids: true |
| "parents", "grandparents", "elderly" | has_seniors: true |
| "solo", "alone", "by myself" | group_type: solo |
| "friends", "group", "girls trip", "boys trip" | group_type: friends |
| "slow", "relaxed", "take our time" | pacing: slow |
| "see everything", "maximize", "efficient" | pacing: fast |
| "budget", "cheap", "affordable" | budget_level: 1-2 |
| "luxury", "best", "splurge" | budget_level: 5 |
| "instagram", "photos", "photography" | vibe: photography |
| "food", "eat", "restaurants", "cuisine" | vibe: foodie |
| "history", "museums", "art", "culture" | vibe: cultural |
| "nightlife", "bars", "clubs", "party" | vibe: nightlife |
| "wheelchair", "accessible", "mobility" | constraint: wheelchair_accessible |
| "vegetarian", "vegan", "gluten-free" | dietary_restriction: [type] |
| "August", "summer", "hot" | season: summer, constraint: avoid_heat |
| "December", "Christmas", "winter" | season: winter |
