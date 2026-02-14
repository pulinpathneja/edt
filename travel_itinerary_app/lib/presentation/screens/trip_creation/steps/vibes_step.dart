import 'package:flutter/material.dart';

import '../../../../domain/entities/persona_config.dart';
import '../../../widgets/organisms/vibe_selection_grid.dart';

/// Step 3: Vibe/experience selection
class VibesStep extends StatelessWidget {
  final List<VibeOption> options;
  final Set<String> selectedVibes;
  final ValueChanged<Set<String>> onVibesChanged;

  const VibesStep({
    super.key,
    required this.options,
    required this.selectedVibes,
    required this.onVibesChanged,
  });

  @override
  Widget build(BuildContext context) {
    return VibeSelectionGrid(
      options: options,
      selectedIds: selectedVibes,
      onSelectionChanged: onVibesChanged,
      maxSelections: 5,
    );
  }
}
