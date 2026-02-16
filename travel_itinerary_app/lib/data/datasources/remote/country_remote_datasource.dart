import '../../../core/constants/api_constants.dart';
import '../../models/country_model.dart';
import '../../models/allocation_model.dart';
import '../../models/country_itinerary_model.dart';
import 'api_client.dart';

class CountryRemoteDataSource {
  final ApiClient _apiClient;

  CountryRemoteDataSource(this._apiClient);

  Future<List<CountryModel>> getCountries() async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '${ApiConstants.apiVersion}/country-itinerary/countries',
    );
    final countries = (response['countries'] as List<dynamic>)
        .map((c) => CountryModel.fromJson(c as Map<String, dynamic>))
        .toList();
    return countries;
  }

  Future<AllocationResponseModel> getAllocations({
    required String countryId,
    required int totalDays,
    required String groupType,
    required List<String> vibes,
    required int budgetLevel,
    required String pacing,
  }) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.apiVersion}/country-itinerary/allocations',
      data: {
        'country_id': countryId,
        'total_days': totalDays,
        'group_type': groupType,
        'vibes': vibes,
        'budget_level': budgetLevel,
        'pacing': pacing,
      },
    );
    return AllocationResponseModel.fromJson(response);
  }

  Future<CountryItineraryModel> generateCountryItinerary({
    required String countryId,
    required String allocationOptionId,
    required String startDate,
    required String endDate,
    required String groupType,
    required int groupSize,
    required List<String> vibes,
    required int budgetLevel,
    required String pacing,
  }) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.apiVersion}/country-itinerary/generate',
      data: {
        'country_id': countryId,
        'allocation_option_id': allocationOptionId,
        'start_date': startDate,
        'end_date': endDate,
        'group_type': groupType,
        'group_size': groupSize,
        'vibes': vibes,
        'budget_level': budgetLevel,
        'pacing': pacing,
      },
    );
    return CountryItineraryModel.fromJson(response);
  }
}
