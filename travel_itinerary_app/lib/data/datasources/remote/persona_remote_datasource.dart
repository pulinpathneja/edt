import '../../../core/constants/api_constants.dart';
import '../../models/persona_config_model.dart';
import 'api_client.dart';

/// Remote data source for persona-related API calls
class PersonaRemoteDataSource {
  final ApiClient _apiClient;

  PersonaRemoteDataSource(this._apiClient);

  /// Fetch persona configuration (group types, vibes, pacing options, etc.)
  Future<PersonaConfigModel> getPersonaConfig() async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      ApiConstants.personaConfig,
    );
    return PersonaConfigModel.fromJson(response);
  }
}
