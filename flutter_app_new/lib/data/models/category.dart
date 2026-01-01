import 'package:json_annotation/json_annotation.dart';

part 'category.g.dart';

@JsonSerializable()
class Category {
  final String id;
  final String name;
  final String? icon;
  final int? count;

  Category({
    required this.id,
    required this.name,
    this.icon,
    this.count,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    // 处理id可能是int的情况
    final idValue = json['id'];
    String idStr;
    if (idValue is int) {
      idStr = idValue.toString();
    } else {
      idStr = idValue as String;
    }

    return Category(
      id: idStr,
      name: json['name'] as String,
      icon: json['icon']?.toString(),
      count: json['count'] as int?,
    );
  }

  Map<String, dynamic> toJson() => _$CategoryToJson(this);

  Category copyWith({
    String? id,
    String? name,
    String? icon,
    int? count,
  }) {
    return Category(
      id: id ?? this.id,
      name: name ?? this.name,
      icon: icon ?? this.icon,
      count: count ?? this.count,
    );
  }
}
