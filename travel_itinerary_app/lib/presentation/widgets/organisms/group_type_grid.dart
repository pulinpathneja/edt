import 'package:flutter/material.dart';

import '../../../domain/entities/persona_config.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../molecules/selection_card.dart';

/// Grid of group type selection cards
class GroupTypeGrid extends StatelessWidget {
  final List<GroupTypeOption> options;
  final String? selectedId;
  final ValueChanged<String>? onSelected;
  final int crossAxisCount;

  const GroupTypeGrid({
    super.key,
    required this.options,
    this.selectedId,
    this.onSelected,
    this.crossAxisCount = 2,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        crossAxisSpacing: AppSpacing.md,
        mainAxisSpacing: AppSpacing.md,
        childAspectRatio: 1.0,
      ),
      itemCount: options.length,
      itemBuilder: (context, index) {
        final option = options[index];
        return SelectionCard(
          id: option.id,
          label: option.label,
          icon: option.icon,
          description: option.description,
          isSelected: selectedId == option.id,
          onTap: () => onSelected?.call(option.id),
        ).animated(
          delay: Duration(milliseconds: index * 50),
        );
      },
    );
  }
}

/// Horizontal scrolling group type selector for compact layouts
class GroupTypeHorizontalList extends StatelessWidget {
  final List<GroupTypeOption> options;
  final String? selectedId;
  final ValueChanged<String>? onSelected;

  const GroupTypeHorizontalList({
    super.key,
    required this.options,
    this.selectedId,
    this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 140,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
        itemCount: options.length,
        separatorBuilder: (_, __) => const SizedBox(width: AppSpacing.md),
        itemBuilder: (context, index) {
          final option = options[index];
          return SizedBox(
            width: 120,
            child: SelectionCard(
              id: option.id,
              label: option.label,
              icon: option.icon,
              isSelected: selectedId == option.id,
              onTap: () => onSelected?.call(option.id),
            ).animated(
              delay: Duration(milliseconds: index * 50),
            ),
          );
        },
      ),
    );
  }
}
