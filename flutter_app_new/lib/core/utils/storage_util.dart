import 'package:hive_flutter/hive_flutter.dart';
import '../config/hive_config.dart';
import '../constants/storage_constants.dart';

/// 存储工具类
class StorageUtil {
  // ============ Token管理 ============

  /// 保存Token
  static Future<void> saveToken(String token) async {
    await HiveConfig.authBox.put(StorageConstants.tokenKey, token);
  }

  /// 获取Token
  static String? getToken() {
    return HiveConfig.authBox.get(StorageConstants.tokenKey) as String?;
  }

  /// 删除Token
  static Future<void> removeToken() async {
    await HiveConfig.authBox.delete(StorageConstants.tokenKey);
  }

  /// 保存RefreshToken
  static Future<void> saveRefreshToken(String refreshToken) async {
    await HiveConfig.authBox.put(StorageConstants.refreshTokenKey, refreshToken);
  }

  /// 获取RefreshToken
  static String? getRefreshToken() {
    return HiveConfig.authBox.get(StorageConstants.refreshTokenKey) as String?;
  }

  /// 删除RefreshToken
  static Future<void> removeRefreshToken() async {
    await HiveConfig.authBox.delete(StorageConstants.refreshTokenKey);
  }

  // ============ 用户信息管理 ============

  /// 保存用户信息
  static Future<void> saveUserInfo(Map<String, dynamic> userInfo) async {
    await HiveConfig.authBox.put(StorageConstants.userInfoKey, userInfo);
  }

  /// 获取用户信息
  static Map<String, dynamic>? getUserInfo() {
    final data = HiveConfig.authBox.get(StorageConstants.userInfoKey);
    if (data == null) return null;
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    return null;
  }

  /// 删除用户信息
  static Future<void> removeUserInfo() async {
    await HiveConfig.authBox.delete(StorageConstants.userInfoKey);
  }

  // ============ 主题管理 ============

  /// 保存主题模式
  static Future<void> saveThemeMode(String themeMode) async {
    await HiveConfig.settingsBox.put(StorageConstants.themeKey, themeMode);
  }

  /// 获取主题模式
  static String? getThemeMode() {
    return HiveConfig.settingsBox.get(StorageConstants.themeKey) as String?;
  }

  // ============ 语言管理 ============

  /// 保存语言
  static Future<void> saveLanguage(String languageCode) async {
    await HiveConfig.settingsBox.put(StorageConstants.languageKey, languageCode);
  }

  /// 获取语言
  static String? getLanguage() {
    return HiveConfig.settingsBox.get(StorageConstants.languageKey) as String?;
  }

  // ============ 通用存储方法 ============

  /// 保存数据
  static Future<void> put(String boxName, String key, dynamic value) async {
    final box = await Hive.openBox(boxName);
    await box.put(key, value);
  }

  /// 获取数据
  static dynamic get(String boxName, String key) {
    final box = Hive.box(boxName);
    return box.get(key);
  }

  /// 删除数据
  static Future<void> delete(String boxName, String key) async {
    final box = await Hive.openBox(boxName);
    await box.delete(key);
  }

  /// 清空指定Box
  static Future<void> clearBox(String boxName) async {
    final box = await Hive.openBox(boxName);
    await box.clear();
  }

  /// 检查Key是否存在
  static bool containsKey(String boxName, String key) {
    final box = Hive.box(boxName);
    return box.containsKey(key);
  }

  // ============ 便捷字符串存储方法 ============

  /// 保存字符串
  static Future<void> setString(String boxName, String key, String value) async {
    final box = await Hive.openBox(boxName);
    await box.put(key, value);
  }

  /// 获取字符串
  static String? getString(String boxName, String key) {
    final box = Hive.box(boxName);
    return box.get(key) as String?;
  }

  // ============ 针对特定Box的便捷方法 ============

  /// 从addressBox获取字符串
  static Future<String?> getAddressString(String key) async {
    final box = await Hive.openBox('addressBox');
    return box.get(key) as String?;
  }

  /// 保存字符串到addressBox
  static Future<void> setAddressString(String key, String value) async {
    final box = await Hive.openBox('addressBox');
    await box.put(key, value);
  }

  /// 从favoriteBox获取字符串
  static Future<String?> getFavoriteString(String key) async {
    final box = await Hive.openBox('favoriteBox');
    return box.get(key) as String?;
  }

  /// 保存字符串到favoriteBox
  static Future<void> setFavoriteString(String key, String value) async {
    final box = await Hive.openBox('favoriteBox');
    await box.put(key, value);
  }

  /// 从favoriteBox删除数据
  static Future<void> removeFavorite(String key) async {
    final box = await Hive.openBox('favoriteBox');
    await box.delete(key);
  }
}
