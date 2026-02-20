import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../config/routes/app_router.dart';
import '../../../domain/entities/country.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../../controllers/home_controller.dart';
import '../../controllers/country_controller.dart';

/// Country selection screen with premium card design
class CountrySelectionScreen extends ConsumerWidget {
  const CountrySelectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final homeState = ref.watch(homeControllerProvider);
    final countryState = ref.watch(countryControllerProvider);
    final controller = ref.read(countryControllerProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => context.go(Routes.home),
        ),
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 0, 24, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Choose Your\nDestination',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 32,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                      height: 1.15,
                    ),
                  ).animate().fadeIn(duration: 400.ms).slideX(begin: -0.05),
                  const SizedBox(height: 8),
                  Text(
                    'Select a country to start planning your multi-city adventure',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 15,
                      color: AppColors.textSecondary,
                      height: 1.4,
                    ),
                  ).animate().fadeIn(delay: 100.ms, duration: 400.ms),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Country list
            Expanded(
              child: homeState.isLoading
                  ? const Center(child: CircularProgressIndicator(color: AppColors.gold))
                  : homeState.countries.isEmpty
                      ? _buildEmptyState()
                      : _buildCountryList(context, ref, homeState.countries, countryState, controller),
            ),

            // Continue button
            _buildBottomBar(context, countryState),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.public_off, size: 64, color: AppColors.textTertiary),
          const SizedBox(height: 16),
          Text(
            'No countries available',
            style: GoogleFonts.plusJakartaSans(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCountryList(
    BuildContext context,
    WidgetRef ref,
    List<Country> countries,
    CountryTripState state,
    CountryController controller,
  ) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      itemCount: countries.length,
      itemBuilder: (context, index) {
        final country = countries[index];
        final isSelected = state.selectedCountry?.id == country.id;
        return _CountryCard(
          country: country,
          isSelected: isSelected,
          onTap: () => controller.selectCountry(country),
          index: index,
        );
      },
    );
  }

  Widget _buildBottomBar(BuildContext context, CountryTripState state) {
    final hasSelection = state.selectedCountry != null;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: const Border(top: BorderSide(color: AppColors.borderLight)),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 10,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: SizedBox(
        width: double.infinity,
        height: 54,
        child: ElevatedButton(
          onPressed: hasSelection ? () => context.go(Routes.countryPreferences) : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: hasSelection ? AppColors.primary : AppColors.surfaceVariant,
            foregroundColor: hasSelection ? Colors.white : AppColors.textDisabled,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 0,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                hasSelection ? 'Continue with ${state.selectedCountry!.name}' : 'Select a Country',
                style: GoogleFonts.plusJakartaSans(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              if (hasSelection) ...[
                const SizedBox(width: 8),
                const Icon(Icons.arrow_forward, size: 20),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _CountryCard extends StatelessWidget {
  final Country country;
  final bool isSelected;
  final VoidCallback onTap;
  final int index;

  const _CountryCard({
    required this.country,
    required this.isSelected,
    required this.onTap,
    required this.index,
  });

  @override
  Widget build(BuildContext context) {
    final countryGradients = {
      'italy': [const Color(0xFF4A7C59), const Color(0xFF6B9E78)],
      'france': [const Color(0xFF5B8DA0), const Color(0xFF7AAAB8)],
      'spain': [const Color(0xFFC44536), const Color(0xFFD4685C)],
      'japan': [const Color(0xFFB85C5C), const Color(0xFFCC8080)],
      'united_kingdom': [const Color(0xFF7A6B5D), const Color(0xFF9A8B7D)],
    };

    final gradient = countryGradients[country.id] ?? [AppColors.primary, AppColors.primaryLight];

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOutCubic,
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(
              color: isSelected ? AppColors.gold : AppColors.borderLight,
              width: isSelected ? 2.5 : 1,
            ),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: AppColors.gold.withOpacity(0.2),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ]
                : [
                    BoxShadow(
                      color: AppColors.shadowLight,
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Row(
              children: [
                // Flag + gradient bg
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: gradient,
                    ),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Center(
                    child: Text(country.flag, style: const TextStyle(fontSize: 30)),
                  ),
                ),
                const SizedBox(width: 16),

                // Country info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        country.name,
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${country.cityCount} cities available',
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 13,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 6),
                      // City preview chips
                      Wrap(
                        spacing: 6,
                        children: country.cities
                            .take(3)
                            .map((c) => Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: AppColors.surfaceWarm,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    c.name,
                                    style: GoogleFonts.plusJakartaSans(
                                      fontSize: 11,
                                      color: AppColors.textSecondary,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ))
                            .toList(),
                      ),
                    ],
                  ),
                ),

                // Selection indicator
                AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: isSelected ? AppColors.gold : Colors.transparent,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: isSelected ? AppColors.gold : AppColors.border,
                      width: 2,
                    ),
                  ),
                  child: isSelected
                      ? const Icon(Icons.check, size: 16, color: Colors.white)
                      : null,
                ),
              ],
            ),
          ),
        ),
      ),
    ).animate(delay: Duration(milliseconds: 200 + index * 100)).fadeIn(duration: 400.ms).slideX(begin: 0.1);
  }
}
