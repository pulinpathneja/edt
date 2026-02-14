import 'package:equatable/equatable.dart';

/// Point of Interest (POI) entity
class POI extends Equatable {
  final String id;
  final String name;
  final String? description;
  final String category;
  final String? startTime;
  final String? endTime;
  final int? durationMinutes;
  final String? address;
  final double? latitude;
  final double? longitude;
  final String? imageUrl;
  final double? rating;
  final int? priceLevel;
  final List<String>? tags;
  final String? bookingUrl;
  final String? phoneNumber;
  final String? website;
  final Map<String, String>? openingHours;
  final Map<String, dynamic>? tips;

  const POI({
    required this.id,
    required this.name,
    this.description,
    required this.category,
    this.startTime,
    this.endTime,
    this.durationMinutes,
    this.address,
    this.latitude,
    this.longitude,
    this.imageUrl,
    this.rating,
    this.priceLevel,
    this.tags,
    this.bookingUrl,
    this.phoneNumber,
    this.website,
    this.openingHours,
    this.tips,
  });

  /// Get formatted duration string
  String get formattedDuration {
    if (durationMinutes == null) return '';
    final hours = durationMinutes! ~/ 60;
    final minutes = durationMinutes! % 60;
    if (hours > 0 && minutes > 0) {
      return '${hours}h ${minutes}m';
    } else if (hours > 0) {
      return '${hours}h';
    } else {
      return '${minutes}m';
    }
  }

  /// Get price level as string
  String get priceLevelString {
    if (priceLevel == null) return '';
    return '\$' * priceLevel!;
  }

  /// Check if has location data
  bool get hasLocation => latitude != null && longitude != null;

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        category,
        startTime,
        endTime,
        durationMinutes,
        address,
        latitude,
        longitude,
        imageUrl,
        rating,
        priceLevel,
        tags,
        bookingUrl,
        phoneNumber,
        website,
        openingHours,
        tips,
      ];
}

/// Meal POI entity
class MealPOI extends Equatable {
  final String id;
  final String name;
  final String mealType;
  final String? cuisine;
  final String? description;
  final String? address;
  final double? latitude;
  final double? longitude;
  final String? imageUrl;
  final double? rating;
  final int? priceLevel;
  final bool? reservationRequired;
  final String? bookingUrl;
  final List<String>? dietaryOptions;

  const MealPOI({
    required this.id,
    required this.name,
    required this.mealType,
    this.cuisine,
    this.description,
    this.address,
    this.latitude,
    this.longitude,
    this.imageUrl,
    this.rating,
    this.priceLevel,
    this.reservationRequired,
    this.bookingUrl,
    this.dietaryOptions,
  });

  /// Get price level as string
  String get priceLevelString {
    if (priceLevel == null) return '';
    return '\$' * priceLevel!;
  }

  @override
  List<Object?> get props => [
        id,
        name,
        mealType,
        cuisine,
        description,
        address,
        latitude,
        longitude,
        imageUrl,
        rating,
        priceLevel,
        reservationRequired,
        bookingUrl,
        dietaryOptions,
      ];
}

/// Transport entity
class Transport extends Equatable {
  final String mode;
  final int durationMinutes;
  final String? description;
  final double? distance;
  final String? estimatedCost;

  const Transport({
    required this.mode,
    required this.durationMinutes,
    this.description,
    this.distance,
    this.estimatedCost,
  });

  /// Get formatted duration string
  String get formattedDuration {
    final hours = durationMinutes ~/ 60;
    final minutes = durationMinutes % 60;
    if (hours > 0 && minutes > 0) {
      return '${hours}h ${minutes}m';
    } else if (hours > 0) {
      return '${hours}h';
    } else {
      return '${minutes}m';
    }
  }

  /// Get transport mode icon
  String get modeIcon {
    return switch (mode.toLowerCase()) {
      'walk' || 'walking' => '🚶',
      'taxi' || 'uber' || 'lyft' => '🚕',
      'bus' || 'public_transit' || 'transit' => '🚌',
      'subway' || 'metro' => '🚇',
      'train' => '🚆',
      'tram' => '🚊',
      'ferry' || 'boat' => '⛴️',
      'bike' || 'bicycle' => '🚴',
      'car' || 'drive' => '🚗',
      _ => '🚶',
    };
  }

  @override
  List<Object?> get props => [
        mode,
        durationMinutes,
        description,
        distance,
        estimatedCost,
      ];
}
