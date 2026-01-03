# ADMIN-003 任务分析

## 任务概述
创建营养成分表的可视化编辑组件，实现营养数据的表单输入、验证和预览功能。

## 技术分析

### 技术栈
- **前端框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **工作目录**: `vue-admin/`

### 功能需求

#### 1. 创建营养表单组件
**文件**: `vue-admin/src/components/NutritionEditor.vue`

```vue
<template>
  <div class="nutrition-editor">
    <el-form :model="formData" :rules="rules" ref="formRef" label-width="140px">
      <!-- 份量 -->
      <el-form-item label="份量" prop="serving_size">
        <el-input
          v-model="formData.serving_size"
          placeholder="如: 1份(200g)"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <!-- 热量 -->
      <el-form-item label="热量 (kcal/100g)" prop="calories">
        <el-input-number
          v-model="formData.calories"
          :min="0"
          :precision="1"
          :step="1"
          controls-position="right"
        />
      </el-form-item>

      <!-- 蛋白质 -->
      <el-form-item label="蛋白质 (g/100g)" prop="protein">
        <el-input-number
          v-model="formData.protein"
          :min="0"
          :max="100"
          :precision="1"
          :step="0.1"
          controls-position="right"
        />
        <div class="nrv-preview">NRV%: {{ calculateNRV('protein', formData.protein) }}%</div>
      </el-form-item>

      <!-- 脂肪 -->
      <el-form-item label="脂肪 (g/100g)" prop="fat">
        <el-input-number
          v-model="formData.fat"
          :min="0"
          :max="100"
          :precision="1"
          :step="0.1"
          controls-position="right"
        />
        <div class="nrv-preview">NRV%: {{ calculateNRV('fat', formData.fat) }}%</div>
      </el-form-item>

      <!-- 碳水化合物 -->
      <el-form-item label="碳水化合物 (g/100g)" prop="carbohydrates">
        <el-input-number
          v-model="formData.carbohydrates"
          :min="0"
          :max="100"
          :precision="1"
          :step="0.1"
          controls-position="right"
        />
        <div class="nrv-preview">NRV%: {{ calculateNRV('carbohydrates', formData.carbohydrates) }}%</div>
      </el-form-item>

      <!-- 钠 -->
      <el-form-item label="钠 (mg/100g)" prop="sodium">
        <el-input-number
          v-model="formData.sodium"
          :min="0"
          :max="10000"
          :precision="0"
          :step="10"
          controls-position="right"
        />
        <div class="nrv-preview">NRV%: {{ calculateNRV('sodium', formData.sodium) }}%</div>
      </el-form-item>

      <!-- 膳食纤维（可选） -->
      <el-form-item label="膳食纤维 (g/100g)">
        <el-input-number
          v-model="formData.dietary_fiber"
          :min="0"
          :max="100"
          :precision="1"
          :step="0.1"
          controls-position="right"
        />
      </el-form-item>

      <!-- 糖（可选） -->
      <el-form-item label="糖 (g/100g)">
        <el-input-number
          v-model="formData.sugars"
          :min="0"
          :max="100"
          :precision="1"
          :step="0.1"
          controls-position="right"
        />
      </el-form-item>
    </el-form>

    <!-- 过敏源提示 -->
    <el-divider>过敏源提示</el-divider>
    <el-checkbox-group v-model="selectedAllergens">
      <el-checkbox label="peanuts">花生</el-checkbox>
      <el-checkbox label="eggs">蛋类</el-checkbox>
      <el-checkbox label="dairy">乳制品</el-checkbox>
      <el-checkbox label="soy">大豆</el-checkbox>
      <el-checkbox label="nuts">坚果</el-checkbox>
      <el-checkbox label="fish">鱼类</el-checkbox>
      <el-checkbox label="shellfish">贝类</el-checkbox>
      <el-checkbox label="wheat">小麦</el-checkbox>
    </el-checkbox-group>

    <el-alert
      v-if="selectedAllergens.length > 0"
      :title="`警告：本产品含有 ${selectedAllergens.length} 种过敏源`"
      type="warning"
      :closable="false"
      style="margin-top: 16px;"
    >
      <template #default>
        本产品含有：{{ allergenNames.join('、') }}。过敏人群请谨慎食用。
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FormInstance } from 'element-plus'

interface Props {
  modelValue: NutritionFactsData
}

interface NutritionFactsData {
  serving_size?: string
  calories?: number
  protein?: number
  fat?: number
  carbohydrates?: number
  sodium?: number
  dietary_fiber?: number
  sugars?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: NutritionFactsData]
}>()

const formRef = ref<FormInstance>()
const formData = ref<NutritionFactsData>({ ...props.modelValue })
const selectedAllergens = ref<string[]>([])

// NRV参考值（中国标准）
const NRV_VALUES = {
  protein: 60,      // g
  fat: 60,          // g
  carbohydrates: 300, // g
  sodium: 2000      // mg
}

// 计算NRV%
function calculateNRV(nutrient: keyof typeof NRV_VALUES, value: number): number {
  if (!value) return 0
  const nrv = NRV_VALUES[nutrient]
  return Math.round((value / nrv) * 100)
}

// 过敏源名称映射
const allergenNamesMap: Record<string, string> = {
  peanuts: '花生',
  eggs: '蛋类',
  dairy: '乳制品',
  soy: '大豆',
  nuts: '坚果',
  fish: '鱼类',
  shellfish: '贝类',
  wheat: '小麦'
}

const allergenNames = computed(() => {
  return selectedAllergens.value.map(key => allergenNamesMap[key])
})

// 验证规则
const rules = {
  calories: [
    { type: 'number', min: 0, message: '热量不能为负数', trigger: 'blur' }
  ],
  protein: [
    { type: 'number', min: 0, max: 100, message: '蛋白质范围0-100', trigger: 'blur' }
  ],
  fat: [
    { type: 'number', min: 0, max: 100, message: '脂肪范围0-100', trigger: 'blur' }
  ],
  carbohydrates: [
    { type: 'number', min: 0, max: 100, message: '碳水化合物范围0-100', trigger: 'blur' }
  ],
  sodium: [
    { type: 'number', min: 0, max: 10000, message: '钠范围0-10000', trigger: 'blur' }
  ]
}

// 监听变化
watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

watch(() => props.modelValue, (newValue) => {
  formData.value = { ...newValue }
}, { deep: true })

// 暴露方法给父组件
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields()
})
</script>

<style scoped>
.nutrition-editor {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.nrv-preview {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-input-number) {
  width: 200px;
}
</style>
```

