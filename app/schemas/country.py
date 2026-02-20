"""
Country-level itinerary schemas.
Supports multi-city trip planning within a country.
"""
from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Optional, List, Union
from datetime import date, timedelta
from decimal import Decimal


class CityInfo(BaseModel):
    """Basic city information for country-level planning."""
    id: str  # city key (e.g., "rome", "florence")
    name: str
    country: str
    min_days: int = 1  # Minimum recommended days
    max_days: int = 7  # Maximum recommended days
    ideal_days: int = 3  # Ideal number of days
    highlights: List[str] = []  # Top attractions
    vibes: List[str] = []  # City vibes
    best_for: List[str] = []  # Best for what type of travelers
    travel_time_from: dict = {}  # Travel time from other cities in minutes


class CountryInfo(BaseModel):
    """Country information with cities."""
    id: str  # country key (e.g., "italy")
    name: str
    currency: str
    languages: List[str] = []
    cities: List[CityInfo] = []
    popular_routes: List[List[str]] = []  # Popular multi-city routes


class CountryListResponse(BaseModel):
    """Response for list of countries."""
    countries: List[CountryInfo]
    total: int


# ============== City Allocation ==============

class CityAllocation(BaseModel):
    """Allocation of days to a city."""
    city_id: str
    city_name: str
    days: int
    arrival_from: Optional[str] = None  # Previous city
    travel_time_minutes: Optional[int] = None
    highlights: List[str] = []


class CityAllocationOption(BaseModel):
    """One option for city allocation."""
    option_id: Union[int, str]
    option_name: str = ""  # e.g., "Classic Italy", "Art Lover's Tour"
    description: str = ""
    cities: List[CityAllocation] = []
    total_days: int = 0
    total_travel_time_minutes: int = 0
    match_score: float = Field(default=0.0, ge=0, le=1)  # How well it matches preferences
    pros: List[str] = []
    cons: List[str] = []


class CityAllocationRequest(BaseModel):
    """Request for city allocation options."""
    country: str = Field(validation_alias=AliasChoices('country', 'country_id'))
    total_days: int = Field(ge=2, le=30)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # Preferences
    group_type: str  # family, couple, solo, friends
    vibes: List[str] = []  # cultural, romantic, adventure, etc.
    budget_level: Optional[int] = None
    pacing: str = "moderate"  # slow, moderate, fast

    # Optional constraints
    must_include_cities: Optional[List[str]] = None  # Cities that must be included
    exclude_cities: Optional[List[str]] = None  # Cities to avoid
    start_city: Optional[str] = None  # Must start in this city
    end_city: Optional[str] = None  # Must end in this city

    # Travel preferences
    prefer_minimal_travel: bool = False  # Prefer fewer cities, more depth
    prefer_variety: bool = False  # Prefer more cities, less depth

    @model_validator(mode='after')
    def fill_dates(self):
        """Auto-fill start_date/end_date from total_days if not provided."""
        if self.start_date is None:
            self.start_date = date.today()
        if self.end_date is None:
            self.end_date = self.start_date + timedelta(days=self.total_days - 1)
        return self


class CityAllocationResponse(BaseModel):
    """Response with city allocation options."""
    country: str
    country_name: str
    total_days: int
    options: List[CityAllocationOption]
    recommended_option: int  # Index of recommended option


# ============== Country Itinerary ==============

class CountryItineraryRequest(BaseModel):
    """Request to generate a country-level itinerary."""
    country: str = Field(validation_alias=AliasChoices('country', 'country_id'))
    selected_allocation: Optional[CityAllocationOption] = None
    allocation_option_id: Optional[str] = None

    # Trip details
    start_date: date
    end_date: date
    group_type: str
    group_size: int = 1
    has_kids: bool = False
    kids_ages: Optional[List[int]] = None
    has_seniors: bool = False

    # Preferences
    vibes: List[str] = []
    budget_level: int = Field(default=3, ge=1, le=5)
    pacing: str = "moderate"

    # Constraints
    mobility_constraints: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None


class TransitInfoSchema(BaseModel):
    """Transport between activities."""
    mode: str  # walk, train, bus, car
    duration: str  # e.g. "15 min"
    note: Optional[str] = None


class ActivityDataSchema(BaseModel):
    """Data for a single activity."""
    type: str  # hotel, meal, transport, sightseeing, shopping
    title: str
    time: str  # HH:MM
    description: Optional[str] = None
    image: Optional[str] = None


class ActivityEntrySchema(BaseModel):
    """One entry in the day timeline."""
    id: str
    data: ActivityDataSchema
    status: Optional[str] = "upcoming"  # completed, current, upcoming
    transit: Optional[TransitInfoSchema] = None


class DayItinerarySchema(BaseModel):
    """Full day itinerary with activities."""
    dayNumber: int
    date: str  # ISO date
    cityName: str
    title: str
    activities: List[ActivityEntrySchema] = []


class InterCityTravelSchema(BaseModel):
    """Travel info between cities."""
    from_city: str
    to_city: str
    duration_minutes: Optional[int] = None
    mode: str = "train"
    notes: Optional[str] = None


class CityItinerarySummary(BaseModel):
    """Summary of itinerary for one city."""
    city_id: str
    city_name: str
    days: int
    start_date: date
    end_date: date
    highlights: List[str]
    estimated_cost: Optional[Decimal] = None
    itinerary_id: Optional[str] = None  # Link to detailed itinerary
    day_itineraries: List[DayItinerarySchema] = []
    travel_to_next: Optional[InterCityTravelSchema] = None


class CountryItineraryResponse(BaseModel):
    """Response for country-level itinerary."""
    id: str
    country: str
    country_name: str
    total_days: int
    start_date: date
    end_date: date

    # Trip preferences (echoed back for Flutter)
    group_type: str = ""
    vibes: List[str] = []
    budget_level: int = 3
    pacing: str = "moderate"

    # City itineraries
    city_itineraries: List[CityItinerarySummary]

    # Travel logistics
    inter_city_travel: List[dict] = []  # Travel between cities

    # Summary
    total_estimated_cost: Optional[Decimal] = None
    packing_suggestions: List[str] = []
    travel_tips: List[str] = []
