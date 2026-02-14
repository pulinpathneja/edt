import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../config/routes/app_router.dart';
import '../../../domain/entities/itinerary.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../../controllers/itinerary_view_controller.dart';
import '../../widgets/atoms/app_loading_indicator.dart';
import '../../widgets/organisms/day_timeline.dart';

/// Itinerary view screen with day tabs and timeline
class ItineraryViewScreen extends ConsumerStatefulWidget {
  final String itineraryId;

  const ItineraryViewScreen({
    super.key,
    required this.itineraryId,
  });

  @override
  ConsumerState<ItineraryViewScreen> createState() => _ItineraryViewScreenState();
}

class _ItineraryViewScreenState extends ConsumerState<ItineraryViewScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 1, vsync: this);

    // Check if we have a current itinerary from generation
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final currentItinerary = ref.read(currentItineraryProvider);
      if (currentItinerary != null && currentItinerary.id == widget.itineraryId) {
        ref
            .read(itineraryViewControllerProvider(widget.itineraryId).notifier)
            .setItinerary(currentItinerary);
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _updateTabController(int length, int currentIndex) {
    if (_tabController.length != length) {
      _tabController.dispose();
      _tabController = TabController(
        length: length,
        vsync: this,
        initialIndex: currentIndex.clamp(0, length - 1),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(itineraryViewControllerProvider(widget.itineraryId));
    final controller = ref.read(itineraryViewControllerProvider(widget.itineraryId).notifier);

    // Update tab controller when itinerary loads
    if (state.itinerary != null && state.totalDays > 0) {
      _updateTabController(state.totalDays, state.selectedDayIndex);
    }

    // Sync tab controller with state
    ref.listen(
      itineraryViewControllerProvider(widget.itineraryId),
      (previous, current) {
        if (current.itinerary != null &&
            _tabController.length == current.totalDays &&
            _tabController.index != current.selectedDayIndex) {
          _tabController.animateTo(current.selectedDayIndex);
        }
      },
    );

    if (state.isLoading) {
      return const Scaffold(
        body: Center(
          child: AppLoadingIndicator(
            size: LoadingIndicatorSize.large,
            message: 'Loading your itinerary...',
          ),
        ),
      );
    }

    if (state.errorMessage != null || state.itinerary == null) {
      return _buildErrorState(state.errorMessage);
    }

    final itinerary = state.itinerary!;

    return Scaffold(
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) => [
          _buildSliverAppBar(itinerary),
          _buildDayTabs(itinerary, controller),
        ],
        body: TabBarView(
          controller: _tabController,
          children: itinerary.days.map((day) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(AppSpacing.md),
              child: DayTimeline(day: day),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildSliverAppBar(Itinerary itinerary) {
    return SliverAppBar(
      expandedHeight: 280,
      pinned: true,
      leading: IconButton(
        icon: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppColors.black.withOpacity(0.3),
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.arrow_back, color: AppColors.white),
        ),
        onPressed: () => context.go(Routes.onboarding),
      ),
      actions: [
        IconButton(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.black.withOpacity(0.3),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.share, color: AppColors.white),
          ),
          onPressed: () {
            // Handle share
          },
        ),
        IconButton(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.black.withOpacity(0.3),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.more_vert, color: AppColors.white),
          ),
          onPressed: () {
            // Handle more options
          },
        ),
      ],
      flexibleSpace: FlexibleSpaceBar(
        background: Stack(
          fit: StackFit.expand,
          children: [
            // Hero image
            if (itinerary.heroImageUrl != null)
              CachedNetworkImage(
                imageUrl: itinerary.heroImageUrl!,
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: AppColors.primary,
                ),
                errorWidget: (context, url, error) => Container(
                  color: AppColors.primary,
                  child: const Icon(
                    Icons.image_not_supported,
                    color: AppColors.white,
                    size: 48,
                  ),
                ),
              )
            else
              Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [AppColors.primary, AppColors.primaryDark],
                  ),
                ),
              ),

            // Gradient overlay
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    AppColors.black.withOpacity(0.7),
                  ],
                ),
              ),
            ),

            // Content
            Positioned(
              left: AppSpacing.md,
              right: AppSpacing.md,
              bottom: AppSpacing.lg,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    itinerary.fullDestination,
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.w700,
                      color: AppColors.white,
                    ),
                  ).animate().fadeIn().slideY(begin: 0.2),

                  const SizedBox(height: AppSpacing.sm),

                  Row(
                    children: [
                      _InfoChip(
                        icon: Icons.calendar_today,
                        label: itinerary.dateRange,
                      ),
                      const SizedBox(width: AppSpacing.sm),
                      _InfoChip(
                        icon: Icons.schedule,
                        label: '${itinerary.totalDays} days',
                      ),
                    ],
                  ).animate(delay: const Duration(milliseconds: 100)).fadeIn().slideY(begin: 0.2),

                  const SizedBox(height: AppSpacing.sm),

                  Wrap(
                    spacing: AppSpacing.xs,
                    children: itinerary.vibes.take(4).map((vibe) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.sm,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                        ),
                        child: Text(
                          vibe,
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppColors.white,
                          ),
                        ),
                      );
                    }).toList(),
                  ).animate(delay: const Duration(milliseconds: 200)).fadeIn().slideY(begin: 0.2),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDayTabs(Itinerary itinerary, ItineraryViewController controller) {
    return SliverPersistentHeader(
      pinned: true,
      delegate: _DayTabsDelegate(
        tabBar: TabBar(
          controller: _tabController,
          isScrollable: true,
          onTap: controller.selectDay,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textTertiary,
          indicatorColor: AppColors.primary,
          indicatorWeight: 3,
          tabs: itinerary.days.map((day) {
            return Tab(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    day.dayLabel,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    day.formattedDate.split(',').first,
                    style: const TextStyle(
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildErrorState(String? errorMessage) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(Routes.onboarding),
        ),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: AppColors.textTertiary,
              ),
              const SizedBox(height: AppSpacing.md),
              Text(
                'Failed to load itinerary',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                errorMessage ?? 'Please try again',
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSpacing.lg),
              ElevatedButton(
                onPressed: () => context.go(Routes.tripCreation),
                child: const Text('Create New Trip'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({
    required this.icon,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.sm,
        vertical: AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: AppColors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 14,
            color: AppColors.white,
          ),
          const SizedBox(width: AppSpacing.xs),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.white,
            ),
          ),
        ],
      ),
    );
  }
}

class _DayTabsDelegate extends SliverPersistentHeaderDelegate {
  final TabBar tabBar;

  _DayTabsDelegate({required this.tabBar});

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: AppColors.surface,
      child: tabBar,
    );
  }

  @override
  double get maxExtent => tabBar.preferredSize.height;

  @override
  double get minExtent => tabBar.preferredSize.height;

  @override
  bool shouldRebuild(covariant _DayTabsDelegate oldDelegate) {
    return tabBar != oldDelegate.tabBar;
  }
}
