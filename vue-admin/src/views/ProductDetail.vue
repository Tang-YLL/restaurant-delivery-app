<template>
  <div class="product-detail">
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span class="product-title">{{ product?.name || '商品详情' }}</span>
      </template>
    </el-page-header>

    <el-card v-loading="loading" class="detail-card">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <div class="basic-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="商品ID">{{ product?.id }}</el-descriptions-item>
              <el-descriptions-item label="商品名称">{{ product?.name }}</el-descriptions-item>
              <el-descriptions-item label="分类">{{ product?.category }}</el-descriptions-item>
              <el-descriptions-item label="价格">¥{{ product?.price }}</el-descriptions-item>
              <el-descriptions-item label="库存">{{ product?.stock }}</el-descriptions-item>
              <el-descriptions-item label="销量">{{ product?.sales }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="product?.status === 'active' ? 'success' : 'danger'">
                  {{ product?.status === 'active' ? '上架' : '下架' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ product?.createdAt }}</el-descriptions-item>
              <el-descriptions-item label="商品描述" :span="2">
                {{ product?.description }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="product-images" v-if="product?.images?.length">
              <h4>商品图片</h4>
              <div class="image-list">
                <el-image
                  v-for="(img, index) in product.images"
                  :key="index"
                  :src="img"
                  fit="cover"
                  style="width: 120px; height: 120px; margin-right: 10px"
                  :preview-src-list="product.images"
                  :z-index="9999"
                  :preview-teleported="true"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 营养成分 -->
        <el-tab-pane label="营养成分" name="nutrition">
          <div class="nutrition-content">
            <div class="nutrition-layout">
              <!-- 左侧编辑器 -->
              <div class="editor-section">
                <h3 class="section-title">编辑营养成分</h3>
                <NutritionEditor v-model="nutritionForm" />
                <div class="save-button-group">
                  <el-button type="primary" @click="handleSaveNutrition" :loading="saving">
                    <el-icon><Check /></el-icon>
                    保存营养成分
                  </el-button>
                  <el-button @click="handleResetNutrition">
                    <el-icon><RefreshLeft /></el-icon>
                    重置
                  </el-button>
                </div>
              </div>

              <!-- 右侧预览 -->
              <div class="preview-section">
                <NutritionTablePreview :nutrition="nutritionPreview" />
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, RefreshLeft } from '@element-plus/icons-vue'
import NutritionEditor from '../components/NutritionEditor.vue'
import NutritionTablePreview from '../components/NutritionTablePreview.vue'
import { getProductDetail, saveProductNutrition, getProductNutrition } from '../api/product'
import type { Product, NutritionFormData, Nutrition } from '../types'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const product = ref<Product | null>(null)
const activeTab = ref('basic')
const originalNutrition = ref<Nutrition | null>(null)

// 营养成分表单
const nutritionForm = reactive<NutritionFormData>({
  serving_size: '',
  calories: null,
  protein: null,
  fat: null,
  carbohydrates: null,
  sodium: null,
  dietary_fiber: null,
  sugar: null,
  allergens: []
})

// 营养成分预览数据
const nutritionPreview = computed<Nutrition | null>(() => {
  const form = nutritionForm
  if (!form.serving_size &&
      !form.calories &&
      !form.protein &&
      !form.fat &&
      !form.carbohydrates &&
      !form.sodium) {
    return null
  }

  return {
    serving_size: form.serving_size || '',
    calories: form.calories || 0,
    protein: form.protein || 0,
    fat: form.fat || 0,
    carbohydrates: form.carbohydrates || 0,
    sodium: form.sodium || 0,
    dietary_fiber: form.dietary_fiber || undefined,
    sugar: form.sugar || undefined,
    allergens: form.allergens || []
  }
})

// 加载商品详情
const loadProductDetail = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('商品ID无效')
    goBack()
    return
  }

  loading.value = true
  try {
    const data = await getProductDetail(id)
    // 处理图片URL
    product.value = {
      ...data,
      image: getImageUrl(data.image || '/images/default.png'),
      images: (data.images || []).map((img: string) => getImageUrl(img))
    }

    // 加载营养成分
    await loadNutrition(id)
  } catch (error) {
    console.error('加载商品详情失败:', error)
    ElMessage.error('加载商品详情失败')
  } finally {
    loading.value = false
  }
}

// 加载营养成分
const loadNutrition = async (id: number) => {
  try {
    const data = await getProductNutrition(id)
    originalNutrition.value = data

    // 填充表单
    Object.assign(nutritionForm, {
      serving_size: data.serving_size || '',
      calories: data.calories || null,
      protein: data.protein || null,
      fat: data.fat || null,
      carbohydrates: data.carbohydrates || null,
      sodium: data.sodium || null,
      dietary_fiber: data.dietary_fiber || null,
      sugar: data.sugar || null,
      allergens: data.allergens || []
    })
  } catch (error: any) {
    // 如果是404错误，说明还没有营养数据，使用默认值
    if (error.response?.status !== 404) {
      console.error('加载营养成分失败:', error)
    }
  }
}

// 保存营养成分
const handleSaveNutrition = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('商品ID无效')
    return
  }

  saving.value = true
  try {
    await saveProductNutrition(id, nutritionForm)
    ElMessage.success('营养成分保存成功')
    // 重新加载以确认保存
    await loadNutrition(id)
  } catch (error: any) {
    console.error('保存营养成分失败:', error)
    ElMessage.error(error.message || '保存营养成分失败')
  } finally {
    saving.value = false
  }
}

// 重置营养成分
const handleResetNutrition = () => {
  if (originalNutrition.value) {
    Object.assign(nutritionForm, {
      serving_size: originalNutrition.value.serving_size || '',
      calories: originalNutrition.value.calories || null,
      protein: originalNutrition.value.protein || null,
      fat: originalNutrition.value.fat || null,
      carbohydrates: originalNutrition.value.carbohydrates || null,
      sodium: originalNutrition.value.sodium || null,
      dietary_fiber: originalNutrition.value.dietary_fiber || null,
      sugar: originalNutrition.value.sugar || null,
      allergens: originalNutrition.value.allergens || []
    })
  } else {
    Object.assign(nutritionForm, {
      serving_size: '',
      calories: null,
      protein: null,
      fat: null,
      carbohydrates: null,
      sodium: null,
      dietary_fiber: null,
      sugar: null,
      allergens: []
    })
  }
  ElMessage.info('已重置为原始数据')
}

const goBack = () => {
  router.back()
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
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'}${path}`
}

onMounted(() => {
  loadProductDetail()
})
</script>

<style scoped>
.product-detail {
  padding: 20px;
  height: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.product-title {
  font-size: 18px;
  font-weight: bold;
}

.detail-card {
  min-height: 600px;
}

.basic-info {
  padding: 20px;
}

.product-images {
  margin-top: 30px;
}

.product-images h4 {
  margin-bottom: 15px;
  color: #303133;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.nutrition-content {
  padding: 20px;
}

.nutrition-layout {
  display: flex;
  gap: 20px;
  height: 100%;
}

.editor-section {
  flex: 1;
  max-width: 600px;
}

.preview-section {
  flex: 1;
  min-width: 500px;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.save-button-group {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
  display: flex;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .nutrition-layout {
    flex-direction: column;
  }

  .preview-section {
    min-width: 100%;
  }
}
</style>
