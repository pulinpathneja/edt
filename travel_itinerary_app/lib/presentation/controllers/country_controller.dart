import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../domain/entities/country.dart';
import '../../domain/entities/allocation.dart';
import '../../domain/entities/country_itinerary.dart';
import '../../domain/entities/itinerary.dart';
import '../../domain/entities/poi.dart';
import '../../config/di/providers.dart';

part 'country_controller.g.dart';

/// State for the country trip flow
class CountryTripState {
  final Country? selectedCountry;
  final DateTime? startDate;
  final DateTime? endDate;
  final String groupType;
  final int groupSize;
  final List<String> vibes;
  final int budgetLevel;
  final String pacing;
  final int currentStep;

  // Allocation state
  final AllocationResponse? allocationResponse;
  final String? selectedAllocationId;
  final bool isLoadingAllocations;

  // Itinerary state
  final CountryItinerary? countryItinerary;
  final bool isGenerating;

  final String? error;

  const CountryTripState({
    this.selectedCountry,
    this.startDate,
    this.endDate,
    this.groupType = '',
    this.groupSize = 2,
    this.vibes = const [],
    this.budgetLevel = 3,
    this.pacing = 'moderate',
    this.currentStep = 0,
    this.allocationResponse,
    this.selectedAllocationId,
    this.isLoadingAllocations = false,
    this.countryItinerary,
    this.isGenerating = false,
    this.error,
  });

  int get totalDays {
    if (startDate == null || endDate == null) return 0;
    return endDate!.difference(startDate!).inDays + 1;
  }

  bool get canProceedToAllocations =>
      selectedCountry != null &&
      startDate != null &&
      endDate != null &&
      groupType.isNotEmpty &&
      vibes.isNotEmpty;

  CountryTripState copyWith({
    Country? selectedCountry,
    DateTime? startDate,
    DateTime? endDate,
    String? groupType,
    int? groupSize,
    List<String>? vibes,
    int? budgetLevel,
    String? pacing,
    int? currentStep,
    AllocationResponse? allocationResponse,
    String? selectedAllocationId,
    bool? isLoadingAllocations,
    CountryItinerary? countryItinerary,
    bool? isGenerating,
    String? error,
  }) {
    return CountryTripState(
      selectedCountry: selectedCountry ?? this.selectedCountry,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      groupType: groupType ?? this.groupType,
      groupSize: groupSize ?? this.groupSize,
      vibes: vibes ?? this.vibes,
      budgetLevel: budgetLevel ?? this.budgetLevel,
      pacing: pacing ?? this.pacing,
      currentStep: currentStep ?? this.currentStep,
      allocationResponse: allocationResponse ?? this.allocationResponse,
      selectedAllocationId: selectedAllocationId ?? this.selectedAllocationId,
      isLoadingAllocations: isLoadingAllocations ?? this.isLoadingAllocations,
      countryItinerary: countryItinerary ?? this.countryItinerary,
      isGenerating: isGenerating ?? this.isGenerating,
      error: error,
    );
  }
}

@riverpod
class CountryController extends _$CountryController {
  @override
  CountryTripState build() {
    return const CountryTripState();
  }

  void selectCountry(Country country) {
    state = state.copyWith(selectedCountry: country);
  }

  void setDateRange(DateTime start, DateTime end) {
    state = state.copyWith(startDate: start, endDate: end);
  }

  void setGroupType(String type) {
    state = state.copyWith(groupType: type);
  }

  void setGroupSize(int size) {
    state = state.copyWith(groupSize: size);
  }

  void toggleVibe(String vibe) {
    final current = List<String>.from(state.vibes);
    if (current.contains(vibe)) {
      current.remove(vibe);
    } else if (current.length < 5) {
      current.add(vibe);
    }
    state = state.copyWith(vibes: current);
  }

  void setBudgetLevel(int level) {
    state = state.copyWith(budgetLevel: level);
  }

  void setPacing(String pacing) {
    state = state.copyWith(pacing: pacing);
  }

  void nextStep() {
    state = state.copyWith(currentStep: state.currentStep + 1);
  }

  void previousStep() {
    if (state.currentStep > 0) {
      state = state.copyWith(currentStep: state.currentStep - 1);
    }
  }

