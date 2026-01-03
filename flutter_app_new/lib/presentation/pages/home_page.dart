import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/product_provider.dart';
import '../providers/cart_provider.dart';
import '../widgets/product_card.dart';
import '../widgets/category_chip.dart';

/// 主页
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('美食外卖'),
      ),
      body: Consumer<ProductProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          return Column(
            children: [
              // 搜索栏
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: TextField(
                  decoration: InputDecoration(
                    hintText: '搜索美食...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: provider.searchQuery != null
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              provider.clearFilters();
                            },
                          )
                        : null,
                  ),
                  onChanged: (value) {
                    provider.searchProducts(value);
                  },
                ),
              ),

              // 分类筛选 - 横向滚动
              SizedBox(
                height: 50,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: provider.categories.length + 1,
                  itemBuilder: (context, index) {
                    return Padding(
                      padding: const EdgeInsets.only(right: 12),
                      child: CategoryChip(
                        name: index == 0 ? '全部' : provider.categories[index - 1].name ?? '',
                        icon: index == 0 ? null : provider.categories[index - 1].icon,
                        isSelected: index == 0
                            ? provider.selectedCategoryId == null
                            : provider.selectedCategoryId == provider.categories[index - 1].id,
                        onTap: () {
                          if (index == 0) {
                            provider.clearFilters();
                          } else {
                            provider.filterByCategory(provider.categories[index - 1].id);
                          }
                        },
                      ),
                    );
                  },
                ),
              ),

              const Divider(height: 1),

              // 商品列表
              Expanded(
                child: provider.products.isEmpty
                    ? const Center(child: Text('暂无商品'))
                    : RefreshIndicator(
                        onRefresh: () => provider.loadProducts(
                          categoryId: provider.selectedCategoryId,
                          search: provider.searchQuery,
                        ),
                        child: GridView.builder(
                          padding: const EdgeInsets.all(16),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            childAspectRatio: 0.75,
                            crossAxisSpacing: 16,
                            mainAxisSpacing: 16,
                          ),
                          itemCount: provider.products.length,
                          itemBuilder: (context, index) {
                            final product = provider.products[index];
                            return ProductCard(product: product);
                          },
                        ),
                      ),
              ),
            ],
          );
        },
      ),
    );
  }
}
