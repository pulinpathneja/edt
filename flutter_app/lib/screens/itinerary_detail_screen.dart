import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../theme/app_theme.dart';
import '../models/itinerary.dart';
import '../models/poi.dart';
import '../services/api_service.dart';
import 'poi_detail_screen.dart';

class ItineraryDetailScreen extends StatefulWidget {
  final Itinerary itinerary;

  const ItineraryDetailScreen({super.key, required this.itinerary});

  @override
  State<ItineraryDetailScreen> createState() => _ItineraryDetailScreenState();
}

class _ItineraryDetailScreenState extends State<ItineraryDetailScreen> {
  late Itinerary _itinerary;
  bool _isLoading = false;
  bool _showMap = false;
  int _selectedDayIndex = 0;
  final Set<int> _expandedDays = {0}; // First day expanded by default
  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    _itinerary = widget.itinerary;
    // Expand all days by default
    for (int i = 0; i < _itinerary.days.length; i++) {
      _expandedDays.add(i);
    }
  }

  Future<void> _refreshItinerary() async {
    setState(() => _isLoading = true);
    try {
      final api = ApiService();
      final refreshed = await api.getItinerary(_itinerary.id);
      setState(() {
        _itinerary = refreshed;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to refresh: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: _showMap ? _buildMapView() : _buildTimelineView(),
      bottomNavigationBar: _buildBottomBar(),
    );
  }

  Widget _buildTimelineView() {
    return RefreshIndicator(
      onRefresh: _refreshItinerary,
      color: AppTheme.primaryDark,
      child: CustomScrollView(
        slivers: [
          // App Bar with Hero Image
          _buildAppBar(),

          // Day Sections (Expandable)
          SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final day = _itinerary.days[index];
                return _DaySection(
                  day: day,
                  isExpanded: _expandedDays.contains(index),
                  onToggle: () {
                    setState(() {
                      if (_expandedDays.contains(index)) {
                        _expandedDays.remove(index);
                      } else {
                        _expandedDays.add(index);
                      }
                    });
                  },
                  onDaySelected: () {
                    setState(() {
                      _selectedDayIndex = index;
                    });
                  },
                );
              },
              childCount: _itinerary.days.length,
            ),
          ),

          // Bottom padding
          const SliverPadding(padding: EdgeInsets.only(bottom: 100)),
        ],
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      expandedHeight: 220,
      pinned: true,
      backgroundColor: AppTheme.primaryDark,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back, color: Colors.white),
        onPressed: () => Navigator.pop(context),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.share, color: Colors.white),
          onPressed: () {},
        ),
        IconButton(
          icon: const Icon(Icons.bookmark_outline, color: Colors.white),
          onPressed: () {},
        ),
      ],
      flexibleSpace: FlexibleSpaceBar(
        background: Stack(
          fit: StackFit.expand,
          children: [
            // Background gradient
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    AppTheme.primaryDark,
                    AppTheme.primaryDark.withBlue(100),
                  ],
                ),
              ),
            ),
            // Content
            Positioned(
              bottom: 60,
              left: 20,
              right: 20,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _itinerary.cityName ?? 'Your Trip',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _InfoChip(
                        icon: Icons.calendar_today,
                        label: '${_itinerary.totalDays} days',
                      ),
                      const SizedBox(width: 12),
                      _InfoChip(
                        icon: Icons.attach_money,
                        label: _itinerary.costText,
                      ),
                      const SizedBox(width: 12),
                      _InfoChip(
                        icon: Icons.place,
                        label: '${_totalPOIs} places',
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Expand/Collapse All Button
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        if (_expandedDays.length == _itinerary.days.length) {
                          _expandedDays.clear();
                        } else {
                          _expandedDays.clear();
                          for (int i = 0; i < _itinerary.days.length; i++) {
                            _expandedDays.add(i);
                          }
                        }
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(AppRadius.pill),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            _expandedDays.length == _itinerary.days.length
                                ? Icons.unfold_less
                                : Icons.unfold_more,
                            color: Colors.white,
                            size: 16,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            _expandedDays.length == _itinerary.days.length
                                ? 'Collapse All'
                                : 'Expand All',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMapView() {
    final day = _itinerary.days[_selectedDayIndex];
    final markers = <Marker>[];
    final points = <LatLng>[];

    for (int i = 0; i < day.items.length; i++) {
      final item = day.items[i];
      if (item.poi != null) {
        final latLng = LatLng(item.poi!.latitude, item.poi!.longitude);
        points.add(latLng);
        markers.add(
          Marker(
            point: latLng,
            width: 40,
            height: 40,
            child: Container(
              decoration: BoxDecoration(
                color: AppTheme.primaryDark,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 2),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    blurRadius: 4,
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  '${i + 1}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
            ),
          ),
        );
      }
    }

    return Scaffold(
      appBar: AppBar(
        backgroundColor: AppTheme.primaryDark,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white),
          onPressed: () => setState(() => _showMap = false),
        ),
        title: Text(
          'Day ${day.dayNumber} Route',
          style: const TextStyle(color: Colors.white),
        ),
        actions: [
          // Day selector
          PopupMenuButton<int>(
            icon: const Icon(Icons.calendar_today, color: Colors.white),
            onSelected: (index) {
              setState(() => _selectedDayIndex = index);
            },
            itemBuilder: (context) {
              return _itinerary.days.asMap().entries.map((entry) {
                return PopupMenuItem<int>(
                  value: entry.key,
                  child: Text('Day ${entry.value.dayNumber}'),
                );
              }).toList();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Map
          Expanded(
            flex: 3,
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: points.isNotEmpty
                    ? points.first
                    : const LatLng(41.9028, 12.4964), // Default Rome
                initialZoom: 14,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.edt.app',
                ),
                // Route polyline
                if (points.length > 1)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: points,
                        strokeWidth: 4,
                        color: AppTheme.primaryDark.withOpacity(0.7),
                        isDotted: true,
                      ),
                    ],
                  ),
                // Markers
                MarkerLayer(markers: markers),
              ],
            ),
          ),
          // POI List
          Expanded(
            flex: 2,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: day.items.length,
                itemBuilder: (context, index) {
                  final item = day.items[index];
                  return _MapPOICard(
                    item: item,
                    index: index + 1,
                    onTap: () {
                      if (item.poi != null) {
                        _mapController.move(
                          LatLng(item.poi!.latitude, item.poi!.longitude),
                          16,
                        );
                      }
                    },
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  int get _totalPOIs {
    return _itinerary.days.fold(0, (sum, day) => sum + day.items.length);
  }

  Widget _buildBottomBar() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.edit),
              label: const Text('Edit'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                side: const BorderSide(color: AppTheme.primaryDark),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            flex: 2,
            child: ElevatedButton.icon(
              onPressed: () {
                setState(() => _showMap = !_showMap);
              },
              icon: Icon(_showMap ? Icons.list : Icons.map),
              label: Text(_showMap ? 'View Timeline' : 'View on Map'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryDark,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Info Chip Widget
class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(AppRadius.pill),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 14),
          const SizedBox(width: 6),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

// Day Section Widget (Expandable)
class _DaySection extends StatelessWidget {
  final ItineraryDay day;
  final bool isExpanded;
  final VoidCallback onToggle;
  final VoidCallback onDaySelected;

  const _DaySection({
    required this.day,
    required this.isExpanded,
    required this.onToggle,
    required this.onDaySelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Day Header (Tap to expand/collapse)
          InkWell(
            onTap: onToggle,
            borderRadius: BorderRadius.circular(AppRadius.lg),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  // Day badge
                  Container(
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          AppTheme.primaryDark,
                          AppTheme.primaryDark.withBlue(100),
                        ],
                      ),
                      borderRadius: BorderRadius.circular(AppRadius.md),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Day',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.8),
                            fontSize: 10,
                          ),
                        ),
                        Text(
                          '${day.dayNumber}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  // Day info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          day.dateText,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: AppTheme.textPrimary,
                          ),
                        ),
                        if (day.theme != null)
                          Text(
                            day.theme!,
                            style: TextStyle(
                              fontSize: 13,
                              color: AppTheme.textSecondary,
                            ),
                          ),
                        const SizedBox(height: 4),
                        Text(
                          '${day.items.length} activities',
                          style: TextStyle(
                            fontSize: 12,
                            color: AppTheme.textSecondary.withOpacity(0.7),
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Expand/Collapse icon
                  Icon(
                    isExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                    color: AppTheme.textSecondary,
                  ),
                ],
              ),
            ),
          ),
          // Day Content (Timeline)
          if (isExpanded)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Column(
                children: List.generate(day.items.length, (index) {
                  final item = day.items[index];
                  final isLast = index == day.items.length - 1;
                  final isFirst = index == 0;
                  return _TimelineItem(
                    item: item,
                    isFirst: isFirst,
                    isLast: isLast,
                  );
                }),
              ),
            ),
        ],
      ),
    );
  }
}

