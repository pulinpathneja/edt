import { create } from 'zustand';
import type {
  CountryInfo,
  CityAllocationOption,
  CityAllocationResponse,
  CountryItineraryResponse,
  DayItinerary,
  ActivityEntry,
} from '@/types';
import * as countryApi from '@/services/countryApi';

// ============== Mock Data ==============

const COUNTRY_FLAGS: Record<string, string> = {
  italy: '\u{1F1EE}\u{1F1F9}',
  france: '\u{1F1EB}\u{1F1F7}',
  spain: '\u{1F1EA}\u{1F1F8}',
  japan: '\u{1F1EF}\u{1F1F5}',
  united_kingdom: '\u{1F1EC}\u{1F1E7}',
};

export const MOCK_COUNTRIES: CountryInfo[] = [
  {
    id: 'italy', name: 'Italy', flag: '\u{1F1EE}\u{1F1F9}', currency: 'EUR', languages: ['Italian'],
    cities: [
      { id: 'rome', name: 'Rome', country: 'Italy', min_days: 2, max_days: 5, ideal_days: 3, highlights: ['Colosseum', 'Vatican', 'Trastevere'], vibes: ['cultural', 'foodie', 'historical'], best_for: ['couple', 'solo', 'family'] },
      { id: 'florence', name: 'Florence', country: 'Italy', min_days: 2, max_days: 4, ideal_days: 3, highlights: ['Uffizi', 'Duomo', 'Ponte Vecchio'], vibes: ['artsy', 'cultural', 'foodie'], best_for: ['couple', 'solo'] },
      { id: 'venice', name: 'Venice', country: 'Italy', min_days: 1, max_days: 3, ideal_days: 2, highlights: ['Grand Canal', "St. Mark's", 'Murano'], vibes: ['romantic', 'cultural'], best_for: ['couple'] },
      { id: 'milan', name: 'Milan', country: 'Italy', min_days: 1, max_days: 3, ideal_days: 2, highlights: ['Duomo', 'Last Supper', 'Fashion District'], vibes: ['shopping', 'cultural', 'foodie'], best_for: ['solo', 'friends'] },
    ],
    popular_routes: [['rome', 'florence', 'venice'], ['rome', 'florence']],
  },
  {
    id: 'france', name: 'France', flag: '\u{1F1EB}\u{1F1F7}', currency: 'EUR', languages: ['French'],
    cities: [
      { id: 'paris', name: 'Paris', country: 'France', min_days: 3, max_days: 6, ideal_days: 4, highlights: ['Eiffel Tower', 'Louvre', 'Montmartre'], vibes: ['romantic', 'cultural', 'foodie'], best_for: ['couple', 'solo'] },
      { id: 'nice', name: 'Nice', country: 'France', min_days: 2, max_days: 4, ideal_days: 2, highlights: ['Promenade', 'Old Town', 'Beach'], vibes: ['relaxation', 'nature'], best_for: ['couple', 'family'] },
      { id: 'lyon', name: 'Lyon', country: 'France', min_days: 1, max_days: 3, ideal_days: 2, highlights: ['Old Lyon', 'Gastronomy', 'Traboules'], vibes: ['foodie', 'cultural'], best_for: ['solo', 'friends'] },
      { id: 'bordeaux', name: 'Bordeaux', country: 'France', min_days: 1, max_days: 3, ideal_days: 2, highlights: ['Wine Region', 'Old Town', 'Cite du Vin'], vibes: ['foodie', 'relaxation'], best_for: ['couple', 'friends'] },
    ],
    popular_routes: [['paris', 'nice'], ['paris', 'lyon', 'nice']],
  },
  {
    id: 'spain', name: 'Spain', flag: '\u{1F1EA}\u{1F1F8}', currency: 'EUR', languages: ['Spanish'],
    cities: [
      { id: 'barcelona', name: 'Barcelona', country: 'Spain', min_days: 3, max_days: 5, ideal_days: 3, highlights: ['Sagrada Familia', 'Park Guell', 'La Rambla'], vibes: ['cultural', 'nightlife', 'foodie'], best_for: ['friends', 'couple'] },
      { id: 'madrid', name: 'Madrid', country: 'Spain', min_days: 2, max_days: 4, ideal_days: 3, highlights: ['Prado', 'Royal Palace', 'Retiro Park'], vibes: ['cultural', 'nightlife', 'foodie'], best_for: ['solo', 'friends'] },
      { id: 'seville', name: 'Seville', country: 'Spain', min_days: 2, max_days: 3, ideal_days: 2, highlights: ['Alcazar', 'Flamenco', 'Plaza de Espana'], vibes: ['cultural', 'romantic'], best_for: ['couple'] },
      { id: 'granada', name: 'Granada', country: 'Spain', min_days: 1, max_days: 3, ideal_days: 2, highlights: ['Alhambra', 'Albaicin', 'Tapas'], vibes: ['historical', 'foodie'], best_for: ['solo', 'couple'] },
    ],
    popular_routes: [['barcelona', 'madrid'], ['madrid', 'seville', 'granada']],
  },
  {
    id: 'japan', name: 'Japan', flag: '\u{1F1EF}\u{1F1F5}', currency: 'JPY', languages: ['Japanese'],
    cities: [
      { id: 'tokyo', name: 'Tokyo', country: 'Japan', min_days: 3, max_days: 6, ideal_days: 4, highlights: ['Shibuya', 'Senso-ji', 'Tsukiji'], vibes: ['cultural', 'foodie', 'shopping'], best_for: ['solo', 'friends'] },
      { id: 'kyoto', name: 'Kyoto', country: 'Japan', min_days: 2, max_days: 5, ideal_days: 3, highlights: ['Fushimi Inari', 'Bamboo Grove', 'Temples'], vibes: ['cultural', 'nature', 'historical'], best_for: ['solo', 'couple'] },
      { id: 'osaka', name: 'Osaka', country: 'Japan', min_days: 2, max_days: 4, ideal_days: 2, highlights: ['Dotonbori', 'Street Food', 'Castle'], vibes: ['foodie', 'nightlife'], best_for: ['friends', 'solo'] },
    ],
    popular_routes: [['tokyo', 'kyoto', 'osaka']],
  },
  {
    id: 'united_kingdom', name: 'United Kingdom', flag: '\u{1F1EC}\u{1F1E7}', currency: 'GBP', languages: ['English'],
    cities: [
      { id: 'london', name: 'London', country: 'UK', min_days: 3, max_days: 6, ideal_days: 4, highlights: ['Big Ben', 'British Museum', 'Tower'], vibes: ['cultural', 'historical', 'shopping'], best_for: ['solo', 'family'] },
      { id: 'edinburgh', name: 'Edinburgh', country: 'UK', min_days: 2, max_days: 4, ideal_days: 3, highlights: ['Castle', 'Royal Mile', "Arthur's Seat"], vibes: ['historical', 'nature', 'cultural'], best_for: ['solo', 'couple'] },
    ],
    popular_routes: [['london', 'edinburgh']],
  },
];

