import '../entities/country_itinerary.dart';
import '../repositories/country_repository.dart';

class GenerateCountryItinerary {
  final CountryRepository repository;

  GenerateCountryItinerary(this.repository);

  Future<CountryItinerary> call({
    required String countryId,
    required String allocationOptionId,
    required String startDate,
    required String endDate,
    required String groupType,
    required int groupSize,
    required List<String> vibes,
    required int budgetLevel,
    required String pacing,
  }) {
    return repository.generateCountryItinerary(
      countryId: countryId,
      allocationOptionId: allocationOptionId,
      startDate: startDate,
      endDate: endDate,
      groupType: groupType,
      groupSize: groupSize,
      vibes: vibes,
      budgetLevel: budgetLevel,
      pacing: pacing,
    );
  }
}
