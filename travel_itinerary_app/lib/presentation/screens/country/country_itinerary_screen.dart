import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:ui';

import '../../../config/routes/app_router.dart';
import '../../../domain/entities/country_itinerary.dart';
import '../../../domain/entities/itinerary.dart';
import '../../../domain/entities/poi.dart';
import '../../../theme/colors/app_colors.dart';
import '../../controllers/country_controller.dart';

/// Country itinerary view matching modular-joy-maker design
class CountryItineraryScreen extends ConsumerStatefulWidget {
  const CountryItineraryScreen({super.key});

  @override
  ConsumerState<CountryItineraryScreen> createState() =>
      _CountryItineraryScreenState();
}

class _CountryItineraryScreenState
    extends ConsumerState<CountryItineraryScreen> {
  int _selectedDayIndex = 0;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(countryControllerProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: state.isGenerating
          ? _buildGeneratingState()
          : state.error != null
              ? _buildErrorState(state.error!)
              : state.countryItinerary != null
                  ? _buildItineraryView(context, state.countryItinerary!)
                  : _buildGeneratingState(),
    );
  }

  Widget _buildGeneratingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(
            width: 60,
            height: 60,
            child: CircularProgressIndicator(
              color: AppColors.primary,
              strokeWidth: 3,
            ),
          ),
          const SizedBox(height: 28),
          Text(
            'Generating Your Itinerary',
            style: GoogleFonts.plusJakartaSans(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ).animate().fadeIn(delay: 200.ms),
          const SizedBox(height: 10),
          Text(
            'Curating the perfect experience\nacross multiple cities...',
            textAlign: TextAlign.center,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 15,
              color: AppColors.textSecondary,
              height: 1.5,
            ),
          ).animate().fadeIn(delay: 400.ms),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 56, color: AppColors.error),
            const SizedBox(height: 16),
            Text(
              'Generation Failed',
              style: GoogleFonts.plusJakartaSans(
                fontSize: 22,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () =>
                  ref.read(countryControllerProvider.notifier).generateItinerary(),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  // Flatten all days across all cities
  List<_FlatDay> _flattenDays(CountryItinerary itinerary) {
    final days = <_FlatDay>[];
    for (final city in itinerary.cityItineraries) {
      for (final day in city.dayItineraries) {
        days.add(_FlatDay(
          day: day,
          cityName: city.cityName,
          travelToNext: city.dayItineraries.last == day ? city.travelToNext : null,
        ));
      }
    }
    return days;
  }

  Widget _buildItineraryView(BuildContext context, CountryItinerary itinerary) {
    final flatDays = _flattenDays(itinerary);
    if (_selectedDayIndex >= flatDays.length) {
      _selectedDayIndex = 0;
    }
    final currentDay = flatDays.isNotEmpty ? flatDays[_selectedDayIndex] : null;

    return SafeArea(
      child: Column(
        children: [
          // Header
          _buildHeader(currentDay, itinerary),
          const SizedBox(height: 12),

          // Date tabs
          _buildDateTabs(flatDays),
          const SizedBox(height: 16),

          // Day content
          Expanded(
            child: currentDay != null
                ? _buildDayContent(currentDay, _selectedDayIndex)
                : const Center(child: Text('No days available')),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(_FlatDay? currentDay, CountryItinerary itinerary) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          // Back button — glass style
          GestureDetector(
            onTap: () => context.go(Routes.home),
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.surface.withValues(alpha: 0.85),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: AppColors.border.withValues(alpha: 0.5),
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.shadowLight,
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(Icons.arrow_back, size: 20, color: AppColors.textPrimary),
            ),
          ),
          const SizedBox(width: 16),

          // Title
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                if (currentDay != null)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.auto_awesome, size: 12, color: AppColors.primary),
                      const SizedBox(width: 4),
                      Text(
                        'Day ${currentDay.day.dayNumber} in ${currentDay.cityName}',
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primary,
                          letterSpacing: 2.0,
                        ),
                      ),
                    ],
                  ),
                Text(
                  itinerary.countryName,
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
          ),

          // Share button
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.surface.withValues(alpha: 0.85),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: AppColors.border.withValues(alpha: 0.5),
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.shadowLight,
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: const Icon(Icons.share_outlined, size: 18, color: AppColors.textPrimary),
          ),
        ],
      ),
    );
  }

  Widget _buildDateTabs(List<_FlatDay> flatDays) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.surface.withValues(alpha: 0.75),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border.withValues(alpha: 0.5)),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
          child: Padding(
            padding: const EdgeInsets.all(6),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: flatDays.asMap().entries.map((entry) {
                  final index = entry.key;
                  final day = entry.value;
                  final isActive = index == _selectedDayIndex;

                  return GestureDetector(
                    onTap: () => setState(() => _selectedDayIndex = index),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 10,
                      ),
                      decoration: BoxDecoration(
                        gradient: isActive
                            ? const LinearGradient(
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                                colors: [AppColors.primary, AppColors.primaryLight],
                              )
                            : null,
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: isActive
                            ? [
                                BoxShadow(
                                  color: AppColors.primary.withValues(alpha: 0.25),
                                  blurRadius: 8,
                                  offset: const Offset(0, 2),
                                ),
                              ]
                            : null,
                      ),
                      child: Text(
                        _shortDate(day.day.date),
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: isActive
                              ? AppColors.white
                              : AppColors.textSecondary,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ),
      ),
    );
  }

  String _shortDate(String date) {
    try {
      final dt = DateTime.parse(date);
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
      ];
      return '${dt.day} ${months[dt.month - 1]}';
    } catch (_) {
      return date;
    }
  }

  Widget _buildDayContent(_FlatDay flatDay, int dayIndex) {
    final day = flatDay.day;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: [
          // Day card
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: AppColors.border.withValues(alpha: 0.3),
              ),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFFBCC2CF).withValues(alpha: 0.15),
                  blurRadius: 3,
                  offset: const Offset(0, 1),
                ),
                BoxShadow(
                  color: const Color(0xFFBCC2CF).withValues(alpha: 0.12),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              children: [
                // Hero / Day header
                _buildDayHeader(day, flatDay.cityName),

                // Summary row
                _buildDaySummary(day),

                // Timeline with activities
                if (day.timeSlots.isNotEmpty)
                  _buildTimeline(day),

                // Meals section
                if (day.hasMeals) _buildMealsSection(day),

                const SizedBox(height: 12),
              ],
            ),
          ).animate(delay: Duration(milliseconds: 100))
              .fadeIn(duration: 500.ms)
              .moveY(begin: 12, end: 0),

          // Travel to next city
          if (flatDay.travelToNext != null) ...[
            const SizedBox(height: 16),
            _buildTravelCard(flatDay.travelToNext!),
          ],

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildDayHeader(DayItinerary day, String cityName) {
    return Container(
      height: 144,
      margin: const EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppColors.primary,
            AppColors.primaryLight,
            AppColors.primary.withValues(alpha: 0.8),
          ],
        ),
      ),
      child: Stack(
        children: [
          // Subtle pattern overlay
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    AppColors.textPrimary.withValues(alpha: 0.4),
                  ],
                ),
              ),
            ),
          ),
          // Content
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      // Day badge
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.9),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          'Day ${day.dayNumber.toString().padLeft(2, '0')}',
                          style: GoogleFonts.plusJakartaSans(
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            color: AppColors.white,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Date badge
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          day.formattedDate,
                          style: GoogleFonts.plusJakartaSans(
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                            color: AppColors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    day.title ?? 'Day ${day.dayNumber}',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: AppColors.white,
                      letterSpacing: -0.3,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.location_on,
                          size: 12,
                          color: AppColors.white.withValues(alpha: 0.7)),
                      const SizedBox(width: 4),
                      Text(
                        cityName,
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: AppColors.white.withValues(alpha: 0.8),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDaySummary(DayItinerary day) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.secondary.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          // Duration
          Icon(Icons.access_time, size: 14, color: AppColors.primary),
          const SizedBox(width: 4),
          Text(
            _estimateDuration(day),
            style: GoogleFonts.plusJakartaSans(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          Container(
            width: 1,
            height: 16,
            margin: const EdgeInsets.symmetric(horizontal: 10),
            color: AppColors.border,
          ),
          // Stops
          Icon(Icons.location_on, size: 14, color: AppColors.primary),
          const SizedBox(width: 4),
          Text(
            '${day.activityCount}',
            style: GoogleFonts.plusJakartaSans(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(width: 2),
          Text(
            'stops',
            style: GoogleFonts.plusJakartaSans(
              fontSize: 8,
              fontWeight: FontWeight.w500,
              color: AppColors.textSecondary,
            ),
          ),
          const Spacer(),
          // Category chips
          ..._buildCategoryChips(day),
        ],
      ),
    );
  }

  List<Widget> _buildCategoryChips(DayItinerary day) {
    final counts = <String, int>{};
    for (final slot in day.timeSlots) {
      final type = _activityType(slot.activity.category);
      counts[type] = (counts[type] ?? 0) + 1;
    }
    if (day.hasMeals) {
      counts['meal'] = (counts['meal'] ?? 0) +
          (day.breakfast != null ? 1 : 0) +
          (day.lunch != null ? 1 : 0) +
          (day.dinner != null ? 1 : 0);
    }

    return counts.entries.take(3).map((e) {
      final colors = _typeColors(e.key);
      return Padding(
        padding: const EdgeInsets.only(left: 4),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: colors.bg,
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: colors.border.withValues(alpha: 0.5)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(colors.icon, size: 10, color: colors.fg),
              const SizedBox(width: 3),
              Text(
                '${e.value}',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 9,
                  fontWeight: FontWeight.w700,
                  color: colors.fg,
                ),
              ),
            ],
          ),
        ),
      );
    }).toList();
  }

  String _estimateDuration(DayItinerary day) {
    int totalMin = 0;
    for (final slot in day.timeSlots) {
      totalMin += slot.activity.durationMinutes ?? 60;
    }
    final h = totalMin ~/ 60;
    final m = totalMin % 60;
    if (h == 0) return '${m}m';
    if (m == 0) return '${h}h';
    return '${h}h ${m}m';
  }

  Widget _buildTimeline(DayItinerary day) {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Stack(
        children: [
          // Time rail background
          Positioned(
            left: 12,
            top: 0,
            bottom: 0,
            width: 28,
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant.withValues(alpha: 0.3),
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(8),
                ),
              ),
            ),
          ),
          // Activities
          Column(
            children: day.timeSlots.asMap().entries.map((entry) {
              final index = entry.key;
              final slot = entry.value;
              final isFirst = index == 0;
              final isLast = index == day.timeSlots.length - 1;

              return Column(
                children: [
                  // Transit connector (between items)
                  if (!isFirst && slot.transport != null)
                    _buildTransitConnector(slot.transport!),

                  // Activity row
                  _buildActivityRow(slot, isFirst, isLast, index),
                ],
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildActivityRow(TimeSlot slot, bool isFirst, bool isLast, int index) {
    final type = _activityType(slot.activity.category);
    final colors = _typeColors(type);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline marker
          SizedBox(
            width: 48,
            child: Column(
              children: [
                // Time label
                Padding(
                  padding: const EdgeInsets.only(top: 14),
                  child: Text(
                    _formatTime(slot.startTime),
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 9,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary.withValues(alpha: 0.8),
                    ),
                  ),
                ),
                const SizedBox(height: 4),
                // Dot
                Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [AppColors.primary, AppColors.primaryLight],
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withValues(alpha: 0.3),
                        blurRadius: 4,
                      ),
                    ],
                  ),
                  child: const Icon(Icons.check, size: 10, color: AppColors.white),
                ),
              ],
            ),
          ),

          // Activity card
          Expanded(
            child: _buildActivityCard(slot, type, colors),
          ),
        ],
      ),
    ).animate(delay: Duration(milliseconds: 80 * index))
        .fadeIn(duration: 400.ms)
        .moveY(begin: 8, end: 0);
  }

  Widget _buildActivityCard(TimeSlot slot, String type, _TypeColors colors) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colors.bg.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: colors.border.withValues(alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              // Icon container
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [colors.iconBg, colors.border.withValues(alpha: 0.5)],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(colors.icon, size: 20, color: colors.fg),
              ),
              const SizedBox(width: 12),
              // Title + duration
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      slot.activity.name,
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (slot.activity.durationMinutes != null)
                      Text(
                        slot.activity.formattedDuration,
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                          color: AppColors.textSecondary,
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
          // Location pill
          if (slot.activity.address != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: colors.bg,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: colors.border.withValues(alpha: 0.5)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.location_on, size: 12, color: colors.fg),
                  const SizedBox(width: 4),
                  Flexible(
                    child: Text(
                      slot.activity.address!,
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        color: colors.fg,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ],
          // Description
          if (slot.activity.description != null) ...[
            const SizedBox(height: 6),
            Text(
              slot.activity.description!,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 12,
                color: AppColors.textSecondary,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTransitConnector(Transport transport) {
    final mode = transport.mode.toLowerCase();
    Color modeColor;
    IconData modeIcon;

    switch (mode) {
      case 'walk' || 'walking':
        modeColor = const Color(0xFF64748B); // slate
        modeIcon = Icons.directions_walk;
      case 'train' || 'subway' || 'metro':
        modeColor = AppColors.activityTransport;
        modeIcon = Icons.train;
      case 'bus' || 'transit':
        modeColor = const Color(0xFFF97316); // orange
        modeIcon = Icons.directions_bus;
      case 'car' || 'taxi' || 'drive':
        modeColor = const Color(0xFF64748B); // slate
        modeIcon = Icons.directions_car;
      default:
        modeColor = const Color(0xFF64748B);
        modeIcon = Icons.directions_walk;
    }

    return Padding(
      padding: const EdgeInsets.only(left: 36, right: 12),
      child: Row(
        children: [
          // Dashed line placeholder
          Container(
            width: 24,
            alignment: Alignment.center,
            child: Container(
              width: 1,
              height: 24,
              decoration: BoxDecoration(
                border: Border(
                  left: BorderSide(
                    color: AppColors.textSecondary.withValues(alpha: 0.2),
                    width: 2,
                    style: BorderStyle.solid,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Mode chip
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: modeColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(modeIcon, size: 14, color: modeColor),
          ),
          const SizedBox(width: 8),
          Text(
            transport.formattedDuration,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            mode,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 11,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMealsSection(DayItinerary day) {
    final meals = <MealPOI>[];
    if (day.breakfast != null) meals.add(day.breakfast!);
    if (day.lunch != null) meals.add(day.lunch!);
    if (day.dinner != null) meals.add(day.dinner!);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Column(
        children: meals.map((meal) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _buildMealCard(meal),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildMealCard(MealPOI meal) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.activityMealBg.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.activityMealBorder.withValues(alpha: 0.5),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  AppColors.activityMealBg,
                  AppColors.activityMealBorder.withValues(alpha: 0.5),
                ],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.restaurant, size: 20, color: AppColors.activityMeal),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  meal.name,
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  '${meal.mealType}${meal.cuisine != null ? ' · ${meal.cuisine}' : ''}',
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          if (meal.priceLevelString.isNotEmpty)
            Text(
              meal.priceLevelString,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: AppColors.activityMeal,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildTravelCard(InterCityTravel travel) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.activityTransportBg.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.activityTransportBorder.withValues(alpha: 0.5),
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  AppColors.activityTransportBg,
                  AppColors.activityTransportBorder.withValues(alpha: 0.5),
                ],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              _travelIcon(travel.mode),
              color: AppColors.activityTransport,
              size: 22,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${travel.fromCity} → ${travel.toCity}',
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '${travel.mode} · ${travel.durationDisplay}',
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 13,
                    color: AppColors.textSecondary,
                  ),
                ),
                if (travel.notes != null)
                  Text(
                    travel.notes!,
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 12,
                      color: AppColors.textTertiary,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  IconData _travelIcon(String mode) {
    return switch (mode.toLowerCase()) {
      'train' => Icons.train,
      'bus' => Icons.directions_bus,
      'flight' || 'plane' => Icons.flight,
      'car' || 'drive' => Icons.directions_car,
      'ferry' || 'boat' => Icons.directions_boat,
      _ => Icons.directions,
    };
  }

  // Map POI category to reference activity types
  String _activityType(String category) {
    return switch (category.toLowerCase()) {
      'accommodation' || 'hotel' => 'hotel',
      'restaurant' || 'food' || 'cafe' || 'bar' => 'meal',
      'transportation' || 'transit' => 'transport',
      'shopping' || 'market' => 'shopping',
      _ => 'sightseeing', // attraction, activity, nightlife, etc.
    };
  }

  String _formatTime(String time) {
    // Remove colon and AM/PM for compact display like "0715"
    return time.replaceAll(':', '').replaceAll(' ', '').replaceAll('AM', '').replaceAll('PM', '');
  }

  _TypeColors _typeColors(String type) {
    return switch (type) {
      'hotel' => _TypeColors(
          bg: AppColors.activityHotelBg,
          border: AppColors.activityHotelBorder,
          fg: AppColors.activityHotel,
          iconBg: AppColors.activityHotelBg,
          icon: Icons.hotel,
        ),
      'meal' => _TypeColors(
          bg: AppColors.activityMealBg,
          border: AppColors.activityMealBorder,
          fg: AppColors.activityMeal,
          iconBg: AppColors.activityMealBg,
          icon: Icons.restaurant,
        ),
      'transport' => _TypeColors(
          bg: AppColors.activityTransportBg,
          border: AppColors.activityTransportBorder,
          fg: AppColors.activityTransport,
          iconBg: AppColors.activityTransportBg,
          icon: Icons.train,
        ),
      'shopping' => _TypeColors(
          bg: AppColors.activityShoppingBg,
          border: AppColors.activityShoppingBorder,
          fg: AppColors.activityShopping,
          iconBg: AppColors.activityShoppingBg,
          icon: Icons.shopping_bag,
        ),
      _ => _TypeColors(
          bg: AppColors.activitySightseeingBg,
          border: AppColors.activitySightseeingBorder,
          fg: AppColors.activitySightseeing,
          iconBg: AppColors.activitySightseeingBg,
          icon: Icons.location_on,
        ),
    };
  }
}

class _TypeColors {
  final Color bg;
  final Color border;
  final Color fg;
  final Color iconBg;
  final IconData icon;

  const _TypeColors({
    required this.bg,
    required this.border,
    required this.fg,
    required this.iconBg,
    required this.icon,
  });
}

class _FlatDay {
  final DayItinerary day;
  final String cityName;
  final InterCityTravel? travelToNext;

  const _FlatDay({
    required this.day,
    required this.cityName,
    this.travelToNext,
  });
}
