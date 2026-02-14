import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../config/routes/app_router.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../../controllers/generation_controller.dart';
import '../../controllers/itinerary_view_controller.dart';
import '../../controllers/trip_creation_controller.dart';
import '../../widgets/atoms/app_button.dart';

/// Itinerary generation loading screen
class GenerationScreen extends ConsumerStatefulWidget {
  const GenerationScreen({super.key});

  @override
  ConsumerState<GenerationScreen> createState() => _GenerationScreenState();
}

class _GenerationScreenState extends ConsumerState<GenerationScreen> {
  int _messageIndex = 0;
  Timer? _messageTimer;

  @override
  void initState() {
    super.initState();
    _startGeneration();
    _startMessageRotation();
  }

  @override
  void dispose() {
    _messageTimer?.cancel();
    super.dispose();
  }

  void _startGeneration() {
    final tripState = ref.read(tripCreationControllerProvider);
    final request = tripState.toTripRequest();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(generationControllerProvider.notifier).generate(request);
    });
  }

  void _startMessageRotation() {
    _messageTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
      if (mounted) {
        setState(() {
          _messageIndex = (_messageIndex + 1) % generationLoadingMessages.length;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(generationControllerProvider);

    // Handle navigation on success
    ref.listen(generationControllerProvider, (previous, current) {
      if (current.isSuccess && current.itinerary != null) {
        // Store itinerary in shared provider
        ref.read(currentItineraryProvider.notifier).set(current.itinerary!);

        // Navigate to itinerary view
        context.go(Routes.itinerary(current.itinerary!.id));
      }
    });

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.primary,
              AppColors.primaryDark,
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: state.isError
                ? _buildErrorState(state.errorMessage)
                : _buildLoadingState(),
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    final tripState = ref.watch(tripCreationControllerProvider);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Spacer(flex: 2),

        // Animated plane icon
        _AnimatedPlane()
            .animate(onPlay: (c) => c.repeat())
            .moveY(
              begin: -10,
              end: 10,
              duration: const Duration(seconds: 2),
              curve: Curves.easeInOut,
            )
            .then()
            .moveY(
              begin: 10,
              end: -10,
              duration: const Duration(seconds: 2),
              curve: Curves.easeInOut,
            ),

        const SizedBox(height: AppSpacing.xl),

        // Destination info
        Text(
          tripState.destinationCity,
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w700,
            color: AppColors.white,
          ),
        ).animate().fadeIn().slideY(begin: 0.3),

        const SizedBox(height: AppSpacing.sm),

        Text(
          '${tripState.tripDuration} days • ${tripState.groupSize} ${tripState.groupSize == 1 ? 'person' : 'people'}',
          style: TextStyle(
            fontSize: 16,
            color: AppColors.white.withOpacity(0.8),
          ),
        ).animate(delay: const Duration(milliseconds: 100)).fadeIn().slideY(begin: 0.3),

        const SizedBox(height: AppSpacing.xxl),

        // Progress indicator
        SizedBox(
          width: 200,
          child: LinearProgressIndicator(
            backgroundColor: AppColors.white.withOpacity(0.2),
            valueColor: const AlwaysStoppedAnimation<Color>(AppColors.secondary),
          ),
        ).animate().fadeIn(delay: const Duration(milliseconds: 200)),

        const SizedBox(height: AppSpacing.lg),

        // Rotating messages
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 500),
          child: Text(
            generationLoadingMessages[_messageIndex],
            key: ValueKey(_messageIndex),
            style: TextStyle(
              fontSize: 16,
              color: AppColors.white.withOpacity(0.9),
            ),
            textAlign: TextAlign.center,
          ),
        ),

        const Spacer(flex: 3),

        // Cancel button
        TextButton(
          onPressed: () {
            ref.read(generationControllerProvider.notifier).reset();
            context.go(Routes.tripCreation);
          },
          child: Text(
            'Cancel',
            style: TextStyle(
              color: AppColors.white.withOpacity(0.7),
            ),
          ),
        ),

        const SizedBox(height: AppSpacing.md),
      ],
    );
  }

  Widget _buildErrorState(String? errorMessage) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: AppColors.error.withOpacity(0.2),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.error_outline,
            size: 40,
            color: AppColors.white,
          ),
        ).animate().scale().fadeIn(),

        const SizedBox(height: AppSpacing.lg),

        const Text(
          'Generation Failed',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w700,
            color: AppColors.white,
          ),
        ).animate(delay: const Duration(milliseconds: 100)).fadeIn(),

        const SizedBox(height: AppSpacing.sm),

        Text(
          errorMessage ?? 'Something went wrong. Please try again.',
          style: TextStyle(
            fontSize: 14,
            color: AppColors.white.withOpacity(0.8),
          ),
          textAlign: TextAlign.center,
        ).animate(delay: const Duration(milliseconds: 200)).fadeIn(),

        const SizedBox(height: AppSpacing.xl),

        AppButton(
          label: 'Try Again',
          variant: AppButtonVariant.primary,
          customColor: AppColors.secondary,
          onPressed: _startGeneration,
        ).animate(delay: const Duration(milliseconds: 300)).fadeIn().slideY(begin: 0.2),

        const SizedBox(height: AppSpacing.md),

        TextButton(
          onPressed: () => context.go(Routes.tripCreation),
          child: Text(
            'Modify Trip Details',
            style: TextStyle(
              color: AppColors.white.withOpacity(0.7),
            ),
          ),
        ),
      ],
    );
  }
}

class _AnimatedPlane extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 100,
      height: 100,
      decoration: BoxDecoration(
        color: AppColors.white.withOpacity(0.15),
        shape: BoxShape.circle,
      ),
      child: const Center(
        child: Text(
          '✈️',
          style: TextStyle(fontSize: 48),
        ),
      ),
    );
  }
}
