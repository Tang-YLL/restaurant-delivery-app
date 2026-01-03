import 'package:hive/hive.dart';
import 'package:json_annotation/json_annotation.dart';

part 'review.g.dart';

/// 评价模型
@HiveType(typeId: 7)
class Review {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String orderId;

  @HiveField(2)
  final String productId;

  @HiveField(3)
  final String productName;

  @HiveField(4)
  final String? productImage;

  @HiveField(5)
  final int rating; // 1-5星

  @HiveField(6)
  final String content;

  @HiveField(7)
  final List<String> images; // 图片URL列表

  @HiveField(8)
  final String userId;

  @HiveField(9)
  final String userName;

  @HiveField(10)
  final String? userAvatar;

  @HiveField(11)
  final DateTime createdAt;

  Review({
    required this.id,
    required this.orderId,
    required this.productId,
    required this.productName,
    this.productImage,
    required this.rating,
    required this.content,
    required this.images,
    required this.userId,
    required this.userName,
    this.userAvatar,
    required this.createdAt,
  });

  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      id: json['id'] as String,
      orderId: json['orderId'] as String,
      productId: json['productId'] as String,
      productName: json['productName'] as String,
      productImage: json['productImage'] as String?,
      rating: json['rating'] as int,
      content: json['content'] as String,
      images: (json['images'] as List?)?.cast<String>() ?? [],
      userId: json['userId'] as String,
      userName: json['userName'] as String,
      userAvatar: json['userAvatar'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'orderId': orderId,
      'productId': productId,
      'productName': productName,
      'productImage': productImage,
      'rating': rating,
      'content': content,
      'images': images,
      'userId': userId,
      'userName': userName,
      'userAvatar': userAvatar,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  Review copyWith({
    String? id,
    String? orderId,
    String? productId,
    String? productName,
    String? productImage,
    int? rating,
    String? content,
    List<String>? images,
    String? userId,
    String? userName,
    String? userAvatar,
    DateTime? createdAt,
  }) {
    return Review(
      id: id ?? this.id,
      orderId: orderId ?? this.orderId,
      productId: productId ?? this.productId,
      productName: productName ?? this.productName,
      productImage: productImage ?? this.productImage,
      rating: rating ?? this.rating,
      content: content ?? this.content,
      images: images ?? this.images,
      userId: userId ?? this.userId,
      userName: userName ?? this.userName,
      userAvatar: userAvatar ?? this.userAvatar,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

/// 商品评价统计
class ReviewStatistics {
  final double averageRating; // 平均评分
  final int totalCount; // 总评价数
  final Map<int, int> ratingDistribution; // 各星级数量分布 {5: 100, 4: 50, ...}

  ReviewStatistics({
    required this.averageRating,
    required this.totalCount,
    required this.ratingDistribution,
  });

  factory ReviewStatistics.fromJson(Map<String, dynamic> json) {
    return ReviewStatistics(
      averageRating: (json['averageRating'] as num).toDouble(),
      totalCount: json['totalCount'] as int,
      ratingDistribution: Map<int, int>.from(
        (json['ratingDistribution'] as Map<String, dynamic>).map(
          (key, value) => MapEntry(int.parse(key), value as int),
        ),
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'averageRating': averageRating,
      'totalCount': totalCount,
      'ratingDistribution': ratingDistribution.map(
        (key, value) => MapEntry(key.toString(), value),
      ),
    };
  }

  /// 获取某星级的百分比
  double getRatingPercentage(int stars) {
    if (totalCount == 0) return 0.0;
    final count = ratingDistribution[stars] ?? 0;
    return count / totalCount;
  }
}
