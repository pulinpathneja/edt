import '../../domain/entities/persona_config.dart';
import '../../domain/repositories/persona_repository.dart';
import '../datasources/remote/persona_remote_datasource.dart';
import '../models/persona_config_model.dart';

/// Implementation of PersonaRepository
class PersonaRepositoryImpl implements PersonaRepository {
  final PersonaRemoteDataSource _remoteDataSource;

  PersonaRepositoryImpl(this._remoteDataSource);

  @override
  Future<PersonaConfig> getPersonaConfig() async {
    try {
      final model = await _remoteDataSource.getPersonaConfig();
      return _mapModelToEntity(model);
    } catch (e) {
      // Return fallback config on error
      return _mapModelToEntity(PersonaConfigModel.fallback());
    }
  }

  PersonaConfig _mapModelToEntity(PersonaConfigModel model) {
    return PersonaConfig(
      groupTypes: model.groupTypes
          .map((g) => GroupTypeOption(
                id: g.id,
                label: g.label,
                icon: g.icon,
                description: g.description,
              ))
          .toList(),
      vibes: model.vibes
          .map((v) => VibeOption(
                id: v.id,
                label: v.label,
                icon: v.icon,
                description: v.description,
              ))
          .toList(),
      pacingOptions: model.pacingOptions
          .map((p) => PacingOption(
                id: p.id,
                label: p.label,
                description: p.description,
              ))
          .toList(),
      budgetMin: model.budgetMin,
      budgetMax: model.budgetMax,
      maxGroupSize: model.maxGroupSize,
      maxTripDays: model.maxTripDays,
    );
  }
}
