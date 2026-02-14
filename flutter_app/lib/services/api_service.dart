import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/city.dart';
import '../models/poi.dart';
import '../models/itinerary.dart';

class ApiService {
  // Production API URL (Cloud Run)
  static const String baseUrl = 'https://edt-api-724289610112.us-central1.run.app';

  // For local development, use:
  // static const String baseUrl = 'http://localhost:8000';

  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  // ==================== CITIES ====================

  Future<List<City>> getCities() async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/v1/cities'),
      headers: _headers,
    );
    _checkResponse(response);
    final data = json.decode(response.body);
    final cities = (data['cities'] as List<dynamic>?)
            ?.map((c) => City.fromJson(c))
            .toList() ??
        [];
    return cities;
  }

  Future<City> getCity(String cityId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/v1/cities/$cityId'),
      headers: _headers,
    );
    _checkResponse(response);
    return City.fromJson(json.decode(response.body));
  }

  // ==================== POIs ====================

  Future<List<POI>> getPOIs({
    String? city,
    String? category,
    String? neighborhood,
    int limit = 50,
  }) async {
    final queryParams = <String, String>{};
    if (city != null) queryParams['city'] = city;
    if (category != null) queryParams['category'] = category;
    if (neighborhood != null) queryParams['neighborhood'] = neighborhood;
    queryParams['limit'] = limit.toString();

    final uri = Uri.parse('$baseUrl/api/v1/pois').replace(queryParameters: queryParams);
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);

    final data = json.decode(response.body);
    return (data['pois'] as List<dynamic>?)
            ?.map((p) => POI.fromJson(p))
            .toList() ??
        [];
  }

  Future<POI> getPOI(String poiId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/v1/pois/$poiId'),
      headers: _headers,
    );
    _checkResponse(response);
    return POI.fromJson(json.decode(response.body));
  }

  // ==================== PERSONAS ====================

  Future<PersonaConfig> getPersonaConfig() async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/v1/personas/config'),
      headers: _headers,
    );
    _checkResponse(response);
    return PersonaConfig.fromJson(json.decode(response.body));
  }

  // ==================== ITINERARIES ====================

  Future<Itinerary> generateItinerary(TripRequest request) async {
    final body = {
      'trip_request': request.toJson(),
      'must_include_pois': [],
      'exclude_pois': [],
    };

    final response = await _client.post(
      Uri.parse('$baseUrl/api/v1/itinerary/generate/'),
      headers: _headers,
      body: json.encode(body),
    );
    _checkResponse(response);
    return Itinerary.fromJson(json.decode(response.body));
  }

  Future<List<Itinerary>> getItineraries({String? userId, int limit = 20}) async {
    final queryParams = <String, String>{};
    if (userId != null) queryParams['user_id'] = userId;
    queryParams['limit'] = limit.toString();

    final uri = Uri.parse('$baseUrl/api/v1/itinerary').replace(queryParameters: queryParams);
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);

    final data = json.decode(response.body);
    return (data['itineraries'] as List<dynamic>?)
            ?.map((i) => Itinerary.fromJson(i))
            .toList() ??
        [];
  }

  Future<Itinerary> getItinerary(String itineraryId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/v1/itinerary/$itineraryId'),
      headers: _headers,
    );
    _checkResponse(response);
    return Itinerary.fromJson(json.decode(response.body));
  }

  // ==================== LANDMARKS ====================

  Future<List<Landmark>> getLandmarks(String cityId, {int limit = 20}) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/v1/landmarks/$cityId?limit=$limit'),
      headers: _headers,
    );
    _checkResponse(response);

    final data = json.decode(response.body);
    return (data['landmarks'] as List<dynamic>?)
            ?.map((l) => Landmark.fromJson(l))
            .toList() ??
        [];
  }

  // ==================== HEALTH ====================

  Future<bool> checkHealth() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/health'),
        headers: _headers,
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // ==================== HELPERS ====================

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  void _checkResponse(http.Response response) {
    if (response.statusCode >= 400) {
      throw ApiException(
        statusCode: response.statusCode,
        message: response.body,
      );
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class PersonaConfig {
  final List<String> groupTypes;
  final List<String> vibeCategories;
  final List<String> pacingOptions;
  final List<int> budgetLevels;

  PersonaConfig({
    required this.groupTypes,
    required this.vibeCategories,
    required this.pacingOptions,
    required this.budgetLevels,
  });

  factory PersonaConfig.fromJson(Map<String, dynamic> json) {
    return PersonaConfig(
      groupTypes: List<String>.from(json['group_types'] ?? []),
      vibeCategories: List<String>.from(json['vibe_categories'] ?? []),
      pacingOptions: List<String>.from(json['pacing_options'] ?? []),
      budgetLevels: List<int>.from(json['budget_levels'] ?? []),
    );
  }
}

class Landmark {
  final String id;
  final String name;
  final String? category;
  final double latitude;
  final double longitude;
  final String? description;
  final int? durationMinutes;
  final bool? mustSee;
  final bool? familyFriendly;

  Landmark({
    required this.id,
    required this.name,
    this.category,
    required this.latitude,
    required this.longitude,
    this.description,
    this.durationMinutes,
    this.mustSee,
    this.familyFriendly,
  });

  factory Landmark.fromJson(Map<String, dynamic> json) {
    return Landmark(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      category: json['category'],
      latitude: (json['latitude'] ?? 0).toDouble(),
      longitude: (json['longitude'] ?? 0).toDouble(),
      description: json['description'],
      durationMinutes: json['duration_minutes'],
      mustSee: json['must_see'],
      familyFriendly: json['family_friendly'],
    );
  }
}
