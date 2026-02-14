import '../entities/persona_config.dart';
import '../repositories/persona_repository.dart';

/// Use case for getting persona configuration
class GetPersonaConfig {
  final PersonaRepository _repository;

  GetPersonaConfig(this._repository);

  /// Execute the use case
  Future<PersonaConfig> call() async {
    return await _repository.getPersonaConfig();
  }
}
