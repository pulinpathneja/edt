import '../../domain/entities/country.dart';
import '../../domain/entities/allocation.dart';
import '../../domain/entities/country_itinerary.dart';
import '../../domain/repositories/country_repository.dart';
import '../datasources/remote/country_remote_datasource.dart';

class CountryRepositoryImpl implements CountryRepository {
  final CountryRemoteDataSource _remoteDataSource;

  CountryRepositoryImpl(this._remoteDataSource);

  @override
  Future<List<Country>> getCountries() {
    return _remoteDataSource.getCountries();
  }

  @override
  Future<AllocationResponse> getAllocations({
    required String countryId,
    required int totalDays,
    required String groupType,
    required List<String> vibes,
    required int budgetLevel,
    required String pacing,
  }) {
    return _remoteDataSource.getAllocations(
      countryId: countryId,
      totalDays: totalDays,
      groupType: groupType,
      vibes: vibes,
      budgetLevel: budgetLevel,
      pacing: pacing,
    );
  }

  @override
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
  }) {
    return _remoteDataSource.generateCountryItinerary(
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
