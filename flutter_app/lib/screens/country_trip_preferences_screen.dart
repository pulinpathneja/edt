import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';
import '../models/country.dart';
import '../models/allocation.dart';
import 'allocation_options_screen.dart';

class CountryTripPreferencesScreen extends StatefulWidget {
  final Country country;

  const CountryTripPreferencesScreen({super.key, required this.country});

  @override
  State<CountryTripPreferencesScreen> createState() =>
      _CountryTripPreferencesScreenState();
}

class _CountryTripPreferencesScreenState
    extends State<CountryTripPreferencesScreen> {
  final ApiService _apiService = ApiService();
  int _currentStep = 0;
  bool _isLoading = false;

  // Step 0: Dates
  DateTime _startDate = DateTime.now().add(const Duration(days: 7));
  DateTime _endDate = DateTime.now().add(const Duration(days: 14));

  // Step 1: Group
  String _groupType = 'couple';
  int _groupSize = 2;
  bool _hasKids = false;
  bool _hasSeniors = false;

  // Step 2: Vibes
  List<String> _selectedVibes = [];

  // Step 3: Preferences
  String _pacing = 'moderate';
  int _budgetLevel = 3;
  List<String> _mustIncludeCities = [];
  List<String> _excludeCities = [];

  final List<_VibeOption> _vibeOptions = [
    _VibeOption('cultural', 'Cultural', Icons.museum),
    _VibeOption('romantic', 'Romantic', Icons.favorite),
    _VibeOption('adventure', 'Adventure', Icons.terrain),
    _VibeOption('foodie', 'Foodie', Icons.restaurant),
    _VibeOption('relaxation', 'Relaxation', Icons.spa),
    _VibeOption('photography', 'Photography', Icons.camera_alt),
    _VibeOption('nightlife', 'Nightlife', Icons.nightlife),
    _VibeOption('nature', 'Nature', Icons.park),
    _VibeOption('shopping', 'Shopping', Icons.shopping_bag),
    _VibeOption('wellness', 'Wellness', Icons.self_improvement),
  ];

  final List<_GroupOption> _groupOptions = [
    _GroupOption('solo', 'Solo', Icons.person),
    _GroupOption('couple', 'Couple', Icons.favorite),
    _GroupOption('family', 'Family', Icons.family_restroom),
    _GroupOption('friends', 'Friends', Icons.group),
    _GroupOption('honeymoon', 'Honeymoon', Icons.celebration),
    _GroupOption('business', 'Business', Icons.business_center),
  ];

  int get _tripDays => _endDate.difference(_startDate).inDays + 1;

  final List<String> _stepLabels = ['Dates', 'Group', 'Vibes', 'Pacing/Budget'];

  Future<void> _getOptions() async {
    setState(() => _isLoading = true);

    try {
      final response = await _apiService.getCityAllocations(
        country: widget.country.id,
        totalDays: _tripDays,
        startDate: _startDate.toIso8601String().split('T').first,
        endDate: _endDate.toIso8601String().split('T').first,
        groupType: _groupType,
        vibes: _selectedVibes,
        pacing: _pacing,
        mustIncludeCities: _mustIncludeCities.isNotEmpty ? _mustIncludeCities : null,
        excludeCities: _excludeCities.isNotEmpty ? _excludeCities : null,
      );

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => AllocationOptionsScreen(
              allocationResponse: response,
              country: widget.country.id,
              startDate: _startDate,
              endDate: _endDate,
              groupType: _groupType,
              groupSize: _groupSize,
              vibes: _selectedVibes,
              budgetLevel: _budgetLevel,
              pacing: _pacing,
              hasKids: _hasKids,
              hasSeniors: _hasSeniors,
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to get allocation options: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
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
          'Plan Your Trip',
          style: AppTheme.textTheme.headlineMedium,
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Progress Bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            child: Column(
              children: [
                Row(
                  children: List.generate(4, (index) {
                    return Expanded(
                      child: Container(
                        height: 4,
                        margin: const EdgeInsets.symmetric(horizontal: 2),
                        decoration: BoxDecoration(
                          color: index <= _currentStep
                              ? AppTheme.primaryDark
                              : Colors.grey.shade300,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    );
                  }),
                ),
                const SizedBox(height: 8),
                Row(
                  children: List.generate(4, (index) {
                    return Expanded(
                      child: Text(
                        _stepLabels[index],
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: index == _currentStep
                              ? FontWeight.w600
                              : FontWeight.w400,
                          color: index <= _currentStep
                              ? AppTheme.primaryDark
                              : AppTheme.textSecondary,
                        ),
                      ),
                    );
                  }),
                ),
              ],
            ),
          ),

          // Country Header
          Container(
            margin: const EdgeInsets.all(20),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(AppRadius.lg),
            ),
            child: Row(
              children: [
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryDark.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppRadius.md),
                  ),
                  child: const Icon(Icons.flag, color: AppTheme.primaryDark),
                ),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.country.name,
                      style: AppTheme.textTheme.titleLarge,
                    ),
                    Text(
                      '${widget.country.cities.length} cities available',
                      style: AppTheme.textTheme.bodyMedium,
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Step Content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: _buildStepContent(),
            ),
          ),

          // Navigation Buttons
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                if (_currentStep > 0)
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => setState(() => _currentStep--),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: const BorderSide(color: AppTheme.primaryDark),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(AppRadius.pill),
                        ),
                      ),
                      child: const Text('Back'),
                    ),
                  ),
                if (_currentStep > 0) const SizedBox(width: 16),
                Expanded(
                  flex: 2,
                  child: ElevatedButton(
                    onPressed: _isLoading
                        ? null
                        : () {
                            if (_currentStep < 3) {
                              setState(() => _currentStep++);
                            } else {
                              _getOptions();
                            }
                          },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryDark,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(AppRadius.pill),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation(Colors.white),
                            ),
                          )
                        : Text(
                            _currentStep < 3 ? 'Continue' : 'Get Options',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepContent() {
    switch (_currentStep) {
      case 0:
        return _buildDatesStep();
      case 1:
        return _buildGroupStep();
      case 2:
        return _buildVibesStep();
      case 3:
        return _buildPreferencesStep();
      default:
        return const SizedBox();
    }
  }

  // ==================== STEP 0: DATES ====================

  Widget _buildDatesStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('When are you traveling?', style: AppTheme.textTheme.headlineMedium),
        const SizedBox(height: 8),
        Text('Select your travel dates', style: AppTheme.textTheme.bodyLarge),
        const SizedBox(height: 24),

        // Start Date
        _DateSelector(
          label: 'Start Date',
          date: _startDate,
          onTap: () async {
            final date = await showDatePicker(
              context: context,
              initialDate: _startDate,
              firstDate: DateTime.now(),
              lastDate: DateTime.now().add(const Duration(days: 365)),
            );
            if (date != null) {
              setState(() {
                _startDate = date;
                if (_endDate.isBefore(_startDate)) {
                  _endDate = _startDate.add(const Duration(days: 7));
                }
              });
            }
          },
        ),
        const SizedBox(height: 16),

        // End Date
        _DateSelector(
          label: 'End Date',
          date: _endDate,
          onTap: () async {
            final date = await showDatePicker(
              context: context,
              initialDate: _endDate,
              firstDate: _startDate,
              lastDate: DateTime.now().add(const Duration(days: 365)),
            );
            if (date != null) {
              setState(() => _endDate = date);
            }
          },
        ),
        const SizedBox(height: 24),

        // Trip Duration Summary
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.primaryDark.withOpacity(0.1),
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.calendar_today, color: AppTheme.primaryDark),
              const SizedBox(width: 12),
              Text(
                '$_tripDays ${_tripDays == 1 ? 'day' : 'days'} in ${widget.country.name}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.primaryDark,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ==================== STEP 1: GROUP ====================

  Widget _buildGroupStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("Who's traveling?", style: AppTheme.textTheme.headlineMedium),
        const SizedBox(height: 8),
        Text('Select your travel group', style: AppTheme.textTheme.bodyLarge),
        const SizedBox(height: 24),

        // Group Type Grid
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            childAspectRatio: 1.1,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: _groupOptions.length,
          itemBuilder: (context, index) {
            final option = _groupOptions[index];
            final isSelected = _groupType == option.id;
            return GestureDetector(
              onTap: () => setState(() => _groupType = option.id),
              child: Container(
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primaryDark : Colors.white,
                  borderRadius: BorderRadius.circular(AppRadius.md),
                  border: Border.all(
                    color:
                        isSelected ? AppTheme.primaryDark : Colors.grey.shade200,
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      option.icon,
                      color:
                          isSelected ? Colors.white : AppTheme.textSecondary,
                      size: 28,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      option.label,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color:
                            isSelected ? Colors.white : AppTheme.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 24),

        // Group Size
        Text('Group Size', style: AppTheme.textTheme.titleMedium),
        const SizedBox(height: 12),
        Row(
          children: [
            IconButton(
              onPressed:
                  _groupSize > 1 ? () => setState(() => _groupSize--) : null,
              icon: const Icon(Icons.remove_circle_outline),
              color: AppTheme.primaryDark,
            ),
            Container(
              width: 60,
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(AppRadius.md),
              ),
              child: Text(
                '$_groupSize',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            IconButton(
              onPressed:
                  _groupSize < 20 ? () => setState(() => _groupSize++) : null,
              icon: const Icon(Icons.add_circle_outline),
              color: AppTheme.primaryDark,
            ),
          ],
        ),
        const SizedBox(height: 24),

        // Special Needs
        _CheckboxTile(
          title: 'Traveling with kids',
          subtitle: 'We\'ll include kid-friendly activities',
          value: _hasKids,
          onChanged: (v) => setState(() => _hasKids = v ?? false),
        ),
        const SizedBox(height: 12),
        _CheckboxTile(
          title: 'Traveling with seniors',
          subtitle: 'We\'ll consider accessibility needs',
          value: _hasSeniors,
          onChanged: (v) => setState(() => _hasSeniors = v ?? false),
        ),
      ],
    );
  }

  // ==================== STEP 2: VIBES ====================

  Widget _buildVibesStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What\'s your vibe?', style: AppTheme.textTheme.headlineMedium),
        const SizedBox(height: 8),
        Text('Select up to 3 vibes for your trip',
            style: AppTheme.textTheme.bodyLarge),
        const SizedBox(height: 24),

        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: _vibeOptions.map((vibe) {
            final isSelected = _selectedVibes.contains(vibe.id);
            return GestureDetector(
              onTap: () {
                setState(() {
                  if (isSelected) {
                    _selectedVibes.remove(vibe.id);
                  } else if (_selectedVibes.length < 3) {
                    _selectedVibes.add(vibe.id);
                  }
                });
              },
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primaryDark : Colors.white,
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                  border: Border.all(
                    color: isSelected
                        ? AppTheme.primaryDark
                        : Colors.grey.shade200,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      vibe.icon,
                      size: 20,
                      color:
                          isSelected ? Colors.white : AppTheme.textSecondary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      vibe.label,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color:
                            isSelected ? Colors.white : AppTheme.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 16),

        Text(
          '${_selectedVibes.length}/3 selected',
          style: TextStyle(color: AppTheme.textSecondary),
        ),
      ],
    );
  }

  // ==================== STEP 3: PACING / BUDGET ====================

  Widget _buildPreferencesStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Almost there!', style: AppTheme.textTheme.headlineMedium),
        const SizedBox(height: 8),
        Text('Set your preferences', style: AppTheme.textTheme.bodyLarge),
        const SizedBox(height: 24),

        // Pacing
        Text('Pacing', style: AppTheme.textTheme.titleMedium),
        const SizedBox(height: 12),
        Row(
          children: [
            _PacingOption(
              label: 'Slow',
              description: '1-2 activities/day',
              isSelected: _pacing == 'slow',
              onTap: () => setState(() => _pacing = 'slow'),
            ),
            const SizedBox(width: 12),
            _PacingOption(
              label: 'Moderate',
              description: '3-4 activities/day',
              isSelected: _pacing == 'moderate',
              onTap: () => setState(() => _pacing = 'moderate'),
            ),
            const SizedBox(width: 12),
            _PacingOption(
              label: 'Fast',
              description: '5+ activities/day',
              isSelected: _pacing == 'fast',
              onTap: () => setState(() => _pacing = 'fast'),
            ),
          ],
        ),
        const SizedBox(height: 32),

        // Budget Level
        Text('Budget Level', style: AppTheme.textTheme.titleMedium),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: List.generate(5, (index) {
            final level = index + 1;
            final isSelected = _budgetLevel == level;
            return GestureDetector(
              onTap: () => setState(() => _budgetLevel = level),
              child: Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primaryDark : Colors.white,
                  borderRadius: BorderRadius.circular(AppRadius.md),
                  border: Border.all(
                    color: isSelected
                        ? AppTheme.primaryDark
                        : Colors.grey.shade200,
                  ),
                ),
                child: Center(
                  child: Text(
                    '\$' * level,
                    style: TextStyle(
                      fontSize: level > 3 ? 10 : 14,
                      fontWeight: FontWeight.w600,
                      color:
                          isSelected ? Colors.white : AppTheme.textSecondary,
                    ),
                  ),
                ),
              ),
            );
          }),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Budget',
                style:
                    TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
            Text('Luxury',
                style:
                    TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
          ],
        ),
        const SizedBox(height: 32),

        // Must-Include Cities
        if (widget.country.cities.isNotEmpty) ...[
          Text('Must-Include Cities', style: AppTheme.textTheme.titleMedium),
          const SizedBox(height: 8),
          Text(
            'Select cities you definitely want to visit',
            style: AppTheme.textTheme.bodyMedium,
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.country.cities.map((city) {
              final isIncluded = _mustIncludeCities.contains(city.id);
              final isExcluded = _excludeCities.contains(city.id);
              return GestureDetector(
                onTap: isExcluded
                    ? null
                    : () {
                        setState(() {
                          if (isIncluded) {
                            _mustIncludeCities.remove(city.id);
                          } else {
                            _mustIncludeCities.add(city.id);
                          }
                        });
                      },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: isIncluded
                        ? AppTheme.primaryDark
                        : isExcluded
                            ? Colors.grey.shade100
                            : Colors.white,
                    borderRadius: BorderRadius.circular(AppRadius.pill),
                    border: Border.all(
                      color: isIncluded
                          ? AppTheme.primaryDark
                          : Colors.grey.shade200,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (isIncluded)
                        const Padding(
                          padding: EdgeInsets.only(right: 6),
                          child: Icon(Icons.check, size: 16, color: Colors.white),
                        ),
                      Text(
                        city.name,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: isIncluded
                              ? Colors.white
                              : isExcluded
                                  ? Colors.grey
                                  : AppTheme.textPrimary,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),

          // Exclude Cities
          Text('Exclude Cities', style: AppTheme.textTheme.titleMedium),
          const SizedBox(height: 8),
          Text(
            'Select cities you want to skip',
            style: AppTheme.textTheme.bodyMedium,
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.country.cities.map((city) {
              final isExcluded = _excludeCities.contains(city.id);
              final isIncluded = _mustIncludeCities.contains(city.id);
              return GestureDetector(
                onTap: isIncluded
                    ? null
                    : () {
                        setState(() {
                          if (isExcluded) {
                            _excludeCities.remove(city.id);
                          } else {
                            _excludeCities.add(city.id);
                          }
                        });
                      },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: isExcluded
                        ? Colors.red.shade700
                        : isIncluded
                            ? Colors.grey.shade100
                            : Colors.white,
                    borderRadius: BorderRadius.circular(AppRadius.pill),
                    border: Border.all(
                      color: isExcluded
                          ? Colors.red.shade700
                          : Colors.grey.shade200,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (isExcluded)
                        const Padding(
                          padding: EdgeInsets.only(right: 6),
                          child:
                              Icon(Icons.close, size: 16, color: Colors.white),
                        ),
                      Text(
                        city.name,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: isExcluded
                              ? Colors.white
                              : isIncluded
                                  ? Colors.grey
                                  : AppTheme.textPrimary,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 32),
        ],

        // Trip Summary
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(AppRadius.lg),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Trip Summary', style: AppTheme.textTheme.titleMedium),
              const SizedBox(height: 16),
              _SummaryRow(label: 'Country', value: widget.country.name),
              _SummaryRow(label: 'Duration', value: '$_tripDays days'),
              _SummaryRow(
                  label: 'Group',
                  value: '$_groupType ($_groupSize people)'),
              if (_selectedVibes.isNotEmpty)
                _SummaryRow(
                    label: 'Vibes', value: _selectedVibes.join(', ')),
              _SummaryRow(label: 'Pacing', value: _pacing),
              _SummaryRow(label: 'Budget', value: '\$' * _budgetLevel),
              if (_mustIncludeCities.isNotEmpty)
                _SummaryRow(
                  label: 'Must-Include',
                  value: widget.country.cities
                      .where((c) => _mustIncludeCities.contains(c.id))
                      .map((c) => c.name)
                      .join(', '),
                ),
              if (_excludeCities.isNotEmpty)
                _SummaryRow(
                  label: 'Excluded',
                  value: widget.country.cities
                      .where((c) => _excludeCities.contains(c.id))
                      .map((c) => c.name)
                      .join(', '),
                ),
            ],
          ),
        ),
        const SizedBox(height: 20),
      ],
    );
  }
}

// ==================== PRIVATE HELPER CLASSES ====================

class _VibeOption {
  final String id;
  final String label;
  final IconData icon;

  _VibeOption(this.id, this.label, this.icon);
}

class _GroupOption {
  final String id;
  final String label;
  final IconData icon;

  _GroupOption(this.id, this.label, this.icon);
}

class _DateSelector extends StatelessWidget {
  final String label;
  final DateTime date;
  final VoidCallback onTap;

  const _DateSelector({
    required this.label,
    required this.date,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Row(
          children: [
            const Icon(Icons.calendar_today, color: AppTheme.primaryDark),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style: TextStyle(
                        color: AppTheme.textSecondary, fontSize: 12)),
                const SizedBox(height: 4),
                Text(
                  '${months[date.month - 1]} ${date.day}, ${date.year}',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.primaryDark,
                  ),
                ),
              ],
            ),
            const Spacer(),
            const Icon(Icons.chevron_right, color: AppTheme.textSecondary),
          ],
        ),
      ),
    );
  }
}

class _CheckboxTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool?> onChanged;

  const _CheckboxTile({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(AppRadius.md),
      ),
      child: Row(
        children: [
          Checkbox(
            value: value,
            onChanged: onChanged,
            activeColor: AppTheme.primaryDark,
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(subtitle,
                    style: TextStyle(
                        fontSize: 12, color: AppTheme.textSecondary)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PacingOption extends StatelessWidget {
  final String label;
  final String description;
  final bool isSelected;
  final VoidCallback onTap;

  const _PacingOption({
    required this.label,
    required this.description,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.primaryDark : Colors.white,
            borderRadius: BorderRadius.circular(AppRadius.md),
            border: Border.all(
              color: isSelected ? AppTheme.primaryDark : Colors.grey.shade200,
            ),
          ),
          child: Column(
            children: [
              Text(
                label,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: isSelected ? Colors.white : AppTheme.textPrimary,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(
                  fontSize: 10,
                  color: isSelected ? Colors.white70 : AppTheme.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  final String label;
  final String value;

  const _SummaryRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: AppTheme.textSecondary)),
          const SizedBox(width: 16),
          Flexible(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w500),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }
}
