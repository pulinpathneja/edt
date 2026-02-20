import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';
import '../models/allocation.dart';
import '../models/country.dart';
import '../models/country_itinerary.dart';
import 'country_itinerary_screen.dart';

class AllocationOptionsScreen extends StatefulWidget {
  final AllocationResponse allocationResponse;
  final String country;
  final DateTime startDate;
  final DateTime endDate;
  final String groupType;
  final int groupSize;
  final List<String> vibes;
  final int budgetLevel;
  final String pacing;
  final bool hasKids;
  final bool hasSeniors;

  const AllocationOptionsScreen({
    super.key,
    required this.allocationResponse,
    required this.country,
    required this.startDate,
    required this.endDate,
    required this.groupType,
    required this.groupSize,
    required this.vibes,
    required this.budgetLevel,
    required this.pacing,
    required this.hasKids,
    required this.hasSeniors,
  });

  @override
  State<AllocationOptionsScreen> createState() =>
      _AllocationOptionsScreenState();
}

class _AllocationOptionsScreenState extends State<AllocationOptionsScreen> {
  final ApiService _apiService = ApiService();
  int? _selectedOptionId;
  bool _isGenerating = false;

  AllocationOption? get _selectedOption {
    if (_selectedOptionId == null) return null;
    return widget.allocationResponse.options.firstWhere(
      (o) => o.optionId == _selectedOptionId,
    );
  }

