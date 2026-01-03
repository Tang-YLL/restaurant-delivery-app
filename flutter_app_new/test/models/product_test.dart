import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app_new/data/models/product.dart';
import 'package:flutter_app_new/data/models/content_section.dart';

void main() {
  group('Product模型测试', () {
    test('应该正确从JSON创建Product（基础字段）', () {
      // Arrange
      final json = {
        'id': 1,
        'title': '测试商品',
        'description': '这是一个测试商品',
        'price': 29.99,
        'local_image_path': '/images/test.jpg',
        'category_id': 1,
        'sales_count': 100,
        'stock': 50,
      };

      // Act
      final product = Product.fromJson(json);

      // Assert
      expect(product.id, '1');
      expect(product.name, '测试商品');
      expect(product.description, '这是一个测试商品');
      expect(product.price, 29.99);
      expect(product.imageUrl, 'http://localhost:8000/images/test.jpg');
      expect(product.category, '1');
      expect(product.sales, 100);
      expect(product.stock, 50);
    });

    test('应该正确解析contentSections', () {
      // Arrange
      final json = {
        'id': 1,
        'title': '测试商品',
        'description': '描述',
        'price': 29.99,
        'local_image_path': '/images/test.jpg',
        'category_id': 1,
        'sales_count': 0,
        'stock': 0,
        'content_sections': [
          {
            'id': 1,
            'product_id': 1,
            'section_type': 'story',
            'title': '品牌故事',
            'content': '<p>故事内容</p>',
            'display_order': 1,
          },
          {
            'id': 2,
            'product_id': 1,
            'section_type': 'nutrition',
            'title': '营养信息',
            'content': '<p>营养内容</p>',
            'display_order': 2,
          },
        ],
      };

      // Act
      final product = Product.fromJson(json);

      // Assert
      expect(product.contentSections, isNotNull);
      expect(product.contentSections!.length, 2);
      expect(product.contentSections![0].sectionType, 'story');
      expect(product.contentSections![1].sectionType, 'nutrition');
    });

    test('应该正确解析nutritionFacts', () {
      // Arrange
      final json = {
        'id': 1,
        'title': '测试商品',
        'description': '描述',
        'price': 29.99,
        'local_image_path': '/images/test.jpg',
        'category_id': 1,
        'sales_count': 0,
        'stock': 0,
        'nutrition_facts': {
          'serving_size': '1份(200g)',
          'calories': 150,
          'protein': 8.5,
          'fat': 5.2,
          'carbohydrates': 18.0,
        },
      };

      // Act
      final product = Product.fromJson(json);

      // Assert
      expect(product.nutritionFacts, isNotNull);
      expect(product.nutritionFacts!['serving_size'], '1份(200g)');
      expect(product.nutritionFacts!['calories'], 150);
      expect(product.nutritionFacts!['protein'], 8.5);
    });

    test('应该正确处理缺失的可选字段', () {
      // Arrange
      final json = {
        'id': 1,
        'title': '测试商品',
        'description': '描述',
        'price': 29.99,
        'local_image_path': '/images/test.jpg',
        'category_id': 1,
        'sales_count': 0,
        'stock': 0,
        // content_sections 和 nutrition_facts 缺失
      };

      // Act
      final product = Product.fromJson(json);

      // Assert
      expect(product.contentSections, isNull);
      expect(product.nutritionFacts, isNull);
    });

    test('应该正确使用copyWith方法', () {
      // Arrange
      final product = Product(
        id: '1',
        name: '原始名称',
        description: '描述',
        price: 29.99,
        imageUrl: '/images/test.jpg',
        category: '1',
        rating: 4.5,
        sales: 100,
        stock: 50,
      );

      // Act
      final updated = product.copyWith(
        name: '更新名称',
        price: 39.99,
      );

      // Assert
      expect(updated.id, '1'); // 未改变
      expect(updated.name, '更新名称');
      expect(updated.price, 39.99);
      expect(updated.description, '描述'); // 未改变
    });

    test('应该正确计算库存状态', () {
      // Arrange
      final inStockProduct = Product(
        id: '1',
        name: '有货商品',
        description: '描述',
        price: 29.99,
        imageUrl: '/images/test.jpg',
        category: '1',
        rating: 4.5,
        sales: 100,
        stock: 10,
      );

      final outOfStockProduct = Product(
        id: '2',
        name: '无货商品',
        description: '描述',
        price: 29.99,
        imageUrl: '/images/test.jpg',
        category: '1',
        rating: 4.5,
        sales: 100,
        stock: 0,
      );

      // Assert
      expect(inStockProduct.inStock, isTrue);
      expect(outOfStockProduct.inStock, isFalse);
    });
  });
}
