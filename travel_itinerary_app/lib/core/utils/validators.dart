/// Input validation utilities
class Validators {
  Validators._();

  /// Validates that a destination is not empty and has reasonable length
  static String? validateDestination(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Please enter a destination';
    }
    if (value.length < 2) {
      return 'Destination must be at least 2 characters';
    }
    if (value.length > 100) {
      return 'Destination must be less than 100 characters';
    }
    return null;
  }

  /// Validates date range
  static String? validateDateRange(DateTime? start, DateTime? end) {
    if (start == null) {
      return 'Please select a start date';
    }
    if (end == null) {
      return 'Please select an end date';
    }
    if (start.isBefore(DateTime.now().subtract(const Duration(days: 1)))) {
      return 'Start date cannot be in the past';
    }
    if (end.isBefore(start)) {
      return 'End date must be after start date';
    }
    final duration = end.difference(start).inDays;
    if (duration > 30) {
      return 'Trip duration cannot exceed 30 days';
    }
    return null;
  }

  /// Validates group size
  static String? validateGroupSize(int? size) {
    if (size == null || size < 1) {
      return 'Group size must be at least 1';
    }
    if (size > 20) {
      return 'Group size cannot exceed 20';
    }
    return null;
  }

  /// Validates vibes selection
  static String? validateVibes(Set<String>? vibes) {
    if (vibes == null || vibes.isEmpty) {
      return 'Please select at least one vibe';
    }
    if (vibes.length > 5) {
      return 'Please select up to 5 vibes';
    }
    return null;
  }

  /// Validates budget level
  static String? validateBudgetLevel(int? level) {
    if (level == null || level < 1 || level > 5) {
      return 'Please select a budget level between 1 and 5';
    }
    return null;
  }
}
