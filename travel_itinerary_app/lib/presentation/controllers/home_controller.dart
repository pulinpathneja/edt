import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../domain/entities/country.dart';
import '../../config/di/providers.dart';

part 'home_controller.g.dart';

/// Mock countries for offline/demo mode
const _mockCountries = [
  Country(
    id: 'italy',
    name: 'Italy',
    flag: '\u{1F1EE}\u{1F1F9}',
    currency: 'EUR',
    languages: ['Italian'],
    cities: [
      CountryCity(id: 'rome', name: 'Rome', country: 'Italy', minDays: 2, maxDays: 5, idealDays: 3, priority: 1, highlights: ['Colosseum', 'Vatican', 'Trastevere'], vibes: ['cultural', 'foodie', 'historical'], bestFor: ['couple', 'solo', 'family']),
      CountryCity(id: 'florence', name: 'Florence', country: 'Italy', minDays: 2, maxDays: 4, idealDays: 3, priority: 2, highlights: ['Uffizi', 'Duomo', 'Ponte Vecchio'], vibes: ['artsy', 'cultural', 'foodie'], bestFor: ['couple', 'solo']),
      CountryCity(id: 'venice', name: 'Venice', country: 'Italy', minDays: 1, maxDays: 3, idealDays: 2, priority: 3, highlights: ['Grand Canal', 'St. Mark\'s', 'Murano'], vibes: ['romantic', 'cultural'], bestFor: ['couple']),
      CountryCity(id: 'milan', name: 'Milan', country: 'Italy', minDays: 1, maxDays: 3, idealDays: 2, priority: 4, highlights: ['Duomo', 'Last Supper', 'Fashion District'], vibes: ['shopping', 'cultural', 'foodie'], bestFor: ['solo', 'friends']),
    ],
    popularRoutes: [['rome', 'florence', 'venice'], ['rome', 'florence']],
  ),
  Country(
    id: 'france',
    name: 'France',
    flag: '\u{1F1EB}\u{1F1F7}',
    currency: 'EUR',
    languages: ['French'],
    cities: [
      CountryCity(id: 'paris', name: 'Paris', country: 'France', minDays: 3, maxDays: 6, idealDays: 4, priority: 1, highlights: ['Eiffel Tower', 'Louvre', 'Montmartre'], vibes: ['romantic', 'cultural', 'foodie'], bestFor: ['couple', 'solo']),
      CountryCity(id: 'nice', name: 'Nice', country: 'France', minDays: 2, maxDays: 4, idealDays: 2, priority: 2, highlights: ['Promenade', 'Old Town', 'Beach'], vibes: ['relaxation', 'nature'], bestFor: ['couple', 'family']),
      CountryCity(id: 'lyon', name: 'Lyon', country: 'France', minDays: 1, maxDays: 3, idealDays: 2, priority: 3, highlights: ['Old Lyon', 'Gastronomy', 'Traboules'], vibes: ['foodie', 'cultural'], bestFor: ['solo', 'friends']),
      CountryCity(id: 'bordeaux', name: 'Bordeaux', country: 'France', minDays: 1, maxDays: 3, idealDays: 2, priority: 4, highlights: ['Wine Region', 'Old Town', 'Cite du Vin'], vibes: ['foodie', 'relaxation'], bestFor: ['couple', 'friends']),
    ],
    popularRoutes: [['paris', 'nice'], ['paris', 'lyon', 'nice']],
  ),
  Country(
    id: 'spain',
    name: 'Spain',
    flag: '\u{1F1EA}\u{1F1F8}',
    currency: 'EUR',
    languages: ['Spanish'],
    cities: [
      CountryCity(id: 'barcelona', name: 'Barcelona', country: 'Spain', minDays: 3, maxDays: 5, idealDays: 3, priority: 1, highlights: ['Sagrada Familia', 'Park Guell', 'La Rambla'], vibes: ['cultural', 'nightlife', 'foodie'], bestFor: ['friends', 'couple']),
      CountryCity(id: 'madrid', name: 'Madrid', country: 'Spain', minDays: 2, maxDays: 4, idealDays: 3, priority: 2, highlights: ['Prado', 'Royal Palace', 'Retiro Park'], vibes: ['cultural', 'nightlife', 'foodie'], bestFor: ['solo', 'friends']),
      CountryCity(id: 'seville', name: 'Seville', country: 'Spain', minDays: 2, maxDays: 3, idealDays: 2, priority: 3, highlights: ['Alcazar', 'Flamenco', 'Plaza de Espana'], vibes: ['cultural', 'romantic'], bestFor: ['couple']),
      CountryCity(id: 'granada', name: 'Granada', country: 'Spain', minDays: 1, maxDays: 3, idealDays: 2, priority: 4, highlights: ['Alhambra', 'Albaicin', 'Tapas'], vibes: ['historical', 'foodie'], bestFor: ['solo', 'couple']),
    ],
    popularRoutes: [['barcelona', 'madrid'], ['madrid', 'seville', 'granada']],
  ),
  Country(
    id: 'japan',
    name: 'Japan',
    flag: '\u{1F1EF}\u{1F1F5}',
    currency: 'JPY',
    languages: ['Japanese'],
    cities: [
      CountryCity(id: 'tokyo', name: 'Tokyo', country: 'Japan', minDays: 3, maxDays: 6, idealDays: 4, priority: 1, highlights: ['Shibuya', 'Senso-ji', 'Tsukiji'], vibes: ['cultural', 'foodie', 'shopping'], bestFor: ['solo', 'friends']),
      CountryCity(id: 'kyoto', name: 'Kyoto', country: 'Japan', minDays: 2, maxDays: 5, idealDays: 3, priority: 2, highlights: ['Fushimi Inari', 'Bamboo Grove', 'Temples'], vibes: ['cultural', 'nature', 'historical'], bestFor: ['solo', 'couple']),
      CountryCity(id: 'osaka', name: 'Osaka', country: 'Japan', minDays: 2, maxDays: 4, idealDays: 2, priority: 3, highlights: ['Dotonbori', 'Street Food', 'Castle'], vibes: ['foodie', 'nightlife'], bestFor: ['friends', 'solo']),
    ],
    popularRoutes: [['tokyo', 'kyoto', 'osaka']],
  ),
  Country(
    id: 'united_kingdom',
    name: 'United Kingdom',
    flag: '\u{1F1EC}\u{1F1E7}',
    currency: 'GBP',
    languages: ['English'],
    cities: [
      CountryCity(id: 'london', name: 'London', country: 'UK', minDays: 3, maxDays: 6, idealDays: 4, priority: 1, highlights: ['Big Ben', 'British Museum', 'Tower'], vibes: ['cultural', 'historical', 'shopping'], bestFor: ['solo', 'family']),
      CountryCity(id: 'edinburgh', name: 'Edinburgh', country: 'UK', minDays: 2, maxDays: 4, idealDays: 3, priority: 2, highlights: ['Castle', 'Royal Mile', 'Arthur\'s Seat'], vibes: ['historical', 'nature', 'cultural'], bestFor: ['solo', 'couple']),
    ],
    popularRoutes: [['london', 'edinburgh']],
  ),
];

/// State for the home screen
class HomeState {
  final List<Country> countries;
  final bool isLoading;
  final String? error;

  const HomeState({
    this.countries = const [],
    this.isLoading = false,
    this.error,
  });

  HomeState copyWith({
    List<Country>? countries,
    bool? isLoading,
    String? error,
  }) {
    return HomeState(
      countries: countries ?? this.countries,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

@riverpod
class HomeController extends _$HomeController {
  @override
  HomeState build() {
    _loadCountries();
    return const HomeState(isLoading: true);
  }

  Future<void> _loadCountries() async {
    try {
      final repository = ref.read(countryRepositoryProvider);
      final countries = await repository.getCountries();
      state = state.copyWith(countries: countries, isLoading: false);
    } catch (e) {
      // Fallback to mock data when backend is unreachable
      state = state.copyWith(
        countries: _mockCountries,
        isLoading: false,
        error: null,
      );
    }
  }

  Future<void> refresh() async {
    state = state.copyWith(isLoading: true, error: null);
    await _loadCountries();
  }
}
