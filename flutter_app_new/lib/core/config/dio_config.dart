import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import '../constants/api_constants.dart';
import '../utils/storage_util.dart';
import '../models/api_response.dart';
import '../../presentation/services/navigation_service.dart';

/// Dio配置类
class DioConfig {
  static Dio? _instance;
  static final Logger _logger = Logger();
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
    _instance!.interceptors.add(InterceptorsWrapper(
      // 请求拦截器
      onRequest: (options, handler) async {
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
              _logger.d('Token即将过期，主动刷新...');
              await _refreshToken();

              // 获取新token
              final newToken = StorageUtil.getToken();
              if (newToken != null && newToken.isNotEmpty) {
                options.headers['Authorization'] = 'Bearer $newToken';
              }
            } else if (timeUntilExpiry.inSeconds <= 0) {
              // token已过期，尝试刷新
              _logger.d('Token已过期，尝试刷新...');
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

        _logger.d('========== Request ==========');
        _logger.d('Method: ${options.method}');
        _logger.d('URL: ${options.uri}');
        _logger.d('Headers: ${options.headers}');
        _logger.d('Data: ${options.data}');
        _logger.d('============================');

        return handler.next(options);
      },

      // 响应拦截器
      onResponse: (response, handler) {
        _logger.d('========== Response ==========');
        _logger.d('Status: ${response.statusCode}');
        _logger.d('Data: ${response.data}');
        _logger.d('=============================');

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
        _logger.e('========== Error ==========');
        _logger.e('Type: ${error.type}');
        _logger.e('Message: ${error.message}');
        _logger.e('Response: ${error.response}');
        _logger.e('===========================');

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
}
