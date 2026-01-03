import 'package:dio/dio.dart';
import '../core/config/dio_config.dart';
import '../core/models/api_response.dart';

/// CartRepository - 购物车数据仓库
class CartRepository {
  final Dio _dio = DioConfig.dio;

  /// 获取购物车列表
  Future<ApiResponse<List<dynamic>>> getCart() async {
    try {
      final response = await _dio.get('/cart');

      if (response.statusCode == 200 && response.data != null) {
        // 后端返回格式可能是直接数组或包含items字段
        final List<dynamic> cartItems = response.data is List
            ? response.data as List<dynamic>
            : (response.data['items'] as List<dynamic>? ?? []);

        return ApiResponse.success(cartItems);
      }

      return ApiResponse.error('获取购物车失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '获取购物车失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 添加商品到购物车
  Future<ApiResponse<Map<String, dynamic>>> addToCart(
    String productId,
    int quantity,
  ) async {
    try {
      final response = await _dio.post(
        '/cart/items',
        data: {
          'product_id': productId,
          'quantity': quantity,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = response.data != null
            ? response.data as Map<String, dynamic>
            : <String, dynamic>{};
        return ApiResponse.success(
          data,
          message: '添加成功',
        );
      }

      return ApiResponse.error('添加失败');
    } on DioException catch (e) {
      String errorMsg = '添加失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 更新购物车商品数量
  Future<ApiResponse<void>> updateCartItem(
    String cartItemId,
    int quantity,
  ) async {
    try {
      final response = await _dio.put(
        '/cart/items/$cartItemId',
        data: {
          'quantity': quantity,
        },
      );

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '更新成功');
      }

      return ApiResponse.error('更新失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '更新失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 从购物车删除商品
  Future<ApiResponse<void>> removeFromCart(String cartItemId) async {
    try {
      final response = await _dio.delete('/cart/items/$cartItemId');

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '删除成功');
      }

      return ApiResponse.error('删除失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '删除失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 清空购物车
  Future<ApiResponse<void>> clearCart() async {
    try {
      final response = await _dio.delete('/cart');

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '清空成功');
      }

      return ApiResponse.error('清空失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '清空失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }
}