// Timeline Item Widget with Photo
class _TimelineItem extends StatelessWidget {
  final ItineraryItem item;
  final bool isFirst;
  final bool isLast;

  const _TimelineItem({
    required this.item,
    required this.isFirst,
    required this.isLast,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Travel time indicator (before this item, except first)
        if (!isFirst && item.travelTimeFromPrevious != null && item.travelTimeFromPrevious! > 0)
          _TravelIndicator(
            minutes: item.travelTimeFromPrevious!,
            mode: item.travelMode ?? 'walk',
          ),

        // POI Card
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Timeline
              SizedBox(
                width: 50,
                child: Column(
                  children: [
                    // Time
                    Text(
                      item.startTime ?? '',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.primaryDark,
                      ),
                    ),
                    const SizedBox(height: 8),
                    // Dot
                    Container(
                      width: 14,
                      height: 14,
                      decoration: BoxDecoration(
                        color: AppTheme.primaryDark,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primaryDark.withOpacity(0.3),
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
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          color: Colors.grey.shade300,
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 12),

              // Content Card with Photo
              Expanded(
                child: GestureDetector(
                  onTap: () {
                    if (item.poi != null) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => POIDetailScreen(poi: item.poi!),
                        ),
                      );
                    }
                  },
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppTheme.background,
                      borderRadius: BorderRadius.circular(AppRadius.md),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Photo
                        if (item.poi?.imageUrl != null)
                          ClipRRect(
                            borderRadius: const BorderRadius.vertical(
                              top: Radius.circular(AppRadius.md),
                            ),
                            child: CachedNetworkImage(
                              imageUrl: item.poi!.imageUrl!,
                              height: 120,
                              width: double.infinity,
                              fit: BoxFit.cover,
                              placeholder: (context, url) => Container(
                                height: 120,
                                color: Colors.grey.shade200,
                                child: const Center(
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: AppTheme.primaryDark,
                                  ),
                                ),
                              ),
                              errorWidget: (context, url, error) => Container(
                                height: 120,
                                color: Colors.grey.shade200,
                                child: Icon(
                                  _getCategoryIcon(item.poi?.category),
                                  size: 40,
                                  color: Colors.grey.shade400,
                                ),
                              ),
                            ),
                          )
                        else
                          Container(
                            height: 80,
                            decoration: BoxDecoration(
                              color: AppTheme.primaryDark.withOpacity(0.1),
                              borderRadius: const BorderRadius.vertical(
                                top: Radius.circular(AppRadius.md),
                              ),
                            ),
                            child: Center(
                              child: Icon(
                                _getCategoryIcon(item.poi?.category),
                                size: 32,
                                color: AppTheme.primaryDark,
                              ),
                            ),
                          ),

                        // Content
                        Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Name & Must See
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      item.poi?.name ?? 'Activity',
                                      style: const TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.w600,
                                        color: AppTheme.textPrimary,
                                      ),
                                    ),
                                  ),
                                  if (item.poi?.isMustSee == true)
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 6,
                                        vertical: 2,
                                      ),
                                      decoration: BoxDecoration(
                                        color: Colors.amber.withOpacity(0.2),
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: const Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Icon(Icons.star, size: 10, color: Colors.amber),
                                          SizedBox(width: 2),
                                          Text(
                                            'Must See',
                                            style: TextStyle(
                                              fontSize: 9,
                                              fontWeight: FontWeight.w600,
                                              color: Colors.amber,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 6),

                              // Description
                              if (item.poi?.description != null)
                                Text(
                                  item.poi!.description!,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: AppTheme.textSecondary,
                                  ),
                                ),
                              const SizedBox(height: 8),

                              // Details Row
                              Row(
                                children: [
                                  Icon(
                                    _getCategoryIcon(item.poi?.category),
                                    size: 12,
                                    color: AppTheme.textSecondary,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    item.poi?.category ?? 'Activity',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: AppTheme.textSecondary,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Icon(
                                    Icons.access_time,
                                    size: 12,
                                    color: AppTheme.textSecondary,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    item.poi?.durationText ?? '',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: AppTheme.textSecondary,
                                    ),
                                  ),
                                  if (item.poi?.costLevel != null) ...[
                                    const SizedBox(width: 12),
                                    Text(
                                      item.poi!.costText,
                                      style: TextStyle(
                                        fontSize: 11,
                                        color: AppTheme.textSecondary,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  IconData _getCategoryIcon(String? category) {
    switch (category?.toLowerCase()) {
      case 'restaurant':
        return Icons.restaurant;
      case 'attraction':
        return Icons.museum;
      case 'activity':
        return Icons.directions_run;
      case 'shopping':
        return Icons.shopping_bag;
      case 'nightlife':
        return Icons.nightlife;
      case 'cafe':
        return Icons.local_cafe;
      case 'park':
        return Icons.park;
      default:
        return Icons.place;
    }
  }
}

// Travel Indicator Widget
class _TravelIndicator extends StatelessWidget {
  final int minutes;
  final String mode;

  const _TravelIndicator({required this.minutes, required this.mode});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 50, bottom: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppRadius.pill),
              border: Border.all(color: Colors.blue.withOpacity(0.3)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  mode == 'transit' ? Icons.directions_transit : Icons.directions_walk,
                  size: 14,
                  color: Colors.blue,
                ),
                const SizedBox(width: 6),
                Text(
                  '$minutes min $mode',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Colors.blue,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Map POI Card Widget
class _MapPOICard extends StatelessWidget {
  final ItineraryItem item;
  final int index;
  final VoidCallback onTap;

  const _MapPOICard({
    required this.item,
    required this.index,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppTheme.background,
          borderRadius: BorderRadius.circular(AppRadius.md),
        ),
        child: Row(
          children: [
            // Number badge
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: AppTheme.primaryDark,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  '$index',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.poi?.name ?? 'Activity',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    '${item.startTime ?? ''} • ${item.poi?.durationText ?? ''}',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            // Travel time
            if (item.travelTimeFromPrevious != null && item.travelTimeFromPrevious! > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '${item.travelTimeFromPrevious}m',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Colors.blue,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
