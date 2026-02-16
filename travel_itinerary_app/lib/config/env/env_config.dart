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
      Environment.development => 'http://34.46.220.220:8000',
      Environment.staging => 'http://34.46.220.220:8000',
      Environment.production => 'http://34.46.220.220:8000',
    };
  }

  static bool get enableLogging {
    return _environment == Environment.development;
  }

  static bool get isDevelopment => _environment == Environment.development;
  static bool get isProduction => _environment == Environment.production;
}
