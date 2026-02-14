import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../domain/entities/itinerary.dart';
import '../../../domain/entities/poi.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import 'poi_detail_card.dart';

/// Vertical timeline for a day's itinerary
class DayTimeline extends StatelessWidget {
  final DayItinerary day;
  final ValueChanged<POI>? onActivityTap;

  const DayTimeline({
    super.key,
    required this.day,
    this.onActivityTap,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Day header
        _DayHeader(day: day),
        const SizedBox(height: AppSpacing.md),

        // Meal: Breakfast
        if (day.breakfast != null)
          _MealCard(
            meal: day.breakfast!,
            index: 0,
          ),

        // Timeline items
        ...day.timeSlots.asMap().entries.map((entry) {
          final index = entry.key;
          final slot = entry.value;
          final isLast = index == day.timeSlots.length - 1;

          return _TimelineItem(
            timeSlot: slot,
            isLast: isLast && day.lunch == null && day.dinner == null,
            index: index,
            onTap: () => onActivityTap?.call(slot.activity),
          );
        }),

        // Meal: Lunch
        if (day.lunch != null)
          _MealCard(
            meal: day.lunch!,
            index: day.timeSlots.length,
          ),

        // Meal: Dinner
        if (day.dinner != null)
          _MealCard(
            meal: day.dinner!,
            index: day.timeSlots.length + 1,
            isLast: true,
          ),
      ],
    );
  }
}

class _DayHeader extends StatelessWidget {
  final DayItinerary day;

  const _DayHeader({required this.day});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.primary,
            AppColors.primaryLight,
          ],
        ),
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(AppSpacing.sm),
            decoration: BoxDecoration(
              color: AppColors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
            ),
            child: Text(
              day.dayLabel,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppColors.white,
              ),
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  day.formattedDate,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: AppColors.white,
                  ),
                ),
                if (day.title != null) ...[
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    day.title!,
                    style: TextStyle(
                      fontSize: 14,
                      color: AppColors.white.withOpacity(0.9),
                    ),
                  ),
                ],
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.sm,
              vertical: AppSpacing.xs,
            ),
            decoration: BoxDecoration(
              color: AppColors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
            ),
            child: Text(
              '${day.activityCount} activities',
              style: const TextStyle(
                fontSize: 12,
                color: AppColors.white,
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn().slideX(begin: -0.1);
  }
}

class _TimelineItem extends StatelessWidget {
  final TimeSlot timeSlot;
  final bool isLast;
  final int index;
  final VoidCallback? onTap;

  const _TimelineItem({
    required this.timeSlot,
    required this.isLast,
    required this.index,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline line and dot
          SizedBox(
            width: 60,
            child: Column(
              children: [
                // Time
                Text(
                  timeSlot.startTime,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: AppSpacing.xs),
                // Dot
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppColors.white,
                      width: 2,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.3),
                        blurRadius: 4,
                      ),
                    ],
                  ),
                ),
                // Line
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 2,
                      color: AppColors.border,
                    ),
                  ),
              ],
            ),
          ),

          // Content
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  POIDetailCard(
                    poi: timeSlot.activity,
                    onTap: onTap,
                  ),

                  // Transport info
                  if (timeSlot.transport != null && !isLast) ...[
                    const SizedBox(height: AppSpacing.sm),
                    _TransportIndicator(transport: timeSlot.transport!),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    ).animate(delay: Duration(milliseconds: index * 100)).fadeIn().slideX(begin: 0.1);
  }
}

class _TransportIndicator extends StatelessWidget {
  final Transport transport;

  const _TransportIndicator({required this.transport});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.sm,
        vertical: AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            transport.modeIcon,
            style: const TextStyle(fontSize: 14),
          ),
          const SizedBox(width: AppSpacing.xs),
          Text(
            transport.formattedDuration,
            style: TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
            ),
          ),
          if (transport.description != null) ...[
            const SizedBox(width: AppSpacing.xs),
            Text(
              transport.description!,
              style: TextStyle(
                fontSize: 12,
                color: AppColors.textTertiary,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _MealCard extends StatelessWidget {
  final MealPOI meal;
  final int index;
  final bool isLast;

  const _MealCard({
    required this.meal,
    required this.index,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    final mealIcon = switch (meal.mealType.toLowerCase()) {
      'breakfast' => '🍳',
      'lunch' => '🥗',
      'dinner' => '🍽️',
      _ => '🍴',
    };

    return Padding(
      padding: const EdgeInsets.only(
        left: 60,
        bottom: AppSpacing.md,
      ),
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: AppColors.secondary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
          border: Border.all(color: AppColors.secondary.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Text(mealIcon, style: const TextStyle(fontSize: 24)),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    meal.mealType.toUpperCase(),
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: AppColors.secondary,
                      letterSpacing: 1,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    meal.name,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (meal.cuisine != null) ...[
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      meal.cuisine!,
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            if (meal.priceLevel != null)
              Text(
                meal.priceLevelString,
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.textTertiary,
                ),
              ),
          ],
        ),
      ),
    ).animate(delay: Duration(milliseconds: index * 100)).fadeIn().slideX(begin: 0.1);
  }
}
