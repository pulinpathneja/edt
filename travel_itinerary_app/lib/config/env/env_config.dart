/// Environment types
enum Environment { development, staging, production }

/// Environment configuration
class EnvConfig {
  EnvConfig._();

  static Environment _environment = Environment.development;

  static void initialize(Environment env) {
    _environment = env;
  }

  static Environment get environment => _environment;

  static String get apiBaseUrl {
    return switch (_environment) {
      Environment.development => 'http://localhost:8000',
      Environment.staging => 'https://edt-api-852352036956.us-central1.run.app',
      Environment.production => 'https://edt-api-852352036956.us-central1.run.app',
    };
  }

  static bool get enableLogging {
    return _environment == Environment.development;
  }

  static bool get isDevelopment => _environment == Environment.development;
  static bool get isProduction => _environment == Environment.production;
}
