import '../entities/allocation.dart';
import '../repositories/country_repository.dart';

class GetAllocations {
  final CountryRepository repository;

  GetAllocations(this.repository);

  Future<AllocationResponse> call({
    required String countryId,
    required int totalDays,
    required String groupType,
    required List<String> vibes,
    required int budgetLevel,
    required String pacing,
  }) {
    return repository.getAllocations(
      countryId: countryId,
      totalDays: totalDays,
      groupType: groupType,
      vibes: vibes,
      budgetLevel: budgetLevel,
      pacing: pacing,
    );
  }
}
