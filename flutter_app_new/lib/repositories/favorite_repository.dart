import 'package:dio/dio.dart';
import '../core/config/dio_config.dart';
import '../core/models/api_response.dart';
import '../data/models/product.dart';

/// FavoriteRepository - 收藏数据仓库
class FavoriteRepository {
  final Dio _dio = DioConfig.dio;

  /// 获取收藏列表
  Future<ApiResponse<List<Product>>> getFavorites() async {
    try {
      final response = await _dio.get('/favorites');

      if (response.statusCode == 200) {
        final List<Product> favorites = (response.data['favorites'] as List)
            .map((item) => Product.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse.success(favorites);
      }

      return ApiResponse.error('获取收藏列表失败');
    } on DioException catch (e) {
      String errorMsg = '获取收藏列表失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 添加收藏
  Future<ApiResponse<void>> addFavorite(String productId) async {
    try {
      final response = await _dio.post(
        '/favorites',
        data: {
          'product_id': productId,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return ApiResponse.success(null, message: '添加成功');
      }

      return ApiResponse.error('添加收藏失败');
    } on DioException catch (e) {
      String errorMsg = '添加收藏失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 取消收藏
  Future<ApiResponse<void>> removeFavorite(String productId) async {
    try {
      final response = await _dio.delete('/favorites/$productId');

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '取消成功');
      }

      return ApiResponse.error('取消收藏失败');
    } on DioException catch (e) {
      String errorMsg = '取消收藏失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 清空所有收藏
  Future<ApiResponse<void>> clearFavorites() async {
    try {
      final response = await _dio.delete('/favorites/all');

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '清空成功');
      }

      return ApiResponse.error('清空收藏失败');
    } on DioException catch (e) {
      String errorMsg = '清空收藏失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }
}
