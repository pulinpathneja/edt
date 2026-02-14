import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';
import '../models/city.dart';
import '../models/itinerary.dart';
import 'city_selection_screen.dart';
import 'itinerary_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  List<City> _cities = [];
  List<Itinerary> _recentItineraries = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final cities = await _apiService.getCities();
      final itineraries = await _apiService.getItineraries(limit: 5);
      setState(() {
        _cities = cities;
        _recentItineraries = itineraries;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : RefreshIndicator(
                onRefresh: _loadData,
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildHeader(),
                        const SizedBox(height: 24),
                        _buildSearchBar(),
                        const SizedBox(height: 32),
                        _buildQuickActions(),
                        const SizedBox(height: 32),
                        _buildPopularDestinations(),
                        const SizedBox(height: 32),
                        _buildRecentTrips(),
                      ],
                    ),
                  ),
                ),
              ),
      ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Hello, Traveler',
              style: AppTheme.textTheme.headlineLarge,
            ),
            const SizedBox(height: 4),
            Text(
              'Where to next?',
              style: AppTheme.textTheme.bodyLarge,
            ),
          ],
        ),
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: AppTheme.primaryDark,
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          child: const Icon(Icons.person, color: Colors.white),
        ),
      ],
    );
  }

  Widget _buildSearchBar() {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const CitySelectionScreen()),
        );
      },
      child: Container(
        height: 56,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(AppRadius.pill),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(Icons.search, color: AppTheme.textSecondary),
            const SizedBox(width: 12),
            Text(
              'Search destinations...',
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _QuickActionCard(
          icon: Icons.add_circle_outline,
          label: 'Plan Trip',
          color: const Color(0xFF6C63FF),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const CitySelectionScreen()),
            );
          },
        ),
        _QuickActionCard(
          icon: Icons.explore,
          label: 'Explore',
          color: const Color(0xFFFF6B6B),
          onTap: () {},
        ),
        _QuickActionCard(
          icon: Icons.bookmark_outline,
          label: 'Saved',
          color: const Color(0xFF4ECDC4),
          onTap: () {},
        ),
        _QuickActionCard(
          icon: Icons.history,
          label: 'History',
          color: const Color(0xFFFFBE0B),
          onTap: () {},
        ),
      ],
    );
  }

  Widget _buildPopularDestinations() {
    final displayCities = _cities.isNotEmpty
        ? _cities
        : [
            City(id: 'rome', name: 'Rome', country: 'Italy'),
            City(id: 'paris', name: 'Paris', country: 'France'),
            City(id: 'tokyo', name: 'Tokyo', country: 'Japan'),
            City(id: 'barcelona', name: 'Barcelona', country: 'Spain'),
          ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Popular Destinations', style: AppTheme.textTheme.headlineMedium),
            TextButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const CitySelectionScreen()),
                );
              },
              child: const Text('See all'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 200,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: displayCities.length,
            itemBuilder: (context, index) {
              final city = displayCities[index];
              return _DestinationCard(
                city: city,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => CitySelectionScreen(preselectedCity: city),
                    ),
                  );
                },
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildRecentTrips() {
    if (_recentItineraries.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Your Trips', style: AppTheme.textTheme.headlineMedium),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(AppRadius.lg),
            ),
            child: Column(
              children: [
                Icon(Icons.luggage, size: 48, color: AppTheme.textSecondary),
                const SizedBox(height: 16),
                Text(
                  'No trips planned yet',
                  style: AppTheme.textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Start planning your next adventure',
                  style: AppTheme.textTheme.bodyMedium,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const CitySelectionScreen()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryDark,
                  ),
                  child: const Text('Plan a Trip'),
                ),
              ],
            ),
          ),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Recent Trips', style: AppTheme.textTheme.headlineMedium),
        const SizedBox(height: 16),
        ..._recentItineraries.map((itinerary) => _TripCard(
              itinerary: itinerary,
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ItineraryDetailScreen(itinerary: itinerary),
                  ),
                );
              },
            )),
      ],
    );
  }

  Widget _buildBottomNav() {
    return Container(
      height: 80,
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
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _NavItem(icon: Icons.home, label: 'Home', isSelected: true),
          _NavItem(icon: Icons.explore, label: 'Explore'),
          _NavItem(icon: Icons.bookmark_outline, label: 'Saved'),
          _NavItem(icon: Icons.person_outline, label: 'Profile'),
        ],
      ),
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(AppRadius.lg),
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: AppTheme.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}

class _DestinationCard extends StatelessWidget {
  final City city;
  final VoidCallback onTap;

  const _DestinationCard({required this.city, required this.onTap});

  String get _cityImage {
    final images = {
      'rome': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400',
      'paris': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400',
      'tokyo': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400',
      'barcelona': 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400',
      'london': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400',
    };
    return images[city.id.toLowerCase()] ?? images['rome']!;
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 160,
        margin: const EdgeInsets.only(right: 16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          child: Stack(
            fit: StackFit.expand,
            children: [
              Image.network(
                _cityImage,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  color: AppTheme.primaryDark.withOpacity(0.3),
                  child: const Icon(Icons.location_city, size: 48, color: Colors.white),
                ),
              ),
              Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      Colors.black.withOpacity(0.7),
                    ],
                  ),
                ),
              ),
              Positioned(
                bottom: 16,
                left: 16,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      city.name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      city.country,
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TripCard extends StatelessWidget {
  final Itinerary itinerary;
  final VoidCallback onTap;

  const _TripCard({required this.itinerary, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(16),
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
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: AppTheme.primaryDark.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppRadius.md),
              ),
              child: const Icon(Icons.map, color: AppTheme.primaryDark),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    itinerary.cityName ?? 'Trip',
                    style: AppTheme.textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${itinerary.totalDays} days | ${itinerary.costText}',
                    style: AppTheme.textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: AppTheme.textSecondary),
          ],
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;

  const _NavItem({
    required this.icon,
    required this.label,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          icon,
          color: isSelected ? AppTheme.primaryDark : AppTheme.textSecondary,
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: isSelected ? AppTheme.primaryDark : AppTheme.textSecondary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
          ),
        ),
      ],
    );
  }
}
