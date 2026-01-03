import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app_new/data/models/content_section.dart';

void main() {
  group('ContentSection模型测试', () {
    test('应该正确从JSON创建ContentSection', () {
      // Arrange
      final json = {
        'id': 1,
        'product_id': 100,
        'section_type': 'story',
        'title': '品牌故事',
        'content': '<p>这是一个精彩的故事</p>',
        'display_order': 1,
        'created_at': '2024-01-01T00:00:00.000Z',
        'updated_at': '2024-01-01T01:00:00.000Z',
      };

      // Act
      final section = ContentSection.fromJson(json);

      // Assert
      expect(section.id, 1);
      expect(section.productId, 100);
      expect(section.sectionType, 'story');
      expect(section.title, '品牌故事');
      expect(section.content, '<p>这是一个精彩的故事</p>');
      expect(section.displayOrder, 1);
      expect(section.createdAt, isNotNull);
      expect(section.updatedAt, isNotNull);
    });

    test('应该正确处理可选字段', () {
      // Arrange
      final json = {
        'product_id': 100,
        'section_type': 'ingredients',
        'content': '<p>食材信息</p>',
        'display_order': 2,
        // id, title, created_at, updated_at 缺失
      };

      // Act
      final section = ContentSection.fromJson(json);

      // Assert
      expect(section.id, isNull);
      expect(section.title, isNull);
      expect(section.createdAt, isNull);
      expect(section.updatedAt, isNull);
      expect(section.displayOrder, 2); // 使用默认值
    });

    test('应该正确序列化为JSON', () {
      // Arrange
      final section = ContentSection(
        id: 1,
        productId: 100,
        sectionType: 'story',
        title: '品牌故事',
        content: '<p>内容</p>',
        displayOrder: 1,
      );

      // Act
      final json = section.toJson();

      // Assert
      expect(json['id'], 1);
      expect(json['product_id'], 100);
      expect(json['section_type'], 'story');
      expect(json['title'], '品牌故事');
      expect(json['content'], '<p>内容</p>');
      expect(json['display_order'], 1);
    });

    test('应该正确解析不同类型的section_type', () {
      // Arrange & Act
      final types = ['story', 'nutrition', 'ingredients', 'process', 'tips'];

      for (final type in types) {
        final json = {
          'product_id': 100,
          'section_type': type,
          'content': '<p>测试</p>',
          'display_order': 1,
        };

        final section = ContentSection.fromJson(json);

        // Assert
        expect(section.sectionType, type);
      }
    });

    test('应该正确处理HTML内容', () {
      // Arrange
      final htmlContent = '''
        <h2>标题</h2>
        <p>段落内容</p>
        <ul>
          <li>列表项1</li>
          <li>列表项2</li>
        </ul>
      ''';

      final json = {
        'product_id': 100,
        'section_type': 'story',
        'content': htmlContent,
        'display_order': 1,
      };

      // Act
      final section = ContentSection.fromJson(json);

      // Assert
      expect(section.content, htmlContent);
      expect(section.content.contains('<h2>'), isTrue);
      expect(section.content.contains('<p>'), isTrue);
      expect(section.content.contains('<ul>'), isTrue);
    });
  });
}
