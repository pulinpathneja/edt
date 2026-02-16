import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../config/routes/app_router.dart';
import '../../../domain/entities/country_itinerary.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../../controllers/country_controller.dart';

/// Country itinerary view showing the generated multi-city plan
class CountryItineraryScreen extends ConsumerStatefulWidget {
  const CountryItineraryScreen({super.key});

  @override
  ConsumerState<CountryItineraryScreen> createState() => _CountryItineraryScreenState();
}

class _CountryItineraryScreenState extends ConsumerState<CountryItineraryScreen>
    with TickerProviderStateMixin {
  TabController? _tabController;
  int _lastTabCount = 0;

  @override
  void dispose() {
    _tabController?.dispose();
    super.dispose();
  }

  TabController _getTabController(int length) {
    if (_tabController == null || _lastTabCount != length) {
      _tabController?.dispose();
      _lastTabCount = length;
      _tabController = TabController(length: length, vsync: this);
    }
    return _tabController!;
  }

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
              color: AppColors.gold,
              strokeWidth: 3,
            ),
          ),
          const SizedBox(height: 28),
          Text(
            'Generating Your Itinerary',
            style: GoogleFonts.playfairDisplay(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ).animate().fadeIn(delay: 200.ms),
          const SizedBox(height: 10),
          Text(
            'Curating the perfect experience\nacross multiple cities...',
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(fontSize: 15, color: AppColors.textSecondary, height: 1.5),
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
              style: GoogleFonts.playfairDisplay(fontSize: 22, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
            ),
            const SizedBox(height: 8),
            Text(error, textAlign: TextAlign.center, style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => ref.read(countryControllerProvider.notifier).generateItinerary(),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildItineraryView(BuildContext context, CountryItinerary itinerary) {
    final tabController = _getTabController(itinerary.cityItineraries.length);

    return NestedScrollView(
      headerSliverBuilder: (context, innerBoxIsScrolled) {
        return [
          // Rich header
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            backgroundColor: AppColors.primary,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => context.go(Routes.home),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.share_outlined, color: Colors.white),
                onPressed: () {},
              ),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF8B6914), Color(0xFF5C4510)],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 56, 24, 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          '${itinerary.countryName} Adventure',
                          style: GoogleFonts.playfairDisplay(
                            fontSize: 28,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            _InfoChip(icon: Icons.calendar_today, label: '${itinerary.totalDays} days'),
                            const SizedBox(width: 10),
                            _InfoChip(icon: Icons.location_city, label: '${itinerary.cityItineraries.length} cities'),
                            const SizedBox(width: 10),
                            _InfoChip(icon: Icons.star, label: '${itinerary.totalActivities} activities'),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),

          // City tabs
          SliverPersistentHeader(
            delegate: _CityTabBarDelegate(
              tabController: tabController,
              cities: itinerary.cityItineraries.map((c) => c.cityName).toList(),
            ),
            pinned: true,
          ),
        ];
      },
      body: TabBarView(
        controller: tabController,
        children: itinerary.cityItineraries.map((citySummary) {
          return _buildCityTab(citySummary);
        }).toList(),
      ),
    );
  }

  Widget _buildCityTab(CityItinerarySummary citySummary) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      children: [
        // City highlight card
        _buildCityHighlightCard(citySummary),
        const SizedBox(height: 20),

        // Day-by-day
        ...citySummary.dayItineraries.asMap().entries.map((entry) {
          final dayIndex = entry.key;
          final day = entry.value;
          return _buildDayCard(day, dayIndex);
        }),

        // Travel to next city
        if (citySummary.travelToNext != null) ...[
          _buildTravelCard(citySummary.travelToNext!),
          const SizedBox(height: 16),
        ],
      ],
    );
  }

  Widget _buildCityHighlightCard(CityItinerarySummary city) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppColors.surfaceWarm, AppColors.surface],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.goldLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            city.cityName,
            style: GoogleFonts.playfairDisplay(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            '${city.days} days · ${city.dayItineraries.fold(0, (sum, d) => sum + d.activityCount)} activities',
            style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary),
          ),
          if (city.highlights != null && city.highlights!.isNotEmpty) ...[
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: city.highlights!.take(4).map((h) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: AppColors.gold.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    h,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: AppColors.primary,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    ).animate().fadeIn(duration: 400.ms);
  }

  Widget _buildDayCard(dynamic day, int dayIndex) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.borderLight),
          boxShadow: [BoxShadow(color: AppColors.shadowLight, blurRadius: 6, offset: const Offset(0, 2))],
        ),
        child: Theme(
          data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
          child: ExpansionTile(
            tilePadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
            childrenPadding: const EdgeInsets.fromLTRB(18, 0, 18, 16),
            leading: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.gold.withOpacity(0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Text(
                  '${day.dayNumber}',
                  style: GoogleFonts.playfairDisplay(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: AppColors.gold,
                  ),
                ),
              ),
            ),
            title: Text(
              day.title ?? 'Day ${day.dayNumber}',
              style: GoogleFonts.inter(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            subtitle: Text(
              day.formattedDate,
              style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
            ),
            children: [
              if (day.summary != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Text(
                    day.summary!,
                    style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary, height: 1.5),
                  ),
                ),
              // Time slots
              ...day.timeSlots.map<Widget>((slot) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(
                        width: 52,
                        child: Text(
                          slot.startTime,
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.gold,
                          ),
                        ),
                      ),
                      Container(
                        width: 2,
                        height: 40,
                        color: AppColors.goldLight,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              slot.activity.name,
                              style: GoogleFonts.inter(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            if (slot.activity.description != null)
                              Text(
                                slot.activity.description!,
                                style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ],
          ),
        ),
      ),
    ).animate(delay: Duration(milliseconds: 100 + dayIndex * 80)).fadeIn(duration: 300.ms).slideX(begin: 0.05);
  }

  Widget _buildTravelCard(InterCityTravel travel) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surfaceWarm,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.goldLight),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.gold.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              _travelIcon(travel.mode),
              color: AppColors.gold,
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
                  style: GoogleFonts.inter(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '${travel.mode} · ${travel.durationDisplay}',
                  style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary),
                ),
                if (travel.notes != null)
                  Text(
                    travel.notes!,
                    style: GoogleFonts.inter(fontSize: 12, color: AppColors.textTertiary),
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
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.white.withOpacity(0.9)),
          const SizedBox(width: 5),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: Colors.white.withOpacity(0.9),
            ),
          ),
        ],
      ),
    );
  }
}

class _CityTabBarDelegate extends SliverPersistentHeaderDelegate {
  final TabController tabController;
  final List<String> cities;

  _CityTabBarDelegate({required this.tabController, required this.cities});

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: AppColors.background,
      child: TabBar(
        controller: tabController,
        isScrollable: cities.length > 3,
        labelColor: AppColors.primary,
        unselectedLabelColor: AppColors.textTertiary,
        indicatorColor: AppColors.gold,
        indicatorWeight: 3,
        labelStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600),
        unselectedLabelStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w400),
        tabs: cities.map((city) => Tab(text: city)).toList(),
      ),
    );
  }

  @override
  double get maxExtent => 48;

  @override
  double get minExtent => 48;

  @override
  bool shouldRebuild(covariant _CityTabBarDelegate oldDelegate) =>
      cities != oldDelegate.cities || tabController != oldDelegate.tabController;
}
