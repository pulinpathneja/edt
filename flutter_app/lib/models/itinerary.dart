import 'poi.dart';

class TripRequest {
  final String? userId;
  final String destinationCity;
  final DateTime startDate;
  final DateTime endDate;
  final String groupType;
  final int groupSize;
  final bool hasKids;
  final bool hasSeniors;
  final List<String> vibes;
  final int budgetLevel;
  final double? dailyBudget;
  final String pacing;

  TripRequest({
    this.userId,
    required this.destinationCity,
    required this.startDate,
    required this.endDate,
    required this.groupType,
    this.groupSize = 2,
    this.hasKids = false,
    this.hasSeniors = false,
    required this.vibes,
    this.budgetLevel = 3,
    this.dailyBudget,
    this.pacing = 'moderate',
  });

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'destination_city': destinationCity,
      'start_date': startDate.toIso8601String().split('T')[0],
      'end_date': endDate.toIso8601String().split('T')[0],
      'group_type': groupType,
      'group_size': groupSize,
      'has_kids': hasKids,
      'has_seniors': hasSeniors,
      'vibes': vibes,
      'budget_level': budgetLevel,
      'daily_budget': dailyBudget,
      'pacing': pacing,
    };
  }
}

class Itinerary {
  final String id;
  final String? tripRequestId;
  final double? totalEstimatedCost;
  final String? generationMethod;
  final DateTime? createdAt;
  final List<ItineraryDay> days;
  final String? cityName;

  Itinerary({
    required this.id,
    this.tripRequestId,
    this.totalEstimatedCost,
    this.generationMethod,
    this.createdAt,
    required this.days,
    this.cityName,
  });

  factory Itinerary.fromJson(Map<String, dynamic> json) {
    return Itinerary(
      id: json['id'] ?? '',
      tripRequestId: json['trip_request_id'],
      totalEstimatedCost: json['total_estimated_cost']?.toDouble(),
      generationMethod: json['generation_method'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      days: (json['days'] as List<dynamic>?)
              ?.map((d) => ItineraryDay.fromJson(d))
              .toList() ??
          [],
      cityName: json['city_name'],
    );
  }

  int get totalDays => days.length;

  String get costText {
    if (totalEstimatedCost == null) return 'N/A';
    return '\$${totalEstimatedCost!.toStringAsFixed(0)}';
  }
}

class ItineraryDay {
  final String id;
  final int dayNumber;
  final DateTime? date;
  final String? theme;
  final double? estimatedCost;
  final double? pacingScore;
  final List<ItineraryItem> items;

  ItineraryDay({
    required this.id,
    required this.dayNumber,
    this.date,
    this.theme,
    this.estimatedCost,
    this.pacingScore,
    required this.items,
  });

  factory ItineraryDay.fromJson(Map<String, dynamic> json) {
    return ItineraryDay(
      id: json['id'] ?? '',
      dayNumber: json['day_number'] ?? 1,
      date: json['date'] != null ? DateTime.parse(json['date']) : null,
      theme: json['theme'],
      estimatedCost: json['estimated_cost']?.toDouble(),
      pacingScore: json['pacing_score']?.toDouble(),
      items: (json['items'] as List<dynamic>?)
              ?.map((i) => ItineraryItem.fromJson(i))
              .toList() ??
          [],
    );
  }

  String get dateText {
    if (date == null) return 'Day $dayNumber';
    final months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[date!.month - 1]} ${date!.day}';
  }
}

class ItineraryItem {
  final String id;
  final String? poiId;
  final int sequenceOrder;
  final String? startTime;
  final String? endTime;
  final String? selectionReason;
  final double? personaMatchScore;
  final int? travelTimeFromPrevious;
  final String? travelMode;
  final POI? poi;

  ItineraryItem({
    required this.id,
    this.poiId,
    required this.sequenceOrder,
    this.startTime,
    this.endTime,
    this.selectionReason,
    this.personaMatchScore,
    this.travelTimeFromPrevious,
    this.travelMode,
    this.poi,
  });

  factory ItineraryItem.fromJson(Map<String, dynamic> json) {
    return ItineraryItem(
      id: json['id'] ?? '',
      poiId: json['poi_id'],
      sequenceOrder: json['sequence_order'] ?? 0,
      startTime: json['start_time'],
      endTime: json['end_time'],
      selectionReason: json['selection_reason'],
      personaMatchScore: json['persona_match_score']?.toDouble(),
      travelTimeFromPrevious: json['travel_time_from_previous'],
      travelMode: json['travel_mode'],
      poi: json['poi'] != null ? POI.fromJson(json['poi']) : null,
    );
  }

  String get timeRange {
    if (startTime == null || endTime == null) return '';
    return '$startTime - $endTime';
  }

  String get travelText {
    if (travelTimeFromPrevious == null || travelTimeFromPrevious == 0) {
      return '';
    }
    final mode = travelMode ?? 'walk';
    final icon = mode == 'transit' ? 'transit' : 'walk';
    return '${travelTimeFromPrevious}min $icon';
  }
}
