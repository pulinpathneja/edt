import '../entities/itinerary.dart';
import '../entities/trip_request.dart';
import '../repositories/itinerary_repository.dart';

/// Use case for generating an itinerary
class GenerateItinerary {
  final ItineraryRepository _repository;

  GenerateItinerary(this._repository);

  /// Execute the use case
  Future<Itinerary> call(TripRequest request) async {
    // Validate request before sending
    if (!request.isValid) {
      throw ArgumentError('Invalid trip request');
    }
    return await _repository.generateItinerary(request);
  }
}

/// Use case for getting an existing itinerary
class GetItinerary {
  final ItineraryRepository _repository;

  GetItinerary(this._repository);

  /// Execute the use case
  Future<Itinerary> call(String id) async {
    if (id.isEmpty) {
      throw ArgumentError('Itinerary ID cannot be empty');
    }
    return await _repository.getItinerary(id);
  }
}
