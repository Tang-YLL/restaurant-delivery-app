import 'package:json_annotation/json_annotation.dart';
import 'content_section.dart';

part 'product.g.dart';

@JsonSerializable()
class Product {
  final String id;
  final String name;
  final String description;
  final double price;
  final double? originalPrice;
  final String imageUrl;
  final String category;
  final double rating;
  final int sales;
  final int stock;
  final List<String>? tags;

  // 新增字段 - 商品详情内容
  final List<ContentSection>? contentSections;
  final Map<String, dynamic>? nutritionFacts;

  Product({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    this.originalPrice,
    required this.imageUrl,
    required this.category,
    required this.rating,
    required this.sales,
    required this.stock,
    this.tags,
    this.contentSections,
    this.nutritionFacts,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    // 处理id可能是int的情况
    final idValue = json['id'];
    String idStr;
    if (idValue is int) {
      idStr = idValue.toString();
    } else {
      idStr = idValue as String;
    }

    // 处理图片URL - 修复端口号和缺失的host
    String imageUrl = json['local_image_path'] as String? ??
                     json['image_url'] as String? ??
                     json['imageUrl'] as String? ?? '';

    // 处理相对路径 - 添加localhost前缀
    if (imageUrl.startsWith('/images/')) {
      imageUrl = 'http://localhost:8000$imageUrl';
    }
    // 将8001端口替换为8000
    else if (imageUrl.contains('localhost:8001')) {
      imageUrl = imageUrl.replaceAll('localhost:8001', 'localhost:8000');
    }

    // 后端字段映射到前端模型
    return Product(
      id: idStr,
      name: json['title'] as String? ?? '', // 后端使用title
      description: json['description'] as String? ?? '',
      price: (json['price'] is num
          ? (json['price'] as num).toDouble()
          : double.tryParse(json['price'].toString())) ?? 0.0,
      originalPrice: null, // 后端没有original_price字段
      imageUrl: imageUrl,
      category: json['category_id']?.toString() ?? '', // 后端使用category_id
      rating: 0.0, // 后端没有rating字段，默认0
      sales: json['sales_count'] as int? ?? 0, // 后端使用sales_count
      stock: json['stock'] as int? ?? 0,
      tags: null, // 后端没有tags字段
      // 解析contentSections
      contentSections: json['content_sections'] != null
          ? (json['content_sections'] as List)
              .map((e) => ContentSection.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
      // 解析nutritionFacts
      nutritionFacts: json['nutrition_facts'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => _$ProductToJson(this);

  // 计算折扣
  double? get discount {
    if (originalPrice != null && originalPrice! > price) {
      return ((originalPrice! - price) / originalPrice! * 100);
    }
    return null;
  }

  // 是否有货
  bool get inStock => stock > 0;

  Product copyWith({
    String? id,
    String? name,
    String? description,
    double? price,
    double? originalPrice,
    String? imageUrl,
    String? category,
    double? rating,
    int? sales,
    int? stock,
    List<String>? tags,
    List<ContentSection>? contentSections,
    Map<String, dynamic>? nutritionFacts,
  }) {
    return Product(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      price: price ?? this.price,
      originalPrice: originalPrice ?? this.originalPrice,
      imageUrl: imageUrl ?? this.imageUrl,
      category: category ?? this.category,
      rating: rating ?? this.rating,
      sales: sales ?? this.sales,
      stock: stock ?? this.stock,
      tags: tags ?? this.tags,
      contentSections: contentSections ?? this.contentSections,
      nutritionFacts: nutritionFacts ?? this.nutritionFacts,
    );
  }
}
