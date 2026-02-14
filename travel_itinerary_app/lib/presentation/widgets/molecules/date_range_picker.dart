import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';

/// Date range picker for trip dates
class DateRangePicker extends StatelessWidget {
  final DateTime? startDate;
  final DateTime? endDate;
  final ValueChanged<DateTimeRange>? onDateRangeSelected;
  final DateTime? firstDate;
  final DateTime? lastDate;
  final int? maxDays;

  const DateRangePicker({
    super.key,
    this.startDate,
    this.endDate,
    this.onDateRangeSelected,
    this.firstDate,
    this.lastDate,
    this.maxDays,
  });

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('MMM d, yyyy');
    final hasStartDate = startDate != null;
    final hasEndDate = endDate != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            // Start date
            Expanded(
              child: _DateField(
                label: 'Start Date',
                value: hasStartDate ? dateFormat.format(startDate!) : null,
                placeholder: 'Select date',
                icon: Icons.calendar_today_outlined,
                onTap: () => _showDatePicker(context, true),
              ),
            ),
            const SizedBox(width: AppSpacing.md),

            // Arrow indicator
            Icon(
              Icons.arrow_forward,
              color: AppColors.textTertiary,
              size: 20,
            ),
            const SizedBox(width: AppSpacing.md),

            // End date
            Expanded(
              child: _DateField(
                label: 'End Date',
                value: hasEndDate ? dateFormat.format(endDate!) : null,
                placeholder: 'Select date',
                icon: Icons.calendar_today_outlined,
                onTap: () => _showDatePicker(context, false),
              ),
            ),
          ],
        ),

        // Trip duration indicator
        if (hasStartDate && hasEndDate) ...[
          const SizedBox(height: AppSpacing.sm),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.sm,
              vertical: AppSpacing.xs,
            ),
            decoration: BoxDecoration(
              color: AppColors.accent.withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.schedule,
                  size: 14,
                  color: AppColors.accent,
                ),
                const SizedBox(width: AppSpacing.xs),
                Text(
                  '${_calculateDays()} days',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.accent,
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  int _calculateDays() {
    if (startDate == null || endDate == null) return 0;
    return endDate!.difference(startDate!).inDays + 1;
  }

  Future<void> _showDatePicker(BuildContext context, bool isStartDate) async {
    final now = DateTime.now();
    final effectiveFirstDate = firstDate ?? now;
    final effectiveLastDate = lastDate ?? now.add(const Duration(days: 365));

    // For range picker
    final initialDateRange = DateTimeRange(
      start: startDate ?? now,
      end: endDate ?? now.add(const Duration(days: 5)),
    );

    final result = await showDateRangePicker(
      context: context,
      initialDateRange: (startDate != null && endDate != null)
          ? initialDateRange
          : null,
      firstDate: effectiveFirstDate,
      lastDate: effectiveLastDate,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: Theme.of(context).colorScheme.copyWith(
                  primary: AppColors.primary,
                  onPrimary: AppColors.textOnPrimary,
                  surface: AppColors.surface,
                  onSurface: AppColors.textPrimary,
                ),
          ),
          child: child!,
        );
      },
    );

    if (result != null && onDateRangeSelected != null) {
      // Check max days constraint
      if (maxDays != null) {
        final days = result.end.difference(result.start).inDays + 1;
        if (days > maxDays!) {
          // Adjust end date if exceeds max days
          final adjustedEnd = result.start.add(Duration(days: maxDays! - 1));
          onDateRangeSelected!(DateTimeRange(
            start: result.start,
            end: adjustedEnd,
          ));
          return;
        }
      }
      onDateRangeSelected!(result);
    }
  }
}

class _DateField extends StatelessWidget {
  final String label;
  final String? value;
  final String placeholder;
  final IconData icon;
  final VoidCallback onTap;

  const _DateField({
    required this.label,
    this.value,
    required this.placeholder,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final hasValue = value != null;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: AppColors.textTertiary,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: AppSpacing.xs),
            Row(
              children: [
                Icon(
                  icon,
                  size: 18,
                  color: hasValue ? AppColors.primary : AppColors.textTertiary,
                ),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text(
                    value ?? placeholder,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: hasValue ? FontWeight.w500 : FontWeight.w400,
                      color: hasValue
                          ? AppColors.textPrimary
                          : AppColors.textTertiary,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
