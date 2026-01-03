import 'package:flutter_driver/driver_extension.dart';
import 'package:integration_test/integration_test_driver.dart';

Future<void> main() async {
  // 启用Flutter Driver扩展
  enableFlutterDriverExtension();

  // 运行集成测试
  await integrationDriver();
}
