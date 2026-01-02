import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../data/models/product.dart';
import '../../data/models/category.dart' as data_models;
import '../../repositories/product_repository.dart';

/// ProductProvider - 商品状态管理
class ProductProvider with ChangeNotifier {
  List<Product> _products = [];
  List<data_models.Category> _categories = [];
  bool _isLoading = false;
  bool _isSearching = false;  // 新增：搜索中状态
  String? _selectedCategoryId;
  String? _searchQuery;

  final ProductRepository _repository = ProductRepository();

  // 搜索防抖定时器
  Timer? _searchDebounce;

  List<Product> get products => _products;
  List<data_models.Category> get categories => _categories;
  bool get isLoading => _isLoading;
  bool get isSearching => _isSearching;  // 新增：搜索中getter
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
      _isSearching = false;  // 搜索完成，重置搜索状态
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

  /// 按分类筛选
  void filterByCategory(String? categoryId) {
    loadProducts(categoryId: categoryId, search: _searchQuery);
  }

  /// 搜索商品（带防抖）
  void searchProducts(String query) {
    // 取消之前的定时器
    if (_searchDebounce?.isActive ?? false) {
      _searchDebounce!.cancel();
    }

    // 如果搜索为空，立即清除筛选
    if (query.isEmpty) {
      _searchDebounce = null;
      _isSearching = false;
      notifyListeners();
      loadProducts(categoryId: _selectedCategoryId, search: null);
      return;
    }

    // 设置搜索中状态
    _isSearching = true;
    notifyListeners();

    // 设置新的防抖定时器（500ms后执行搜索）
    _searchDebounce = Timer(const Duration(milliseconds: 500), () {
      debugPrint('🔍 [防抖] 执行搜索: $query');
      loadProducts(categoryId: _selectedCategoryId, search: query);
    });
  }

  /// 清除筛选
  void clearFilters() {
    _selectedCategoryId = null;
    _searchQuery = null;
    loadProducts();
  }

  @override
  void dispose() {
    // 取消防抖定时器
    _searchDebounce?.cancel();
    super.dispose();
  }
}