function buildMockAllocations(countryId: string, totalDays: number): CityAllocationResponse {
  const country = MOCK_COUNTRIES.find((c) => c.id === countryId);
  const name = country?.name ?? countryId;
  const cities = country?.cities ?? [];

  const balanced = cities.slice(0, 3).map((c, i) => ({
    city_id: c.id,
    city_name: c.name,
    days: Math.max(1, Math.round(totalDays / Math.min(3, cities.length))),
    arrival_from: i > 0 ? cities[i - 1].name : null,
    travel_time_minutes: i > 0 ? 120 : null,
    highlights: c.highlights.slice(0, 2),
  }));

  const deepDive = cities.slice(0, 2).map((c, i) => ({
    city_id: c.id,
    city_name: c.name,
    days: Math.max(2, Math.round(totalDays / 2)),
    arrival_from: i > 0 ? cities[i - 1].name : null,
    travel_time_minutes: i > 0 ? 90 : null,
    highlights: c.highlights,
  }));

  return {
    country: countryId,
    country_name: name,
    total_days: totalDays,
    options: [
      {
        option_id: 1,
        option_name: 'Classic Route',
        description: `The classic ${name} experience covering the highlights`,
        cities: balanced,
        total_days: totalDays,
        total_travel_time_minutes: 240,
        match_score: 0.87,
        pros: ['See more cities', 'Diverse experiences', 'Popular route'],
        cons: ['More time in transit', 'Less depth per city'],
      },
      {
        option_id: 2,
        option_name: 'Deep Dive',
        description: `Fewer cities, more depth — immerse yourself`,
        cities: deepDive,
        total_days: totalDays,
        total_travel_time_minutes: 90,
        match_score: 0.82,
        pros: ['More relaxed pace', 'Deeper local experience'],
        cons: ['Fewer cities visited', 'May miss highlights'],
      },
    ],
    recommended_option: 0,
  };
}

