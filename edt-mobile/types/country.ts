/** Mirrors app/schemas/country.py */

export interface CityInfo {
  id: string;
  name: string;
  country: string;
  min_days: number;
  max_days: number;
  ideal_days: number;
  highlights: string[];
  vibes: string[];
  best_for: string[];
  travel_time_from?: Record<string, number>;
}

export interface CountryInfo {
  id: string;
  name: string;
  flag?: string; // Not in API — added client-side
  currency: string;
  languages: string[];
  cities: CityInfo[];
  popular_routes: string[][];
}

export interface CountryListResponse {
  countries: CountryInfo[];
  total: number;
}

// ============== City Allocation ==============

export interface CityAllocation {
  city_id: string;
  city_name: string;
  days: number;
  arrival_from?: string | null;
  travel_time_minutes?: number | null;
  highlights: string[];
}

export interface CityAllocationOption {
  option_id: number | string;
  option_name: string;
  description: string;
  cities: CityAllocation[];
  total_days: number;
  total_travel_time_minutes: number;
  match_score: number; // 0-1
  pros: string[];
  cons: string[];
}

export interface CityAllocationRequest {
  country: string;
  total_days: number;
  start_date?: string;
  end_date?: string;
  group_type: string;
  vibes: string[];
  budget_level?: number;
  pacing?: string;
  must_include_cities?: string[];
  exclude_cities?: string[];
  start_city?: string;
  end_city?: string;
  prefer_minimal_travel?: boolean;
  prefer_variety?: boolean;
}

export interface CityAllocationResponse {
  country: string;
  country_name: string;
  total_days: number;
  options: CityAllocationOption[];
  recommended_option: number;
}

// ============== Country Itinerary ==============

export interface CountryItineraryRequest {
  country: string;
  selected_allocation?: CityAllocationOption;
  allocation_option_id?: string;
  start_date: string;
  end_date: string;
  group_type: string;
  group_size?: number;
  has_kids?: boolean;
  kids_ages?: number[];
  has_seniors?: boolean;
  vibes: string[];
  budget_level?: number;
  pacing?: string;
}

export interface InterCityTravelInfo {
  from_city: string;
  to_city: string;
  duration_minutes?: number | null;
  mode: string;
  notes?: string | null;
}

export interface CityItinerarySummary {
  city_id: string;
  city_name: string;
  days: number;
  start_date: string;
  end_date: string;
  highlights: string[];
  estimated_cost?: number | null;
  itinerary_id?: string | null;
  day_itineraries?: DayItinerary[];
  travel_to_next?: InterCityTravelInfo | null;
}

export interface InterCityTravel {
  from_city: string;
  to_city: string;
  travel_time_minutes: number | null;
  date: string;
  mode: string;
}

export interface CountryItineraryResponse {
  id: string;
  country: string;
  country_name: string;
  total_days: number;
  start_date: string;
  end_date: string;
  group_type: string;
  vibes: string[];
  budget_level: number;
  pacing: string;
  city_itineraries: CityItinerarySummary[];
  inter_city_travel: InterCityTravel[];
  total_estimated_cost?: number | null;
  packing_suggestions: string[];
  travel_tips: string[];
}

// ============== Activity Types (for itinerary display) ==============

export type ActivityType = 'hotel' | 'meal' | 'transport' | 'sightseeing' | 'shopping';

export interface ActivityData {
  type: ActivityType;
  title: string;
  time: string;
  description?: string;
  image?: string;
}

export interface TransitInfo {
  mode: 'walk' | 'train' | 'car' | 'bus';
  duration: string;
  note?: string;
}

export interface ActivityEntry {
  id: string;
  data: ActivityData;
  status?: 'completed' | 'current' | 'upcoming';
  transit?: TransitInfo;
}

export interface DayItinerary {
  dayNumber: number;
  date: string;
  cityName: string;
  title: string;
  activities: ActivityEntry[];
}
