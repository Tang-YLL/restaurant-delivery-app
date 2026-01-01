import 'package:dio/dio.dart';
import '../core/config/dio_config.dart';
import '../core/models/api_response.dart';

/// OrderRepository - 订单数据仓库
class OrderRepository {
  final Dio _dio = DioConfig.dio;

  /// 创建订单
  Future<ApiResponse<Map<String, dynamic>>> createOrder({
    required List<Map<String, dynamic>> items,
    required String deliveryType,
    String? deliveryAddress,
    String? contactName,
    String? contactPhone,
    String? remark,
  }) async {
    try {
      // 根据配送类型确定字段名
      final data = <String, dynamic>{
        'items': items,
        'delivery_type': deliveryType,
        'remark': remark,
      };

      // 外卖配送
      if (deliveryType == 'delivery') {
        data['delivery_address'] = deliveryAddress;
        data['pickup_name'] = contactName;
        data['pickup_phone'] = contactPhone;
      }
      // 到店自取
      else {
        data['pickup_name'] = contactName;
        data['pickup_phone'] = contactPhone;
      }

      final response = await _dio.post(
        '/orders',
        data: data,
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return ApiResponse.success(
          response.data as Map<String, dynamic>,
          message: '订单创建成功',
        );
      }

      return ApiResponse.error('订单创建失败');
    } on DioException catch (e) {
      String errorMsg = '订单创建失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 获取订单列表
  Future<ApiResponse<List<dynamic>>> getOrders({
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (status != null && status.isNotEmpty) {
        queryParams['status'] = status;
      }

      final response = await _dio.get(
        '/orders',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200 && response.data != null) {
        // 后端返回格式: {"orders": [...], "pagination": {...}}
        final List<dynamic> orders = response.data['orders'] as List<dynamic>? ??
            (response.data is List ? response.data as List<dynamic> : []);

        return ApiResponse.success(orders);
      }

      return ApiResponse.error('获取订单列表失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '获取订单列表失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 获取订单详情
  Future<ApiResponse<Map<String, dynamic>>> getOrderDetail(String orderId) async {
    try {
      final response = await _dio.get('/orders/$orderId');

      if (response.statusCode == 200 && response.data != null) {
        return ApiResponse.success(
          response.data as Map<String, dynamic>,
          message: '获取成功',
        );
      }

      return ApiResponse.error('获取订单详情失败');
    } on DioException catch (e) {
      return ApiResponse.error(e.message ?? '获取订单详情失败');
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 取消订单
  Future<ApiResponse<void>> cancelOrder(String orderId) async {
    try {
      final response = await _dio.post('/orders/$orderId/cancel');

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '订单已取消');
      }

      return ApiResponse.error('取消订单失败');
    } on DioException catch (e) {
      String errorMsg = '取消订单失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  /// 确认订单
  Future<ApiResponse<void>> confirmOrder(String orderId) async {
    try {
      final response = await _dio.post('/orders/$orderId/confirm');

      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: '订单已确认');
      }

      return ApiResponse.error('确认订单失败');
    } on DioException catch (e) {
      String errorMsg = '确认订单失败';
      if (e.response?.data != null) {
        errorMsg = e.response?.data['message'] ?? errorMsg;
      }
      return ApiResponse.error(errorMsg);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }
}
