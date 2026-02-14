# City Intelligence - Travel Resources Guide

## Overview
This document contains curated sources for gathering city intelligence including local insights, challenges, family-friendly recommendations, walking tours, and events.

---

## 1. Reddit Subreddits

### General Travel Communities
| Subreddit | Members | Best For |
|-----------|---------|----------|
| r/travel | 7M+ | General travel advice, destination reviews |
| r/solotravel | 1.8M+ | Solo traveler tips, safety info |
| r/shoestring | 1M+ | Budget travel, cheap eats |
| r/TravelHacks | 500K+ | Travel tips and tricks |
| r/backpacking | 400K+ | Adventure travel, hostels |

### City-Specific Subreddits (Pattern)
```
r/{cityname}           - Main city subreddit (e.g., r/toronto, r/london)
r/Ask{cityname}        - Q&A format (e.g., r/askTO, r/AskNYC, r/AskSF)
r/{cityname}food       - Food recommendations (e.g., r/FoodNYC)
r/visit{cityname}      - Tourist-focused (e.g., r/visitseattle)
```

### Search Queries for Reddit
```
site:reddit.com "{city}" things to do
site:reddit.com "{city}" hidden gems
site:reddit.com "{city}" avoid tourist traps
site:reddit.com "{city}" with kids family friendly
site:reddit.com "{city}" local tips
site:reddit.com "{city}" best neighborhoods
site:reddit.com "{city}" safety concerns
```

---

## 2. Travel Blogs by Category

### Local Experience Blogs
| Blog | URL | Focus |
|------|-----|-------|
| Spotted by Locals | spottedbylocals.com | Local recommendations only |
| Atlas Obscura | atlasobscura.com | Hidden gems, unusual places |
| Lonely Planet | lonelyplanet.com | Comprehensive guides |
| Rick Steves | ricksteves.com | European travel, walking tours |
| Culture Trip | theculturetrip.com | Culture, food, experiences |

### Food & Culinary
| Blog | URL | Focus |
|------|-----|-------|
| Mark Wiens | migrationology.com | Street food, authentic cuisine |
| Eater City Guides | eater.com | Restaurant recommendations |
| Serious Eats | seriouseats.com | Food destinations |
| Legal Nomads | legalnomads.com | Food history & culture |

### Family & Kids-Friendly
| Blog | URL | Focus |
|------|-----|-------|
| Mommy Poppins | mommypoppins.com | Family activities, kid-friendly |
| Trekaroo | trekaroo.com | Family travel reviews |
| Travel Mad Mum | travelmadmum.com | Traveling with children |
| Y Travel Blog | ytravelblog.com | Family adventures |
| Have Baby Will Travel | havebabywilltravel.com | Baby/toddler travel |

### Budget Travel
| Blog | URL | Focus |
|------|-----|-------|
| Nomadic Matt | nomadicmatt.com | Budget tips, backpacking |
| The Broke Backpacker | thebrokebackpacker.com | Ultra-budget travel |
| Budget Your Trip | budgetyourtrip.com | Cost breakdowns |

### Adventure & Outdoor
| Blog | URL | Focus |
|------|-----|-------|
| Expert Vagabond | expertvagabond.com | Adventure travel |
| The Planet D | theplanetd.com | Adventure couple travel |
| Adventurous Kate | adventurouskate.com | Solo female adventure |

---

## 3. Walking Tours & Events Platforms

### Walking Tour Platforms
| Platform | URL | API Available | Notes |
|----------|-----|---------------|-------|
| Viator | viator.com | Yes | TripAdvisor company, huge inventory |
| GetYourGuide | getyourguide.com | Yes | European focus, quality tours |
| GuruWalk | guruwalk.com | Limited | Free walking tours, tip-based |
| Free Tour Community | freetour.com | No | Free walking tours globally |
| Airbnb Experiences | airbnb.com/experiences | Yes | Local-hosted experiences |
| WithLocals | withlocals.com | No | Private tours with locals |

