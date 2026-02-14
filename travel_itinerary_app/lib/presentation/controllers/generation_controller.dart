import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../config/di/providers.dart';
import '../../domain/entities/itinerary.dart';
import '../../domain/entities/trip_request.dart';

part 'generation_controller.g.dart';

/// State for itinerary generation
enum GenerationStatus {
  idle,
  generating,
  success,
  error,
}

class GenerationState {
  final GenerationStatus status;
  final Itinerary? itinerary;
  final String? errorMessage;
  final TripRequest? request;

  const GenerationState({
    this.status = GenerationStatus.idle,
    this.itinerary,
    this.errorMessage,
    this.request,
  });

  GenerationState copyWith({
    GenerationStatus? status,
    Itinerary? itinerary,
    String? errorMessage,
    TripRequest? request,
  }) {
    return GenerationState(
      status: status ?? this.status,
      itinerary: itinerary ?? this.itinerary,
      errorMessage: errorMessage ?? this.errorMessage,
      request: request ?? this.request,
    );
  }

  bool get isGenerating => status == GenerationStatus.generating;
  bool get isSuccess => status == GenerationStatus.success;
  bool get isError => status == GenerationStatus.error;
  bool get hasItinerary => itinerary != null;
}

/// Controller for itinerary generation
@riverpod
class GenerationController extends _$GenerationController {
  @override
  GenerationState build() {
    return const GenerationState();
  }

  Future<void> generate(TripRequest request) async {
    state = GenerationState(
      status: GenerationStatus.generating,
      request: request,
    );

    try {
      final repository = ref.read(itineraryRepositoryProvider);
      final itinerary = await repository.generateItinerary(request);

      state = state.copyWith(
        status: GenerationStatus.success,
        itinerary: itinerary,
      );
    } catch (e) {
      state = state.copyWith(
        status: GenerationStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  void reset() {
    state = const GenerationState();
  }
}

/// Loading messages for generation animation
const generationLoadingMessages = [
  'Analyzing your preferences...',
  'Searching for the best experiences...',
  'Curating hidden gems...',
  'Optimizing your daily routes...',
  'Adding local favorites...',
  'Finding the perfect restaurants...',
  'Crafting your perfect itinerary...',
  'Almost there...',
];
