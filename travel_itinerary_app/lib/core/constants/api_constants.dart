/// API endpoint constants for the travel itinerary backend
class ApiConstants {
  ApiConstants._();

  // API Paths
  static const String apiVersion = '/api/v1';

  // Persona endpoints
  static const String personaConfig = '$apiVersion/personas/config';

  // Itinerary endpoints
  static const String itineraryGenerate = '$apiVersion/itinerary/generate';
  static String itineraryById(String id) => '$apiVersion/itinerary/$id';

  // Timeouts (in milliseconds)
  static const int connectTimeout = 5000;
  static const int receiveTimeout = 60000;
  static const int sendTimeout = 30000;

  // Generation timeout (longer for AI processing)
  static const int generationTimeout = 120000;
}