### Events Platforms
| Platform | URL | API Available | Notes |
|----------|-----|---------------|-------|
| Eventbrite | eventbrite.com | Yes | All event types |
| Meetup | meetup.com | Yes | Local group events |
| Facebook Events | facebook.com/events | Limited | Social events |
| Time Out | timeout.com | No | Curated city events |
| Fever | feverup.com | No | Unique experiences |
| Resident Advisor | ra.co | Limited | Music/nightlife events |

---

## 4. API Integration Details

### Viator API
```
Base URL: https://api.viator.com/partner
Authentication: API Key
Endpoints:
  - /products/search - Search tours by destination
  - /products/{code} - Get product details
  - /taxonomy/destinations - List destinations
Rate Limit: 100 requests/minute
```

### GetYourGuide Partner API
```
Base URL: https://api.getyourguide.com/1
Authentication: OAuth2
Endpoints:
  - /tours - Search tours
  - /locations - Get locations
  - /categories - Tour categories
```

### Eventbrite API
```
Base URL: https://www.eventbriteapi.com/v3
Authentication: OAuth2
Endpoints:
  - /events/search - Search events
  - /venues - Venue details
  - /categories - Event categories
```

### Reddit API
```
Base URL: https://oauth.reddit.com
Authentication: OAuth2
Endpoints:
  - /r/{subreddit}/search - Search subreddit
  - /r/{subreddit}/top - Top posts
  - /r/{subreddit}/hot - Hot posts
Rate Limit: 60 requests/minute
```

---

## 5. Search Query Templates

### Pros & Cons
```
"{city} pros and cons living"
"{city} honest review tourist"
"{city} overrated underrated"
"{city} worth visiting why"
```

### Safety & Challenges
```
"{city} safety concerns 2024"
"{city} areas to avoid"
"{city} tourist scams"
"{city} crime neighborhoods"
```

### Family-Friendly
```
"{city} with kids things to do"
"{city} family friendly activities"
"{city} best playgrounds parks"
"{city} kid friendly restaurants"
"{city} stroller friendly"
```

### Hidden Gems
```
"{city} hidden gems locals"
"{city} off the beaten path"
"{city} secret spots"
"{city} underrated places"
```

### Food & Dining
```
"{city} best local food"
"{city} where locals eat"
"{city} street food"
"{city} food markets"
```

### Walking & Neighborhoods
```
"{city} best walking neighborhoods"
"{city} walkable areas"
"{city} self guided walking tour"
"{city} free walking tour"
```

---

## 6. Persona-Based Search Filters

### Solo Traveler
- Safety information
- Hostels and social stays
- Solo-friendly restaurants
- Group tours and meetups

### Couple / Romantic
- Romantic restaurants
- Scenic viewpoints
- Couples activities
- Date night spots

### Family with Kids
- Kid-friendly attractions
- Family restaurants
- Parks and playgrounds
- Stroller accessibility

### Budget Traveler
- Free attractions
- Cheap eats
- Budget accommodation
- Happy hours

### Luxury Traveler
- Fine dining
- Luxury hotels
- VIP experiences
- Private tours

### Adventure Seeker
- Outdoor activities
- Adventure sports
- Hiking trails
- Extreme experiences

### Food Enthusiast
- Food tours
- Local markets
- Cooking classes
- Restaurant recommendations

### Culture & History Buff
- Museums
- Historical sites
- Walking tours
- Cultural events

---

## 7. Data Collection Frequency

| Source Type | Refresh Frequency | Reason |
|-------------|-------------------|--------|
| Reddit Posts | Weekly | New discussions, changing opinions |
| Blog Articles | Monthly | Less frequent updates |
| Events | Daily | Time-sensitive |
| Walking Tours | Weekly | Seasonal availability |
| Reviews | Weekly | Fresh perspectives |

---

## 8. Quality Indicators

### Reddit Post Quality
- Upvotes > 100
- Comments > 20
- Recent (< 2 years old)
- Detailed responses

### Blog Quality
- Published date recent
- Author credibility
- Specific recommendations
- Local knowledge evident

### Tour Quality (Viator/GYG)
- Rating > 4.5
- Reviews > 50
- Recent reviews
- Detailed description

---
