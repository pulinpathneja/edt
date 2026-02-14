import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../models/poi.dart';

class POIDetailScreen extends StatelessWidget {
  final POI poi;

  const POIDetailScreen({super.key, required this.poi});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: CustomScrollView(
        slivers: [
          // Hero Image
          SliverAppBar(
            expandedHeight: 280,
            pinned: true,
            backgroundColor: AppTheme.primaryDark,
            leading: IconButton(
              icon: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.3),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.arrow_back, color: Colors.white, size: 20),
              ),
              onPressed: () => Navigator.pop(context),
            ),
            actions: [
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.3),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.bookmark_outline, color: Colors.white, size: 20),
                ),
                onPressed: () {},
              ),
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.3),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.share, color: Colors.white, size: 20),
                ),
                onPressed: () {},
              ),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: Stack(
                fit: StackFit.expand,
                children: [
                  poi.imageUrl != null
                      ? Image.network(
                          poi.imageUrl!,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => _buildPlaceholder(),
                        )
                      : _buildPlaceholder(),
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
                ],
              ),
            ),
          ),

          // Content
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title Row
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              poi.name,
                              style: AppTheme.textTheme.displayMedium,
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Icon(Icons.location_on, size: 14, color: AppTheme.textSecondary),
                                const SizedBox(width: 4),
                                Expanded(
                                  child: Text(
                                    poi.neighborhood ?? poi.city,
                                    style: TextStyle(
                                      color: AppTheme.textSecondary,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      if (poi.isMustSee == true)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.amber.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(AppRadius.pill),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.star, size: 14, color: Colors.amber),
                              SizedBox(width: 4),
                              Text(
                                'Must See',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.amber,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Quick Info Cards
                  Row(
                    children: [
                      _InfoCard(
                        icon: Icons.access_time,
                        label: 'Duration',
                        value: poi.durationText,
                      ),
                      const SizedBox(width: 12),
                      _InfoCard(
                        icon: Icons.attach_money,
                        label: 'Cost',
                        value: poi.costText,
                      ),
                      const SizedBox(width: 12),
                      _InfoCard(
                        icon: Icons.wb_sunny,
                        label: 'Best Time',
                        value: poi.bestTimeOfDay ?? 'Any',
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Description
                  if (poi.description != null) ...[
                    Text('About', style: AppTheme.textTheme.headlineMedium),
                    const SizedBox(height: 12),
                    Text(
                      poi.description!,
                      style: AppTheme.textTheme.bodyLarge,
                    ),
                    const SizedBox(height: 24),
                  ],

                  // Tags
                  _buildTags(),
                  const SizedBox(height: 24),

                  // Vibe Scores
                  if (poi.personaScores != null) ...[
                    Text('Vibe Match', style: AppTheme.textTheme.headlineMedium),
                    const SizedBox(height: 16),
                    _buildVibeScores(),
                    const SizedBox(height: 24),
                  ],

                  // Address & Map Preview
                  if (poi.address != null) ...[
                    Text('Location', style: AppTheme.textTheme.headlineMedium),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(AppRadius.lg),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
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
                                  poi.address!,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '${poi.city}, ${poi.country ?? ""}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: AppTheme.textSecondary,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.directions, color: AppTheme.primaryDark),
                            onPressed: () {},
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 100), // Bottom padding for FAB
                ],
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        backgroundColor: AppTheme.primaryDark,
        icon: const Icon(Icons.add),
        label: const Text('Add to Itinerary'),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.primaryDark,
            AppTheme.primaryDark.withBlue(80),
          ],
        ),
      ),
      child: Center(
        child: Icon(
          _getCategoryIcon(poi.category),
          size: 80,
          color: Colors.white.withOpacity(0.3),
        ),
      ),
    );
  }

  Widget _buildTags() {
    final tags = <_TagInfo>[];

    if (poi.category.isNotEmpty) {
      tags.add(_TagInfo(poi.category, Icons.category));
    }
    if (poi.subcategory != null) {
      tags.add(_TagInfo(poi.subcategory!, Icons.label));
    }
    if (poi.isHiddenGem == true) {
      tags.add(_TagInfo('Hidden Gem', Icons.diamond));
    }
    if (poi.instagramWorthy == true) {
      tags.add(_TagInfo('Instagram Worthy', Icons.camera_alt));
    }

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: tags.map((tag) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(AppRadius.pill),
            border: Border.all(color: Colors.grey.shade200),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(tag.icon, size: 14, color: AppTheme.textSecondary),
              const SizedBox(width: 6),
              Text(
                tag.label,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildVibeScores() {
    final scores = poi.personaScores;
    if (scores == null) return const SizedBox();

    final vibes = <_VibeScore>[
      if (scores.cultural != null) _VibeScore('Cultural', scores.cultural!, Icons.museum),
      if (scores.romantic != null) _VibeScore('Romantic', scores.romantic!, Icons.favorite),
      if (scores.adventure != null) _VibeScore('Adventure', scores.adventure!, Icons.terrain),
      if (scores.foodie != null) _VibeScore('Foodie', scores.foodie!, Icons.restaurant),
      if (scores.photography != null) _VibeScore('Photography', scores.photography!, Icons.camera_alt),
    ];

    // Sort by score descending and take top 5
    vibes.sort((a, b) => b.score.compareTo(a.score));
    final topVibes = vibes.take(5).toList();

    return Column(
      children: topVibes.map((vibe) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: _getVibeColor(vibe.score).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(AppRadius.sm),
                ),
                child: Icon(vibe.icon, size: 18, color: _getVibeColor(vibe.score)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(vibe.label, style: const TextStyle(fontWeight: FontWeight.w500)),
                        Text(
                          '${(vibe.score * 100).toInt()}%',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: _getVibeColor(vibe.score),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: vibe.score,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: AlwaysStoppedAnimation(_getVibeColor(vibe.score)),
                        minHeight: 6,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Color _getVibeColor(double score) {
    if (score >= 0.8) return Colors.green;
    if (score >= 0.6) return Colors.teal;
    if (score >= 0.4) return Colors.orange;
    return Colors.grey;
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
      default:
        return Icons.place;
    }
  }
}

class _InfoCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoCard({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(AppRadius.md),
        ),
        child: Column(
          children: [
            Icon(icon, color: AppTheme.primaryDark, size: 24),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TagInfo {
  final String label;
  final IconData icon;

  _TagInfo(this.label, this.icon);
}

class _VibeScore {
  final String label;
  final double score;
  final IconData icon;

  _VibeScore(this.label, this.score, this.icon);
}
