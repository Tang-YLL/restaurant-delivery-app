import 'package:flutter/foundation.dart';
import '../../data/models/product.dart';
import '../../data/models/category.dart' as data_models;
import '../../services/mock_service.dart';

/// ProductProvider - 商品状态管理
class ProductProvider with ChangeNotifier {
  List<Product> _products = [];
  List<data_models.Category> _categories = [];
  bool _isLoading = false;
  String? _selectedCategory;
  String? _searchQuery;

  List<Product> get products => _products;
  List<data_models.Category> get categories => _categories;
  bool get isLoading => _isLoading;
  String? get selectedCategory => _selectedCategory;
  String? get searchQuery => _searchQuery;

  ProductProvider() {
    loadCategories();
    loadProducts();
  }

  /// 加载商品列表
  Future<void> loadProducts({String? category, String? search}) async {
    _isLoading = true;
    _selectedCategory = category;
    _searchQuery = search;
    notifyListeners();

    try {
      final response = await MockService.getProducts(
        category: category,
        search: search,
      );

      if (response.success && response.data != null) {
        _products = (response.data! as List)
            .map((item) => Product.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (e) {
      debugPrint('加载商品失败: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 加载分类列表
  Future<void> loadCategories() async {
    try {
      final response = await MockService.getCategories();

      if (response.success && response.data != null) {
        _categories = (response.data! as List)
            .map((item) => data_models.Category.fromJson(item as Map<String, dynamic>))
            .toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint('加载分类失败: $e');
    }
  }

  /// 获取商品详情
  Future<Product?> getProductDetail(String id) async {
    try {
      final response = await MockService.getProductDetail(id);

      if (response.success && response.data != null) {
        return Product.fromJson(response.data!);
      }
      return null;
    } catch (e) {
      debugPrint('获取商品详情失败: $e');
      return null;
    }
  }

  /// 按分类筛选
  void filterByCategory(String? category) {
    loadProducts(category: category, search: _searchQuery);
  }

  /// 搜索商品
  void searchProducts(String query) {
    loadProducts(category: _selectedCategory, search: query);
  }

  /// 清除筛选
  void clearFilters() {
    _selectedCategory = null;
    _searchQuery = null;
    loadProducts();
  }
}
