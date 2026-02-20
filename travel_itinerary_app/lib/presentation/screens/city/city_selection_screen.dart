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

/// City selection screen for single-city trips
class CitySelectionScreen extends ConsumerStatefulWidget {
  const CitySelectionScreen({super.key});

  @override
  ConsumerState<CitySelectionScreen> createState() => _CitySelectionScreenState();
}

class _CitySelectionScreenState extends ConsumerState<CitySelectionScreen> {
  String? _selectedCityId;

  @override
  Widget build(BuildContext context) {
    final homeState = ref.watch(homeControllerProvider);

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
                    'Pick a City',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 32,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ).animate().fadeIn(duration: 400.ms).slideX(begin: -0.05),
                  const SizedBox(height: 8),
                  Text(
                    'Choose a city for your single-city deep-dive itinerary',
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

            // City grid
            Expanded(
              child: homeState.isLoading
                  ? const Center(child: CircularProgressIndicator(color: AppColors.gold))
                  : homeState.countries.isEmpty
                      ? _buildEmptyState()
                      : _buildCityGrid(homeState.countries),
            ),

            // Continue button
            _buildBottomBar(context),
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
          const Icon(Icons.location_off, size: 64, color: AppColors.textTertiary),
          const SizedBox(height: 16),
          Text(
            'No cities available',
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

  Widget _buildCityGrid(List<Country> countries) {
    // Flatten all cities from all countries
    final allCities = <_CityWithCountry>[];
    for (final country in countries) {
      for (final city in country.cities) {
        allCities.add(_CityWithCountry(city: city, country: country));
      }
    }

    return GridView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.85,
      ),
      itemCount: allCities.length,
      itemBuilder: (context, index) {
        final item = allCities[index];
        final isSelected = _selectedCityId == item.city.id;
        return _CityCard(
          city: item.city,
          country: item.country,
          isSelected: isSelected,
          onTap: () => setState(() => _selectedCityId = item.city.id),
          index: index,
        );
      },
    );
  }

  Widget _buildBottomBar(BuildContext context) {
    final hasSelection = _selectedCityId != null;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: const Border(top: BorderSide(color: AppColors.borderLight)),
        boxShadow: [BoxShadow(color: AppColors.shadowLight, blurRadius: 10, offset: const Offset(0, -4))],
      ),
      child: SizedBox(
        width: double.infinity,
        height: 54,
        child: ElevatedButton(
          onPressed: hasSelection ? () => context.go(Routes.tripCreation) : null,
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
                hasSelection ? 'Plan This City' : 'Select a City',
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

class _CityWithCountry {
  final CountryCity city;
  final Country country;

  const _CityWithCountry({required this.city, required this.country});
}

class _CityCard extends StatelessWidget {
  final CountryCity city;
  final Country country;
  final bool isSelected;
  final VoidCallback onTap;
  final int index;

  const _CityCard({
    required this.city,
    required this.country,
    required this.isSelected,
    required this.onTap,
    required this.index,
  });

  @override
  Widget build(BuildContext context) {
    // Assign gradient colors based on country
    final cityGradients = {
      'italy': [const Color(0xFF4A7C59), const Color(0xFF6B9E78)],
      'france': [const Color(0xFF5B8DA0), const Color(0xFF7AAAB8)],
      'spain': [const Color(0xFFC44536), const Color(0xFFD4685C)],
      'japan': [const Color(0xFFB85C5C), const Color(0xFFCC8080)],
      'united_kingdom': [const Color(0xFF7A6B5D), const Color(0xFF9A8B7D)],
    };

    final gradient = cityGradients[country.id] ?? [AppColors.primary, AppColors.primaryLight];

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.gold : Colors.transparent,
            width: isSelected ? 3 : 0,
          ),
          boxShadow: isSelected
              ? [BoxShadow(color: AppColors.gold.withOpacity(0.25), blurRadius: 16, offset: const Offset(0, 6))]
              : [BoxShadow(color: AppColors.shadowLight, blurRadius: 8, offset: const Offset(0, 3))],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(isSelected ? 17 : 20),
          child: Stack(
            children: [
              // Gradient background
              Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: gradient,
                  ),
                ),
              ),

              // Content
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Country flag
                    Text(country.flag, style: const TextStyle(fontSize: 24)),
                    const Spacer(),
                    // City name
                    Text(
                      city.name,
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      country.name,
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 12,
                        color: Colors.white.withOpacity(0.75),
                      ),
                    ),
                    const SizedBox(height: 8),
                    // Info row
                    Row(
                      children: [
                        Icon(Icons.schedule, size: 12, color: Colors.white.withOpacity(0.7)),
                        const SizedBox(width: 4),
                        Text(
                          '${city.idealDays}d ideal',
                          style: GoogleFonts.plusJakartaSans(
                            fontSize: 11,
                            color: Colors.white.withOpacity(0.7),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Selection check
              if (isSelected)
                Positioned(
                  top: 12,
                  right: 12,
                  child: Container(
                    width: 28,
                    height: 28,
                    decoration: const BoxDecoration(
                      color: AppColors.gold,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check, size: 16, color: Colors.white),
                  ),
                ),
            ],
          ),
        ),
      ),
    ).animate(delay: Duration(milliseconds: 150 + index * 60)).fadeIn(duration: 350.ms).scale(begin: const Offset(0.95, 0.95));
  }
}
