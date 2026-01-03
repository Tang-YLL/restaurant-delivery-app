import 'package:flutter/foundation.dart';
import 'dart:convert';
import '../../data/models/review.dart';
import '../../services/api_service.dart';
import '../../core/utils/storage_util.dart';

/// ReviewProvider - 评价状态管理
class ReviewProvider with ChangeNotifier {
  List<Review> _reviews = [];
  ReviewStatistics? _statistics;
  bool _isLoading = false;
  String? _errorMessage;

  List<Review> get reviews => _reviews;
  ReviewStatistics? get statistics => _statistics;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// 加载商品评价列表
  Future<void> loadReviews(String productId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // 先尝试从本地缓存读取
      final cachedData = await StorageUtil.getString('reviewBox', 'reviews_$productId');
      if (cachedData != null) {
        final jsonData = jsonDecode(cachedData);
        _reviews = (jsonData['reviews'] as List)
            .map((item) => Review.fromJson(item as Map<String, dynamic>))
            .toList();
        _statistics = jsonData['statistics'] != null
            ? ReviewStatistics.fromJson(jsonData['statistics'])
            : null;
        notifyListeners();
      }

      // 从API获取最新数据
      final response = await ApiService.get('/products/$productId/reviews');

      if (response.success && response.data != null) {
        final data = response.data!;
        _reviews = (data['reviews'] as List)
            .map((item) => Review.fromJson(item as Map<String, dynamic>))
            .toList();
        _statistics = data['statistics'] != null
            ? ReviewStatistics.fromJson(data['statistics'])
            : null;

        // 缓存到本地
        await StorageUtil.setString(
          'reviewBox',
          'reviews_$productId',
          jsonEncode({
            'reviews': _reviews.map((r) => r.toJson()).toList(),
            'statistics': _statistics?.toJson(),
          }),
        );
      }
    } catch (e) {
      _errorMessage = '加载评价失败: $e';
      debugPrint('加载评价失败: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 提交评价
  Future<bool> submitReview(Review review) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await ApiService.post('/reviews', data: review.toJson());

      if (response.success) {
        // 添加到本地列表
        _reviews.insert(0, review);

        // 更新缓存
        final cachedData = await StorageUtil.getString('reviewBox', 'reviews_${review.productId}');
        if (cachedData != null) {
          final jsonData = jsonDecode(cachedData);
          final reviews = (jsonData['reviews'] as List)
              .map((item) => Review.fromJson(item as Map<String, dynamic>))
              .toList();
          reviews.insert(0, review);
          await StorageUtil.setString(
            'reviewBox',
            'reviews_${review.productId}',
            jsonEncode({
              'reviews': reviews.map((r) => r.toJson()).toList(),
              'statistics': _statistics?.toJson(),
            }),
          );
        }

        _isLoading = false;
        notifyListeners();
        return true;
      }

      _errorMessage = response.message ?? '提交评价失败';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = '提交评价失败: $e';
      debugPrint('提交评价失败: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 获取订单的评价状态
  Future<bool> hasReviewed(String orderId) async {
    try {
      final response = await ApiService.get('/orders/$orderId/review-status');
      return response.data?['hasReviewed'] as bool? ?? false;
    } catch (e) {
      debugPrint('获取评价状态失败: $e');
      return false;
    }
  }

  /// 清除错误信息
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
