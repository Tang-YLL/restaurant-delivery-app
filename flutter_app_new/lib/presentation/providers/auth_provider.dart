import 'package:flutter/foundation.dart';
import '../../core/utils/storage_util.dart';
import '../../data/models/user.dart';
import '../../repositories/auth_repository.dart';

/// 认证状态
enum AuthStatus {
  uninitialized,
  authenticated,
  unauthenticated,
  loading,
}

/// AuthProvider - 用户认证状态管理
class AuthProvider with ChangeNotifier {
  AuthStatus _status = AuthStatus.uninitialized;
  User? _user;
  String? _token;

  final AuthRepository _repository = AuthRepository();

  AuthStatus get status => _status;
  User? get user => _user;
  String? get token => _token;
  bool get isAuthenticated => _status == AuthStatus.authenticated;

  AuthProvider();

  /// 初始化认证状态
  Future<void> initAuth() async {
    _status = AuthStatus.loading;
    notifyListeners();

    // 从本地存储读取Token和用户信息
    final token = StorageUtil.getToken();
    final userInfo = StorageUtil.getUserInfo();

    if (token != null && userInfo != null) {
      _token = token;
      _user = User.fromJson(userInfo);
      _status = AuthStatus.authenticated;
    } else {
      _status = AuthStatus.unauthenticated;
    }

    notifyListeners();
  }

  /// 登录
  Future<bool> login(String username, String password) async {
    _status = AuthStatus.loading;
    notifyListeners();

    try {
      final response = await _repository.login(username, password);

      if (response.success) {
        final data = response.data!;
        _token = data['token'] as String;
        _user = User.fromJson(data['user'] as Map<String, dynamic>);

        // 保存到本地存储
        await StorageUtil.saveToken(_token!);

        // 计算并保存token过期时间（当前时间 + 120分钟）
        final expiry = DateTime.now().add(const Duration(minutes: 120));
        await StorageUtil.saveTokenExpiry(expiry);

        await StorageUtil.saveUserInfo(data['user'] as Map<String, dynamic>);

        // 保存refresh_token（如果有）
        if (data.containsKey('refresh_token')) {
          await StorageUtil.saveRefreshToken(data['refresh_token'] as String);
        }

        _status = AuthStatus.authenticated;
        notifyListeners();
        return true;
      } else {
        _status = AuthStatus.unauthenticated;
        notifyListeners();
        return false;
      }
    } catch (e) {
      debugPrint('登录失败: $e');
      _status = AuthStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  /// 手机号验证码登录
  Future<bool> loginWithCode(String phone, String code) async {
    _status = AuthStatus.loading;
    notifyListeners();

    try {
      final response = await _repository.loginWithCode(phone, code);

      if (response.success) {
        final data = response.data!;
        _token = data['token'] as String;
        _user = User.fromJson(data['user'] as Map<String, dynamic>);

        // 保存到本地存储
        await StorageUtil.saveToken(_token!);

        // 计算并保存token过期时间（当前时间 + 120分钟）
        final expiry = DateTime.now().add(const Duration(minutes: 120));
        await StorageUtil.saveTokenExpiry(expiry);

        await StorageUtil.saveUserInfo(data['user'] as Map<String, dynamic>);

        // 保存refresh_token（如果有）
        if (data.containsKey('refresh_token')) {
          await StorageUtil.saveRefreshToken(data['refresh_token'] as String);
        }

        _status = AuthStatus.authenticated;
        notifyListeners();
        return true;
      } else {
        _status = AuthStatus.unauthenticated;
        notifyListeners();
        return false;
      }
    } catch (e) {
      debugPrint('验证码登录失败: $e');
      _status = AuthStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  /// 发送验证码
  Future<bool> sendVerificationCode(String phone) async {
    try {
      final response = await _repository.sendVerificationCode(phone);
      return response.success;
    } catch (e) {
      debugPrint('发送验证码失败: $e');
      return false;
    }
  }

  /// 注册
  Future<bool> register(String username, String password, String email) async {
    _status = AuthStatus.loading;
    notifyListeners();

    try {
      final response = await _repository.register(username, password, email);

      if (response.success) {
        final data = response.data!;
        _token = data['token'] as String;
        _user = User.fromJson(data['user'] as Map<String, dynamic>);

        // 保存到本地存储
        await StorageUtil.saveToken(_token!);
        await StorageUtil.saveRefreshToken(data['refreshToken'] as String);
        await StorageUtil.saveUserInfo(data['user'] as Map<String, dynamic>);

        _status = AuthStatus.authenticated;
        notifyListeners();
        return true;
      } else {
        _status = AuthStatus.unauthenticated;
        notifyListeners();
        return false;
      }
    } catch (e) {
      debugPrint('注册失败: $e');
      _status = AuthStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  /// 登出
  Future<void> logout() async {
    _status = AuthStatus.loading;
    notifyListeners();

    try {
      await _repository.logout();
    } catch (e) {
      debugPrint('登出失败: $e');
    }

    // 清除本地存储
    await StorageUtil.removeToken();
    await StorageUtil.removeUserInfo();

    _token = null;
    _user = null;
    _status = AuthStatus.unauthenticated;
    notifyListeners();
  }

  /// 更新用户信息
  Future<bool> updateUserInfo(Map<String, dynamic> data) async {
    try {
      final response = await _repository.updateUserInfo(data);

      if (response.success && response.data != null) {
        _user = User.fromJson(response.data!);
        await StorageUtil.saveUserInfo(_user!.toJson());
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('更新用户信息失败: $e');
      return false;
    }
  }
}
