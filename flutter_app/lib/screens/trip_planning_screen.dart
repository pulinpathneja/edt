import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';
import '../models/city.dart';
import '../models/itinerary.dart';
import 'itinerary_detail_screen.dart';

class TripPlanningScreen extends StatefulWidget {
  final City city;

  const TripPlanningScreen({super.key, required this.city});

  @override
  State<TripPlanningScreen> createState() => _TripPlanningScreenState();
}

class _TripPlanningScreenState extends State<TripPlanningScreen> {
  final ApiService _apiService = ApiService();
  int _currentStep = 0;
  bool _isGenerating = false;

  // Trip details
  DateTime _startDate = DateTime.now().add(const Duration(days: 7));
  DateTime _endDate = DateTime.now().add(const Duration(days: 10));
  String _groupType = 'couple';
  int _groupSize = 2;
  List<String> _selectedVibes = ['cultural', 'romantic'];
  int _budgetLevel = 3;
  String _pacing = 'moderate';
  bool _hasKids = false;
  bool _hasSeniors = false;

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

  Future<void> _generateItinerary() async {
    setState(() => _isGenerating = true);

    try {
      final request = TripRequest(
        destinationCity: widget.city.id,
        startDate: _startDate,
        endDate: _endDate,
        groupType: _groupType,
        groupSize: _groupSize,
        vibes: _selectedVibes,
        budgetLevel: _budgetLevel,
        pacing: _pacing,
        hasKids: _hasKids,
        hasSeniors: _hasSeniors,
      );

      final itinerary = await _apiService.generateItinerary(request);

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ItineraryDetailScreen(itinerary: itinerary),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to generate itinerary: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isGenerating = false);
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
          // Progress Indicator
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            child: Row(
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
          ),

          // City Header
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
                  child: const Icon(Icons.location_on, color: AppTheme.primaryDark),
                ),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.city.name,
                      style: AppTheme.textTheme.titleLarge,
                    ),
                    Text(
                      widget.city.country,
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
                    onPressed: _isGenerating
                        ? null
                        : () {
                            if (_currentStep < 3) {
                              setState(() => _currentStep++);
                            } else {
                              _generateItinerary();
                            }
                          },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryDark,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(AppRadius.pill),
                      ),
                    ),
                    child: _isGenerating
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation(Colors.white),
                            ),
                          )
                        : Text(
                            _currentStep < 3 ? 'Continue' : 'Generate Itinerary',
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
                  _endDate = _startDate.add(const Duration(days: 3));
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
                '$_tripDays ${_tripDays == 1 ? 'day' : 'days'} in ${widget.city.name}',
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
                    color: isSelected ? AppTheme.primaryDark : Colors.grey.shade200,
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      option.icon,
                      color: isSelected ? Colors.white : AppTheme.textSecondary,
                      size: 28,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      option.label,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: isSelected ? Colors.white : AppTheme.textPrimary,
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
              onPressed: _groupSize > 1 ? () => setState(() => _groupSize--) : null,
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
              onPressed: _groupSize < 20 ? () => setState(() => _groupSize++) : null,
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

  Widget _buildVibesStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What\'s your vibe?', style: AppTheme.textTheme.headlineMedium),
        const SizedBox(height: 8),
        Text('Select up to 3 vibes for your trip', style: AppTheme.textTheme.bodyLarge),
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
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primaryDark : Colors.white,
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                  border: Border.all(
                    color: isSelected ? AppTheme.primaryDark : Colors.grey.shade200,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      vibe.icon,
                      size: 20,
                      color: isSelected ? Colors.white : AppTheme.textSecondary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      vibe.label,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: isSelected ? Colors.white : AppTheme.textPrimary,
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

        // Budget
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
                    color: isSelected ? AppTheme.primaryDark : Colors.grey.shade200,
                  ),
                ),
                child: Center(
                  child: Text(
                    '\$' * level,
                    style: TextStyle(
                      fontSize: level > 3 ? 10 : 14,
                      fontWeight: FontWeight.w600,
                      color: isSelected ? Colors.white : AppTheme.textSecondary,
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
            Text('Budget', style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
            Text('Luxury', style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
          ],
        ),
        const SizedBox(height: 32),

        // Summary
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
              _SummaryRow(label: 'Destination', value: widget.city.name),
              _SummaryRow(label: 'Duration', value: '$_tripDays days'),
              _SummaryRow(label: 'Group', value: '$_groupType ($_groupSize people)'),
              _SummaryRow(label: 'Vibes', value: _selectedVibes.join(', ')),
              _SummaryRow(label: 'Pacing', value: _pacing),
              _SummaryRow(label: 'Budget', value: '\$' * _budgetLevel),
            ],
          ),
        ),
      ],
    );
  }
}

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
                Text(label, style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
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
                Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(subtitle, style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
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
        children: [
          Text(label, style: TextStyle(color: AppTheme.textSecondary)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