#### 2. 创建表格预览组件
**文件**: `vue-admin/src/components/NutritionTablePreview.vue`

```vue
<template>
  <div class="nutrition-table-preview">
    <h3>营养成分表</h3>
    <p v-if="data.serving_size">份量: {{ data.serving_size }}</p>

    <el-table :data="tableData" border style="width: 100%">
      <el-table-column prop="nutrient" label="营养成分" width="180" />
      <el-table-column prop="per100g" label="每100克" />
      <el-table-column prop="nrv" label="NRV%" width="100" />
    </el-table>

    <div v-if="allergens.length > 0" class="allergen-warning">
      <el-alert
        title="过敏源提示"
        type="warning"
        :closable="false"
      >
        本产品含有：{{ allergens.join('、') }}
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  data: NutritionFactsData
  allergens: string[]
}

interface NutritionFactsData {
  serving_size?: string
  calories?: number
  protein?: number
  fat?: number
  carbohydrates?: number
  sodium?: number
  dietary_fiber?: number
  sugars?: number
}

const props = defineProps<Props>()

const NRV_VALUES = {
  protein: 60,
  fat: 60,
  carbohydrates: 300,
  sodium: 2000
}

function calculateNRV(nutrient: keyof typeof NRV_VALUES, value: number): number {
  if (!value) return 0
  return Math.round((value / NRV_VALUES[nutrient]) * 100)
}

const tableData = computed(() => {
  const rows = []

  if (props.data.calories !== undefined) {
    rows.push({
      nutrient: '热量',
      per100g: `${props.data.calories} kcal`
    })
  }

  if (props.data.protein !== undefined) {
    rows.push({
      nutrient: '蛋白质',
      per100g: `${props.data.protein} g`,
      nrv: `${calculateNRV('protein', props.data.protein)}%`
    })
  }

  if (props.data.fat !== undefined) {
    rows.push({
      nutrient: '脂肪',
      per100g: `${props.data.fat} g`,
      nrv: `${calculateNRV('fat', props.data.fat)}%`
    })
  }

  if (props.data.carbohydrates !== undefined) {
    rows.push({
      nutrient: '碳水化合物',
      per100g: `${props.data.carbohydrates} g`,
      nrv: `${calculateNRV('carbohydrates', props.data.carbohydrates)}%`
    })
  }

  if (props.data.sodium !== undefined) {
    rows.push({
      nutrient: '钠',
      per100g: `${props.data.sodium} mg`,
      nrv: `${calculateNRV('sodium', props.data.sodium)}%`
    })
  }

  if (props.data.dietary_fiber !== undefined) {
    rows.push({
      nutrient: '膳食纤维',
      per100g: `${props.data.dietary_fiber} g`
    })
  }

  if (props.data.sugars !== undefined) {
    rows.push({
      nutrient: '糖',
      per100g: `${props.data.sugars} g`
    })
  }

  return rows
})

const allergens = computed(() => {
  const map: Record<string, string> = {
    peanuts: '花生',
    eggs: '蛋类',
    dairy: '乳制品',
    soy: '大豆',
    nuts: '坚果',
    fish: '鱼类',
    shellfish: '贝类',
    wheat: '小麦'
  }
  return props.allergens.map(key => map[key])
})
</script>

<style scoped>
.nutrition-table-preview {
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
}

h3 {
  margin-top: 0;
  color: #303133;
}

.allergen-warning {
  margin-top: 20px;
}

:deep(.el-table__cell) {
  padding: 8px 0;
}

:deep(.el-table__cell.is-highligft) {
  background: #fdf6ec;
}
</style>
```

