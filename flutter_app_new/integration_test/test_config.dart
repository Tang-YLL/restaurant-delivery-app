/// 集成测试配置
class TestConfig {
  /// 后端API基础URL
  static const String baseUrl = 'http://localhost:8001/api';

  /// 测试用手机号
  static const List<String> testPhones = [
    '13900139000',
    '13900139001',
    '13900139002',
  ];

  /// 测试用验证码（后端测试环境固定验证码）
  static const String testVerificationCode = '1234';

  /// 测试超时时间
  static const Duration defaultTimeout = Duration(seconds: 10);

  /// 页面加载等待时间
  static const Duration pageLoadTimeout = Duration(seconds: 3);

  /// API响应等待时间
  static const Duration apiWaitTimeout = Duration(seconds: 2);

  /// 动画等待时间
  static const Duration animationTimeout = Duration(milliseconds: 500);
}