function buildMockDayItineraries(
  cityName: string,
  days: number,
  startDate: string,
): DayItinerary[] {
  const result: DayItinerary[] = [];
  const base = new Date(startDate);

  for (let d = 0; d < days; d++) {
    const date = new Date(base);
    date.setDate(date.getDate() + d);
    const dateStr = date.toISOString().split('T')[0];

    const activities: ActivityEntry[] = [
      {
        id: `${cityName}-d${d + 1}-hotel`,
        data: { type: 'hotel', title: `Hotel in ${cityName}`, time: '08:00' },
        status: d === 0 ? 'current' : 'upcoming',
      },
      {
        id: `${cityName}-d${d + 1}-breakfast`,
        data: { type: 'meal', title: 'Breakfast', time: '08:30', description: `Local breakfast spot in ${cityName}` },
        status: 'upcoming',
        transit: { mode: 'walk', duration: '5 min' },
      },
      {
        id: `${cityName}-d${d + 1}-sight1`,
        data: { type: 'sightseeing', title: `${cityName} Highlight ${d + 1}`, time: '10:00', description: 'A must-see landmark' },
        status: 'upcoming',
        transit: { mode: 'walk', duration: '15 min' },
      },
      {
        id: `${cityName}-d${d + 1}-lunch`,
        data: { type: 'meal', title: 'Lunch', time: '13:00', description: 'Traditional local cuisine' },
        status: 'upcoming',
        transit: { mode: 'bus', duration: '10 min' },
      },
      {
        id: `${cityName}-d${d + 1}-sight2`,
        data: { type: 'sightseeing', title: `${cityName} Discovery ${d + 1}`, time: '15:00', description: 'Explore the neighborhood' },
        status: 'upcoming',
        transit: { mode: 'walk', duration: '20 min' },
      },
      {
        id: `${cityName}-d${d + 1}-dinner`,
        data: { type: 'meal', title: 'Dinner', time: '19:30', description: 'Evening dining experience' },
        status: 'upcoming',
        transit: { mode: 'walk', duration: '10 min' },
      },
    ];

    result.push({
      dayNumber: d + 1,
      date: dateStr,
      cityName,
      title: d === 0 ? `Arrival & First Impressions` : `Day ${d + 1} in ${cityName}`,
      activities,
    });
  }

  return result;
}

// ============== Store ==============

export interface CountryTripState {
  // Countries
  countries: CountryInfo[];
  isLoadingCountries: boolean;

  // Selection
  selectedCountry: CountryInfo | null;

  // Trip preferences
  startDate: string | null;
  endDate: string | null;
  groupType: string;
  groupSize: number;
  vibes: string[];
  budgetLevel: number;
  pacing: string;
  currentStep: number;

  // Allocations
  allocationResponse: CityAllocationResponse | null;
  selectedAllocationIndex: number | null;
  isLoadingAllocations: boolean;

  // Itinerary
  countryItinerary: CountryItineraryResponse | null;
  dayItineraries: DayItinerary[];
  isGenerating: boolean;
  error: string | null;

  // Computed
  totalDays: () => number;
  canProceedToAllocations: () => boolean;

  // Actions
  loadCountries: () => Promise<void>;
  selectCountry: (country: CountryInfo) => void;
  setDateRange: (start: string, end: string) => void;
  setGroupType: (type: string) => void;
  setGroupSize: (size: number) => void;
  toggleVibe: (vibe: string) => void;
  setBudgetLevel: (level: number) => void;
  setPacing: (pacing: string) => void;
  nextStep: () => void;
  previousStep: () => void;
  fetchAllocations: () => Promise<void>;
  selectAllocation: (index: number) => void;
  generateItinerary: () => Promise<void>;
  reset: () => void;
}

const initialState = {
  countries: [],
  isLoadingCountries: false,
  selectedCountry: null,
  startDate: null,
  endDate: null,
  groupType: '',
  groupSize: 2,
  vibes: [] as string[],
  budgetLevel: 3,
  pacing: 'moderate',
  currentStep: 0,
  allocationResponse: null,
  selectedAllocationIndex: null,
  isLoadingAllocations: false,
  countryItinerary: null,
  dayItineraries: [] as DayItinerary[],
  isGenerating: false,
  error: null as string | null,
};

