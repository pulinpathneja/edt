import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';
import '../models/city.dart';
import 'trip_planning_screen.dart';

class CitySelectionScreen extends StatefulWidget {
  final City? preselectedCity;

  const CitySelectionScreen({super.key, this.preselectedCity});

  @override
  State<CitySelectionScreen> createState() => _CitySelectionScreenState();
}

class _CitySelectionScreenState extends State<CitySelectionScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _searchController = TextEditingController();
  List<City> _cities = [];
  List<City> _filteredCities = [];
  bool _isLoading = true;
  City? _selectedCity;

  final List<_CityPreview> _defaultCities = [
    _CityPreview('Rome', 'Italy', 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400'),
    _CityPreview('Paris', 'France', 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400'),
    _CityPreview('Tokyo', 'Japan', 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400'),
    _CityPreview('Barcelona', 'Spain', 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400'),
    _CityPreview('London', 'United Kingdom', 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400'),
  ];

  @override
  void initState() {
    super.initState();
    _selectedCity = widget.preselectedCity;
    _loadCities();
  }

  Future<void> _loadCities() async {
    try {
      final cities = await _apiService.getCities();
      setState(() {
        _cities = cities;
        _filteredCities = cities;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        // Use default cities if API fails
        _cities = _defaultCities
            .map((c) => City(id: c.name.toLowerCase(), name: c.name, country: c.country))
            .toList();
        _filteredCities = _cities;
        _isLoading = false;
      });
    }
  }

  void _filterCities(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredCities = _cities;
      } else {
        _filteredCities = _cities
            .where((c) =>
                c.name.toLowerCase().contains(query.toLowerCase()) ||
                c.country.toLowerCase().contains(query.toLowerCase()))
            .toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppTheme.primaryDark),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Choose Destination',
          style: AppTheme.textTheme.headlineMedium,
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(20),
            child: TextField(
              controller: _searchController,
              onChanged: _filterCities,
              decoration: InputDecoration(
                hintText: 'Search cities...',
                prefixIcon: const Icon(Icons.search, color: AppTheme.textSecondary),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(AppRadius.lg),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              ),
            ),
          ),

          // Selected City Indicator
          if (_selectedCity != null)
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryDark.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppRadius.md),
                border: Border.all(color: AppTheme.primaryDark, width: 2),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: AppTheme.primaryDark),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _selectedCity!.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 16,
                            color: AppTheme.primaryDark,
                          ),
                        ),
                        Text(
                          _selectedCity!.country,
                          style: TextStyle(
                            fontSize: 14,
                            color: AppTheme.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: AppTheme.primaryDark),
                    onPressed: () => setState(() => _selectedCity = null),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 16),

          // Cities Grid
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : GridView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      childAspectRatio: 0.85,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                    ),
                    itemCount: _filteredCities.length,
                    itemBuilder: (context, index) {
                      final city = _filteredCities[index];
                      final isSelected = _selectedCity?.id == city.id;
                      return _CityCard(
                        city: city,
                        isSelected: isSelected,
                        onTap: () {
                          setState(() => _selectedCity = city);
                        },
                      );
                    },
                  ),
          ),

          // Continue Button
          Padding(
            padding: const EdgeInsets.all(20),
            child: SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _selectedCity == null
                    ? null
                    : () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => TripPlanningScreen(city: _selectedCity!),
                          ),
                        );
                      },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryDark,
                  disabledBackgroundColor: Colors.grey.shade300,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppRadius.pill),
                  ),
                ),
                child: const Text(
                  'Continue',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CityPreview {
  final String name;
  final String country;
  final String imageUrl;

  _CityPreview(this.name, this.country, this.imageUrl);
}

class _CityCard extends StatelessWidget {
  final City city;
  final bool isSelected;
  final VoidCallback onTap;

  const _CityCard({
    required this.city,
    required this.isSelected,
    required this.onTap,
  });

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
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: isSelected
              ? Border.all(color: AppTheme.primaryDark, width: 3)
              : null,
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
              if (isSelected)
                Positioned(
                  top: 12,
                  right: 12,
                  child: Container(
                    width: 28,
                    height: 28,
                    decoration: const BoxDecoration(
                      color: AppTheme.primaryDark,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check, color: Colors.white, size: 18),
                  ),
                ),
              Positioned(
                bottom: 16,
                left: 16,
                right: 16,
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
                    const SizedBox(height: 2),
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
