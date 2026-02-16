import 'package:equatable/equatable.dart';

class CountryCity extends Equatable {
  final String id;
  final String name;
  final String country;
  final int minDays;
  final int maxDays;
  final int idealDays;
  final int priority;
  final List<String> highlights;
  final List<String> vibes;
  final List<String> bestFor;

  const CountryCity({
    required this.id,
    required this.name,
    required this.country,
    required this.minDays,
    required this.maxDays,
    required this.idealDays,
    required this.priority,
    required this.highlights,
    required this.vibes,
    required this.bestFor,
  });

  @override
  List<Object?> get props => [id, name, country, minDays, maxDays, idealDays, priority, highlights, vibes, bestFor];
}

class Country extends Equatable {
  final String id;
  final String name;
  final String flag;
  final String currency;
  final List<String> languages;
  final List<CountryCity> cities;
  final List<List<String>> popularRoutes;

  const Country({
    required this.id,
    required this.name,
    required this.flag,
    required this.currency,
    required this.languages,
    required this.cities,
    required this.popularRoutes,
  });

  int get cityCount => cities.length;

  @override
  List<Object?> get props => [id, name, flag, currency, languages, cities, popularRoutes];
}
