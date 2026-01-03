import 'package:flutter/foundation.dart';
import '../../data/models/product.dart';
import '../../data/models/category.dart' as data_models;
import '../../repositories/product_repository.dart';

/// ProductProvider - 商品状态管理
class ProductProvider with ChangeNotifier {
  List<Product> _products = [];
  List<data_models.Category> _categories = [];
  bool _isLoading = false;
  String? _selectedCategoryId;
  String? _searchQuery;

  final ProductRepository _repository = ProductRepository();

  List<Product> get products => _products;
  List<data_models.Category> get categories => _categories;
  bool get isLoading => _isLoading;
  String? get selectedCategoryId => _selectedCategoryId;
  String? get searchQuery => _searchQuery;

  ProductProvider() {
    loadCategories();
    loadProducts();
  }

  /// 加载商品列表
  Future<void> loadProducts({String? categoryId, String? search}) async {
    _isLoading = true;
    _selectedCategoryId = categoryId;
    _searchQuery = search;
    notifyListeners();

    try {
      // 将categoryId转换为int（如果存在）
      int? categoryIdInt;
      if (categoryId != null) {
        categoryIdInt = int.tryParse(categoryId);
      }

      final response = await _repository.getProducts(
        categoryId: categoryIdInt,
        search: search,
      );

      if (response.success && response.data != null) {
        _products = response.data!;
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
      final response = await _repository.getCategories();

      if (response.success && response.data != null) {
        _categories = response.data!;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('加载分类失败: $e');
    }
  }

  /// 获取商品详情
  Future<Product?> getProductDetail(String id) async {
    try {
      final response = await _repository.getProductDetail(id);

      if (response.success && response.data != null) {
        return response.data!;
      }
      return null;
    } catch (e) {
      debugPrint('获取商品详情失败: $e');
      return null;
    }
  }

  /// 获取商品完整详情（包含内容分区和营养信息）
  Future<Product?> getFullProductDetails(String id) async {
    try {
      final response = await _repository.getFullProductDetails(id);

      if (response.success && response.data != null) {
        return response.data!;
      }
      return null;
    } catch (e) {
      debugPrint('获取商品完整详情失败: $e');
      return null;
    }
  }

  /// 按分类筛选
  void filterByCategory(String? categoryId) {
    loadProducts(categoryId: categoryId, search: _searchQuery);
  }

  /// 搜索商品
  void searchProducts(String query) {
    loadProducts(categoryId: _selectedCategoryId, search: query);
  }

  /// 清除筛选
  void clearFilters() {
    _selectedCategoryId = null;
    _searchQuery = null;
    loadProducts();
  }
}
