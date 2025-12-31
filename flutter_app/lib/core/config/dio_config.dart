import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import '../constants/api_constants.dart';
import '../utils/storage_util.dart';
import '../models/api_response.dart';

/// Dio配置类
class DioConfig {
  static Dio? _instance;
  static final Logger _logger = Logger();

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
        // 注入Token
        final token = StorageUtil.getToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
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
      onError: (error, handler) {
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

          switch (errorCode) {
            case 400:
              errorMessage = error.response?.data?['message'] ?? '请求参数错误';
              break;
            case 401:
              errorMessage = '未授权,请重新登录';
              // TODO: 跳转到登录页或刷新Token
              _handleUnauthorized();
              break;
            case 403:
              errorMessage = '拒绝访问';
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

  /// 处理401未授权
  static void _handleUnauthorized() async {
    // 清除Token
    await StorageUtil.removeToken();
    await StorageUtil.removeRefreshToken();
    await StorageUtil.removeUserInfo();

    // TODO: 跳转到登录页
    // NavigationService.navigateTo(Routes.login);
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
