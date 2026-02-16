import 'package:equatable/equatable.dart';

class CityAllocation extends Equatable {
  final String cityId;
  final String cityName;
  final int days;
  final int priority;

  const CityAllocation({
    required this.cityId,
    required this.cityName,
    required this.days,
    required this.priority,
  });

  @override
  List<Object?> get props => [cityId, cityName, days, priority];
}

class AllocationOption extends Equatable {
  final String optionId;
  final String name;
  final String description;
  final double matchScore;
  final List<CityAllocation> cities;
  final List<String> pros;
  final List<String> cons;
  final bool isRecommended;

  const AllocationOption({
    required this.optionId,
    required this.name,
    required this.description,
    required this.matchScore,
    required this.cities,
    required this.pros,
    required this.cons,
    this.isRecommended = false,
  });

  int get totalDays => cities.fold(0, (sum, c) => sum + c.days);
  int get cityCount => cities.length;

  @override
  List<Object?> get props => [optionId, name, description, matchScore, cities, pros, cons, isRecommended];
}

class AllocationResponse extends Equatable {
  final String countryId;
  final String countryName;
  final int totalDays;
  final List<AllocationOption> options;

  const AllocationResponse({
    required this.countryId,
    required this.countryName,
    required this.totalDays,
    required this.options,
  });

  @override
  List<Object?> get props => [countryId, countryName, totalDays, options];
}
