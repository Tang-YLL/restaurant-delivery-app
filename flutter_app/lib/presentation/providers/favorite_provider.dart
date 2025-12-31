import 'package:flutter/foundation.dart';
import 'dart:convert';
import '../../data/models/product.dart';
import '../../services/api_service.dart';
import '../../core/utils/storage_util.dart';

/// FavoriteProvider - 收藏状态管理
class FavoriteProvider with ChangeNotifier {
  List<Product> _favorites = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<Product> get favorites => _favorites;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// 检查商品是否已收藏
  bool isFavorite(String productId) {
    return _favorites.any((product) => product.id == productId);
  }

  /// 获取收藏数量
  int get favoriteCount => _favorites.length;

  /// 加载收藏列表
  Future<void> loadFavorites() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // 从本地存储读取
      final cachedData = await StorageUtil.getString('favorites');
      if (cachedData != null) {
        final productIds = jsonDecode(cachedData) as List;
        // 这里简化处理,实际应该从产品列表中查找
        debugPrint('缓存的收藏商品ID: $productIds');
      }

      // 从API获取最新数据
      final response = await ApiService.get('/favorites');

      if (response.success && response.data != null) {
        _favorites = (response.data! as List)
            .map((item) => Product.fromJson(item as Map<String, dynamic>))
            .toList();

        // 缓存商品ID列表
        final productIds = _favorites.map((p) => p.id).toList();
        await StorageUtil.setString('favorites', jsonEncode(productIds));
      }
    } catch (e) {
      _errorMessage = '加载收藏失败: $e';
      debugPrint('加载收藏失败: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 添加收藏
  Future<bool> addFavorite(Product product) async {
    _errorMessage = null;

    try {
      final response = await ApiService.post(
        '/favorites',
        data: {'productId': product.id},
      );

      if (response.success) {
        _favorites.add(product);
        await _updateCache();

        notifyListeners();
        return true;
      }

      _errorMessage = response.message ?? '添加收藏失败';
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = '添加收藏失败: $e';
      debugPrint('添加收藏失败: $e');
      notifyListeners();
      return false;
    }
  }

  /// 取消收藏
  Future<bool> removeFavorite(String productId) async {
    _errorMessage = null;

    try {
      final response = await ApiService.delete('/favorites/$productId');

      if (response.success) {
        _favorites.removeWhere((product) => product.id == productId);
        await _updateCache();

        notifyListeners();
        return true;
      }

      _errorMessage = response.message ?? '取消收藏失败';
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = '取消收藏失败: $e';
      debugPrint('取消收藏失败: $e');
      notifyListeners();
      return false;
    }
  }

  /// 切换收藏状态
  Future<bool> toggleFavorite(Product product) async {
    if (isFavorite(product.id)) {
      return await removeFavorite(product.id);
    } else {
      return await addFavorite(product);
    }
  }

  /// 清空所有收藏
  Future<bool> clearAll() async {
    try {
      final response = await ApiService.delete('/favorites/all');

      if (response.success) {
        _favorites.clear();
        await StorageUtil.remove('favorites');

        notifyListeners();
        return true;
      }

      _errorMessage = response.message ?? '清空收藏失败';
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = '清空收藏失败: $e';
      debugPrint('清空收藏失败: $e');
      notifyListeners();
      return false;
    }
  }

  /// 更新缓存
  Future<void> _updateCache() async {
    final productIds = _favorites.map((p) => p.id).toList();
    await StorageUtil.setString('favorites', jsonEncode(productIds));
  }

  /// 清除错误信息
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
