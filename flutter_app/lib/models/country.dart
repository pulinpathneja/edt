class Country {
  final String id;
  final String name;
  final String currency;
  final List<String> languages;
  final List<CountryCity> cities;
  final List<List<String>> popularRoutes;

  Country({
    required this.id,
    required this.name,
    required this.currency,
    this.languages = const [],
    this.cities = const [],
    this.popularRoutes = const [],
  });

  factory Country.fromJson(Map<String, dynamic> json) {
    return Country(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      currency: json['currency'] ?? 'EUR',
      languages: List<String>.from(json['languages'] ?? []),
      cities: (json['cities'] as List<dynamic>?)
              ?.map((c) => CountryCity.fromJson(c))
              .toList() ??
          [],
      popularRoutes: (json['popular_routes'] as List<dynamic>?)
              ?.map((r) => List<String>.from(r))
              .toList() ??
          [],
    );
  }

  int get cityCount => cities.length;
}

class CountryCity {
  final String id;
  final String name;
  final String country;
  final int minDays;
  final int maxDays;
  final int idealDays;
  final List<String> highlights;
  final List<String> vibes;
  final List<String> bestFor;

  CountryCity({
    required this.id,
    required this.name,
    required this.country,
    this.minDays = 1,
    this.maxDays = 7,
    this.idealDays = 3,
    this.highlights = const [],
    this.vibes = const [],
    this.bestFor = const [],
  });

  factory CountryCity.fromJson(Map<String, dynamic> json) {
    return CountryCity(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      country: json['country'] ?? '',
      minDays: json['min_days'] ?? 1,
      maxDays: json['max_days'] ?? 7,
      idealDays: json['ideal_days'] ?? 3,
      highlights: List<String>.from(json['highlights'] ?? []),
      vibes: List<String>.from(json['vibes'] ?? []),
      bestFor: List<String>.from(json['best_for'] ?? []),
    );
  }
}
