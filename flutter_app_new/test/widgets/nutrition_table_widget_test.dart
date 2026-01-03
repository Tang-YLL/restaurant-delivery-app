import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app_new/widgets/nutrition_table_widget.dart';

void main() {
  group('NutritionTableWidget Tests', () {
    testWidgets('应该渲染营养成分表标题', (WidgetTester tester) async {
      // Arrange
      final nutritionData = {
        'calories': 150,
        'protein': 8.5,
      };

      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NutritionTableWidget(
              nutritionData: nutritionData,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('营养成分表'), findsOneWidget);
    });

    testWidgets('应该渲染份量信息', (WidgetTester tester) async {
      // Arrange
      final nutritionData = {
        'serving_size': '1份(200g)',
        'calories': 150,
      };

      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NutritionTableWidget(
              nutritionData: nutritionData,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('份量: 1份(200g)'), findsOneWidget);
    });

    testWidgets('应该渲染表格头部', (WidgetTester tester) async {
      // Arrange
      final nutritionData = {
        'calories': 150,
      };

      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NutritionTableWidget(
              nutritionData: nutritionData,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('营养成分'), findsOneWidget);
      expect(find.text('含量'), findsOneWidget);
      expect(find.text('单位'), findsOneWidget);
    });

    testWidgets('应该渲染营养数据行', (WidgetTester tester) async {
      // Arrange
      final nutritionData = {
        'calories': 150,
        'protein': 8.5,
        'fat': 5.2,
      };

      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NutritionTableWidget(
              nutritionData: nutritionData,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('热量'), findsOneWidget);
      expect(find.text('150'), findsOneWidget);
      expect(find.text('kcal'), findsOneWidget);
      expect(find.text('蛋白质'), findsOneWidget);
    });

    testWidgets('应该处理缺失的营养数据', (WidgetTester tester) async {
      // Arrange
      final nutritionData = {
        'calories': 150,
        // protein缺失
      };

      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NutritionTableWidget(
              nutritionData: nutritionData,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('蛋白质'), findsOneWidget);
      expect(find.text('-'), findsWidgets); // 应该显示占位符
    });

    testWidgets('应该正确构建表格', (WidgetTester tester) async {
      // Arrange
      final nutritionData = {
        'calories': 150,
        'protein': 8.5,
        'fat': 5.2,
        'carbohydrates': 18.0,
        'sodium': 450,
      };

      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NutritionTableWidget(
              nutritionData: nutritionData,
            ),
          ),
        ),
      );

      // Assert - 验证所有营养素都被渲染
      expect(find.text('热量'), findsOneWidget);
      expect(find.text('蛋白质'), findsOneWidget);
      expect(find.text('脂肪'), findsOneWidget);
      expect(find.text('碳水化合物'), findsOneWidget);
      expect(find.text('钠'), findsOneWidget);
    });
  });
}
