import 'package:flutter/foundation.dart';
import '../../core/utils/storage_util.dart';
import '../../data/models/user.dart';
import '../../services/mock_service.dart';

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
      final response = await MockService.login(username, password);

      if (response.success) {
        final data = response.data!;
        _token = data['token'] as String;
        _user = User.fromJson(data['user'] as Map<String, dynamic>);

        // 保存到本地存储
        await StorageUtil.saveToken(_token!);
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
      final response = await MockService.verifyCode(phone, code);

      if (response.success) {
        final data = response.data!;
        _token = data['token'] as String;
        _user = User.fromJson(data['user'] as Map<String, dynamic>);

        // 保存到本地存储
        await StorageUtil.saveToken(_token!);
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
      _status = AuthStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  /// 发送验证码
  Future<bool> sendVerificationCode(String phone) async {
    try {
      final response = await MockService.sendVerificationCode(phone);
      return response.success;
    } catch (e) {
      return false;
    }
  }

  /// 注册
  Future<bool> register(String username, String password, String email) async {
    _status = AuthStatus.loading;
    notifyListeners();

    try {
      final response = await MockService.register(username, password, email);

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
      _status = AuthStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  /// 登出
  Future<void> logout() async {
    _status = AuthStatus.loading;
    notifyListeners();

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
      final response = await MockService.updateUserInfo(data);

      if (response.success && response.data != null) {
        _user = User.fromJson(response.data!);
        await StorageUtil.saveUserInfo(_user!.toJson());
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
