import 'package:dio/dio.dart';

import '../../../core/errors/exceptions.dart';

/// Generic API client wrapper around Dio
class ApiClient {
  final Dio _dio;

  ApiClient(this._dio);

  /// GET request
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// POST request
  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// PUT request
  Future<T> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// DELETE request
  Future<T> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// Handle Dio errors and convert to app exceptions
  AppException _handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return NetworkException(
          message: 'Connection timed out. Please check your internet connection.',
          code: 'TIMEOUT',
          originalError: error,
        );

      case DioExceptionType.connectionError:
        return NetworkException(
          message: 'Unable to connect to the server. Please check your internet connection.',
          code: 'CONNECTION_ERROR',
          originalError: error,
        );

      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final data = error.response?.data;
        final message = data is Map ? data['detail'] ?? data['message'] : null;

        if (statusCode != null && statusCode >= 500) {
          return ServerException(
            message: message ?? 'Server error. Please try again later.',
            code: 'SERVER_ERROR',
            statusCode: statusCode,
            originalError: error,
          );
        }

        if (statusCode == 400) {
          return ValidationException(
            message: message ?? 'Invalid request.',
            code: 'VALIDATION_ERROR',
            originalError: error,
          );
        }

        if (statusCode == 401) {
          return ClientException(
            message: 'Authentication required.',
            code: 'UNAUTHORIZED',
            statusCode: statusCode,
            originalError: error,
          );
        }

        if (statusCode == 403) {
          return ClientException(
            message: 'Access denied.',
            code: 'FORBIDDEN',
            statusCode: statusCode,
            originalError: error,
          );
        }

        if (statusCode == 404) {
          return ClientException(
            message: message ?? 'Resource not found.',
            code: 'NOT_FOUND',
            statusCode: statusCode,
            originalError: error,
          );
        }

        return ClientException(
          message: message ?? 'Request failed.',
          code: 'CLIENT_ERROR',
          statusCode: statusCode,
          originalError: error,
        );

      case DioExceptionType.cancel:
        return NetworkException(
          message: 'Request was cancelled.',
          code: 'CANCELLED',
          originalError: error,
        );

      case DioExceptionType.badCertificate:
        return NetworkException(
          message: 'Security certificate error.',
          code: 'CERTIFICATE_ERROR',
          originalError: error,
        );

      case DioExceptionType.unknown:
      default:
        return NetworkException(
          message: 'An unexpected error occurred.',
          code: 'UNKNOWN',
          originalError: error,
        );
    }
  }
}
