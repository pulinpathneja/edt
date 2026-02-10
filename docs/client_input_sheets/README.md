# Client Input Sheets for POI Data Collection

## Overview

These CSV templates are designed for collecting POI (Point of Interest) data for the travel itinerary system. Share these with your client or data team to gather structured information.

---

## Sheet Summary

| # | Sheet Name | Purpose | Priority |
|---|------------|---------|----------|
| 00 | Reference Values | Dropdown options & valid values | Reference |
| 01 | POI Data | Core POI information (name, location, category) | **Required** |
| 02 | Persona Scores | Group & vibe suitability scores + pros/cons | **Required** |
| 03 | Seasonality | Season scores & weather attributes | **Required** |
| 04 | Accessibility | Wheelchair, family, physical requirements | High |
| 05 | Instagram/Photography | Photo spots, golden hour, restrictions | High |
| 06 | Crowd & Atmosphere | Crowd levels, quiet times, vibe descriptions | Medium |
| 07 | Dining Specific | Restaurant-only attributes (cuisine, dietary) | Medium |
| 08 | Itinerary Config | System configuration (pacing, timing) | Setup |

---

## How to Use

### Step 1: Start with Reference Values (00)
Review `00_reference_values.csv` to understand all valid dropdown options.

### Step 2: Fill Core POI Data (01)
For each POI, fill in:
- Unique ID (POI_001, POI_002, etc.)
- Name, description, coordinates
- Category, subcategory
- Duration, cost, timing

### Step 3: Add Persona Scores (02)
For each POI, rate suitability (0.0 - 1.0):
- 8 Group Types: family, kids, couple, honeymoon, solo, friends, seniors, business
- 10 Vibes: cultural, foodie, romantic, adventure, relaxation, nightlife, shopping, nature, photography, wellness
- Add pros/cons for each major group

### Step 4: Add Seasonality (03)
For each POI:
- Season scores (spring, summer, fall, winter)
- Weather sensitivity (heat, rain, cold)
- Best/avoid months
- Seasonal notes

### Step 5: Complete Additional Sheets (04-07)
Based on POI type:
- Accessibility for all POIs
- Instagram for photogenic spots
- Dining details for restaurants only

---

## Scoring Guide

### Persona Scores (0.0 - 1.0)

| Score | Meaning | Example |
|-------|---------|---------|
| 0.9-1.0 | Perfect fit | Playground for kids |
| 0.7-0.8 | Great fit | Family-friendly museum |
| 0.5-0.6 | Neutral | Works for anyone |
| 0.3-0.4 | Not ideal | Noisy bar for seniors |
| 0.0-0.2 | Poor fit | Nightclub for families |

### Season Scores (0.0 - 1.0)

| Score | Meaning | Example |
|-------|---------|---------|
| 0.9-1.0 | Perfect season | Rooftop bar in summer |
| 0.7-0.8 | Great season | Gardens in spring |
| 0.5-0.6 | Acceptable | Indoor museum anytime |
| 0.3-0.4 | Not ideal | Outdoor cafe in winter |
| 0.0-0.2 | Avoid | Rooftop bar in December |

### Crowd Level (1-5)

| Level | Description |
|-------|-------------|
| 1 | Empty - you'll likely be alone |
| 2 | Quiet - few people, peaceful |
| 3 | Moderate - noticeable but comfortable |
| 4 | Busy - crowded but manageable |
| 5 | Very Crowded - expect queues |

### Physical Intensity (1-5)

| Level | Description |
|-------|-------------|
| 1 | Sedentary - sitting, minimal movement |
| 2 | Light - some walking, mostly flat |
| 3 | Moderate - significant walking, some stairs |
| 4 | Active - lots of walking, hills, stairs |
| 5 | Strenuous - hiking, climbing, physical activity |

---

## Tips for Data Collection

### General
- Use semicolon (;) to separate multiple values
- Boolean fields: TRUE or FALSE (all caps)
- Leave blank if unknown (don't guess)
- Add notes for context

### Pros/Cons
- Be specific and actionable
- Focus on differentiators
- Think from traveler's perspective
- Example: "Kids under 5 may get bored" vs "Not for kids"

### Photography
- Visit at different times to assess
- Note actual restrictions (signs, guards)
- Consider tripod/drone rules
- Best photo spots should be specific locations

### Seasonality
- Consider local holidays and events
- Factor in tourist seasons
- Note any closures or reduced hours
- Weather impact on experience

---

## Minimum Data Requirements

### Per City (Minimum)
- 15+ Attractions
- 30+ Restaurants
- 10+ Activities
- 5+ Shopping
- 5+ Nightlife
- 4+ Neighborhoods covered

### Per POI (Required Fields)
- name, latitude, longitude
- category, subcategory
- description (50+ characters)
- 8 group scores
- 10 vibe scores
- 4 season scores
- typical_duration_minutes
- cost_level

---

## File Format

- Format: CSV (Comma Separated Values)
- Encoding: UTF-8
- Line endings: Unix (LF) or Windows (CRLF)
- Open with: Excel, Google Sheets, Numbers

---

## Questions?

Contact the data team for clarification on any fields.
