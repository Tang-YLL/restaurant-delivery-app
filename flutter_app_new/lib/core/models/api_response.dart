/// API响应基础模型
class ApiResponse<T> {
  final int code;
  final String message;
  final T? data;
  final bool success;

  ApiResponse({
    required this.code,
    required this.message,
    this.data,
    required this.success,
  });

  factory ApiResponse.success(T data, {String message = 'Success'}) {
    return ApiResponse(
      code: 200,
      message: message,
      data: data,
      success: true,
    );
  }

  factory ApiResponse.error(int code, String message) {
    return ApiResponse(
      code: code,
      message: message,
      success: false,
    );
  }

  factory ApiResponse.fromJson(Map<String, dynamic> json, T Function(dynamic)? dataParser) {
    return ApiResponse(
      code: json['code'] as int,
      message: json['message'] as String,
      data: dataParser != null && json['data'] != null ? dataParser(json['data']) : json['data'],
      success: json['success'] as bool? ?? json['code'] == 200,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'code': code,
      'message': message,
      'data': data,
      'success': success,
    };
  }
}

/// API异常
class ApiException implements Exception {
  final int code;
  final String message;
  final dynamic data;

  ApiException(this.code, this.message, {this.data});

  @override
  String toString() => 'ApiException: $code - $message';
}

/// 网络异常
class NetworkException implements Exception {
  final String message;

  NetworkException(this.message);

  @override
  String toString() => 'NetworkException: $message';
}