#### 3. 集成到分区管理
在商品详情页中添加营养成分编辑和预览：

```vue
<template>
  <el-tabs v-model="activeTab">
    <!-- ... 其他Tab ... -->

    <el-tab-pane label="营养成分" name="nutrition">
      <el-row :gutter="20">
        <el-col :span="12">
          <h4>编辑</h4>
          <NutritionEditor
            v-model="nutritionData"
            ref="nutritionEditorRef"
          />
          <el-button
            type="primary"
            @click="saveNutrition"
            style="margin-top: 20px;"
          >
            保存营养成分
          </el-button>
        </el-col>

        <el-col :span="12">
          <h4>预览</h4>
          <NutritionTablePreview
            :data="nutritionData"
            :allergens="selectedAllergens"
          />
        </el-col>
      </el-row>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NutritionEditor from '@/components/NutritionEditor.vue'
import NutritionTablePreview from '@/components/NutritionTablePreview.vue'
import { updateNutritionFacts } from '@/api/product'

const activeTab = ref('nutrition')
const nutritionData = ref({})
const selectedAllergens = ref<string[]>([])
const nutritionEditorRef = ref()

async function saveNutrition() {
  try {
    await nutritionEditorRef.value.validate()

    await updateNutritionFacts(productId, {
      ...nutritionData.value,
      allergens: selectedAllergens.value
    })

    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}
</script>
```

## 实施步骤

### 步骤1: 创建NutritionEditor组件
创建`vue-admin/src/components/NutritionEditor.vue`

### 步骤2: 实现表单字段
- 份量（serving_size）
- 热量、蛋白质、脂肪、碳水、钠
- 膳食纤维、糖（可选）
- 所有字段使用el-input-number

### 步骤3: 实现数据验证
- 热量≥0
- 蛋白质、脂肪、碳水 0-100
- 钠 0-10000
- 实时验证和错误提示

### 步骤4: 实现NRV%计算
- 使用中国营养标签标准
- 实时计算并显示NRV%
- 蛋白质60g、脂肪60g、碳水300g、钠2000mg

### 步骤5: 创建预览组件
创建`vue-admin/src/components/NutritionTablePreview.vue`

### 步骤6: 添加过敏源提示
- 8种常见过敏源选择
- 自动生成警告声明
- 高亮显示警告

### 步骤7: 集成到商品详情页
在ProductDetail.vue中添加"营养成分"Tab

### 步骤8: 测试
- 测试表单验证
- 测试NRV%计算
- 测试过敏源提示
- 测试保存功能

## 验收标准

| 验收标准 | 测试方法 |
|---------|---------|
| 表单包含所有必需字段 | 检查所有字段存在 |
| 数据验证正常工作 | 输入负值、超大值 |
| 表格预览正确显示 | 切换到预览模式 |
| NRV%自动计算正确 | 手动计算验证 |
| 过敏源提示显示正常 | 选择过敏源查看 |
| 保存到数据库成功 | 保存后刷新页面 |

## NRV参考值（中国标准）

| 营养素 | NRV值 | 单位 |
|--------|-------|------|
| 蛋白质 | 60 | g |
| 脂肪 | 60 | g |
| 碳水化合物 | 300 | g |
| 钠 | 2000 | mg |

## 文件清单

**新建文件**:
- `vue-admin/src/components/NutritionEditor.vue`
- `vue-admin/src/components/NutritionTablePreview.vue`

**修改文件**:
- `vue-admin/src/views/ProductDetail.vue` - 添加营养成分Tab
- `vue-admin/src/api/product.ts` - 添加API方法（如果需要）

## 技术要点

### 表单验证
使用Element Plus的el-form和el-input-number
设置min、max、precision属性进行验证

### NRV%计算公式
```
NRV% = (每100g含量 / NRV参考值) × 100%
```

### 过敏源管理
使用el-checkbox-group选择
自动生成中文警告声明

## 注意事项

1. **数据类型**: 确保数值字段正确处理undefined和null
2. **验证规则**: 热量≥0，其他字段也有合理范围
3. **NRV精度**: 使用Math.round四舍五入到整数
4. **过敏源**: 存储为字符串数组（可能需要后端支持）
5. **预览同步**: 编辑时实时更新预览

## 与其他任务的集成

- **依赖API-003**: 调用后端营养数据API
- **与ADMIN-002协作**: 可以作为分区类型之一集成
