import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../core/constants/api_constants.dart';
import '../../config/env/env_config.dart';
import '../../data/datasources/remote/api_client.dart';
import '../../data/datasources/remote/itinerary_remote_datasource.dart';
import '../../data/datasources/remote/persona_remote_datasource.dart';
import '../../data/repositories/itinerary_repository_impl.dart';
import '../../data/repositories/persona_repository_impl.dart';
import '../../domain/repositories/itinerary_repository.dart';
import '../../domain/repositories/persona_repository.dart';

part 'providers.g.dart';

/// Dio HTTP client provider (keepAlive for singleton)
@Riverpod(keepAlive: true)
Dio dio(DioRef ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: EnvConfig.apiBaseUrl,
      connectTimeout: const Duration(milliseconds: ApiConstants.connectTimeout),
      receiveTimeout: const Duration(milliseconds: ApiConstants.receiveTimeout),
      sendTimeout: const Duration(milliseconds: ApiConstants.sendTimeout),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  // Add logging interceptor in development
  if (EnvConfig.enableLogging) {
    dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (obj) => print('[API] $obj'),
      ),
    );
  }

  // Add retry interceptor
  dio.interceptors.add(
    InterceptorsWrapper(
      onError: (error, handler) async {
        if (_shouldRetry(error)) {
          try {
            final response = await _retry(dio, error.requestOptions);
            handler.resolve(response);
          } catch (e) {
            handler.next(error);
          }
        } else {
          handler.next(error);
        }
      },
    ),
  );

  return dio;
}

bool _shouldRetry(DioException error) {
  return error.type == DioExceptionType.connectionTimeout ||
      error.type == DioExceptionType.receiveTimeout ||
      (error.response?.statusCode != null &&
          error.response!.statusCode! >= 500);
}

Future<Response> _retry(Dio dio, RequestOptions requestOptions) async {
  await Future.delayed(const Duration(seconds: 1));
  return dio.fetch(requestOptions);
}

/// API Client provider
@riverpod
ApiClient apiClient(ApiClientRef ref) {
  return ApiClient(ref.watch(dioProvider));
}

/// Persona Remote DataSource provider
@riverpod
PersonaRemoteDataSource personaRemoteDataSource(
    PersonaRemoteDataSourceRef ref) {
  return PersonaRemoteDataSource(ref.watch(apiClientProvider));
}

/// Itinerary Remote DataSource provider
@riverpod
ItineraryRemoteDataSource itineraryRemoteDataSource(
    ItineraryRemoteDataSourceRef ref) {
  return ItineraryRemoteDataSource(ref.watch(apiClientProvider));
}

/// Persona Repository provider
@riverpod
PersonaRepository personaRepository(PersonaRepositoryRef ref) {
  return PersonaRepositoryImpl(ref.watch(personaRemoteDataSourceProvider));
}

/// Itinerary Repository provider
@riverpod
ItineraryRepository itineraryRepository(ItineraryRepositoryRef ref) {
  return ItineraryRepositoryImpl(ref.watch(itineraryRemoteDataSourceProvider));
}
