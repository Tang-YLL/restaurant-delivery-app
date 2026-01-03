import 'package:flutter/foundation.dart';
import '../../data/models/product.dart';
import '../../repositories/favorite_repository.dart';

/// FavoriteProvider - 收藏状态管理
class FavoriteProvider with ChangeNotifier {
  List<Product> _favorites = [];
  bool _isLoading = false;
  String? _errorMessage;

  final FavoriteRepository _repository = FavoriteRepository();

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
      final response = await _repository.getFavorites();

      if (response.success && response.data != null) {
        _favorites = response.data!;
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
      final response = await _repository.addFavorite(product.id);

      if (response.success) {
        _favorites.add(product);
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
      final response = await _repository.removeFavorite(productId);

      if (response.success) {
        _favorites.removeWhere((product) => product.id == productId);
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
      final response = await _repository.clearFavorites();

      if (response.success) {
        _favorites.clear();
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

  /// 清除错误信息
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
