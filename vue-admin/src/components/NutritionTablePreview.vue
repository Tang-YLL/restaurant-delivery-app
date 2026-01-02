<template>
  <div class="nutrition-table-preview">
    <el-card class="preview-card">
      <template #header>
        <div class="card-header">
          <span>营养成分表预览</span>
        </div>
      </template>

      <div v-if="!hasData" class="no-data">
        <el-empty description="暂无营养数据" />
      </div>

      <div v-else class="nutrition-content">
        <!-- 份量信息 -->
        <div class="serving-info">
          <strong>份量：</strong>{{ nutritionData.serving_size || '未填写' }}
        </div>

        <!-- 营养成分表 -->
        <el-table
          :data="nutritionRows"
          border
          stripe
          class="nutrition-table"
          :show-header="true"
        >
          <el-table-column prop="name" label="营养成分" width="150" />
          <el-table-column prop="value" label="含量" width="120" />
          <el-table-column prop="nrv" label="NRV%" width="100">
            <template #default="{ row }">
              <span v-if="row.nrv !== null" :class="getNrvClass(row.nrv)">
                {{ row.nrv }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>

        <!-- 过敏源警告 -->
        <el-alert
          v-if="nutritionData.allergens && nutritionData.allergens.length > 0"
          type="warning"
          :closable="false"
          class="allergen-alert"
          show-icon
        >
          <template #default>
            <div class="allergen-content">
              <div class="allergen-title">过敏源提示</div>
              <div class="allergen-text">
                本产品含有 <strong>{{ nutritionData.allergens.join('、') }}</strong>，相关过敏者请谨慎食用。
              </div>
            </div>
          </template>
        </el-alert>

        <!-- 营养提示 -->
        <div class="nutrition-tips">
          <el-icon><InfoFilled /></el-icon>
          <span>NRV%表示每100g（或每份）食品中所含营养成分占人体日需要量的百分比</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import type { Nutrition } from '../types'
import { NRV_VALUES } from '../types'

interface Props {
  nutrition: Nutrition | null
}

const props = defineProps<Props>()

const hasData = computed(() => {
  return props.nutrition && (
    props.nutrition.serving_size ||
    props.nutrition.calories > 0 ||
    props.nutrition.protein > 0 ||
    props.nutrition.fat > 0 ||
    props.nutrition.carbohydrates > 0 ||
    props.nutrition.sodium > 0
  )
})

const nutritionData = computed(() => {
  return props.nutrition || {
    serving_size: '',
    calories: 0,
    protein: 0,
    fat: 0,
    carbohydrates: 0,
    sodium: 0,
    dietary_fiber: 0,
    sugar: 0,
    allergens: []
  }
})

// 计算NRV%
const calculateNRV = (value: number, nrv: number): number | null => {
  if (!value || value <= 0) return null
  return Math.round((value / nrv) * 100)
}

// 营养成分表格数据
const nutritionRows = computed(() => {
  const data = nutritionData.value
  return [
    {
      name: '热量',
      value: data.calories !== undefined && data.calories !== null ? `${data.calories} kJ` : '-',
      nrv: null
    },
    {
      name: '蛋白质',
      value: data.protein !== undefined && data.protein !== null ? `${data.protein} g` : '-',
      nrv: calculateNRV(data.protein || 0, NRV_VALUES.protein)
    },
    {
      name: '脂肪',
      value: data.fat !== undefined && data.fat !== null ? `${data.fat} g` : '-',
      nrv: calculateNRV(data.fat || 0, NRV_VALUES.fat)
    },
    {
      name: '碳水化合物',
      value: data.carbohydrates !== undefined && data.carbohydrates !== null ? `${data.carbohydrates} g` : '-',
      nrv: calculateNRV(data.carbohydrates || 0, NRV_VALUES.carbohydrates)
    },
    {
      name: '钠',
      value: data.sodium !== undefined && data.sodium !== null ? `${data.sodium} mg` : '-',
      nrv: calculateNRV(data.sodium || 0, NRV_VALUES.sodium)
    },
    {
      name: '膳食纤维',
      value: data.dietary_fiber !== undefined && data.dietary_fiber !== null && data.dietary_fiber > 0
        ? `${data.dietary_fiber} g`
        : '-',
      nrv: null
    },
    {
      name: '糖',
      value: data.sugar !== undefined && data.sugar !== null && data.sugar > 0
        ? `${data.sugar} g`
        : '-',
      nrv: null
    }
  ]
})

// 根据NRV%返回样式类
const getNrvClass = (nrv: number) => {
  if (nrv >= 30) return 'nrv-high'
  if (nrv >= 15) return 'nrv-medium'
  return 'nrv-low'
}
</script>

<style scoped>
.nutrition-table-preview {
  height: 100%;
}

.preview-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}

.nutrition-content {
  padding: 10px 0;
}

.serving-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.serving-info strong {
  color: #303133;
  margin-right: 5px;
}

.nutrition-table {
  margin-bottom: 20px;
}

.allergen-alert {
  margin-bottom: 20px;
}

.allergen-content {
  padding: 5px 0;
}

.allergen-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #e6a23c;
}

.allergen-text {
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.allergen-text strong {
  color: #e6a23c;
  font-weight: bold;
}

.nutrition-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #ecf5ff;
  border-radius: 4px;
  color: #409eff;
  font-size: 13px;
}

/* NRV%样式 */
.nrv-high {
  color: #f56c6c;
  font-weight: bold;
}

.nrv-medium {
  color: #e6a23c;
  font-weight: bold;
}

.nrv-low {
  color: #67c23a;
}

/* 表格样式优化 */
:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #303133;
  font-weight: bold;
}

:deep(.el-table td) {
  color: #606266;
}
</style>
