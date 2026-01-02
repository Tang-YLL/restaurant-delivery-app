<template>
  <div class="nutrition-editor">
    <el-form :model="formData" label-width="120px" class="editor-form">
      <!-- 份量 -->
      <el-form-item label="份量">
        <el-input
          v-model="formData.serving_size"
          placeholder="例如：100g、1份(200g)"
          clearable
        />
      </el-form-item>

      <!-- 热量 -->
      <el-form-item label="热量 (kJ)">
        <el-input-number
          v-model="formData.calories"
          :min="0"
          :max="100000"
          :precision="0"
          placeholder="0"
        />
      </el-form-item>

      <!-- 蛋白质 -->
      <el-form-item label="蛋白质 (g)">
        <el-input-number
          v-model="formData.protein"
          :min="0"
          :max="1000"
          :precision="1"
          placeholder="0"
        />
      </el-form-item>

      <!-- 脂肪 -->
      <el-form-item label="脂肪 (g)">
        <el-input-number
          v-model="formData.fat"
          :min="0"
          :max="1000"
          :precision="1"
          placeholder="0"
        />
      </el-form-item>

      <!-- 碳水化合物 -->
      <el-form-item label="碳水化合物 (g)">
        <el-input-number
          v-model="formData.carbohydrates"
          :min="0"
          :max="1000"
          :precision="1"
          placeholder="0"
        />
      </el-form-item>

      <!-- 钠 -->
      <el-form-item label="钠 (mg)">
        <el-input-number
          v-model="formData.sodium"
          :min="0"
          :max="100000"
          :precision="0"
          placeholder="0"
        />
      </el-form-item>

      <!-- 膳食纤维（可选） -->
      <el-form-item label="膳食纤维 (g)">
        <el-input-number
          v-model="formData.dietary_fiber"
          :min="0"
          :max="1000"
          :precision="1"
          placeholder="0"
        />
      </el-form-item>

      <!-- 糖（可选） -->
      <el-form-item label="糖 (g)">
        <el-input-number
          v-model="formData.sugar"
          :min="0"
          :max="1000"
          :precision="1"
          placeholder="0"
        />
      </el-form-item>

      <!-- 过敏源 -->
      <el-form-item label="过敏源">
        <el-checkbox-group v-model="formData.allergens">
          <el-checkbox
            v-for="allergen in ALLERGEN_LIST"
            :key="allergen"
            :label="allergen"
          >
            {{ allergen }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <!-- 过敏源警告 -->
      <el-alert
        v-if="formData.allergens && formData.allergens.length > 0"
        type="warning"
        :closable="false"
        class="allergen-alert"
      >
        <template #title>
          <div class="allergen-warning">
            <strong>过敏源提示：</strong>
            本产品含有 {{ formData.allergens.join('、') }}，相关过敏者请谨慎食用。
          </div>
        </template>
      </el-alert>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { NutritionFormData } from '../types'
import { ALLERGEN_LIST } from '../types'

interface Props {
  modelValue: NutritionFormData
}

interface Emits {
  (e: 'update:modelValue', value: NutritionFormData): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formData = reactive<NutritionFormData>({
  serving_size: props.modelValue.serving_size || '',
  calories: props.modelValue.calories ?? null,
  protein: props.modelValue.protein ?? null,
  fat: props.modelValue.fat ?? null,
  carbohydrates: props.modelValue.carbohydrates ?? null,
  sodium: props.modelValue.sodium ?? null,
  dietary_fiber: props.modelValue.dietary_fiber ?? null,
  sugar: props.modelValue.sugar ?? null,
  allergens: props.modelValue.allergens || []
})

// 监听变化，同步到父组件
watch(
  formData,
  (newData) => {
    emit('update:modelValue', { ...newData })
  },
  { deep: true }
)

// 监听外部变化，同步到本地
watch(
  () => props.modelValue,
  (newValue) => {
    Object.assign(formData, {
      serving_size: newValue.serving_size || '',
      calories: newValue.calories ?? null,
      protein: newValue.protein ?? null,
      fat: newValue.fat ?? null,
      carbohydrates: newValue.carbohydrates ?? null,
      sodium: newValue.sodium ?? null,
      dietary_fiber: newValue.dietary_fiber ?? null,
      sugar: newValue.sugar ?? null,
      allergens: newValue.allergens || []
    })
  },
  { deep: true }
)
</script>

<style scoped>
.nutrition-editor {
  padding: 20px;
}

.editor-form {
  max-width: 600px;
}

.editor-form .el-form-item {
  margin-bottom: 22px;
}

.allergen-alert {
  margin-top: 10px;
}

.allergen-warning {
  font-size: 14px;
  line-height: 1.6;
}

.allergen-warning strong {
  color: #e6a23c;
}
</style>
