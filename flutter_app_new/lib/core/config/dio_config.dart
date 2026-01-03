import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';
import '../constants/api_constants.dart';
import '../utils/storage_util.dart';
import '../models/api_response.dart';
import '../../presentation/services/navigation_service.dart';

/// Dio配置类
class DioConfig {
  static Dio? _instance;
  static final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 0,
      errorMethodCount: 5,
      lineLength: 120,
      colors: true,
      printEmojis: true,
      printTime: true,
    ),
  );
  static bool _isRefreshing = false;

  /// Token提前刷新时间（秒）- 在过期前5分钟刷新
  static const int _refreshBufferSeconds = 300; // 5分钟

  /// 获取单例Dio实例
  static Dio get dio {
    if (_instance == null) {
      _instance = Dio(_baseOptions);
      _setupInterceptors();
    }
    return _instance!;
  }

  /// 基础配置
  static final BaseOptions _baseOptions = BaseOptions(
    baseUrl: ApiConstants.baseUrl,
    connectTimeout: const Duration(milliseconds: ApiConstants.connectTimeout),
    receiveTimeout: const Duration(milliseconds: ApiConstants.receiveTimeout),
    sendTimeout: const Duration(milliseconds: ApiConstants.sendTimeout),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  );

  /// 设置拦截器
  static void _setupInterceptors() {
    // 记录请求开始时间
    final Map<String, DateTime> requestTimes = {};

    _instance!.interceptors.add(InterceptorsWrapper(
      // 请求拦截器
      onRequest: (options, handler) async {
        // 记录请求开始时间
        final requestKey = '${options.method}-${options.uri}';
        requestTimes[requestKey] = DateTime.now();

        // 检查token是否需要主动刷新
        final token = StorageUtil.getToken();
        if (token != null && token.isNotEmpty) {
          // 检查是否即将过期
          final expiry = StorageUtil.getTokenExpiry();
          if (expiry != null) {
            final now = DateTime.now();
            final timeUntilExpiry = expiry.difference(now);

            // 如果在5分钟内过期，先刷新token
            if (timeUntilExpiry.inSeconds < _refreshBufferSeconds &&
                timeUntilExpiry.inSeconds > 0) {
              debugPrint('🔄 Token即将过期，主动刷新...');
              await _refreshToken();

              // 获取新token
              final newToken = StorageUtil.getToken();
              if (newToken != null && newToken.isNotEmpty) {
                options.headers['Authorization'] = 'Bearer $newToken';
              }
            } else if (timeUntilExpiry.inSeconds <= 0) {
              // token已过期，尝试刷新
              debugPrint('⏰ Token已过期，尝试刷新...');
              final refreshed = await _refreshToken();
              if (refreshed) {
                final newToken = StorageUtil.getToken();
                if (newToken != null && newToken.isNotEmpty) {
                  options.headers['Authorization'] = 'Bearer $newToken';
                }
              }
            }
          }

          // 注入Token（如果还没有）
          if (!options.headers.containsKey('Authorization')) {
            options.headers['Authorization'] = 'Bearer $token';
          }
        }

        // ========== 详细的请求日志 ==========
        debugPrint('┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');
        debugPrint('│ 🚀 网络请求开始');
        debugPrint('├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');
        debugPrint('│ 📌 请求方法: ${options.method.toUpperCase()}');
        debugPrint('│ 🌐 请求URL: ${options.uri}');
        debugPrint('│ ⏰ 请求时间: ${DateTime.now().toIso8601String()}');

        // 请求头（隐藏敏感信息）
        final headers = Map<String, dynamic>.from(options.headers);
        if (headers.containsKey('Authorization')) {
          final auth = headers['Authorization'] as String;
          if (auth.length > 50) {
            headers['Authorization'] = '${auth.substring(0, 20)}...${auth.substring(auth.length - 20)}';
          }
        }
        debugPrint('│ 📋 请求头: ${_formatJson(headers)}');

        // 请求体
        if (options.data != null) {
          if (options.data is FormData) {
            debugPrint('│ 📦 请求类型: FormData (文件上传)');
            debugPrint('│ 📦 FormData字段: ${(options.data as FormData).fields.map((e) => e.key).join(', ')}');
          } else {
            debugPrint('│ 📦 请求体: ${_formatJson(options.data)}');
          }
        } else {
          debugPrint('│ 📦 请求体: (无)');
        }

        // 查询参数
        if (options.queryParameters.isNotEmpty) {
          debugPrint('│ 🔍 查询参数: ${_formatJson(options.queryParameters)}');
        }

        debugPrint('└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');

        return handler.next(options);
      },

      // 响应拦截器
      onResponse: (response, handler) {
        // 计算请求耗时
        final requestKey = '${response.requestOptions.method}-${response.requestOptions.uri}';
        final startTime = requestTimes[requestKey];
        final duration = startTime != null
            ? DateTime.now().difference(startTime).inMilliseconds
            : 0;

        debugPrint('┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');
        debugPrint('│ ✅ 响应成功');
        debugPrint('├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');
        debugPrint('│ 📌 响应状态: ${response.statusCode} ${_getStatusText(response.statusCode)}');
        debugPrint('│ ⏱️ 请求耗时: ${duration}ms');
        debugPrint('│ 🌐 响应URL: ${response.requestOptions.uri}');

        // 响应体（格式化）
        if (response.data != null) {
          final String dataStr = _formatJson(response.data);
          if (dataStr.length > 1000) {
            debugPrint('│ 📦 响应体: ${dataStr.substring(0, 1000)}...\n│ (数据过长，已截断，完整长度: ${dataStr.length} 字符)');
          } else {
            debugPrint('│ 📦 响应体: $dataStr');
          }
        } else {
          debugPrint('│ 📦 响应体: (空)');
        }

        debugPrint('└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');

        // 统一处理响应
        if (response.statusCode == 200 || response.statusCode == 201) {
          return handler.next(response);
        } else {
          throw ApiException(
            response.statusCode ?? -1,
            response.data?['message'] ?? '请求失败',
          );
        }
      },

      // 错误拦截器
      onError: (error, handler) async {
        // 计算请求耗时
        final requestKey = '${error.requestOptions.method}-${error.requestOptions.uri}';
        final startTime = requestTimes[requestKey];
        final duration = startTime != null
            ? DateTime.now().difference(startTime).inMilliseconds
            : 0;

        debugPrint('┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');
        debugPrint('│ ❌ 请求失败');
        debugPrint('├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');
        debugPrint('│ ⏱️ 请求耗时: ${duration}ms');
        debugPrint('│ 🌐 请求URL: ${error.requestOptions.uri}');
        debugPrint('│ 📌 错误类型: ${error.type}');

        // 错误消息
        debugPrint('│ 💬 错误消息: ${error.message}');

        // 状态码和响应
        if (error.response != null) {
          debugPrint('│ 🔴 状态码: ${error.response?.statusCode} ${_getStatusText(error.response?.statusCode)}');

          if (error.response?.data != null) {
            final String errorStr = _formatJson(error.response?.data);
            if (errorStr.length > 500) {
              debugPrint('│ 📄 错误详情: ${errorStr.substring(0, 500)}...\n│ (数据过长，已截断)');
            } else {
              debugPrint('│ 📄 错误详情: $errorStr');
            }
          }
        }

        // 堆栈跟踪（仅在调试模式）
        if (kDebugMode && error.error != null) {
          debugPrint('│ 🔧 原始错误: ${error.error}');
        }

        debugPrint('└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────');

        // 统一错误处理
        String errorMessage;
        int errorCode = -1;

        if (error.type == DioExceptionType.connectionTimeout ||
            error.type == DioExceptionType.sendTimeout ||
            error.type == DioExceptionType.receiveTimeout) {
          errorMessage = '网络连接超时,请检查网络';
        } else if (error.type == DioExceptionType.connectionError) {
          errorMessage = '网络连接失败,请检查网络';
        } else if (error.type == DioExceptionType.badResponse) {
          errorCode = error.response?.statusCode ?? -1;

          // 401/403错误 - 尝试刷新Token
          if ((errorCode == 401 || errorCode == 403) &&
              error.requestOptions.path != '/auth/refresh' &&
              error.requestOptions.path != '/auth/login') {
            try {
              final refreshed = await _refreshToken();
              if (refreshed) {
                // 重试原请求
                final token = StorageUtil.getToken();
                error.requestOptions.headers['Authorization'] = 'Bearer $token';

                final response = await dio.fetch(error.requestOptions);
                return handler.resolve(response);
              }
            } catch (e) {
              _logger.e('刷新Token失败: $e');
            }

            // 刷新失败，清除Token并跳转登录
            await _handleUnauthorized();
          }

          switch (errorCode) {
            case 400:
              errorMessage = error.response?.data?['message'] ?? '请求参数错误';
              break;
            case 401:
              errorMessage = '未授权,请重新登录';
              break;
            case 403:
              errorMessage = '登录已过期,请重新登录';
              break;
            case 404:
              errorMessage = '请求的资源不存在';
              break;
            case 500:
              errorMessage = '服务器内部错误';
              break;
            case 502:
            case 503:
            case 504:
              errorMessage = '服务器维护中,请稍后重试';
              break;
            default:
              errorMessage = error.response?.data?['message'] ?? '网络请求失败';
          }
        } else {
          errorMessage = '未知错误: ${error.message}';
        }

        return handler.reject(DioException(
          requestOptions: error.requestOptions,
          error: ApiException(errorCode, errorMessage),
          response: error.response,
          type: error.type,
        ));
      },
    ));
  }

  /// 刷新Token
  static Future<bool> _refreshToken() async {
    if (_isRefreshing) {
      _logger.d('Token正在刷新中，跳过重复请求');
      return false;
    }

    _isRefreshing = true;
    try {
      final refreshToken = StorageUtil.getRefreshToken();
      if (refreshToken == null || refreshToken.isEmpty) {
        _logger.e('RefreshToken不存在');
        return false;
      }

      // 创建临时Dio实例避免拦截器循环
      final tempDio = Dio(BaseOptions(
        baseUrl: ApiConstants.baseUrl,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ));

      final response = await tempDio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200 && response.data != null) {
        final newToken = response.data['access_token'] as String?;
        final newRefreshToken = response.data['refresh_token'] as String?;

        if (newToken != null) {
          await StorageUtil.saveToken(newToken);

          // 计算并保存token过期时间（当前时间 + 120分钟）
          final expiry = DateTime.now().add(const Duration(minutes: 120));
          await StorageUtil.saveTokenExpiry(expiry);
          _logger.d('Token过期时间: $expiry');

          if (newRefreshToken != null) {
            await StorageUtil.saveRefreshToken(newRefreshToken);
          }

          updateToken(newToken);
          _logger.d('Token刷新成功');
          return true;
        }
      }
      return false;
    } catch (e) {
      _logger.e('刷新Token异常: $e');
      return false;
    } finally {
      _isRefreshing = false;
    }
  }

  /// 处理401未授权
  static Future<void> _handleUnauthorized() async {
    // 清除Token
    await StorageUtil.removeToken();
    await StorageUtil.removeRefreshToken();
    await StorageUtil.removeUserInfo();

    // 跳转到登录页
    NavigationService.logoutAndNavigateToLogin();
  }

  /// 更新Token
  static void updateToken(String token) {
    dio.options.headers['Authorization'] = 'Bearer $token';
  }

  /// 清除Token
  static void clearToken() {
    dio.options.headers.remove('Authorization');
  }

  /// 格式化JSON输出
  static String _formatJson(dynamic data) {
    if (data == null) return '(null)';

    try {
      if (data is String) {
        // 尝试解析JSON字符串
        try {
          final parsed = jsonDecode(data);
          return const JsonEncoder.withIndent('  ').convert(parsed);
        } catch (e) {
          return data;
        }
      } else if (data is Map || data is List) {
        // 直接格式化Map或List
        return const JsonEncoder.withIndent('  ').convert(data);
      } else {
        return data.toString();
      }
    } catch (e) {
      return data.toString();
    }
  }

  /// 获取HTTP状态码文本
  static String _getStatusText(int? statusCode) {
    if (statusCode == null) return '';

    switch (statusCode) {
      case 200:
        return 'OK';
      case 201:
        return 'Created';
      case 204:
        return 'No Content';
      case 400:
        return 'Bad Request';
      case 401:
        return 'Unauthorized';
      case 403:
        return 'Forbidden';
      case 404:
        return 'Not Found';
      case 500:
        return 'Internal Server Error';
      case 502:
        return 'Bad Gateway';
      case 503:
        return 'Service Unavailable';
      default:
        return '';
    }
  }
}
