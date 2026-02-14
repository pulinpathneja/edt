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
  EnvConfig.initialize(Environment.development);

  runApp(
    const ProviderScope(
      child: TravelItineraryApp(),
    ),
  );
}
