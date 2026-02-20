import { api } from './api';
import type {
  CountryListResponse,
  CityAllocationRequest,
  CityAllocationResponse,
  CountryItineraryRequest,
  CountryItineraryResponse,
} from '@/types';

const BASE = '/api/v1/country-itinerary';

export async function fetchCountries(): Promise<CountryListResponse> {
  const { data } = await api.get<CountryListResponse>(`${BASE}/countries`);
  return data;
}

export async function fetchAllocations(
  request: CityAllocationRequest,
): Promise<CityAllocationResponse> {
  const { data } = await api.post<CityAllocationResponse>(
    `${BASE}/allocations`,
    request,
  );
  return data;
}

export async function generateItinerary(
  request: CountryItineraryRequest,
): Promise<CountryItineraryResponse> {
  const { data } = await api.post<CountryItineraryResponse>(
    `${BASE}/generate`,
    request,
  );
  return data;
}
