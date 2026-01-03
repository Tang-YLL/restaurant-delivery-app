import 'package:flutter/material.dart';
import '../../core/utils/storage_util.dart';
import '../../core/constants/storage_constants.dart';

/// ThemeProvider - 主题状态管理
class ThemeProvider with ChangeNotifier {
  ThemeData _themeData;
  ThemeMode _themeMode;
  bool _isDarkMode;

  ThemeProvider({bool isDarkMode = false})
      : _isDarkMode = isDarkMode,
        _themeMode = isDarkMode ? ThemeMode.dark : ThemeMode.light,
        _themeData = isDarkMode ? _darkTheme : _lightTheme {
    _loadThemeMode();
  }

  ThemeData get themeData => _themeData;
  ThemeMode get themeMode => _themeMode;
  bool get isDarkMode => _isDarkMode;

  /// 浅色主题
  static final ThemeData _lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.orange,
      brightness: Brightness.light,
    ),
    scaffoldBackgroundColor: Colors.grey[50],
    cardTheme: CardThemeData(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
    ),
  );

  /// 深色主题
  static final ThemeData _darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.orange,
      brightness: Brightness.dark,
    ),
    scaffoldBackgroundColor: Colors.grey[900],
    cardTheme: CardThemeData(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
    ),
  );

  /// 从本地加载主题模式
  Future<void> _loadThemeMode() async {
    final savedTheme = StorageUtil.getThemeMode();

    if (savedTheme != null) {
      if (savedTheme == 'dark') {
        _isDarkMode = true;
        _themeMode = ThemeMode.dark;
        _themeData = _darkTheme;
      } else {
        _isDarkMode = false;
        _themeMode = ThemeMode.light;
        _themeData = _lightTheme;
      }
      notifyListeners();
    }
  }

  /// 切换主题模式
  Future<void> toggleTheme() async {
    _isDarkMode = !_isDarkMode;
    _themeMode = _isDarkMode ? ThemeMode.dark : ThemeMode.light;
    _themeData = _isDarkMode ? _darkTheme : _lightTheme;

    // 保存到本地
    await StorageUtil.saveThemeMode(_isDarkMode ? 'dark' : 'light');

    notifyListeners();
  }

  /// 设置主题模式
  Future<void> setThemeMode(bool isDark) async {
    if (_isDarkMode != isDark) {
      await toggleTheme();
    }
  }
}