  Future<void> _generateItinerary() async {
    final selected = _selectedOption;
    if (selected == null) return;

    setState(() => _isGenerating = true);

    try {
      final itinerary = await _apiService.generateCountryItinerary(
        country: widget.country,
        selectedAllocation: selected,
        startDate: widget.startDate.toIso8601String().split('T').first,
        endDate: widget.endDate.toIso8601String().split('T').first,
        groupType: widget.groupType,
        groupSize: widget.groupSize,
        vibes: widget.vibes,
        budgetLevel: widget.budgetLevel,
        pacing: widget.pacing,
        hasKids: widget.hasKids,
        hasSeniors: widget.hasSeniors,
      );

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) =>
                CountryItineraryScreen(itinerary: itinerary),
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
    final response = widget.allocationResponse;

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
          'Choose Your Route',
          style: AppTheme.textTheme.headlineMedium,
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Country header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryDark.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppRadius.md),
                  ),
                  child: const Icon(
                    Icons.map_outlined,
                    color: AppTheme.primaryDark,
                    size: 22,
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      response.countryName,
                      style: AppTheme.textTheme.titleLarge,
                    ),
                    Text(
                      '${response.totalDays} days \u2022 ${response.options.length} options',
                      style: AppTheme.textTheme.bodyMedium,
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 8),

          // Option cards list
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              itemCount: response.options.length,
              itemBuilder: (context, index) {
                final option = response.options[index];
                final isSelected = _selectedOptionId == option.optionId;
                final isRecommended =
                    option.optionId == response.recommendedOption;
                return _OptionCard(
                  option: option,
                  isSelected: isSelected,
                  isRecommended: isRecommended,
                  totalDays: response.totalDays,
                  onTap: () {
                    setState(() => _selectedOptionId = option.optionId);
                  },
                );
              },
            ),
          ),

          // Generate Itinerary button
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed:
                    (_selectedOptionId != null && !_isGenerating)
                        ? _generateItinerary
                        : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryDark,
                  disabledBackgroundColor: AppTheme.primaryDark.withOpacity(0.3),
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
                          valueColor:
                              AlwaysStoppedAnimation(Colors.white),
                        ),
                      )
                    : const Text(
                        'Generate Itinerary',
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

// ---------------------------------------------------------------------------
// Option Card
// ---------------------------------------------------------------------------

class _OptionCard extends StatelessWidget {
  final AllocationOption option;
  final bool isSelected;
  final bool isRecommended;
  final int totalDays;
  final VoidCallback onTap;

  const _OptionCard({
    required this.option,
    required this.isSelected,
    required this.isRecommended,
    required this.totalDays,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(
            color: isSelected ? AppTheme.primaryDark : Colors.grey.shade200,
            width: isSelected ? 2.0 : 1.0,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppTheme.primaryDark.withOpacity(0.1),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ]
              : [],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header row: name + recommended badge + match score
            _buildHeader(),

            const SizedBox(height: 16),

            // Description
            Text(
              option.description,
              style: AppTheme.textTheme.bodyMedium,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),

            const SizedBox(height: 16),

            // City breakdown
            _buildCityBreakdown(),

            const SizedBox(height: 16),

            // Pros and Cons
            if (option.pros.isNotEmpty || option.cons.isNotEmpty)
              _buildProsAndCons(),

            if (option.pros.isNotEmpty || option.cons.isNotEmpty)
              const SizedBox(height: 12),

            // Travel time footer
            _buildTravelTime(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Option name and recommended badge
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                option.optionName,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimary,
                ),
              ),
              if (isRecommended) ...[
                const SizedBox(height: 6),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF4CAF50).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppRadius.sm),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.star_rounded,
                        size: 14,
                        color: Color(0xFF4CAF50),
                      ),
                      SizedBox(width: 4),
                      Text(
                        'Recommended',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF4CAF50),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),

        // Match score circle
        _buildMatchScoreCircle(),
      ],
    );
  }

  Widget _buildMatchScoreCircle() {
    final percent = option.matchPercent;
    final scoreColor = percent >= 80
        ? const Color(0xFF4CAF50)
        : percent >= 60
            ? const Color(0xFFFFA726)
            : const Color(0xFFEF5350);

    return SizedBox(
      width: 56,
      height: 56,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: 56,
            height: 56,
            child: CircularProgressIndicator(
              value: option.matchScore,
              strokeWidth: 4,
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation(scoreColor),
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '$percent%',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: scoreColor,
                ),
              ),
              const Text(
                'match',
                style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.textSecondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCityBreakdown() {
    final maxDays = option.cities.fold<int>(
      0,
      (max, city) => city.days > max ? city.days : max,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'City Breakdown',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: AppTheme.textSecondary,
            letterSpacing: 0.3,
          ),
        ),
        const SizedBox(height: 10),
        ...option.cities.map((city) {
          final barFraction = maxDays > 0 ? city.days / maxDays : 0.0;
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                // City name
                SizedBox(
                  width: 100,
                  child: Text(
                    city.cityName,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: AppTheme.textPrimary,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 8),
                // Proportional bar
                Expanded(
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      return Stack(
                        children: [
                          Container(
                            height: 20,
                            decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius:
                                  BorderRadius.circular(AppRadius.sm),
                            ),
                          ),
                          FractionallySizedBox(
                            widthFactor: barFraction,
                            child: Container(
                              height: 20,
                              decoration: BoxDecoration(
                                color:
                                    AppTheme.primaryDark.withOpacity(0.15),
                                borderRadius:
                                    BorderRadius.circular(AppRadius.sm),
                              ),
                              alignment: Alignment.centerLeft,
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 8),
                              child: FittedBox(
                                fit: BoxFit.scaleDown,
                                child: Text(
                                  '${city.days} ${city.days == 1 ? 'day' : 'days'}',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: AppTheme.primaryDark,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildProsAndCons() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Pros
        ...option.pros.map((pro) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.check_circle,
                  size: 16,
                  color: Color(0xFF4CAF50),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    pro,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          );
        }),

        // Cons
        ...option.cons.map((con) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.warning_amber_rounded,
                  size: 16,
                  color: Color(0xFFFFA726),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    con,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildTravelTime() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(AppRadius.sm),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.directions_car_outlined,
            size: 16,
            color: AppTheme.textSecondary,
          ),
          const SizedBox(width: 6),
          Text(
            'Total travel: ${option.travelTimeText}',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: AppTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}
