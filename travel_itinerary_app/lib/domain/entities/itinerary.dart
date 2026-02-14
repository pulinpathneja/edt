import 'package:equatable/equatable.dart';

import 'poi.dart';

/// Time slot entity
class TimeSlot extends Equatable {
  final String startTime;
  final String endTime;
  final POI activity;
  final Transport? transport;
  final List<String>? notes;

  const TimeSlot({
    required this.startTime,
    required this.endTime,
    required this.activity,
    this.transport,
    this.notes,
  });

  /// Get time range string
  String get timeRange => '$startTime - $endTime';

  @override
  List<Object?> get props => [startTime, endTime, activity, transport, notes];
}

/// Day itinerary entity
class DayItinerary extends Equatable {
  final int dayNumber;
  final String date;
  final String? title;
  final String? summary;
  final List<TimeSlot> timeSlots;
  final MealPOI? breakfast;
  final MealPOI? lunch;
  final MealPOI? dinner;
  final String? weatherNote;
  final List<String>? tips;

  const DayItinerary({
    required this.dayNumber,
    required this.date,
    this.title,
    this.summary,
    required this.timeSlots,
    this.breakfast,
    this.lunch,
    this.dinner,
    this.weatherNote,
    this.tips,
  });

  /// Get formatted date
  String get formattedDate {
    try {
      final dt = DateTime.parse(date);
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return '${weekdays[dt.weekday - 1]}, ${months[dt.month - 1]} ${dt.day}';
    } catch (_) {
      return date;
    }
  }

  /// Get day label (e.g., "Day 1")
  String get dayLabel => 'Day $dayNumber';

  /// Get activity count
  int get activityCount => timeSlots.length;

  /// Check if day has meals
  bool get hasMeals => breakfast != null || lunch != null || dinner != null;

  @override
  List<Object?> get props => [
        dayNumber,
        date,
        title,
        summary,
        timeSlots,
        breakfast,
        lunch,
        dinner,
        weatherNote,
        tips,
      ];
}

/// Complete itinerary entity
class Itinerary extends Equatable {
  final String id;
  final String destinationCity;
  final String? country;
  final String startDate;
  final String endDate;
  final int totalDays;
  final String groupType;
  final int groupSize;
  final List<String> vibes;
  final int budgetLevel;
  final String pacing;
  final String? title;
  final String? overview;
  final String? heroImageUrl;
  final List<DayItinerary> days;
  final List<String>? generalTips;
  final List<String>? packingSuggestions;
  final Map<String, dynamic>? estimatedBudget;
  final String? createdAt;
  final String? updatedAt;

  const Itinerary({
    required this.id,
    required this.destinationCity,
    this.country,
    required this.startDate,
    required this.endDate,
    required this.totalDays,
    required this.groupType,
    required this.groupSize,
    required this.vibes,
    required this.budgetLevel,
    required this.pacing,
    this.title,
    this.overview,
    this.heroImageUrl,
    required this.days,
    this.generalTips,
    this.packingSuggestions,
    this.estimatedBudget,
    this.createdAt,
    this.updatedAt,
  });

  /// Get destination with country
  String get fullDestination {
    if (country != null && country!.isNotEmpty) {
      return '$destinationCity, $country';
    }
    return destinationCity;
  }

  /// Get formatted date range
  String get dateRange {
    try {
      final start = DateTime.parse(startDate);
      final end = DateTime.parse(endDate);
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];

      if (start.month == end.month && start.year == end.year) {
        return '${months[start.month - 1]} ${start.day}-${end.day}, ${start.year}';
      } else if (start.year == end.year) {
        return '${months[start.month - 1]} ${start.day} - ${months[end.month - 1]} ${end.day}, ${start.year}';
      } else {
        return '${months[start.month - 1]} ${start.day}, ${start.year} - ${months[end.month - 1]} ${end.day}, ${end.year}';
      }
    } catch (_) {
      return '$startDate - $endDate';
    }
  }

  /// Get total activity count
  int get totalActivities {
    return days.fold(0, (sum, day) => sum + day.activityCount);
  }

  /// Get budget level string
  String get budgetLevelString {
    return '\$' * budgetLevel;
  }

  /// Get pacing display string
  String get pacingDisplay {
    return switch (pacing.toLowerCase()) {
      'slow' => 'Relaxed',
      'moderate' => 'Moderate',
      'fast' => 'Action-packed',
      _ => pacing,
    };
  }

  @override
  List<Object?> get props => [
        id,
        destinationCity,
        country,
        startDate,
        endDate,
        totalDays,
        groupType,
        groupSize,
        vibes,
        budgetLevel,
        pacing,
        title,
        overview,
        heroImageUrl,
        days,
        generalTips,
        packingSuggestions,
        estimatedBudget,
        createdAt,
        updatedAt,
      ];
}
