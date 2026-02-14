import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';
import '../../theme/colors/app_colors.dart';
import '../../theme/spacing/app_spacing.dart';
import '../../theme/typography/app_typography.dart';

/// Extension methods for BuildContext
extension ContextExtensions on BuildContext {
  // Theme shortcuts
  ThemeData get theme => Theme.of(this);
  ColorScheme get colorScheme => theme.colorScheme;
  TextTheme get textTheme => theme.textTheme;

  // Custom theme access
  AppColors get colors => AppTheme.colors;
  AppTypography get typography => AppTypography.instance;
  AppSpacing get spacing => AppSpacing.instance;

  // Media query shortcuts
  MediaQueryData get mediaQuery => MediaQuery.of(this);
  Size get screenSize => mediaQuery.size;
  double get screenWidth => screenSize.width;
  double get screenHeight => screenSize.height;
  EdgeInsets get padding => mediaQuery.padding;
  EdgeInsets get viewInsets => mediaQuery.viewInsets;

  // Responsive breakpoints
  bool get isMobile => screenWidth < 600;
  bool get isTablet => screenWidth >= 600 && screenWidth < 1200;
  bool get isDesktop => screenWidth >= 1200;

  // Navigation shortcuts
  NavigatorState get navigator => Navigator.of(this);
  void pop<T>([T? result]) => navigator.pop(result);
}

/// Extension methods for String
extension StringExtensions on String {
  String get capitalize =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';

  String get capitalizeWords =>
      split(' ').map((word) => word.capitalize).join(' ');
}

/// Extension methods for DateTime
extension DateTimeExtensions on DateTime {
  String get dateString =>
      '${year.toString()}-${month.toString().padLeft(2, '0')}-${day.toString().padLeft(2, '0')}';

  String get displayDate {
    const months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec'
    ];
    return '${months[month - 1]} $day, $year';
  }

  int get daysUntil => difference(DateTime.now()).inDays;
}
