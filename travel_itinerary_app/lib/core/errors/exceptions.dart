/// Base exception class for the application
sealed class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic originalError;

  const AppException({
    required this.message,
    this.code,
    this.originalError,
  });

  @override
  String toString() => 'AppException: $message (code: $code)';
}

/// Network-related exceptions
class NetworkException extends AppException {
  const NetworkException({
    required super.message,
    super.code,
    super.originalError,
  });
}

/// Server-side exceptions (5xx errors)
class ServerException extends AppException {
  final int? statusCode;

  const ServerException({
    required super.message,
    super.code,
    super.originalError,
    this.statusCode,
  });
}

/// Client-side exceptions (4xx errors)
class ClientException extends AppException {
  final int? statusCode;

  const ClientException({
    required super.message,
    super.code,
    super.originalError,
    this.statusCode,
  });
}

/// Data parsing/serialization exceptions
class ParseException extends AppException {
  const ParseException({
    required super.message,
    super.code,
    super.originalError,
  });
}

/// Cache/storage exceptions
class CacheException extends AppException {
  const CacheException({
    required super.message,
    super.code,
    super.originalError,
  });
}

/// Validation exceptions
class ValidationException extends AppException {
  final Map<String, List<String>>? fieldErrors;

  const ValidationException({
    required super.message,
    super.code,
    super.originalError,
    this.fieldErrors,
  });
}

/// Generation-specific exceptions
class GenerationException extends AppException {
  const GenerationException({
    required super.message,
    super.code,
    super.originalError,
  });
}
