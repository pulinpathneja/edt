import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../config/routes/app_router.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../../controllers/country_controller.dart';
import '../../widgets/molecules/date_range_picker.dart';

/// Trip preferences wizard for country trips
/// Steps: Dates → Group → Vibes → Pacing/Budget
class TripPreferencesScreen extends ConsumerWidget {
  const TripPreferencesScreen({super.key});

  static const _stepTitles = [
    'When are you\ntraveling?',
    'Who\'s coming\nalong?',
    'What\'s your\ntravel vibe?',
    'Set your pace\n& budget',
  ];

  static const _stepSubtitles = [
    'Choose your travel dates to calculate how many days you have',
    'Tell us about your travel group so we can personalize',
    'Select up to 5 vibes that match your ideal trip',
    'How fast do you want to go, and how much to spend?',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(countryControllerProvider);
    final controller = ref.read(countryControllerProvider.notifier);
    final step = state.currentStep;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () {
            if (step > 0) {
              controller.previousStep();
            } else {
              context.go(Routes.countrySelect);
            }
          },
        ),
        actions: [
          if (state.selectedCountry != null)
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Center(
                child: Text(
                  '${state.selectedCountry!.flag} ${state.selectedCountry!.name}',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: AppColors.textSecondary,
                  ),
                ),
              ),
            ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Gold progress bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: _buildProgressBar(step),
            ),
            const SizedBox(height: 24),

            // Title
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _stepTitles[step],
                    style: GoogleFonts.playfairDisplay(
                      fontSize: 28,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                      height: 1.15,
                    ),
                  ).animate().fadeIn(duration: 300.ms).slideX(begin: -0.05),
                  const SizedBox(height: 8),
                  Text(
                    _stepSubtitles[step],
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      color: AppColors.textSecondary,
                      height: 1.4,
                    ),
                  ).animate().fadeIn(delay: 80.ms, duration: 300.ms),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // Step content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: _buildStepContent(step, state, controller),
              ),
            ),

            // Bottom bar
            _buildBottomBar(context, step, state, controller),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressBar(int step) {
    return Column(
      children: [
        Row(
          children: List.generate(4, (i) {
            return Expanded(
              child: Container(
                height: 4,
                margin: EdgeInsets.only(right: i < 3 ? 6 : 0),
                decoration: BoxDecoration(
                  color: i <= step ? AppColors.gold : AppColors.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            );
          }),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              ['Dates', 'Group', 'Vibes', 'Pace & Budget'][step],
              style: GoogleFonts.inter(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: AppColors.gold,
              ),
            ),
            Text(
              'Step ${step + 1} of 4',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: AppColors.textTertiary,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStepContent(int step, CountryTripState state, CountryController controller) {
    return switch (step) {
      0 => _buildDatesStep(state, controller),
      1 => _buildGroupStep(state, controller),
      2 => _buildVibesStep(state, controller),
      3 => _buildPacingBudgetStep(state, controller),
      _ => const SizedBox.shrink(),
    };
  }

  // --- Step 0: Dates ---
  Widget _buildDatesStep(CountryTripState state, CountryController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DateRangePicker(
          startDate: state.startDate,
          endDate: state.endDate,
          onDateRangeSelected: (range) {
            controller.setDateRange(range.start, range.end);
          },
          maxDays: 21,
        ),
        if (state.totalDays > 0) ...[
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surfaceWarm,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.goldLight),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.gold.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.calendar_month, color: AppColors.gold, size: 20),
                ),
                const SizedBox(width: 14),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${state.totalDays} days',
                      style: GoogleFonts.playfairDisplay(
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    Text(
                      'across ${state.selectedCountry?.name ?? 'your trip'}',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  // --- Step 1: Group ---
  Widget _buildGroupStep(CountryTripState state, CountryController controller) {
    final groupTypes = [
      ('solo', 'Solo', Icons.person, 'Just me'),
      ('couple', 'Couple', Icons.favorite, 'Romantic duo'),
      ('family', 'Family', Icons.family_restroom, 'With kids'),
      ('friends', 'Friends', Icons.groups, 'Squad goals'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Group type grid
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.4,
          children: groupTypes.map((type) {
            final isSelected = state.groupType == type.$1;
            return GestureDetector(
              onTap: () => controller.setGroupType(type.$1),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.gold.withOpacity(0.08) : AppColors.surface,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(
                    color: isSelected ? AppColors.gold : AppColors.borderLight,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      type.$3,
                      size: 28,
                      color: isSelected ? AppColors.gold : AppColors.textSecondary,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      type.$2,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                        color: isSelected ? AppColors.primary : AppColors.textPrimary,
                      ),
                    ),
                    Text(
                      type.$4,
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        color: AppColors.textTertiary,
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 24),

        // Group size
        Text(
          'Group Size',
          style: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _CircleButton(
              icon: Icons.remove,
              onTap: state.groupSize > 1
                  ? () => controller.setGroupSize(state.groupSize - 1)
                  : null,
            ),
            const SizedBox(width: 24),
            Text(
              '${state.groupSize}',
              style: GoogleFonts.playfairDisplay(
                fontSize: 36,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(width: 24),
            _CircleButton(
              icon: Icons.add,
              onTap: state.groupSize < 12
                  ? () => controller.setGroupSize(state.groupSize + 1)
                  : null,
            ),
          ],
        ),
      ],
    );
  }

  // --- Step 2: Vibes ---
  Widget _buildVibesStep(CountryTripState state, CountryController controller) {
    final vibes = [
      ('cultural', 'Cultural', '🏛️'),
      ('foodie', 'Foodie', '🍕'),
      ('romantic', 'Romantic', '💕'),
      ('adventure', 'Adventure', '🏔️'),
      ('relaxation', 'Relaxation', '🌴'),
      ('nature', 'Nature', '🌿'),
      ('shopping', 'Shopping', '🛍️'),
      ('nightlife', 'Nightlife', '🌙'),
      ('historical', 'Historical', '📜'),
      ('artsy', 'Artsy', '🎨'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 10,
          runSpacing: 10,
          children: vibes.map((vibe) {
            final isSelected = state.vibes.contains(vibe.$1);
            final vibeColor = AppColors.vibeColor(vibe.$1);
            return GestureDetector(
              onTap: () => controller.toggleVibe(vibe.$1),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? vibeColor.withOpacity(0.12) : AppColors.surface,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                  border: Border.all(
                    color: isSelected ? vibeColor : AppColors.border,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(vibe.$3, style: const TextStyle(fontSize: 16)),
                    const SizedBox(width: 6),
                    Text(
                      vibe.$2,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                        color: isSelected ? vibeColor : AppColors.textPrimary,
                      ),
                    ),
                    if (isSelected) ...[
                      const SizedBox(width: 4),
                      Icon(Icons.check_circle, size: 16, color: vibeColor),
                    ],
                  ],
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 16),
        Text(
          '${state.vibes.length}/5 selected',
          style: GoogleFonts.inter(
            fontSize: 13,
            color: state.vibes.isNotEmpty ? AppColors.gold : AppColors.textTertiary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  // --- Step 3: Pacing & Budget ---
  Widget _buildPacingBudgetStep(CountryTripState state, CountryController controller) {
    final pacingOptions = [
      ('slow', 'Relaxed', 'Take it easy, fewer activities per day', Icons.spa),
      ('moderate', 'Moderate', 'A balanced mix of activity and downtime', Icons.balance),
      ('fast', 'Action-packed', 'See as much as possible each day', Icons.bolt),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Pacing
        Text(
          'Travel Pace',
          style: GoogleFonts.playfairDisplay(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 14),
        ...pacingOptions.map((option) {
          final isSelected = state.pacing == option.$1;
          return Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: GestureDetector(
              onTap: () => controller.setPacing(option.$1),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.gold.withOpacity(0.08) : AppColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isSelected ? AppColors.gold : AppColors.borderLight,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(option.$4, color: isSelected ? AppColors.gold : AppColors.textTertiary, size: 24),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            option.$2,
                            style: GoogleFonts.inter(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: isSelected ? AppColors.primary : AppColors.textPrimary,
                            ),
                          ),
                          Text(
                            option.$3,
                            style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                          ),
                        ],
                      ),
                    ),
                    if (isSelected) const Icon(Icons.check_circle, color: AppColors.gold, size: 22),
                  ],
                ),
              ),
            ),
          );
        }),
        const SizedBox(height: 24),

        // Budget
        Text(
          'Budget Level',
          style: GoogleFonts.playfairDisplay(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          _budgetLabel(state.budgetLevel),
          style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary),
        ),
        const SizedBox(height: 16),
        Row(
          children: List.generate(5, (i) {
            final level = i + 1;
            final isActive = level <= state.budgetLevel;
            return Expanded(
              child: GestureDetector(
                onTap: () => controller.setBudgetLevel(level),
                child: Container(
                  margin: EdgeInsets.only(right: i < 4 ? 8 : 0),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  decoration: BoxDecoration(
                    color: isActive ? AppColors.gold.withOpacity(0.12) : AppColors.surface,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isActive ? AppColors.gold : AppColors.borderLight,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      '\$' * level,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: isActive ? AppColors.gold : AppColors.textTertiary,
                      ),
                    ),
                  ),
                ),
              ),
            );
          }),
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  String _budgetLabel(int level) {
    return switch (level) {
      1 => 'Budget-friendly — hostels, street food, walking',
      2 => 'Economy — affordable hotels, casual dining',
      3 => 'Mid-range — comfortable hotels, nice restaurants',
      4 => 'Premium — boutique hotels, fine dining',
      5 => 'Luxury — 5-star hotels, exclusive experiences',
      _ => '',
    };
  }

  Widget _buildBottomBar(
    BuildContext context,
    int step,
    CountryTripState state,
    CountryController controller,
  ) {
    final isLastStep = step == 3;
    final canProceed = switch (step) {
      0 => state.startDate != null && state.endDate != null,
      1 => state.groupType.isNotEmpty,
      2 => state.vibes.isNotEmpty,
      3 => true,
      _ => false,
    };

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: const Border(top: BorderSide(color: AppColors.borderLight)),
      ),
      child: Row(
        children: [
          if (step > 0)
            Expanded(
              child: SizedBox(
                height: 52,
                child: OutlinedButton(
                  onPressed: () => controller.previousStep(),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: AppColors.border),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: Text(
                    'Back',
                    style: GoogleFonts.inter(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                  ),
                ),
              ),
            ),
          if (step > 0) const SizedBox(width: 12),
          Expanded(
            flex: step > 0 ? 2 : 1,
            child: SizedBox(
              height: 52,
              child: ElevatedButton(
                onPressed: canProceed
                    ? () {
                        if (isLastStep) {
                          controller.fetchAllocations();
                          context.go(Routes.countryAllocations);
                        } else {
                          controller.nextStep();
                        }
                      }
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: canProceed ? AppColors.primary : AppColors.surfaceVariant,
                  foregroundColor: canProceed ? Colors.white : AppColors.textDisabled,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  elevation: 0,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      isLastStep ? 'See Options' : 'Continue',
                      style: GoogleFonts.inter(fontSize: 15, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(width: 6),
                    Icon(isLastStep ? Icons.auto_awesome : Icons.arrow_forward, size: 18),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CircleButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onTap;

  const _CircleButton({required this.icon, this.onTap});

  @override
  Widget build(BuildContext context) {
    final isEnabled = onTap != null;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: isEnabled ? AppColors.surfaceWarm : AppColors.surfaceVariant,
          shape: BoxShape.circle,
          border: Border.all(color: isEnabled ? AppColors.border : AppColors.borderLight),
        ),
        child: Icon(
          icon,
          color: isEnabled ? AppColors.textPrimary : AppColors.textDisabled,
          size: 22,
        ),
      ),
    );
  }
}
