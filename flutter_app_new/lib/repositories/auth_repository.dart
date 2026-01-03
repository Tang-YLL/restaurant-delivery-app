import 'package:dio/dio.dart';
import '../core/config/dio_config.dart';
import '../core/models/api_response.dart';
import '../data/models/user.dart';

/// AuthRepository - 认证数据仓库
class AuthRepository {
  final Dio _dio = DioConfig.dio;

  /// 用户登录
  /// 后端接受 phone 和 password 参数
  Future<ApiResponse<Map<String, dynamic>>> login(
    String phone,
    String password,
  ) async {
    try {
      final response = await _dio.post(
        '/auth/login',
        data: {
          'phone': phone,
          'password': password,
        },
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        // 后端返回格式: {"access_token": "...", "refresh_token": "...", "user": {...}}
        final data = response.data;
        return ApiResponse.success({
          'token': data['access_token'],
          'refreshToken': data['refresh_token'],
          'user': data['user'],
        }, message: '登录成功');
      }

      return ApiResponse.error('登录失败');
    } on DioException catch (e) {
      String errorMsg = '登录失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 用户注册
  Future<ApiResponse<Map<String, dynamic>>> register(
    String username,
    String password,
    String email,
  ) async {
    try {
      final response = await _dio.post(
        '/auth/register',
        data: {
          'phone': username, // 后端使用phone字段
          'password': password,
          'email': email,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        // 后端返回格式: {"access_token": "...", "refresh_token": "...", "user": {...}}
        final data = response.data;
        return ApiResponse.success({
          'token': data['access_token'],
          'refreshToken': data['refresh_token'],
          'user': data['user'],
        }, message: '注册成功');
      }

      return ApiResponse.error('注册失败');
    } on DioException catch (e) {
      String errorMsg = '注册失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 用户登出
  Future<ApiResponse<void>> logout() async {
    try {
      final response = await _dio.post('/auth/logout');

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '登出成功');
      }

      return ApiResponse.error('登出失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '登出失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 刷新Token
  Future<ApiResponse<Map<String, dynamic>>> refreshToken(String refreshToken) async {
    try {
      final response = await _dio.post(
        '/auth/refresh',
        data: {
          'refresh_token': refreshToken,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        return ApiResponse.success({
          'token': data['access_token'],
          'refreshToken': data['refresh_token'],
        });
      }

      return ApiResponse.error('Token刷新失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? 'Token刷新失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 更新用户信息
  Future<ApiResponse<Map<String, dynamic>>> updateUserInfo(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _dio.put(
        '/users/me',
        data: data,
      );

      if (response.statusCode == 200) {
        return ApiResponse.success(
          response.data['user'] as Map<String, dynamic>,
          message: '更新成功',
        );
      }

      return ApiResponse.error('更新失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '更新失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 验证码登录
  Future<ApiResponse<Map<String, dynamic>>> loginWithCode(
    String phone,
    String code,
  ) async {
    try {
      final response = await _dio.post(
        '/auth/login-with-code',
        data: {
          'phone': phone,
          'code': code,
        },
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        // 后端返回格式: {"access_token": "...", "refresh_token": "...", "user": {...}}
        final data = response.data;
        return ApiResponse.success({
          'token': data['access_token'],
          'refreshToken': data['refresh_token'],
          'user': data['user'],
        }, message: '登录成功');
      }

      return ApiResponse.error('登录失败');
    } on DioException catch (e) {
      String errorMsg = '登录失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['detail'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 发送验证码
  Future<ApiResponse<Map<String, dynamic>>> sendVerificationCode(String phone) async {
    try {
      final response = await _dio.post(
        '/auth/send-code',
        data: {
          'phone': phone,
        },
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        // 后端返回格式: {"message": "...", "success": true, "data": {"code": "123456", "expires_in": 300}}
        final data = response.data;
        final codeData = data['data'] != null
            ? data['data'] as Map<String, dynamic>
            : <String, dynamic>{'code': '123456', 'expires_in': 300};
        return ApiResponse.success(
          codeData,
          message: data['message'] ?? '验证码已发送',
        );
      }

      return ApiResponse.error('发送验证码失败');
    } on DioException catch (e) {
      String errorMsg = '发送验证码失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['detail'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }
}
