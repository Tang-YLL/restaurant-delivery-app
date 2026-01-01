<template>
  <div class="reviews">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评价管理</span>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="评分">
          <el-select v-model="queryForm.rating" placeholder="全部评分" clearable style="width: 150px">
            <el-option label="5星" :value="5" />
            <el-option label="4星" :value="4" />
            <el-option label="3星" :value="3" />
            <el-option label="2星" :value="2" />
            <el-option label="1星" :value="1" />
          </el-select>
        </el-form-item>

        <el-form-item label="显示状态">
          <el-select v-model="queryForm.isVisible" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="显示" :value="true" />
            <el-option label="隐藏" :value="false" />
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

        <el-table-column label="商品信息" min-width="200">
          <template #default="{ row }">
            <div>{{ row.product_name }}</div>
            <el-tag size="small" type="info">ID: {{ row.product_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="用户信息" width="150">
          <template #default="{ row }">
            <div>{{ row.user_nickname || '未知' }}</div>
            <div class="text-xs text-gray">{{ row.user_phone || '' }}</div>
          </template>
        </el-table-column>

        <el-table-column label="评分" width="150">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled show-score text-color="#ff9900" score-template="{value}" />
          </template>
        </el-table-column>

        <el-table-column label="评价内容" min-width="250">
          <template #default="{ row }">
            <div class="review-content">{{ row.content }}</div>
            <div v-if="row.images && row.images.length > 0" class="review-images">
              <el-image
                v-for="(img, idx) in row.images.slice(0, 3)"
                :key="idx"
                :src="getImageUrl(img)"
                :preview-src-list="row.images?.map(getImageUrl)"
                fit="cover"
                style="width: 60px; height: 60px; margin-right: 5px"
                :z-index="9999"
                :preview-teleported="true"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column label="商家回复" width="200">
          <template #default="{ row }">
            <div v-if="row.admin_reply" class="admin-reply">
              {{ row.admin_reply }}
            </div>
            <el-tag v-else size="small" type="info">未回复</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_visible"
              active-text="显示"
              inactive-text="隐藏"
              @change="handleToggleVisibility(row)"
            />
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="评价时间" width="180" />

        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleReply(row)" :disabled="!!row.admin_reply">
              {{ row.admin_reply ? '已回复' : '回复' }}
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

    <!-- 回复对话框 -->
    <el-dialog v-model="replyDialogVisible" title="回复评价" width="600px">
      <el-form :model="replyForm" label-width="100px">
        <el-form-item label="评价内容">
          <div class="review-content-text">{{ currentReview?.content }}</div>
        </el-form-item>

        <el-form-item label="商家回复">
          <el-input
            v-model="replyForm.reply"
            type="textarea"
            :rows="5"
            placeholder="请输入回复内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitReply">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft } from '@element-plus/icons-vue'
import { getReviewList, deleteReview, replyReview, toggleReviewVisibility } from '../api/review'
import type { Review, ReviewQuery } from '../types'

const loading = ref(false)
const reviewList = ref<Review[]>([])
const total = ref(0)
const replyDialogVisible = ref(false)
const currentReview = ref<Review | null>(null)

const queryForm = reactive<ReviewQuery>({
  page: 1,
  pageSize: 10,
  rating: undefined,
  isVisible: undefined
})

const replyForm = reactive({
  reply: ''
})

const loadReviews = async () => {
  loading.value = true
  try {
    const data = await getReviewList(queryForm)
    reviewList.value = data.reviews || []
    total.value = data.pagination?.total || 0
  } catch (error) {
    console.error('Failed to load reviews:', error)
    ElMessage.error('加载评价列表失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  queryForm.rating = undefined
  queryForm.isVisible = undefined
  queryForm.page = 1
  loadReviews()
}

const handleToggleVisibility = async (row: Review) => {
  try {
    await toggleReviewVisibility(row.id, row.is_visible)
    ElMessage.success(row.is_visible ? '评价已显示' : '评价已隐藏')
    loadReviews()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
    // 恢复开关状态
    row.is_visible = !row.is_visible
  }
}

const handleReply = (row: Review) => {
  currentReview.value = row
  replyForm.reply = ''
  replyDialogVisible.value = true
}

const handleSubmitReply = async () => {
  if (!replyForm.reply.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }

  if (!currentReview.value) return

  try {
    await replyReview(currentReview.value.id, replyForm.reply)
    ElMessage.success('回复成功')
    replyDialogVisible.value = false
    loadReviews()
  } catch (error: any) {
    ElMessage.error(error.message || '回复失败')
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

const getImageUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http')) {
    return path
  }
  if (path.startsWith('/images')) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8001'
    return `${baseUrl}${path}`
  }
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}${path}`
}

onMounted(() => {
  loadReviews()
})
</script>

<style scoped>
.reviews {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.review-content {
  color: #303133;
  line-height: 1.6;
}

.review-images {
  display: flex;
  margin-top: 10px;
}

.admin-reply {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  color: #606266;
  line-height: 1.6;
}

.review-content-text {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 10px;
}

.text-xs {
  font-size: 12px;
}

.text-gray {
  color: #909399;
}
</style>
