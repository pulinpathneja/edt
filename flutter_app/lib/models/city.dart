class City {
  final String id;
  final String name;
  final String country;
  final String currency;
  final BoundingBox? bbox;
  final Coordinates? center;
  final int? landmarkCount;
  final String? imageUrl;

  City({
    required this.id,
    required this.name,
    required this.country,
    this.currency = 'EUR',
    this.bbox,
    this.center,
    this.landmarkCount,
    this.imageUrl,
  });

  factory City.fromJson(Map<String, dynamic> json) {
    return City(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      country: json['country'] ?? '',
      currency: json['currency'] ?? 'EUR',
      bbox: json['bbox'] != null ? BoundingBox.fromJson(json['bbox']) : null,
      center: json['center'] != null ? Coordinates.fromJson(json['center']) : null,
      landmarkCount: json['landmark_count'],
      imageUrl: json['image_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'country': country,
      'currency': currency,
      'bbox': bbox?.toJson(),
      'center': center?.toJson(),
      'landmark_count': landmarkCount,
      'image_url': imageUrl,
    };
  }
}

class BoundingBox {
  final double minLon;
  final double maxLon;
  final double minLat;
  final double maxLat;

  BoundingBox({
    required this.minLon,
    required this.maxLon,
    required this.minLat,
    required this.maxLat,
  });

  factory BoundingBox.fromJson(Map<String, dynamic> json) {
    return BoundingBox(
      minLon: (json['min_lon'] ?? 0).toDouble(),
      maxLon: (json['max_lon'] ?? 0).toDouble(),
      minLat: (json['min_lat'] ?? 0).toDouble(),
      maxLat: (json['max_lat'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'min_lon': minLon,
      'max_lon': maxLon,
      'min_lat': minLat,
      'max_lat': maxLat,
    };
  }
}

class Coordinates {
  final double lat;
  final double lon;

  Coordinates({required this.lat, required this.lon});

  factory Coordinates.fromJson(Map<String, dynamic> json) {
    return Coordinates(
      lat: (json['lat'] ?? json['latitude'] ?? 0).toDouble(),
      lon: (json['lon'] ?? json['longitude'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {'lat': lat, 'lon': lon};
  }
}
