import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'app.dart';
import 'config/env/env_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Hive for local storage
  await Hive.initFlutter();

  // Initialize environment configuration
  // Use --dart-define=ENV=production for deployed builds
  const envStr = String.fromEnvironment('ENV', defaultValue: 'development');
  final env = switch (envStr) {
    'production' => Environment.production,
    'staging' => Environment.staging,
    _ => Environment.development,
  };
  EnvConfig.initialize(env);

  runApp(
    const ProviderScope(
      child: TravelItineraryApp(),
    ),
  );
}