  Future<void> fetchAllocations() async {
    if (!state.canProceedToAllocations) return;

    state = state.copyWith(isLoadingAllocations: true, error: null);

    try {
      final repository = ref.read(countryRepositoryProvider);
      final response = await repository.getAllocations(
        countryId: state.selectedCountry!.id,
        totalDays: state.totalDays,
        groupType: state.groupType,
        vibes: state.vibes,
        budgetLevel: state.budgetLevel,
        pacing: state.pacing,
      );
      state = state.copyWith(
        allocationResponse: response,
        isLoadingAllocations: false,
      );
    } catch (e) {
      // Fallback to mock allocations
      final mockResponse = _buildMockAllocations();
      state = state.copyWith(
        allocationResponse: mockResponse,
        isLoadingAllocations: false,
      );
    }
  }

  void selectAllocation(String optionId) {
    state = state.copyWith(selectedAllocationId: optionId);
  }

  Future<void> generateItinerary() async {
    if (state.selectedAllocationId == null) return;

    state = state.copyWith(isGenerating: true, error: null);

    try {
      final repository = ref.read(countryRepositoryProvider);
      final itinerary = await repository.generateCountryItinerary(
        countryId: state.selectedCountry!.id,
        allocationOptionId: state.selectedAllocationId!,
        startDate: _formatDate(state.startDate!),
        endDate: _formatDate(state.endDate!),
        groupType: state.groupType,
        groupSize: state.groupSize,
        vibes: state.vibes,
        budgetLevel: state.budgetLevel,
        pacing: state.pacing,
      );
      state = state.copyWith(
        countryItinerary: itinerary,
        isGenerating: false,
      );
    } catch (e) {
      // Fallback to mock itinerary
      final mockItinerary = _buildMockItinerary();
      state = state.copyWith(
        countryItinerary: mockItinerary,
        isGenerating: false,
      );
    }
  }

