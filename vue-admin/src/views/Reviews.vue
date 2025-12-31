<template>
  <div class="reviews">
    <el-card>
      <template #header>
        <span>评价管理</span>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="queryForm.keyword" placeholder="商品名称/用户名" clearable />
        </el-form-item>

        <el-form-item label="审核状态">
          <el-select v-model="queryForm.status" placeholder="请选择状态" clearable>
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>

        <el-form-item label="评分">
          <el-select v-model="queryForm.rating" placeholder="请选择评分" clearable>
            <el-option label="5星" :value="5" />
            <el-option label="4星" :value="4" />
            <el-option label="3星" :value="3" />
            <el-option label="2星" :value="2" />
            <el-option label="1星" :value="1" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadReviews">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 评价列表 -->
      <el-table :data="reviewList" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="productName" label="商品名称" min-width="150" />
        <el-table-column prop="userName" label="用户" width="120" />
        <el-table-column prop="rating" label="评分" width="150">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled show-score />
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评价内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="评价时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button
              type="success"
              link
              @click="handleApprove(row.id)"
              v-if="row.status === 'pending'"
            >
              通过
            </el-button>
            <el-button
              type="warning"
              link
              @click="handleReject(row.id)"
              v-if="row.status === 'pending'"
            >
              拒绝
            </el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryForm.page"
          v-model:page-size="queryForm.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadReviews"
          @current-change="loadReviews"
        />
      </div>
    </el-card>

    <!-- 评价详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="评价详情" width="600px">
      <div class="review-detail">
        <div class="review-header">
          <el-avatar :src="currentReview.userAvatar" :size="50">
            {{ currentReview.userName?.charAt(0) }}
          </el-avatar>
          <div class="user-info">
            <div class="username">{{ currentReview.userName }}</div>
            <div class="product-name">商品: {{ currentReview.productName }}</div>
          </div>
          <el-rate v-model="currentReview.rating" disabled class="rating" />
        </div>

        <div class="review-content">
          {{ currentReview.content }}
        </div>

        <div class="review-images" v-if="currentReview.images && currentReview.images.length > 0">
          <el-image
            v-for="(img, index) in currentReview.images"
            :key="index"
            :src="img"
            :preview-src-list="currentReview.images"
            fit="cover"
            style="width: 100px; height: 100px; margin-right: 10px"
          />
        </div>

        <div class="review-footer">
          <el-tag :type="getStatusType(currentReview.status)">
            {{ getStatusText(currentReview.status) }}
          </el-tag>
          <span class="time">{{ currentReview.createdAt }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft } from '@element-plus/icons-vue'
import { getReviewList, approveReview, rejectReview, deleteReview } from '../api/review'
import type { Review, ReviewQuery } from '../types'

const loading = ref(false)
const reviewList = ref<Review[]>([])
const total = ref(0)
const detailDialogVisible = ref(false)
const currentReview = ref<Review>({
  id: 0,
  productId: 0,
  productName: '',
  userId: 0,
  userName: '',
  userAvatar: '',
  rating: 5,
  content: '',
  status: 'pending',
  createdAt: ''
})

const queryForm = reactive<ReviewQuery>({
  page: 1,
  pageSize: 10,
  keyword: '',
  status: undefined as any,
  rating: undefined as any
})

const loadReviews = async () => {
  loading.value = true
  try {
    const data = await getReviewList(queryForm)
    reviewList.value = data.list
    total.value = data.total
  } catch (error) {
    console.error('Failed to load reviews:', error)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  queryForm.keyword = ''
  queryForm.status = undefined
  queryForm.rating = undefined
  queryForm.page = 1
  loadReviews()
}

const handleView = (review: Review) => {
  currentReview.value = review
  detailDialogVisible.value = true
}

const handleApprove = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要通过这条评价吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })

    await approveReview(id)
    ElMessage.success('审核通过')
    loadReviews()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleReject = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要拒绝这条评价吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await rejectReview(id)
    ElMessage.success('已拒绝')
    loadReviews()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评价吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteReview(id)
    ElMessage.success('删除成功')
    loadReviews()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return textMap[status] || status
}

onMounted(() => {
  loadReviews()
})
</script>

<style scoped>
.reviews {
  height: 100%;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.review-detail {
  padding: 10px;
}

.review-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.user-info {
  flex: 1;
  margin-left: 15px;
}

.username {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 5px;
}

.product-name {
  color: #909399;
  font-size: 14px;
}

.rating {
  margin-left: auto;
}

.review-content {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 15px;
  color: #606266;
}

.review-images {
  display: flex;
  margin-bottom: 15px;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #EBEEF5;
}

.time {
  color: #909399;
  font-size: 14px;
}
</style>
