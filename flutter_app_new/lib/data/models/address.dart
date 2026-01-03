import 'package:hive/hive.dart';
import 'package:json_annotation/json_annotation.dart';

part 'address.g.dart';

/// 地址模型
@HiveType(typeId: 8)
class Address {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String userId;

  @HiveField(2)
  final String contactName; // 联系人姓名

  @HiveField(3)
  final String contactPhone; // 联系电话

  @HiveField(4)
  final String province; // 省

  @HiveField(5)
  final String city; // 市

  @HiveField(6)
  final String district; // 区

  @HiveField(7)
  final String detailAddress; // 详细地址

  @HiveField(8)
  final bool isDefault; // 是否默认地址

  @HiveField(9)
  final String addressType; // 地址类型: home, company, other

  @HiveField(10)
  final DateTime createdAt;

  @HiveField(11)
  final DateTime? updatedAt;

  Address({
    required this.id,
    required this.userId,
    required this.contactName,
    required this.contactPhone,
    required this.province,
    required this.city,
    required this.district,
    required this.detailAddress,
    this.isDefault = false,
    this.addressType = 'other',
    required this.createdAt,
    this.updatedAt,
  });

  /// 获取完整地址字符串
  String get fullAddress {
    return '$province$city$district${detailAddress}';
  }

  /// 获取地址类型标签
  String get addressTypeLabel {
    switch (addressType) {
      case 'home':
        return '家';
      case 'company':
        return '公司';
      case 'other':
      default:
        return '其他';
    }
  }

  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      id: json['id'] as String,
      userId: json['userId'] as String,
      contactName: json['contactName'] as String,
      contactPhone: json['contactPhone'] as String,
      province: json['province'] as String,
      city: json['city'] as String,
      district: json['district'] as String,
      detailAddress: json['detailAddress'] as String,
      isDefault: json['isDefault'] as bool? ?? false,
      addressType: json['addressType'] as String? ?? 'other',
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'contactName': contactName,
      'contactPhone': contactPhone,
      'province': province,
      'city': city,
      'district': district,
      'detailAddress': detailAddress,
      'isDefault': isDefault,
      'addressType': addressType,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }

  Address copyWith({
    String? id,
    String? userId,
    String? contactName,
    String? contactPhone,
    String? province,
    String? city,
    String? district,
    String? detailAddress,
    bool? isDefault,
    String? addressType,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Address(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      contactName: contactName ?? this.contactName,
      contactPhone: contactPhone ?? this.contactPhone,
      province: province ?? this.province,
      city: city ?? this.city,
      district: district ?? this.district,
      detailAddress: detailAddress ?? this.detailAddress,
      isDefault: isDefault ?? this.isDefault,
      addressType: addressType ?? this.addressType,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
