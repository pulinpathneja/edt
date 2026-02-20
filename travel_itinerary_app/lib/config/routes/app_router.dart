import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../presentation/screens/onboarding/onboarding_screen.dart';
import '../../presentation/screens/home/home_screen.dart';
import '../../presentation/screens/country/country_selection_screen.dart';
import '../../presentation/screens/country/trip_preferences_screen.dart';
import '../../presentation/screens/country/allocation_options_screen.dart';
import '../../presentation/screens/country/country_itinerary_screen.dart';
import '../../presentation/screens/city/city_selection_screen.dart';
import '../../presentation/screens/generation/generation_screen.dart';
import '../../presentation/screens/itinerary_view/itinerary_view_screen.dart';
import '../../presentation/screens/trip_creation/trip_creation_screen.dart';

/// Route names
class Routes {
  Routes._();

  static const String onboarding = '/';
  static const String home = '/home';
  static const String countrySelect = '/country/select';
  static const String countryPreferences = '/country/preferences';
  static const String countryAllocations = '/country/allocations';
  static const String countryItinerary = '/country/itinerary';
  static const String citySelect = '/city/select';
  static const String tripCreation = '/trip/create';
  static const String generation = '/trip/generate';
  static const String itineraryView = '/itinerary/:id';

  static String itinerary(String id) => '/itinerary/$id';
}

/// GoRouter provider
final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: Routes.onboarding,
    debugLogDiagnostics: true,
    routes: [
      GoRoute(
        path: Routes.onboarding,
        name: 'onboarding',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const OnboardingScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(opacity: animation, child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.home,
        name: 'home',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const HomeScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(opacity: animation, child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.countrySelect,
        name: 'country_select',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const CountrySelectionScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = Offset(1.0, 0.0);
            const end = Offset.zero;
            const curve = Curves.easeInOutCubic;
            final tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
            return SlideTransition(position: animation.drive(tween), child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.countryPreferences,
        name: 'country_preferences',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const TripPreferencesScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = Offset(1.0, 0.0);
            const end = Offset.zero;
            const curve = Curves.easeInOutCubic;
            final tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
            return SlideTransition(position: animation.drive(tween), child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.countryAllocations,
        name: 'country_allocations',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const AllocationOptionsScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = Offset(1.0, 0.0);
            const end = Offset.zero;
            const curve = Curves.easeInOutCubic;
            final tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
            return SlideTransition(position: animation.drive(tween), child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.countryItinerary,
        name: 'country_itinerary',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const CountryItineraryScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(opacity: animation, child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.citySelect,
        name: 'city_select',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const CitySelectionScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = Offset(1.0, 0.0);
            const end = Offset.zero;
            const curve = Curves.easeInOutCubic;
            final tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
            return SlideTransition(position: animation.drive(tween), child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.tripCreation,
        name: 'trip_creation',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const TripCreationScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = Offset(1.0, 0.0);
            const end = Offset.zero;
            const curve = Curves.easeInOutCubic;
            final tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
            return SlideTransition(position: animation.drive(tween), child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.generation,
        name: 'generation',
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const GenerationScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(opacity: animation, child: child);
          },
        ),
      ),
      GoRoute(
        path: Routes.itineraryView,
        name: 'itinerary_view',
        pageBuilder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return CustomTransitionPage(
            key: state.pageKey,
            child: ItineraryViewScreen(itineraryId: id),
            transitionsBuilder: (context, animation, secondaryAnimation, child) {
              const begin = Offset(0.0, 1.0);
              const end = Offset.zero;
              const curve = Curves.easeOutCubic;
              final tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
              return SlideTransition(position: animation.drive(tween), child: child);
            },
          );
        },
      ),
    ],
    errorPageBuilder: (context, state) => MaterialPage(
      key: state.pageKey,
      child: Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64),
              const SizedBox(height: 16),
              Text(
                'Page not found',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => context.go(Routes.onboarding),
                child: const Text('Go Home'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
});
