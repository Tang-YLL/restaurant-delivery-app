import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/product_provider.dart';
import '../widgets/product_card.dart';

/// 分类页面
class CategoryPage extends StatefulWidget {
  const CategoryPage({super.key});

  @override
  State<CategoryPage> createState() => _CategoryPageState();
}

class _CategoryPageState extends State<CategoryPage> {
  String? _selectedCategoryId;

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<ProductProvider>().loadCategories();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('商品分类'),
      ),
      body: Consumer<ProductProvider>(
        builder: (context, provider, _) {
          return Row(
            children: [
              // 左侧分类列表
              SizedBox(
                width: 100,
                child: ListView.builder(
                  itemCount: provider.categories.length + 1,
                  itemBuilder: (context, index) {
                    if (index == 0) {
                      // 全部分类
                      return _buildCategoryItem(
                        context,
                        null,
                        '全部',
                        _selectedCategoryId == null,
                      );
                    }
                    final category = provider.categories[index - 1];
                    return _buildCategoryItem(
                      context,
                      category.id,
                      category.name ?? '',
                      _selectedCategoryId == category.id,
                      icon: category.icon,
                    );
                  },
                ),
              ),
              // 右侧商品列表
              Expanded(
                child: provider.isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : provider.products.isEmpty
                        ? const Center(child: Text('暂无商品'))
                        : GridView.builder(
                            padding: const EdgeInsets.all(12),
                            gridDelegate:
                                const SliverGridDelegateWithFixedCrossAxisCount(
                              crossAxisCount: 1,
                              childAspectRatio: 1.8,
                              mainAxisSpacing: 12,
                            ),
                            itemCount: provider.products.length,
                            itemBuilder: (context, index) {
                              final product = provider.products[index];
                              return ProductCard(product: product);
                            },
                          ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildCategoryItem(
    BuildContext context,
    String? categoryId,
    String label,
    bool isSelected, {
    String? icon,
  }) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedCategoryId = categoryId;
        });
        context.read<ProductProvider>().filterByCategory(categoryId);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.orange.withOpacity(0.1) : Colors.white,
          border: Border(
            left: BorderSide(
              color: isSelected ? Colors.orange : Colors.transparent,
              width: 3,
            ),
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (icon != null)
              Text(
                icon,
                style: const TextStyle(fontSize: 24),
              )
            else
              Icon(
                Icons.apps,
                color: isSelected ? Colors.orange : Colors.grey,
              ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: isSelected ? Colors.orange : Colors.grey[700],
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
