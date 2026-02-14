import 'package:equatable/equatable.dart';

/// Trip request entity for generating itineraries
class TripRequest extends Equatable {
  final String destinationCity;
  final String startDate;
  final String endDate;
  final String groupType;
  final int groupSize;
  final bool hasKids;
  final bool hasSeniors;
  final List<String> vibes;
  final int budgetLevel;
  final String pacing;
  final bool avoidHeat;
  final bool mobilityConstraints;
  final List<String>? dietaryRestrictions;
  final List<String>? specialInterests;
  final bool avoidCrowds;
  final bool preferOutdoor;
  final bool preferIndoor;

  const TripRequest({
    required this.destinationCity,
    required this.startDate,
    required this.endDate,
    required this.groupType,
    required this.groupSize,
    this.hasKids = false,
    this.hasSeniors = false,
    required this.vibes,
    required this.budgetLevel,
    required this.pacing,
    this.avoidHeat = false,
    this.mobilityConstraints = false,
    this.dietaryRestrictions,
    this.specialInterests,
    this.avoidCrowds = false,
    this.preferOutdoor = false,
    this.preferIndoor = false,
  });

  /// Create an empty trip request
  factory TripRequest.empty() => const TripRequest(
        destinationCity: '',
        startDate: '',
        endDate: '',
        groupType: 'solo',
        groupSize: 1,
        vibes: [],
        budgetLevel: 3,
        pacing: 'moderate',
      );

  /// Create a copy with updated values
  TripRequest copyWith({
    String? destinationCity,
    String? startDate,
    String? endDate,
    String? groupType,
    int? groupSize,
    bool? hasKids,
    bool? hasSeniors,
    List<String>? vibes,
    int? budgetLevel,
    String? pacing,
    bool? avoidHeat,
    bool? mobilityConstraints,
    List<String>? dietaryRestrictions,
    List<String>? specialInterests,
    bool? avoidCrowds,
    bool? preferOutdoor,
    bool? preferIndoor,
  }) {
    return TripRequest(
      destinationCity: destinationCity ?? this.destinationCity,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      groupType: groupType ?? this.groupType,
      groupSize: groupSize ?? this.groupSize,
      hasKids: hasKids ?? this.hasKids,
      hasSeniors: hasSeniors ?? this.hasSeniors,
      vibes: vibes ?? this.vibes,
      budgetLevel: budgetLevel ?? this.budgetLevel,
      pacing: pacing ?? this.pacing,
      avoidHeat: avoidHeat ?? this.avoidHeat,
      mobilityConstraints: mobilityConstraints ?? this.mobilityConstraints,
      dietaryRestrictions: dietaryRestrictions ?? this.dietaryRestrictions,
      specialInterests: specialInterests ?? this.specialInterests,
      avoidCrowds: avoidCrowds ?? this.avoidCrowds,
      preferOutdoor: preferOutdoor ?? this.preferOutdoor,
      preferIndoor: preferIndoor ?? this.preferIndoor,
    );
  }

  /// Calculate trip duration in days
  int get tripDuration {
    try {
      final start = DateTime.parse(startDate);
      final end = DateTime.parse(endDate);
      return end.difference(start).inDays + 1;
    } catch (_) {
      return 0;
    }
  }

  /// Check if request is valid
  bool get isValid =>
      destinationCity.isNotEmpty &&
      startDate.isNotEmpty &&
      endDate.isNotEmpty &&
      vibes.isNotEmpty &&
      tripDuration > 0;

  @override
  List<Object?> get props => [
        destinationCity,
        startDate,
        endDate,
        groupType,
        groupSize,
        hasKids,
        hasSeniors,
        vibes,
        budgetLevel,
        pacing,
        avoidHeat,
        mobilityConstraints,
        dietaryRestrictions,
        specialInterests,
        avoidCrowds,
        preferOutdoor,
        preferIndoor,
      ];
}