export const useCountryStore = create<CountryTripState>((set, get) => ({
  ...initialState,

  totalDays: () => {
    const { startDate, endDate } = get();
    if (!startDate || !endDate) return 0;
    const diff = new Date(endDate).getTime() - new Date(startDate).getTime();
    return Math.round(diff / (1000 * 60 * 60 * 24)) + 1;
  },

  canProceedToAllocations: () => {
    const { selectedCountry, startDate, endDate, groupType, vibes } = get();
    return !!(selectedCountry && startDate && endDate && groupType && vibes.length > 0);
  },

  loadCountries: async () => {
    set({ isLoadingCountries: true });
    try {
      const resp = await countryApi.fetchCountries();
      // Add flags from our map
      const withFlags = resp.countries.map((c) => ({
        ...c,
        flag: COUNTRY_FLAGS[c.id] ?? '',
      }));
      set({ countries: withFlags, isLoadingCountries: false });
    } catch {
      // Fallback to mock data
      set({ countries: MOCK_COUNTRIES, isLoadingCountries: false });
    }
  },

  selectCountry: (country) => set({ selectedCountry: country }),

  setDateRange: (start, end) => set({ startDate: start, endDate: end }),

  setGroupType: (type) => set({ groupType: type }),

  setGroupSize: (size) => set({ groupSize: Math.max(1, Math.min(20, size)) }),

  toggleVibe: (vibe) => {
    const { vibes } = get();
    if (vibes.includes(vibe)) {
      set({ vibes: vibes.filter((v) => v !== vibe) });
    } else if (vibes.length < 5) {
      set({ vibes: [...vibes, vibe] });
    }
  },

  setBudgetLevel: (level) => set({ budgetLevel: Math.max(1, Math.min(5, level)) }),

  setPacing: (pacing) => set({ pacing }),

  nextStep: () => set((s) => ({ currentStep: Math.min(s.currentStep + 1, 3) })),

  previousStep: () => set((s) => ({ currentStep: Math.max(s.currentStep - 1, 0) })),

  fetchAllocations: async () => {
    const { selectedCountry, startDate, endDate, groupType, vibes, budgetLevel, pacing } = get();
    if (!selectedCountry || !startDate || !endDate) return;

    set({ isLoadingAllocations: true, error: null });
    const totalDays = get().totalDays();

    try {
      const resp = await countryApi.fetchAllocations({
        country: selectedCountry.id,
        total_days: totalDays,
        start_date: startDate,
        end_date: endDate,
        group_type: groupType,
        vibes,
        budget_level: budgetLevel,
        pacing,
      });
      set({ allocationResponse: resp, isLoadingAllocations: false });
    } catch {
      // Fallback to mock
      const mock = buildMockAllocations(selectedCountry.id, totalDays);
      set({ allocationResponse: mock, isLoadingAllocations: false });
    }
  },

  selectAllocation: (index) => set({ selectedAllocationIndex: index }),

  generateItinerary: async () => {
    const state = get();
    const { selectedCountry, allocationResponse, selectedAllocationIndex, startDate, endDate, groupType, groupSize, vibes, budgetLevel, pacing } = state;
    if (!selectedCountry || !allocationResponse || selectedAllocationIndex == null || !startDate || !endDate) return;

    set({ isGenerating: true, error: null });
    const allocation = allocationResponse.options[selectedAllocationIndex];

    try {
      const resp = await countryApi.generateItinerary({
        country: selectedCountry.id,
        selected_allocation: allocation,
        start_date: startDate,
        end_date: endDate,
        group_type: groupType,
        group_size: groupSize,
        vibes,
        budget_level: budgetLevel,
        pacing,
      });

      // Use day_itineraries from the API if available, otherwise fall back to mock
      const days: DayItinerary[] = [];
      for (const city of resp.city_itineraries) {
        if (city.day_itineraries && city.day_itineraries.length > 0) {
          days.push(...city.day_itineraries);
        } else {
          const cityDays = buildMockDayItineraries(city.city_name, city.days, city.start_date);
          days.push(...cityDays);
        }
      }

      set({ countryItinerary: resp, dayItineraries: days, isGenerating: false });
    } catch {
      // Build mock itinerary from allocation
      const days: DayItinerary[] = [];
      let currentDate = startDate;
      for (const city of allocation.cities) {
        const cityDays = buildMockDayItineraries(city.city_name, city.days, currentDate);
        days.push(...cityDays);
        const d = new Date(currentDate);
        d.setDate(d.getDate() + city.days);
        currentDate = d.toISOString().split('T')[0];
      }

      set({
        countryItinerary: {
          id: 'mock-' + Date.now(),
          country: selectedCountry.id,
          country_name: selectedCountry.name,
          total_days: state.totalDays(),
          start_date: startDate,
          end_date: endDate,
          group_type: groupType,
          vibes,
          budget_level: budgetLevel,
          pacing,
          city_itineraries: allocation.cities.map((c) => ({
            city_id: c.city_id,
            city_name: c.city_name,
            days: c.days,
            start_date: startDate, // simplified
            end_date: endDate,
            highlights: c.highlights,
          })),
          inter_city_travel: [],
          packing_suggestions: [],
          travel_tips: [],
        },
        dayItineraries: days,
        isGenerating: false,
      });
    }
  },

  reset: () => set({ ...initialState, countries: get().countries }),
}));
