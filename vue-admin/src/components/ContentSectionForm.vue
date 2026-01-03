<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑分区' : '创建分区'"
    width="900px"
    @close="handleClose"
    :close-on-click-modal="false"
  >
    <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="分区类型" prop="section_type">
        <el-select
          v-model="formData.section_type"
          placeholder="选择类型"
          :disabled="isEdit"
        >
          <el-option label="故事" value="story">
            <div class="option-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>故事</span>
            </div>
          </el-option>
          <el-option label="营养" value="nutrition">
            <div class="option-item">
              <el-icon><Document /></el-icon>
              <span>营养</span>
            </div>
          </el-option>
          <el-option label="食材" value="ingredients">
            <div class="option-item">
              <el-icon><ShoppingBag /></el-icon>
              <span>食材</span>
            </div>
          </el-option>
          <el-option label="工艺" value="process">
            <div class="option-item">
              <el-icon><Picture /></el-icon>
              <span>工艺</span>
            </div>
          </el-option>
          <el-option label="贴士" value="tips">
            <div class="option-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>贴士</span>
            </div>
          </el-option>
        </el-select>
        <div class="form-tip">
          {{ getTypeDescription(formData.section_type) }}
        </div>
      </el-form-item>

      <el-form-item label="标题" prop="title">
        <el-input
          v-model="formData.title"
          placeholder="可选的分区标题，如：菜品故事、营养价值等"
          maxlength="200"
          show-word-limit
          clearable
        />
      </el-form-item>

      <el-form-item label="内容" prop="content">
        <QuillEditor
          v-model="formData.content"
          placeholder="请输入分区内容，支持富文本编辑..."
          :min-height="300"
        />
      </el-form-item>

      <el-form-item label="显示顺序">
        <el-input-number
          v-model="formData.display_order"
          :min="0"
          :max="999"
          :step="1"
        />
        <div class="form-tip">
          数值越小越靠前，支持拖拽排序自动更新
        </div>
      </el-form-item>

      <!-- 快速模板应用 -->
      <el-form-item label="快速模板" v-if="!isEdit">
        <el-button-group>
          <el-button
            v-for="template in getCurrentTemplates()"
            :key="template.type"
            size="small"
            @click="applyTemplate(template)"
          >
            {{ template.name }}
          </el-button>
        </el-button-group>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Picture,
  ShoppingBag,
  ChatDotRound
} from '@element-plus/icons-vue'
import QuillEditor from './QuillEditor.vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ContentSection, SectionType } from '@/types'

interface Props {
  modelValue: boolean
  section: ContentSection | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': [section: ContentSection]
}>()

const formRef = ref<FormInstance>()
const visible = ref(props.modelValue)
const submitting = ref(false)
const formData = ref<ContentSection>({
  id: undefined,
  product_id: 0,
  section_type: 'story',
  title: '',
  content: '',
  display_order: 0
})

const isEdit = computed(() => !!props.section?.id)

const rules: FormRules = {
  section_type: [
    { required: true, message: '请选择分区类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' },
    {
      min: 10,
      message: '内容至少需要10个字符',
      trigger: 'blur'
    }
  ]
}

