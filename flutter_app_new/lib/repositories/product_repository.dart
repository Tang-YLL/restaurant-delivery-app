import 'package:dio/dio.dart';
import '../core/config/dio_config.dart';
import '../core/models/api_response.dart';
import '../data/models/product.dart';
import '../data/models/category.dart' as data_models;

/// ProductRepository - 商品数据仓库
class ProductRepository {
  final Dio _dio = DioConfig.dio;

  /// 获取商品列表
  Future<ApiResponse<List<Product>>> getProducts({
    int? categoryId,
    String? search,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (categoryId != null) {
        queryParams['category_id'] = categoryId;
      }

      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }

      final response = await _dio.get(
        '/products',
        queryParameters: queryParams,
      );

      // 后端返回格式: {"products": [...], "pagination": {...}}
      if (response.statusCode == 200 && response.data != null) {
        final List<Product> products = (response.data['products'] as List)
            .map((item) => Product.fromJson(item as Map<String, dynamic>))
            .toList();

        return ApiResponse.success(products);
      }

      return ApiResponse.error('获取商品列表失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '网络请求失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 获取商品详情
  Future<ApiResponse<Product>> getProductDetail(String id) async {
    try {
      final response = await _dio.get('/products/$id');

      if (response.statusCode == 200 && response.data != null) {
        final product = Product.fromJson(response.data);
        return ApiResponse.success(product);
      }

      return ApiResponse.error('获取商品详情失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '网络请求失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 获取分类列表
  Future<ApiResponse<List<data_models.Category>>> getCategories() async {
    try {
      final response = await _dio.get('/categories');

      if (response.statusCode == 200 && response.data != null) {
        final List<data_models.Category> categories =
            (response.data as List)
                .map((item) => data_models.Category.fromJson(item as Map<String, dynamic>))
                .toList();

        return ApiResponse.success(categories);
      }

      return ApiResponse.error('获取分类列表失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '网络请求失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }
}
