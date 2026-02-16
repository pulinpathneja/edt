import '../entities/country.dart';
import '../entities/allocation.dart';
import '../entities/country_itinerary.dart';

abstract class CountryRepository {
  Future<List<Country>> getCountries();
  Future<AllocationResponse> getAllocations({
    required String countryId,
    required int totalDays,
    required String groupType,
    required List<String> vibes,
    required int budgetLevel,
    required String pacing,
  });
  Future<CountryItinerary> generateCountryItinerary({
    required String countryId,
    required String allocationOptionId,
    required String startDate,
    required String endDate,
    required String groupType,
    required int groupSize,
    required List<String> vibes,
    required int budgetLevel,
    required String pacing,
  });
}
