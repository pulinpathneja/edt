import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';
import '../models/country.dart';
import 'country_trip_preferences_screen.dart';

class CountrySelectionScreen extends StatefulWidget {
  const CountrySelectionScreen({super.key});

  @override
  State<CountrySelectionScreen> createState() => _CountrySelectionScreenState();
}

class _CountrySelectionScreenState extends State<CountrySelectionScreen> {
  final ApiService _apiService = ApiService();
  List<Country> _countries = [];
  bool _isLoading = true;
  Country? _selectedCountry;

  final _countryFlags = {
    'italy': '\u{1F1EE}\u{1F1F9}',
    'france': '\u{1F1EB}\u{1F1F7}',
    'spain': '\u{1F1EA}\u{1F1F8}',
    'japan': '\u{1F1EF}\u{1F1F5}',
    'uk': '\u{1F1EC}\u{1F1E7}',
  };

  final _countryImages = {
    'italy': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400',
    'france': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400',
    'spain': 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400',
    'japan': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400',
    'uk': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400',
  };

  final List<_CountryPreview> _defaultCountries = [
    _CountryPreview('Italy', 'EUR', 3),
    _CountryPreview('France', 'EUR', 4),
    _CountryPreview('Spain', 'EUR', 3),
    _CountryPreview('Japan', 'JPY', 5),
    _CountryPreview('UK', 'GBP', 2),
  ];

  @override
  void initState() {
    super.initState();
    _loadCountries();
  }

  Future<void> _loadCountries() async {
    try {
      final countries = await _apiService.getCountries();
      setState(() {
        _countries = countries;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _countries = _defaultCountries
            .map((c) => Country(
                  id: c.name.toLowerCase(),
                  name: c.name,
                  currency: c.currency,
                ))
            .toList();
        _isLoading = false;
      });
    }
  }

  String _getFlagEmoji(String countryId) {
    return _countryFlags[countryId.toLowerCase()] ?? '';
  }

  String _getCountryImage(String countryId) {
    return _countryImages[countryId.toLowerCase()] ?? _countryImages['italy']!;
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
          'Choose Country',
          style: AppTheme.textTheme.headlineMedium,
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Selected Country Indicator
          if (_selectedCountry != null)
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
                          '${_getFlagEmoji(_selectedCountry!.id)} ${_selectedCountry!.name}',
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 16,
                            color: AppTheme.primaryDark,
                          ),
                        ),
                        Text(
                          '${_selectedCountry!.cityCount} cities \u00B7 ${_selectedCountry!.currency}',
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
                    onPressed: () => setState(() => _selectedCountry = null),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 16),

          // Countries Grid
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
                    itemCount: _countries.length,
                    itemBuilder: (context, index) {
                      final country = _countries[index];
                      final isSelected = _selectedCountry?.id == country.id;
                      return _CountryCard(
                        country: country,
                        isSelected: isSelected,
                        flagEmoji: _getFlagEmoji(country.id),
                        imageUrl: _getCountryImage(country.id),
                        onTap: () {
                          setState(() => _selectedCountry = country);
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
                onPressed: _selectedCountry == null
                    ? null
                    : () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => CountryTripPreferencesScreen(
                              country: _selectedCountry!,
                            ),
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

class _CountryPreview {
  final String name;
  final String currency;
  final int cityCount;

  _CountryPreview(this.name, this.currency, this.cityCount);
}

class _CountryCard extends StatelessWidget {
  final Country country;
  final bool isSelected;
  final String flagEmoji;
  final String imageUrl;
  final VoidCallback onTap;

  const _CountryCard({
    required this.country,
    required this.isSelected,
    required this.flagEmoji,
    required this.imageUrl,
    required this.onTap,
  });

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
                imageUrl,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  color: AppTheme.primaryDark.withOpacity(0.3),
                  child: const Icon(Icons.public, size: 48, color: Colors.white),
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
                top: 12,
                left: 12,
                child: Text(
                  flagEmoji,
                  style: const TextStyle(fontSize: 28),
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
                      country.name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${country.cityCount} cities',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      country.currency,
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 13,
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