// 模板列表
const allTemplates = [
  {
    type: 'story' as SectionType,
    name: '菜品故事',
    content: `<h3>菜品故事</h3>
<p>这是一道传承已久的经典菜品，承载着深厚的文化底蕴和历史记忆。</p>
<p>它的制作工艺源自古老的烹饪智慧，经过一代代厨师的传承和创新，形成了今天独特的风味。</p>
<h4>特色亮点</h4>
<ul>
  <li>选用最新鲜的食材</li>
  <li>传统工艺精心制作</li>
  <li>口感层次丰富</li>
</ul>`
  },
  {
    type: 'nutrition' as SectionType,
    name: '营养成分',
    content: `<h3>营养价值</h3>
<p>本菜品富含多种营养元素，是健康饮食的优质选择。</p>
<h4>主要营养成分</h4>
<table>
  <tr>
    <td>蛋白质</td>
    <td>含量丰富，有助于肌肉发育</td>
  </tr>
  <tr>
    <td>维生素</td>
    <td>多种维生素，增强免疫力</td>
  </tr>
  <tr>
    <td>膳食纤维</td>
    <td>促进消化，维护肠道健康</td>
  </tr>
</table>
<h4>适宜人群</h4>
<p>适合所有年龄段人群食用，尤其推荐注重健康饮食的消费者。</p>`
  },
  {
    type: 'ingredients' as SectionType,
    name: '食材来源',
    content: `<h3>精选食材</h3>
<p>我们对食材的选择极其严格，确保每一道菜品都使用最新鲜、最优质的原料。</p>
<h4>主料来源</h4>
<ul>
  <li><strong>主料：</strong>精选优质产区，保证新鲜度</li>
  <li><strong>辅料：</strong>严格筛选，确保品质</li>
  <li><strong>调料：</strong>选用知名品牌，口味纯正</li>
</ul>
<h4>采购标准</h4>
<p>每日新鲜采购，严格质检，确保食材安全、新鲜、营养。</p>`
  },
  {
    type: 'process' as SectionType,
    name: '制作工艺',
    content: `<h3>制作工艺</h3>
<p>采用传统与现代相结合的烹饪工艺，确保菜品既保留传统风味，又符合现代健康标准。</p>
<h4>制作步骤</h4>
<ol>
  <li><strong>食材准备：</strong>精心挑选并处理食材</li>
  <li><strong>火候掌控：</strong>严格控制火候和时间</li>
  <li><strong>调味平衡：</strong>精准调配各种调料</li>
  <li><strong>摆盘装饰：</strong>精心设计，美观大方</li>
</ol>
<h4>工艺特点</h4>
<p>遵循传统工艺精髓，结合现代营养学理念，打造健康美味的菜品。</p>`
  },
  {
    type: 'tips' as SectionType,
    name: '食用贴士',
    content: `<h3>食用建议</h3>
<p>为了让您获得最佳的用餐体验，我们提供以下食用建议。</p>
<h4>最佳食用方式</h4>
<ul>
  <li>建议趁热食用，口感最佳</li>
  <li>可搭配米饭或面食</li>
  <li>适合2-3人分享</li>
</ul>
<h4>注意事项</h4>
<p>如有特殊饮食需求或过敏史，请在点餐时告知我们的服务人员。</p>
<h4>保存建议</h4>
<p>建议即时食用，如需保存请密封冷藏，并在24小时内食用完毕。</p>`
  }
]

watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

watch(() => props.section, (section) => {
  if (section) {
    formData.value = { ...section }
  } else {
    resetForm()
  }
})

function getTypeDescription(type: SectionType): string {
  const descriptions: Record<SectionType, string> = {
    story: '讲述菜品的故事、历史背景或文化内涵',
    nutrition: '介绍营养成分、健康价值和适宜人群',
    ingredients: '说明食材来源、品质标准和采购要求',
    process: '描述制作工艺、烹饪步骤和特色技法',
    tips: '提供食用建议、注意事项和保存方法'
  }
  return descriptions[type] || ''
}

function getCurrentTemplates() {
  return allTemplates.filter(t => t.type === formData.value.section_type)
}

function applyTemplate(template: any) {
  formData.value.content = template.content
  if (!formData.value.title) {
    formData.value.title = template.name
  }
  ElMessage.success(`已应用"${template.name}"模板`)
}

function resetForm() {
  formData.value = {
    id: undefined,
    product_id: 0,
    section_type: 'story',
    title: '',
    content: '',
    display_order: 0
  }
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  try {
    submitting.value = true
    await formRef.value?.validate()

    emit('save', { ...formData.value })
    handleClose()
    ElMessage.success('保存成功')
  } catch (error: any) {
    if (error?.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('表单验证失败，请检查输入')
    }
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  visible.value = false
  resetForm()
}
</script>

<style scoped>
.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-select-dropdown__item) {
  height: auto;
  padding: 8px 12px;
}

:deep(.el-input-number) {
  width: 180px;
}
</style>