  void reset() {
    state = const CountryTripState();
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  // --- Mock data generators ---

  AllocationResponse _buildMockAllocations() {
    final country = state.selectedCountry!;
    final totalDays = state.totalDays;
    final cities = country.cities;

    // Option 1: Balanced - spread days evenly
    final balancedCities = <CityAllocation>[];
    int remaining = totalDays;
    for (int i = 0; i < cities.length && remaining > 0; i++) {
      final days = i == cities.length - 1
          ? remaining
          : (totalDays / cities.length.clamp(1, 4)).round().clamp(1, remaining);
      balancedCities.add(CityAllocation(
        cityId: cities[i].id,
        cityName: cities[i].name,
        days: days,
        priority: cities[i].priority,
      ));
      remaining -= days;
      if (balancedCities.length >= 4) break;
    }

    // Option 2: Deep dive - focus on top 2 cities
    final deepCities = <CityAllocation>[];
    if (cities.length >= 2) {
      final primary = (totalDays * 0.6).round().clamp(2, totalDays - 1);
      deepCities.add(CityAllocation(cityId: cities[0].id, cityName: cities[0].name, days: primary, priority: 1));
      deepCities.add(CityAllocation(cityId: cities[1].id, cityName: cities[1].name, days: totalDays - primary, priority: 2));
    } else {
      deepCities.add(CityAllocation(cityId: cities[0].id, cityName: cities[0].name, days: totalDays, priority: 1));
    }

    return AllocationResponse(
      countryId: country.id,
      countryName: country.name,
      totalDays: totalDays,
      options: [
        AllocationOption(
          optionId: 'balanced',
          name: 'Balanced Explorer',
          description: 'Experience the best of each city with a well-balanced day distribution across ${balancedCities.length} cities.',
          matchScore: 0.92,
          cities: balancedCities,
          pros: ['See more variety', 'Well-rounded experience', 'Popular route'],
          cons: ['Less time per city', 'More travel between cities'],
          isRecommended: true,
        ),
        AllocationOption(
          optionId: 'deep_dive',
          name: 'Deep Dive',
          description: 'Spend more time in the top destinations for a deeper, more immersive experience.',
          matchScore: 0.85,
          cities: deepCities,
          pros: ['More time to explore', 'Less rushing', 'Deeper cultural immersion'],
          cons: ['Fewer cities visited', 'May miss some highlights'],
        ),
      ],
    );
  }

  CountryItinerary _buildMockItinerary() {
    final country = state.selectedCountry!;
    final startDate = state.startDate!;
    final selectedOption = state.allocationResponse?.options
        .where((o) => o.optionId == state.selectedAllocationId)
        .firstOrNull;

    final cityAllocations = selectedOption?.cities ?? [];
    final cityItineraries = <CityItinerarySummary>[];

    int dayOffset = 0;
    for (int ci = 0; ci < cityAllocations.length; ci++) {
      final allocation = cityAllocations[ci];
      final days = <DayItinerary>[];

      for (int d = 0; d < allocation.days; d++) {
        final date = startDate.add(Duration(days: dayOffset + d));
        final dayNum = dayOffset + d + 1;
        days.add(DayItinerary(
          dayNumber: dayNum,
          date: _formatDate(date),
          title: d == 0 ? 'Arrival & ${allocation.cityName} Highlights' : 'Exploring ${allocation.cityName}',
          summary: 'A wonderful day discovering the best of ${allocation.cityName}.',
          timeSlots: [
            TimeSlot(
              startTime: '09:00',
              endTime: '11:00',
              activity: POI(
                id: '${allocation.cityId}_morning_$d',
                name: d == 0 ? '${allocation.cityName} Walking Tour' : 'Morning Sightseeing',
                description: 'Explore the iconic landmarks and hidden gems.',
                category: 'attraction',
              ),
            ),
            TimeSlot(
              startTime: '12:00',
              endTime: '13:30',
              activity: POI(
                id: '${allocation.cityId}_lunch_$d',
                name: 'Local Restaurant',
                description: 'Authentic local cuisine at a highly-rated spot.',
                category: 'restaurant',
              ),
            ),
            TimeSlot(
              startTime: '14:30',
              endTime: '17:00',
              activity: POI(
                id: '${allocation.cityId}_afternoon_$d',
                name: d == 0 ? 'Cultural District' : 'Neighborhood Exploration',
                description: 'Immerse yourself in the local culture and atmosphere.',
                category: 'attraction',
              ),
            ),
            TimeSlot(
              startTime: '19:00',
              endTime: '21:00',
              activity: POI(
                id: '${allocation.cityId}_dinner_$d',
                name: 'Dinner Experience',
                description: 'End the day with a memorable dining experience.',
                category: 'restaurant',
              ),
            ),
          ],
        ));
      }

      dayOffset += allocation.days;

      // Travel to next city
      InterCityTravel? travelToNext;
      if (ci < cityAllocations.length - 1) {
        final nextCity = cityAllocations[ci + 1];
        travelToNext = InterCityTravel(
          fromCity: allocation.cityName,
          toCity: nextCity.cityName,
          mode: 'Train',
          durationMinutes: 120 + (ci * 30),
          notes: 'High-speed train recommended. Book in advance for best prices.',
        );
      }

      // Find highlights from country city data
      final countryCity = country.cities.where((c) => c.id == allocation.cityId).firstOrNull;

      cityItineraries.add(CityItinerarySummary(
        cityId: allocation.cityId,
        cityName: allocation.cityName,
        days: allocation.days,
        dayItineraries: days,
        travelToNext: travelToNext,
        highlights: countryCity?.highlights,
      ));
    }

    return CountryItinerary(
      id: 'mock_${country.id}_${DateTime.now().millisecondsSinceEpoch}',
      countryId: country.id,
      countryName: country.name,
      startDate: _formatDate(startDate),
      endDate: _formatDate(state.endDate!),
      totalDays: state.totalDays,
      groupType: state.groupType,
      vibes: state.vibes,
      budgetLevel: state.budgetLevel,
      pacing: state.pacing,
      cityItineraries: cityItineraries,
      generalTips: [
        'Book train tickets in advance for better prices.',
        'Consider getting a city pass for museum discounts.',
        'Try local street food markets for authentic flavors.',
        'Download offline maps before your trip.',
      ],
    );
  }
}
