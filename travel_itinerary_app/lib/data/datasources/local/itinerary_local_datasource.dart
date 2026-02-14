import 'dart:convert';

import 'package:hive/hive.dart';

import '../../models/itinerary_model.dart';

/// Local data source for caching itineraries
class ItineraryLocalDataSource {
  static const String _boxName = 'itineraries';

  Future<Box<String>> get _box async => Hive.openBox<String>(_boxName);

  /// Save itinerary to local storage
  Future<void> saveItinerary(ItineraryModel itinerary) async {
    final box = await _box;
    await box.put(itinerary.id, jsonEncode(itinerary.toJson()));
  }

  /// Get itinerary from local storage
  Future<ItineraryModel?> getItinerary(String id) async {
    final box = await _box;
    final json = box.get(id);
    if (json == null) return null;

    return ItineraryModel.fromJson(jsonDecode(json));
  }

  /// Get all cached itineraries
  Future<List<ItineraryModel>> getAllItineraries() async {
    final box = await _box;
    return box.values.map((json) {
      return ItineraryModel.fromJson(jsonDecode(json));
    }).toList();
  }

  /// Delete itinerary from local storage
  Future<void> deleteItinerary(String id) async {
    final box = await _box;
    await box.delete(id);
  }

  /// Clear all cached itineraries
  Future<void> clearAll() async {
    final box = await _box;
    await box.clear();
  }

  /// Check if itinerary exists in cache
  Future<bool> hasItinerary(String id) async {
    final box = await _box;
    return box.containsKey(id);
  }
}
