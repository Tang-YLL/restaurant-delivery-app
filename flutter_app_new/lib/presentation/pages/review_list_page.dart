import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/review_provider.dart';
import '../../data/models/review.dart';
import '../widgets/loading_widgets.dart';
import '../widgets/empty_state_widget.dart';

/// 商品评价列表页面
class ProductReviewsPage extends StatefulWidget {
  final String productId;
  final String productName;

  const ProductReviewsPage({
    super.key,
    required this.productId,
    required this.productName,
  });

  @override
  State<ProductReviewsPage> createState() => _ProductReviewsPageState();
}

class _ProductReviewsPageState extends State<ProductReviewsPage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<ReviewProvider>().loadReviews(widget.productId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.productName}的评价'),
      ),
      body: Consumer<ReviewProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.reviews.isEmpty) {
            return ListView.builder(
              itemCount: 5,
              itemBuilder: (context, index) => const ReviewSkeleton(),
            );
          }

          if (provider.reviews.isEmpty) {
            return RefreshIndicator(
              onRefresh: () => provider.loadReviews(widget.productId),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: EmptyStates.reviews(),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => provider.loadReviews(widget.productId),
            child: CustomScrollView(
              slivers: [
                // 统计信息
                if (provider.statistics != null)
                  SliverToBoxAdapter(
                    child: _buildStatistics(provider.statistics!),
                  ),

                // 评价列表
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final review = provider.reviews[index];
                      return _buildReviewCard(review);
                    },
                    childCount: provider.reviews.length,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildStatistics(ReviewStatistics statistics) {
    return Container(
      padding: const EdgeInsets.all(20),
      color: Theme.of(context).colorScheme.surface,
      child: Row(
        children: [
          // 左侧:平均分
          Column(
            children: [
              Text(
                statistics.averageRating.toStringAsFixed(1),
                style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                '${statistics.totalCount}条评价',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey,
                    ),
              ),
            ],
          ),

          const SizedBox(width: 32),

          // 右侧:评分分布
          Expanded(
            child: Column(
              children: [5, 4, 3, 2, 1].map((stars) {
                final count = statistics.ratingDistribution[stars] ?? 0;
                final percentage = statistics.getRatingPercentage(stars);

                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    children: [
                      Text('$stars'),
                      const SizedBox(width: 8),
                      Icon(Icons.star, size: 16, color: Colors.amber),
                      const SizedBox(width: 8),
                      Expanded(
                        child: LinearProgressIndicator(
                          value: percentage,
                          backgroundColor: Colors.grey[300],
                          valueColor: AlwaysStoppedAnimation<Color>(
                            stars >= 4 ? Colors.amber : Colors.grey,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        count.toString(),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReviewCard(Review review) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 用户信息
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundImage:
                      review.userAvatar != null ? NetworkImage(review.userAvatar!) : null,
                  child: review.userAvatar == null ? Text(review.userName[0]) : null,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        review.userName,
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      Text(
                        _formatDate(review.createdAt),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey,
                            ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // 星级评分
            Row(
              children: List.generate(5, (index) {
                return Icon(
                  index < review.rating ? Icons.star : Icons.star_border,
                  color: Colors.amber,
                  size: 18,
                );
              }),
            ),

            const SizedBox(height: 12),

            // 评价内容
            if (review.content.isNotEmpty)
              Text(
                review.content,
                style: Theme.of(context).textTheme.bodyMedium,
              ),

            // 评价图片
            if (review.images.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: review.images.map((imageUrl) {
                  return ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      imageUrl,
                      width: 100,
                      height: 100,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          width: 100,
                          height: 100,
                          color: Colors.grey[300],
                          child: const Icon(Icons.broken_image),
                        );
                      },
                    ),
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays > 30) {
      return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    } else if (difference.inDays > 0) {
      return '${difference.inDays}天前';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '刚刚';
    }
  }
}
