import '../entities/persona_config.dart';

/// Repository interface for persona-related operations
abstract class PersonaRepository {
  /// Get persona configuration (group types, vibes, pacing options, etc.)
  Future<PersonaConfig> getPersonaConfig();
}
