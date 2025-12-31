import 'package:hive_flutter/hive_flutter.dart';
import '../constants/storage_constants.dart';

/// Hive配置类
class HiveConfig {
  static bool _initialized = false;

  /// 初始化Hive
  static Future<void> init() async {
    if (_initialized) return;

    await Hive.initFlutter();

    // 注册适配器(如果需要存储自定义对象)
    // Hive.registerAdapter(UserAdapter());

    // 打开Box
    await Hive.openBox(StorageConstants.authBox);
    await Hive.openBox(StorageConstants.settingsBox);
    await Hive.openBox(StorageConstants.cacheBox);

    _initialized = true;
  }

  /// 获取认证Box
  static Box get authBox => Hive.box(StorageConstants.authBox);

  /// 获取设置Box
  static Box get settingsBox => Hive.box(StorageConstants.settingsBox);

  /// 获取缓存Box
  static Box get cacheBox => Hive.box(StorageConstants.cacheBox);

  /// 清空所有数据
  static Future<void> clearAll() async {
    await authBox.clear();
    await settingsBox.clear();
    await cacheBox.clear();
  }

  /// 关闭所有Box
  static Future<void> close() async {
    await Hive.close();
    _initialized = false;
  }
}
