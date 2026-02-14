import 'package:dio/dio.dart';

import '../../../core/constants/api_constants.dart';
import '../../models/itinerary_model.dart';
import '../../models/trip_request_model.dart';
import 'api_client.dart';

/// Remote data source for itinerary-related API calls
class ItineraryRemoteDataSource {
  final ApiClient _apiClient;

  ItineraryRemoteDataSource(this._apiClient);

  /// Generate a new itinerary based on trip request
  Future<ItineraryModel> generateItinerary(TripRequestModel request) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      ApiConstants.itineraryGenerate,
      data: request.toJson(),
      options: Options(
        receiveTimeout: const Duration(
          milliseconds: ApiConstants.generationTimeout,
        ),
      ),
    );
    return ItineraryModel.fromJson(response);
  }

  /// Get itinerary by ID
  Future<ItineraryModel> getItinerary(String id) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      ApiConstants.itineraryById(id),
    );
    return ItineraryModel.fromJson(response);
  }
}
