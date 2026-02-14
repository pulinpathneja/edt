class POI {
  final String id;
  final String name;
  final String? description;
  final double latitude;
  final double longitude;
  final String? address;
  final String? neighborhood;
  final String city;
  final String? country;
  final String category;
  final String? subcategory;
  final int? typicalDurationMinutes;
  final String? bestTimeOfDay;
  final int? costLevel;
  final double? avgCostPerPerson;
  final String? costCurrency;
  final bool? isMustSee;
  final bool? isHiddenGem;
  final bool? instagramWorthy;
  final String? imageUrl;
  final PersonaScores? personaScores;

  POI({
    required this.id,
    required this.name,
    this.description,
    required this.latitude,
    required this.longitude,
    this.address,
    this.neighborhood,
    required this.city,
    this.country,
    required this.category,
    this.subcategory,
    this.typicalDurationMinutes,
    this.bestTimeOfDay,
    this.costLevel,
    this.avgCostPerPerson,
    this.costCurrency,
    this.isMustSee,
    this.isHiddenGem,
    this.instagramWorthy,
    this.imageUrl,
    this.personaScores,
  });

  factory POI.fromJson(Map<String, dynamic> json) {
    return POI(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'],
      latitude: (json['latitude'] ?? 0).toDouble(),
      longitude: (json['longitude'] ?? 0).toDouble(),
      address: json['address'],
      neighborhood: json['neighborhood'],
      city: json['city'] ?? '',
      country: json['country'],
      category: json['category'] ?? 'attraction',
      subcategory: json['subcategory'],
      typicalDurationMinutes: json['typical_duration_minutes'],
      bestTimeOfDay: json['best_time_of_day'],
      costLevel: json['cost_level'],
      avgCostPerPerson: json['avg_cost_per_person']?.toDouble(),
      costCurrency: json['cost_currency'],
      isMustSee: json['attributes']?['is_must_see'],
      isHiddenGem: json['attributes']?['is_hidden_gem'],
      instagramWorthy: json['attributes']?['instagram_worthy'],
      imageUrl: json['image_url'],
      personaScores: json['persona_scores'] != null
          ? PersonaScores.fromJson(json['persona_scores'])
          : null,
    );
  }

  String get durationText {
    if (typicalDurationMinutes == null) return 'Varies';
    if (typicalDurationMinutes! < 60) return '${typicalDurationMinutes}min';
    final hours = typicalDurationMinutes! ~/ 60;
    final mins = typicalDurationMinutes! % 60;
    return mins > 0 ? '${hours}h ${mins}min' : '${hours}h';
  }

  String get costText {
    if (costLevel == null) return 'Free';
    return '\$' * costLevel!;
  }
}

class PersonaScores {
  final double? family;
  final double? couple;
  final double? solo;
  final double? honeymoon;
  final double? friends;
  final double? cultural;
  final double? romantic;
  final double? adventure;
  final double? foodie;
  final double? photography;

  PersonaScores({
    this.family,
    this.couple,
    this.solo,
    this.honeymoon,
    this.friends,
    this.cultural,
    this.romantic,
    this.adventure,
    this.foodie,
    this.photography,
  });

  factory PersonaScores.fromJson(Map<String, dynamic> json) {
    return PersonaScores(
      family: json['score_family']?.toDouble(),
      couple: json['score_couple']?.toDouble(),
      solo: json['score_solo']?.toDouble(),
      honeymoon: json['score_honeymoon']?.toDouble(),
      friends: json['score_friends']?.toDouble(),
      cultural: json['score_cultural']?.toDouble(),
      romantic: json['score_romantic']?.toDouble(),
      adventure: json['score_adventure']?.toDouble(),
      foodie: json['score_foodie']?.toDouble(),
      photography: json['score_photography']?.toDouble(),
    );
  }
}
