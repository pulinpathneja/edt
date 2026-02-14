import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../theme/colors/app_colors.dart';
import '../../../../theme/spacing/app_spacing.dart';
import '../../../widgets/molecules/date_range_picker.dart';

/// Step 1: Destination and dates
class DestinationStep extends StatelessWidget {
  final String destination;
  final DateTime? startDate;
  final DateTime? endDate;
  final ValueChanged<String> onDestinationChanged;
  final ValueChanged<DateTimeRange> onDateRangeChanged;
  final int maxDays;

  const DestinationStep({
    super.key,
    required this.destination,
    this.startDate,
    this.endDate,
    required this.onDestinationChanged,
    required this.onDateRangeChanged,
    this.maxDays = 30,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Destination input
        Text(
          'Destination',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate()
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.sm),

        TextFormField(
          initialValue: destination,
          decoration: InputDecoration(
            hintText: 'e.g., Rome, Italy',
            prefixIcon: const Icon(Icons.location_on_outlined),
            suffixIcon: destination.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () => onDestinationChanged(''),
                  )
                : null,
          ),
          textCapitalization: TextCapitalization.words,
          onChanged: onDestinationChanged,
        )
            .animate()
            .fadeIn(delay: const Duration(milliseconds: 100))
            .slideX(begin: -0.1),

        const SizedBox(height: AppSpacing.xl),

        // Travel dates
        Text(
          'Travel Dates',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 200))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.sm),

        DateRangePicker(
          startDate: startDate,
          endDate: endDate,
          onDateRangeSelected: onDateRangeChanged,
          firstDate: DateTime.now(),
          lastDate: DateTime.now().add(const Duration(days: 365)),
          maxDays: maxDays,
        )
            .animate(delay: const Duration(milliseconds: 300))
            .fadeIn()
            .slideX(begin: -0.1),

        const SizedBox(height: AppSpacing.xl),

        // Popular destinations suggestion
        Text(
          'Popular Destinations',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 400))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.sm),

        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            'Paris, France',
            'Tokyo, Japan',
            'Rome, Italy',
            'Barcelona, Spain',
            'New York, USA',
            'Bali, Indonesia',
          ].asMap().entries.map((entry) {
            final index = entry.key;
            final city = entry.value;
            return _DestinationChip(
              label: city,
              isSelected: destination == city,
              onTap: () => onDestinationChanged(city),
            )
                .animate(delay: Duration(milliseconds: 450 + index * 50))
                .fadeIn()
                .scale(begin: const Offset(0.9, 0.9));
          }).toList(),
        ),
      ],
    );
  }
}

class _DestinationChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _DestinationChip({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        decoration: BoxDecoration(
          color: isSelected
              ? AppColors.primary.withOpacity(0.15)
              : AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.border,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 14,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            color: isSelected ? AppColors.primary : AppColors.textPrimary,
          ),
        ),
      ),
    );
  }
}
