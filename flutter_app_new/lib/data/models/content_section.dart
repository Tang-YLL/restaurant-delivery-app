class ContentSection {
  final int? id;
  final int productId;
  final String sectionType; // story, nutrition, ingredients, process, tips
  final String? title;
  final String content; // HTML content
  final int displayOrder;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  ContentSection({
    this.id,
    required this.productId,
    required this.sectionType,
    this.title,
    required this.content,
    required this.displayOrder,
    this.createdAt,
    this.updatedAt,
  });

  factory ContentSection.fromJson(Map<String, dynamic> json) {
    return ContentSection(
      id: json['id'] as int?,
      productId: json['product_id'] as int,
      sectionType: json['section_type'] as String,
      title: json['title'] as String?,
      content: json['content'] as String,
      displayOrder: json['display_order'] as int? ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_id': productId,
      'section_type': sectionType,
      'title': title,
      'content': content,
      'display_order': displayOrder,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
}
