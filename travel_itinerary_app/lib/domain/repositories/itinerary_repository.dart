import '../entities/itinerary.dart';
import '../entities/trip_request.dart';

/// Repository interface for itinerary-related operations
abstract class ItineraryRepository {
  /// Generate a new itinerary based on trip request
  Future<Itinerary> generateItinerary(TripRequest request);

  /// Get itinerary by ID
  Future<Itinerary> getItinerary(String id);
}
