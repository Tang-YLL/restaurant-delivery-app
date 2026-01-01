import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String? username;  // 改为可选
  final String? email;     // 改为可选
  final String? phone;
  final String? avatar;
  final String? nickname;
  final DateTime? createdAt;

  User({
    required this.id,
    this.username,
    this.email,
    this.phone,
    this.avatar,
    this.nickname,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    // 处理id可能是int的情况
    final idValue = json['id'];
    String idStr;
    if (idValue is int) {
      idStr = idValue.toString();
    } else {
      idStr = idValue as String;
    }

    return User(
      id: idStr,
      username: json['username']?.toString(),
      email: json['email']?.toString(),
      phone: json['phone']?.toString(),
      avatar: json['avatar']?.toString(),
      nickname: json['nickname']?.toString(),
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() => _$UserToJson(this);

  User copyWith({
    String? id,
    String? username,
    String? email,
    String? phone,
    String? avatar,
    String? nickname,
    DateTime? createdAt,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      avatar: avatar ?? this.avatar,
      nickname: nickname ?? this.nickname,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
