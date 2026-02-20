import '../../domain/entities/allocation.dart';

class CityAllocationModel extends CityAllocation {
  const CityAllocationModel({
    required super.cityId,
    required super.cityName,
    required super.days,
    required super.priority,
  });

  factory CityAllocationModel.fromJson(Map<String, dynamic> json) {
    return CityAllocationModel(
      cityId: json['city_id'] as String,
      cityName: json['city_name'] as String,
      days: json['days'] as int,
      priority: json['priority'] as int? ?? 3,
    );
  }
}

class AllocationOptionModel extends AllocationOption {
  const AllocationOptionModel({
    required super.optionId,
    required super.name,
    required super.description,
    required super.matchScore,
    required super.cities,
    required super.pros,
    required super.cons,
    super.isRecommended,
  });

  factory AllocationOptionModel.fromJson(Map<String, dynamic> json) {
    return AllocationOptionModel(
      optionId: json['option_id']?.toString() ?? '',
      name: json['name'] as String? ?? json['option_name'] as String? ?? '',
      description: json['description'] as String? ?? '',
      matchScore: (json['match_score'] as num?)?.toDouble() ?? 0.0,
      cities: (json['cities'] as List<dynamic>?)
              ?.map((c) => CityAllocationModel.fromJson(c as Map<String, dynamic>))
              .toList() ??
          [],
      pros: List<String>.from(json['pros'] ?? []),
      cons: List<String>.from(json['cons'] ?? []),
      isRecommended: json['is_recommended'] as bool? ?? false,
    );
  }
}

class AllocationResponseModel extends AllocationResponse {
  const AllocationResponseModel({
    required super.countryId,
    required super.countryName,
    required super.totalDays,
    required super.options,
  });

  factory AllocationResponseModel.fromJson(Map<String, dynamic> json) {
    return AllocationResponseModel(
      countryId: json['country_id'] as String? ?? json['country'] as String? ?? '',
      countryName: json['country_name'] as String? ?? '',
      totalDays: json['total_days'] as int? ?? 0,
      options: (json['options'] as List<dynamic>?)
              ?.map((o) => AllocationOptionModel.fromJson(o as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}
