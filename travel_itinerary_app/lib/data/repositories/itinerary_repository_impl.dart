import '../../domain/entities/itinerary.dart';
import '../../domain/entities/poi.dart';
import '../../domain/entities/trip_request.dart';
import '../../domain/repositories/itinerary_repository.dart';
import '../datasources/remote/itinerary_remote_datasource.dart';
import '../models/itinerary_model.dart';
import '../models/poi_model.dart';
import '../models/trip_request_model.dart';

/// Implementation of ItineraryRepository
class ItineraryRepositoryImpl implements ItineraryRepository {
  final ItineraryRemoteDataSource _remoteDataSource;

  ItineraryRepositoryImpl(this._remoteDataSource);

  @override
  Future<Itinerary> generateItinerary(TripRequest request) async {
    final requestModel = _mapRequestToModel(request);
    final model = await _remoteDataSource.generateItinerary(requestModel);
    return _mapModelToEntity(model);
  }

  @override
  Future<Itinerary> getItinerary(String id) async {
    final model = await _remoteDataSource.getItinerary(id);
    return _mapModelToEntity(model);
  }

  TripRequestModel _mapRequestToModel(TripRequest request) {
    return TripRequestModel(
      destinationCity: request.destinationCity,
      startDate: request.startDate,
      endDate: request.endDate,
      groupType: request.groupType,
      groupSize: request.groupSize,
      hasKids: request.hasKids,
      hasSeniors: request.hasSeniors,
      vibes: request.vibes,
      budgetLevel: request.budgetLevel,
      pacing: request.pacing,
      avoidHeat: request.avoidHeat,
      mobilityConstraints: request.mobilityConstraints,
      dietaryRestrictions: request.dietaryRestrictions,
      specialInterests: request.specialInterests,
      avoidCrowds: request.avoidCrowds,
      preferOutdoor: request.preferOutdoor,
      preferIndoor: request.preferIndoor,
    );
  }

  Itinerary _mapModelToEntity(ItineraryModel model) {
    return Itinerary(
      id: model.id,
      destinationCity: model.destinationCity,
      country: model.country,
      startDate: model.startDate,
      endDate: model.endDate,
      totalDays: model.totalDays,
      groupType: model.groupType,
      groupSize: model.groupSize,
      vibes: model.vibes,
      budgetLevel: model.budgetLevel,
      pacing: model.pacing,
      title: model.title,
      overview: model.overview,
      heroImageUrl: model.heroImageUrl,
      days: model.days.map((d) => _mapDayToEntity(d)).toList(),
      generalTips: model.generalTips,
      packingSuggestions: model.packingSuggestions,
      estimatedBudget: model.estimatedBudget,
      createdAt: model.createdAt,
      updatedAt: model.updatedAt,
    );
  }

  DayItinerary _mapDayToEntity(DayItineraryModel model) {
    return DayItinerary(
      dayNumber: model.dayNumber,
      date: model.date,
      title: model.title,
      summary: model.summary,
      timeSlots: model.timeSlots.map((t) => _mapTimeSlotToEntity(t)).toList(),
      breakfast: model.breakfast != null ? _mapMealToEntity(model.breakfast!) : null,
      lunch: model.lunch != null ? _mapMealToEntity(model.lunch!) : null,
      dinner: model.dinner != null ? _mapMealToEntity(model.dinner!) : null,
      weatherNote: model.weatherNote,
      tips: model.tips,
    );
  }

  TimeSlot _mapTimeSlotToEntity(TimeSlotModel model) {
    return TimeSlot(
      startTime: model.startTime,
      endTime: model.endTime,
      activity: _mapPOIToEntity(model.activity),
      transport: model.transport != null ? _mapTransportToEntity(model.transport!) : null,
      notes: model.notes,
    );
  }

  POI _mapPOIToEntity(POIModel model) {
    return POI(
      id: model.id,
      name: model.name,
      description: model.description,
      category: model.category,
      startTime: model.startTime,
      endTime: model.endTime,
      durationMinutes: model.durationMinutes,
      address: model.address,
      latitude: model.latitude,
      longitude: model.longitude,
      imageUrl: model.imageUrl,
      rating: model.rating,
      priceLevel: model.priceLevel,
      tags: model.tags,
      bookingUrl: model.bookingUrl,
      phoneNumber: model.phoneNumber,
      website: model.website,
      openingHours: model.openingHours,
      tips: model.tips,
    );
  }

  MealPOI _mapMealToEntity(MealPOIModel model) {
    return MealPOI(
      id: model.id,
      name: model.name,
      mealType: model.mealType,
      cuisine: model.cuisine,
      description: model.description,
      address: model.address,
      latitude: model.latitude,
      longitude: model.longitude,
      imageUrl: model.imageUrl,
      rating: model.rating,
      priceLevel: model.priceLevel,
      reservationRequired: model.reservationRequired,
      bookingUrl: model.bookingUrl,
      dietaryOptions: model.dietaryOptions,
    );
  }

  Transport _mapTransportToEntity(TransportModel model) {
    return Transport(
      mode: model.mode,
      durationMinutes: model.durationMinutes,
      description: model.description,
      distance: model.distance,
      estimatedCost: model.estimatedCost,
    );
  }
}
