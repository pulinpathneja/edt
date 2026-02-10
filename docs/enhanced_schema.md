# Enhanced Attribute Schema for Cities and POIs

## City-Level Attributes

### Core City Information
```sql
CREATE TABLE cities (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(3),

    -- Geographic
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    timezone VARCHAR(50),

    -- Travel Context
    primary_language VARCHAR(50),
    secondary_languages TEXT[],
    currency_code VARCHAR(3),
    avg_daily_budget_budget DECIMAL(10,2),      -- Budget traveler
    avg_daily_budget_midrange DECIMAL(10,2),    -- Mid-range
    avg_daily_budget_luxury DECIMAL(10,2),      -- Luxury

    -- Logistics
    has_metro BOOLEAN DEFAULT false,
    has_tram BOOLEAN DEFAULT false,
    has_bus BOOLEAN DEFAULT true,
    has_bike_share BOOLEAN DEFAULT false,
    is_walkable BOOLEAN DEFAULT true,
    uber_available BOOLEAN DEFAULT false,

    -- Best Times
    peak_season_months INT[],           -- [6,7,8] for summer
    shoulder_season_months INT[],       -- [4,5,9,10]
    off_season_months INT[],            -- [11,12,1,2,3]

    -- Safety & Practical
    safety_score DECIMAL(3,2),          -- 0-1 scale
    tourist_friendliness DECIMAL(3,2),
    english_proficiency DECIMAL(3,2),

    -- Metadata
    wikipedia_url TEXT,
    official_tourism_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Neighborhoods
```sql
CREATE TABLE neighborhoods (
    id UUID PRIMARY KEY,
    city_id UUID REFERENCES cities(id),
    name VARCHAR(100) NOT NULL,
    local_name VARCHAR(100),            -- Local language name

    -- Geographic
    latitude DECIMAL(10, 8),            -- Center point
    longitude DECIMAL(11, 8),
    boundary_geojson JSONB,             -- Polygon boundary

    -- Character
    vibe_tags TEXT[],                   -- ['hip', 'historic', 'foodie', 'nightlife']
    description TEXT,

    -- Practical
    safety_day DECIMAL(3,2),
    safety_night DECIMAL(3,2),
    walkability_score DECIMAL(3,2),
    transit_accessibility DECIMAL(3,2),

    -- Recommendations
    best_for TEXT[],                    -- ['couples', 'foodies', 'budget']
    avoid_for TEXT[],                   -- ['families_with_kids', 'seniors']
    best_time_of_day VARCHAR(20),       -- 'evening', 'morning', 'any'

    -- Density
    poi_density INT,                    -- Number of POIs
    restaurant_density INT,
    hotel_density INT
);
```

### City Events & Seasons
```sql
CREATE TABLE city_events (
    id UUID PRIMARY KEY,
    city_id UUID REFERENCES cities(id),
    name VARCHAR(200),
    event_type VARCHAR(50),             -- festival, holiday, sporting, cultural

    -- Timing
    start_date DATE,
    end_date DATE,
    is_recurring BOOLEAN DEFAULT false,
    recurrence_pattern VARCHAR(50),     -- 'annual', 'monthly', etc.

    -- Impact
    crowd_impact INT,                   -- 1-5 how much it affects crowds
    price_impact INT,                   -- 1-5 how much prices increase

    -- Relevance
    relevant_for TEXT[],                -- ['cultural', 'foodie', 'nightlife']

    description TEXT
);
```

---

## POI-Level Attributes (Enhanced)

### Core POI (Extended)
```sql
-- Additional columns for pois table
ALTER TABLE pois ADD COLUMN IF NOT EXISTS (
    -- Naming
    local_name VARCHAR(255),            -- Name in local language
    alternate_names TEXT[],             -- Other common names

    -- Geographic Context
    neighborhood_id UUID REFERENCES neighborhoods(id),
    nearest_metro_station VARCHAR(100),
    metro_distance_meters INT,

    -- Classification (Extended)
    category_primary VARCHAR(50),       -- Main category
    category_secondary VARCHAR(50),     -- Secondary category
    tags TEXT[],                        -- Flexible tagging
    cuisine_types TEXT[],               -- For restaurants

    -- Timing (Extended)
    opening_hours JSONB,                -- Structured hours
    best_visit_duration_min INT,
    best_visit_duration_max INT,
    last_entry_before_close_minutes INT,
    closed_days TEXT[],                 -- ['monday', 'tuesday']

    -- Booking & Access
    booking_url TEXT,
    booking_required_level VARCHAR(20), -- 'required', 'recommended', 'not_needed'
    skip_the_line_available BOOLEAN,
    guided_tour_available BOOLEAN,
    audio_guide_available BOOLEAN,
    free_entry_times TEXT,              -- "First Sunday of month"

    -- Pricing (Extended)
    price_adult DECIMAL(10,2),
    price_child DECIMAL(10,2),
    price_senior DECIMAL(10,2),
    price_student DECIMAL(10,2),
    free_under_age INT,

    -- Quality Signals
    google_rating DECIMAL(2,1),
    google_review_count INT,
    tripadvisor_rating DECIMAL(2,1),
    tripadvisor_review_count INT,
    michelin_stars INT,                 -- For restaurants

    -- Content
    short_description VARCHAR(280),     -- Tweet-length
    long_description TEXT,
    highlights TEXT[],                  -- Key things to see/do
    tips TEXT[],                        -- Insider tips

    -- Media
    primary_image_url TEXT,
    image_urls TEXT[],
    video_url TEXT
);
```

### POI Relationships (For Knowledge Graph)
```sql
CREATE TABLE poi_relationships (
    id UUID PRIMARY KEY,
    source_poi_id UUID REFERENCES pois(id),
    target_poi_id UUID REFERENCES pois(id),
    relationship_type VARCHAR(50),      -- See types below

    -- Metadata
    strength DECIMAL(3,2),              -- 0-1 how strong the relationship
    bidirectional BOOLEAN DEFAULT false,
    description TEXT,

    -- For distance-based relationships
    distance_meters INT,
    walking_time_minutes INT,

    UNIQUE(source_poi_id, target_poi_id, relationship_type)
);

