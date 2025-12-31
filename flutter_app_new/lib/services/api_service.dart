import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import '../core/config/dio_config.dart';
import '../core/models/api_response.dart';
import 'dart:developer' as developer;

/// API服务基类（静态方法）
class ApiService {
  static final Dio _dio = DioConfig.dio;
  static final Logger _logger = Logger();

  /// GET请求
  static Future<ApiResponse<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    T Function(dynamic)? dataParser,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
      return ApiResponse.fromJson(response.data, dataParser);
    } on DioException catch (e) {
      throw e.error ?? ApiException(-1, '请求失败');
    } catch (e) {
      _logger.e('GET请求失败: $e');
      throw NetworkException(e.toString());
    }
  }

  /// POST请求
  static Future<ApiResponse<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    T Function(dynamic)? dataParser,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return ApiResponse.fromJson(response.data, dataParser);
    } on DioException catch (e) {
      throw e.error ?? ApiException(-1, '请求失败');
    } catch (e) {
      _logger.e('POST请求失败: $e');
      throw NetworkException(e.toString());
    }
  }

  /// PUT请求
  static Future<ApiResponse<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    T Function(dynamic)? dataParser,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return ApiResponse.fromJson(response.data, dataParser);
    } on DioException catch (e) {
      throw e.error ?? ApiException(-1, '请求失败');
    } catch (e) {
      _logger.e('PUT请求失败: $e');
      throw NetworkException(e.toString());
    }
  }

  /// DELETE请求
  static Future<ApiResponse<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    T Function(dynamic)? dataParser,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return ApiResponse.fromJson(response.data, dataParser);
    } on DioException catch (e) {
      throw e.error ?? ApiException(-1, '请求失败');
    } catch (e) {
      _logger.e('DELETE请求失败: $e');
      throw NetworkException(e.toString());
    }
  }

  /// PATCH请求
  static Future<ApiResponse<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    T Function(dynamic)? dataParser,
  }) async {
    try {
      final response = await _dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return ApiResponse.fromJson(response.data, dataParser);
    } on DioException catch (e) {
      throw e.error ?? ApiException(-1, '请求失败');
    } catch (e) {
      _logger.e('PATCH请求失败: $e');
      throw NetworkException(e.toString());
    }
  }

  /// 文件上传
  static Future<ApiResponse<T>> upload<T>(
    String path,
    FormData formData, {
    Options? options,
    T Function(dynamic)? dataParser,
    ProgressCallback? onSendProgress,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: formData,
        options: options,
        onSendProgress: onSendProgress,
      );
      return ApiResponse.fromJson(response.data, dataParser);
    } on DioException catch (e) {
      throw e.error ?? ApiException(-1, '上传失败');
    } catch (e) {
      _logger.e('文件上传失败: $e');
      throw NetworkException(e.toString());
    }
  }

  /// 文件下载
  static Future<void> download(
    String url,
    String savePath, {
    ProgressCallback? onReceiveProgress,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      await _dio.download(
        url,
        savePath,
        onReceiveProgress: onReceiveProgress,
        queryParameters: queryParameters,
      );
    } on DioException catch (e) {
      throw e.error ?? ApiException(-1, '下载失败');
    } catch (e) {
      _logger.e('文件下载失败: $e');
      throw NetworkException(e.toString());
    }
  }
}
