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
  // 搜索框文本控制器
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocusNode = FocusNode();

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocusNode.dispose();
    super.dispose();
  }

  // 清除搜索
  void _clearSearch(ProductProvider provider) {
    _searchController.clear();
    _searchFocusNode.unfocus();  // 收起键盘
    provider.clearFilters();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('美食外卖'),
      ),
      body: Consumer<ProductProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading && provider.products.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          return Column(
            children: [
              // 搜索栏
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: TextField(
                  controller: _searchController,
                  focusNode: _searchFocusNode,
                  decoration: InputDecoration(
                    hintText: '搜索美食...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: provider.isSearching
                        ? const Padding(
                            padding: EdgeInsets.all(12.0),
                            child: SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                              ),
                            ),
                          )
                        : _searchController.text.isNotEmpty
                            ? IconButton(
                                icon: const Icon(Icons.clear),
                                onPressed: () => _clearSearch(provider),
                              )
                            : null,
                  ),
                  onChanged: (value) {
                    provider.searchProducts(value);
                  },
                  onSubmitted: (value) {
                    // 提交时收起键盘
                    _searchFocusNode.unfocus();
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
                            // 点击"全部"时清空搜索框
                            _searchController.clear();
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
