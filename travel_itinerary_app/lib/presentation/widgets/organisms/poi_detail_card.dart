import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../../../domain/entities/poi.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';

/// Expandable POI detail card
class POIDetailCard extends StatefulWidget {
  final POI poi;
  final VoidCallback? onTap;
  final bool initiallyExpanded;

  const POIDetailCard({
    super.key,
    required this.poi,
    this.onTap,
    this.initiallyExpanded = false,
  });

  @override
  State<POIDetailCard> createState() => _POIDetailCardState();
}

class _POIDetailCardState extends State<POIDetailCard> {
  late bool _isExpanded;

  @override
  void initState() {
    super.initState();
    _isExpanded = widget.initiallyExpanded;
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap ?? () => setState(() => _isExpanded = !_isExpanded),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOutCubic,
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
          border: Border.all(color: AppColors.border),
          boxShadow: [
            BoxShadow(
              color: AppColors.shadowLight,
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image (if available)
            if (widget.poi.imageUrl != null)
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(AppSpacing.radiusMD),
                ),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: CachedNetworkImage(
                    imageUrl: widget.poi.imageUrl!,
                    fit: BoxFit.cover,
                    placeholder: (context, url) => Container(
                      color: AppColors.surfaceVariant,
                      child: const Center(
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    ),
                    errorWidget: (context, url, error) => Container(
                      color: AppColors.surfaceVariant,
                      child: Icon(
                        Icons.image_not_supported_outlined,
                        color: AppColors.textTertiary,
                      ),
                    ),
                  ),
                ),
              ),

            // Content
            Padding(
              padding: const EdgeInsets.all(AppSpacing.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header row
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Category icon
                      Container(
                        padding: const EdgeInsets.all(AppSpacing.sm),
                        decoration: BoxDecoration(
                          color: _getCategoryColor().withOpacity(0.15),
                          borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
                        ),
                        child: Text(
                          _getCategoryIcon(),
                          style: const TextStyle(fontSize: 16),
                        ),
                      ),
                      const SizedBox(width: AppSpacing.sm),

                      // Title and category
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.poi.name,
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: AppSpacing.xs),
                            Row(
                              children: [
                                Text(
                                  widget.poi.category,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: _getCategoryColor(),
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                if (widget.poi.durationMinutes != null) ...[
                                  const SizedBox(width: AppSpacing.sm),
                                  Icon(
                                    Icons.schedule,
                                    size: 12,
                                    color: AppColors.textTertiary,
                                  ),
                                  const SizedBox(width: 2),
                                  Text(
                                    widget.poi.formattedDuration,
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: AppColors.textTertiary,
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ],
                        ),
                      ),

                      // Expand/collapse icon
                      Icon(
                        _isExpanded
                            ? Icons.keyboard_arrow_up
                            : Icons.keyboard_arrow_down,
                        color: AppColors.textTertiary,
                      ),
                    ],
                  ),

                  // Expanded content
                  AnimatedCrossFade(
                    firstChild: const SizedBox.shrink(),
                    secondChild: _buildExpandedContent(),
                    crossFadeState: _isExpanded
                        ? CrossFadeState.showSecond
                        : CrossFadeState.showFirst,
                    duration: const Duration(milliseconds: 200),
                  ),

                  // Tags
                  if (widget.poi.tags != null && widget.poi.tags!.isNotEmpty) ...[
                    const SizedBox(height: AppSpacing.sm),
                    Wrap(
                      spacing: AppSpacing.xs,
                      runSpacing: AppSpacing.xs,
                      children: widget.poi.tags!.take(4).map((tag) {
                        return Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: AppSpacing.sm,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.surfaceVariant,
                            borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                          ),
                          child: Text(
                            tag,
                            style: TextStyle(
                              fontSize: 10,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExpandedContent() {
    return Padding(
      padding: const EdgeInsets.only(top: AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Description
          if (widget.poi.description != null) ...[
            Text(
              widget.poi.description!,
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: AppSpacing.md),
          ],

          // Address
          if (widget.poi.address != null)
            _buildInfoRow(
              Icons.location_on_outlined,
              widget.poi.address!,
            ),

          // Rating
          if (widget.poi.rating != null)
            _buildInfoRow(
              Icons.star,
              widget.poi.rating!.toStringAsFixed(1),
              iconColor: AppColors.warning,
            ),

          // Price level
          if (widget.poi.priceLevel != null)
            _buildInfoRow(
              Icons.payments_outlined,
              widget.poi.priceLevelString,
            ),

          // Website
          if (widget.poi.website != null)
            _buildInfoRow(
              Icons.language,
              widget.poi.website!,
              isLink: true,
            ),

          // Booking button
          if (widget.poi.bookingUrl != null) ...[
            const SizedBox(height: AppSpacing.md),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  // Handle booking URL
                },
                icon: const Icon(Icons.calendar_today, size: 16),
                label: const Text('Book Now'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String text, {Color? iconColor, bool isLink = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            size: 16,
            color: iconColor ?? AppColors.textTertiary,
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 12,
                color: isLink ? AppColors.primary : AppColors.textSecondary,
                decoration: isLink ? TextDecoration.underline : null,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getCategoryIcon() {
    return switch (widget.poi.category.toLowerCase()) {
      'museum' || 'art' => '🏛️',
      'restaurant' || 'food' || 'dining' => '🍽️',
      'landmark' || 'monument' => '🗿',
      'park' || 'garden' || 'nature' => '🌳',
      'shopping' || 'market' => '🛍️',
      'entertainment' || 'show' => '🎭',
      'beach' => '🏖️',
      'religious' || 'temple' || 'church' => '⛪',
      'viewpoint' || 'scenic' => '🌅',
      'activity' || 'adventure' => '🎯',
      'nightlife' || 'bar' => '🌃',
      'spa' || 'wellness' => '💆',
      'sports' => '⚽',
      'tour' => '🚌',
      _ => '📍',
    };
  }

  Color _getCategoryColor() {
    return switch (widget.poi.category.toLowerCase()) {
      'museum' || 'art' => AppColors.cultural,
      'restaurant' || 'food' || 'dining' => AppColors.foodie,
      'landmark' || 'monument' => AppColors.historical,
      'park' || 'garden' || 'nature' => AppColors.nature,
      'shopping' || 'market' => AppColors.shopping,
      'entertainment' || 'show' => AppColors.artsy,
      'beach' => AppColors.relaxation,
      'activity' || 'adventure' => AppColors.adventure,
      'nightlife' || 'bar' => AppColors.nightlife,
      'spa' || 'wellness' => AppColors.relaxation,
      _ => AppColors.primary,
    };
  }
}
