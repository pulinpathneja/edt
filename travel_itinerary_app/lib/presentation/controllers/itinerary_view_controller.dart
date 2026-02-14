import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../config/di/providers.dart';
import '../../domain/entities/itinerary.dart';

part 'itinerary_view_controller.g.dart';

/// State for itinerary view
class ItineraryViewState {
  final Itinerary? itinerary;
  final int selectedDayIndex;
  final bool isLoading;
  final String? errorMessage;

  const ItineraryViewState({
    this.itinerary,
    this.selectedDayIndex = 0,
    this.isLoading = false,
    this.errorMessage,
  });

  ItineraryViewState copyWith({
    Itinerary? itinerary,
    int? selectedDayIndex,
    bool? isLoading,
    String? errorMessage,
  }) {
    return ItineraryViewState(
      itinerary: itinerary ?? this.itinerary,
      selectedDayIndex: selectedDayIndex ?? this.selectedDayIndex,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  DayItinerary? get selectedDay {
    if (itinerary == null || selectedDayIndex >= itinerary!.days.length) {
      return null;
    }
    return itinerary!.days[selectedDayIndex];
  }

  int get totalDays => itinerary?.days.length ?? 0;
}

/// Controller for itinerary view
@riverpod
class ItineraryViewController extends _$ItineraryViewController {
  @override
  ItineraryViewState build(String itineraryId) {
    // Load itinerary on initialization
    _loadItinerary(itineraryId);
    return const ItineraryViewState(isLoading: true);
  }

  Future<void> _loadItinerary(String id) async {
    try {
      final repository = ref.read(itineraryRepositoryProvider);
      final itinerary = await repository.getItinerary(id);
      state = state.copyWith(
        itinerary: itinerary,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
    }
  }

  void selectDay(int index) {
    if (index >= 0 && index < state.totalDays) {
      state = state.copyWith(selectedDayIndex: index);
    }
  }

  void nextDay() {
    if (state.selectedDayIndex < state.totalDays - 1) {
      state = state.copyWith(selectedDayIndex: state.selectedDayIndex + 1);
    }
  }

  void previousDay() {
    if (state.selectedDayIndex > 0) {
      state = state.copyWith(selectedDayIndex: state.selectedDayIndex - 1);
    }
  }

  Future<void> refresh() async {
    state = state.copyWith(isLoading: true);
    await _loadItinerary(state.itinerary?.id ?? '');
  }

  /// Set itinerary directly (used when coming from generation)
  void setItinerary(Itinerary itinerary) {
    state = ItineraryViewState(
      itinerary: itinerary,
      isLoading: false,
    );
  }
}

/// Provider for current itinerary (shared between generation and view)
@Riverpod(keepAlive: true)
class CurrentItinerary extends _$CurrentItinerary {
  @override
  Itinerary? build() {
    return null;
  }

  void set(Itinerary itinerary) {
    state = itinerary;
  }

  void clear() {
    state = null;
  }
}
