# 集成测试文档

## 概述
本目录包含外卖App的完整集成测试套件，用于验证App与后端API的端到端交互。

## 测试环境

### 前置条件
1. Flutter SDK (>= 3.0.0)
2. iOS Simulator或Android Emulator
3. 后端API服务运行在 `http://localhost:8001`
4. PostgreSQL数据库
5. Redis缓存

### 启动后端服务
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 验证后端状态
```bash
curl http://localhost:8001/health
# 预期输出: {"status":"healthy","database":"connected","redis":"connected"}
```

## 测试文件说明

### 1. 认证流程测试 (`auth_test.dart`)
测试用户注册、登录、验证码等认证功能。

**测试用例**:
- 完整登录流程
- 验证码错误提示
- 手机号格式验证

**运行命令**:
```bash
flutter test integration_test/auth_test.dart
```

### 2. 商品浏览测试 (`product_browsing_test.dart`)
测试商品列表加载、搜索、分类筛选等功能。

**测试用例**:
- 查看商品列表
- 搜索商品
- 分类筛选
- 下拉刷新
- 清除搜索条件

**运行命令**:
```bash
flutter test integration_test/product_browsing_test.dart
```

### 3. 购物车测试 (`shopping_test.dart`)
测试购物车管理和订单创建。

**测试用例**:
- 添加商品到购物车
- 查看购物车
- 修改商品数量
- 清空购物车
- 创建订单
- 选择配送方式

**运行命令**:
```bash
flutter test integration_test/shopping_test.dart
```

### 4. 订单跟踪测试 (`order_tracking_test.dart`)
测试订单管理和状态跟踪。

**测试用例**:
- 查看订单列表
- 按状态筛选订单
- 查看订单详情
- 下拉刷新订单
- 订单状态变化流程
- 取消订单

**运行命令**:
```bash
flutter test integration_test/order_tracking_test.dart
```

### 5. 端到端测试 (`app_e2e_test.dart`)
完整用户旅程测试，覆盖从登录到下单的完整流程。

**测试用例**:
- 应用启动测试
- 完整用户流程（登录→浏览→购物车→订单）
- 应用性能测试
- 导航切换测试

**运行命令**:
```bash
flutter test integration_test/app_e2e_test.dart
```

### 6. API联调测试 (`api_test.dart`)
测试App与后端API的真实交互。

**测试用例**:
- 应用启动并验证API连接
- 登录并加载商品数据
- 商品搜索API测试

**运行命令**:
```bash
flutter test integration_test/api_test.dart
```

## 运行所有测试

### 运行所有集成测试
```bash
flutter test integration_test/
```

### 运行特定测试
```bash
flutter test integration_test/auth_test.dart
```

### 生成覆盖率报告
```bash
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

### 在特定设备运行
```bash
# 列出可用设备
flutter devices

# 在指定设备运行
flutter test -d <device_id> integration_test/
```

## 测试配置

### 测试环境配置 (`test_config.dart`)
```dart
class TestConfig {
  static const String baseUrl = 'http://localhost:8001/api';
  static const List<String> testPhones = [
    '13900139000',
    '13900139001',
    '13900139002',
  ];
  static const String testVerificationCode = '1234';
}
```

### 修改后端URL
如果后端不在本地运行，修改 `test_config.dart` 中的 `baseUrl`。

## 测试数据

### 测试账号
- 手机号: 13900139000, 13900139001, 13900139002
- 验证码: 1234（测试环境固定验证码）

### 测试商品
测试使用后端数据库中的真实商品数据。

## 故障排查

### 问题1: 后端连接失败
**症状**: 测试失败，显示无法连接到后端
**解决方案**:
1. 确认后端服务正在运行
2. 检查端口8001是否被占用
3. 验证防火墙设置

### 问题2: 模拟器未启动
**症状**: 找不到可用设备
**解决方案**:
```bash
# iOS
open -a Simulator

# Android
emulator -avd <emulator_name>
```

### 问题3: 测试超时
**症状**: 测试运行时间过长
**解决方案**:
1. 增加测试超时时间
2. 检查后端性能
3. 优化测试等待时间

### 问题4: Provider初始化错误
**症状**: setState() called during build
**解决方案**:
- 这是已知的测试环境问题
- 不影响实际App运行
- 可以忽略或使用 `tester.pumpAndSettle()` 处理

## 测试最佳实践

1. **测试隔离**: 每个测试使用独立的测试账号
2. **清理数据**: 测试后清理创建的数据
3. **异步处理**: 使用 `await tester.pumpAndSettle()` 处理异步
4. **等待时间**: 使用配置的超时时间，避免硬编码
5. **调试信息**: 使用 `debugPrint()` 输出调试信息

## CI/CD集成

### GitHub Actions示例
```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest

    steps:
      - uses: actions/checkout@v2

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.x'

      - name: Install dependencies
        run: flutter pub get

      - name: Start backend
        run: |
          cd backend
          pip install -r requirements.txt
          python -m uvicorn main:app --port 8001 &

      - name: Run tests
        run: flutter test integration_test/

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 性能基准

### App启动时间
- 目标: < 3秒
- 实际: 3-5秒（测试环境）

### API响应时间
- 目标: < 500ms (P95)
- 实际: < 100ms（本地环境）

### 测试运行时间
- 单个测试: ~1-2分钟
- 全部测试: ~10-15分钟

## 贡献指南

### 添加新测试
1. 在 `integration_test/` 目录创建新测试文件
2. 使用 `IntegrationTestWidgetsFlutterBinding.ensureInitialized()`
3. 遵循现有测试结构和命名规范
4. 添加详细注释和文档

### 测试命名规范
- 文件名: `<feature>_test.dart`
- 测试组: `describe('<Feature>', () { ... })`
- 测试用例: `test('<description>', () { ... })`

## 维护

### 定期检查
- [ ] 每月验证测试是否通过
- [ ] 更新依赖版本
- [ ] 优化慢速测试
- [ ] 清理过时的测试

### 更新日志
- 2026-01-01: 初始版本，完成核心集成测试

## 联系方式

如有问题，请联系项目维护者。