-- Relationship Types:
-- 'near_to'           - Physical proximity
-- 'same_neighborhood' - In same area
-- 'same_theme'        - Thematic connection (both Renaissance art)
-- 'pairs_well_with'   - Good to combine (museum + nearby cafe)
-- 'alternative_to'    - Similar experience (if one is crowded)
-- 'part_of'           - Parent-child (Vatican Museums contains Sistine Chapel)
-- 'historical_connection' - Historical link
-- 'view_of'           - Has view of another POI
-- 'on_route_to'       - Commonly visited on way to
```

### POI Crowd Patterns
```sql
CREATE TABLE poi_crowd_patterns (
    poi_id UUID REFERENCES pois(id),
    day_of_week INT,                    -- 0=Monday, 6=Sunday
    hour_of_day INT,                    -- 0-23

    crowd_level DECIMAL(3,2),           -- 0-1 normalized
    wait_time_minutes INT,              -- Expected wait

    -- Seasonal variation
    season VARCHAR(20),                 -- 'peak', 'shoulder', 'off'

    PRIMARY KEY (poi_id, day_of_week, hour_of_day, season)
);
```

### POI Accessibility Details
```sql
CREATE TABLE poi_accessibility (
    poi_id UUID REFERENCES pois(id) PRIMARY KEY,

    -- Mobility
    wheelchair_accessible BOOLEAN,
    wheelchair_rental_available BOOLEAN,
    elevator_available BOOLEAN,
    ramps_available BOOLEAN,
    accessible_parking BOOLEAN,
    accessible_restroom BOOLEAN,

    -- Sensory
    braille_available BOOLEAN,
    audio_description BOOLEAN,
    sign_language_tours BOOLEAN,
    large_print_available BOOLEAN,
    quiet_hours_available BOOLEAN,      -- For sensory sensitivities

    -- Family
    stroller_accessible BOOLEAN,
    stroller_rental BOOLEAN,
    baby_changing_facilities BOOLEAN,
    kids_menu_available BOOLEAN,        -- For restaurants
    highchair_available BOOLEAN,
    play_area BOOLEAN,

    -- Pet
    pets_allowed BOOLEAN,
    pets_allowed_outside_only BOOLEAN,
    water_bowls_available BOOLEAN,

    -- Notes
    accessibility_notes TEXT
);
```

### Restaurant-Specific Attributes
```sql
CREATE TABLE restaurant_details (
    poi_id UUID REFERENCES pois(id) PRIMARY KEY,

    -- Cuisine
    cuisine_primary VARCHAR(50),
    cuisine_secondary VARCHAR(50),
    cuisine_tags TEXT[],                -- ['roman', 'seafood', 'vegetarian-friendly']

    -- Dining Style
    dining_style VARCHAR(50),           -- 'fine_dining', 'casual', 'fast_casual', 'street_food'
    ambiance TEXT[],                    -- ['romantic', 'lively', 'quiet']
    dress_code VARCHAR(50),             -- 'casual', 'smart_casual', 'formal'

    -- Practical
    reservation_required BOOLEAN,
    reservation_difficulty VARCHAR(20), -- 'easy', 'moderate', 'hard', 'very_hard'
    walk_ins_accepted BOOLEAN,
    average_wait_minutes INT,

    -- Pricing
    price_range VARCHAR(20),            -- '$', '$$', '$$$', '$$$$'
    avg_price_lunch DECIMAL(10,2),
    avg_price_dinner DECIMAL(10,2),
    tasting_menu_price DECIMAL(10,2),

    -- Features
    outdoor_seating BOOLEAN,
    private_dining BOOLEAN,
    bar_area BOOLEAN,
    wine_list_notable BOOLEAN,
    cocktail_menu BOOLEAN,

    -- Dietary
    vegetarian_options BOOLEAN,
    vegan_options BOOLEAN,
    gluten_free_options BOOLEAN,
    halal_options BOOLEAN,
    kosher_options BOOLEAN,

    -- Quality
    michelin_stars INT,
    michelin_bib_gourmand BOOLEAN,
    local_favorite BOOLEAN,
    tourist_trap_risk BOOLEAN,

    -- Signature
    signature_dishes TEXT[],
    must_try_items TEXT[]
);
```

---

## Knowledge Graph Edges (Conceptual)

```
POI ──[LOCATED_IN]──> Neighborhood
POI ──[IN_CITY]──> City
POI ──[NEAR_TO]──> POI (distance < 500m)
POI ──[PAIRS_WITH]──> POI (good combinations)
POI ──[SAME_THEME]──> POI (thematic grouping)
POI ──[ALTERNATIVE_TO]──> POI (similar experience)
POI ──[HAS_VIEW_OF]──> POI
POI ──[PART_OF]──> POI (parent-child)

Neighborhood ──[ADJACENT_TO]──> Neighborhood
Neighborhood ──[IN_CITY]──> City

City ──[IN_COUNTRY]──> Country
City ──[SIMILAR_TO]──> City (for "if you liked X, try Y")
```

---

## Recommended Data Sources by Attribute

| Attribute Category | Primary Source | Enrichment Source |
|-------------------|----------------|-------------------|
| Location, Hours | Overture Maps | Google Places |
| Ratings, Reviews | Google Places | TripAdvisor API |
| Accessibility | Manual curation | AccessibleGO API |
| Crowd Patterns | Google Popular Times | Manual observation |
| Relationships | Manual curation | Graph algorithms |
| Pricing | Google Places | Manual verification |
| Restaurant Details | Yelp Fusion | TheFork API |
| Events | Manual + APIs | Eventbrite, local sources |
