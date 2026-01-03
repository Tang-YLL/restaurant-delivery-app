# ADMIN-002 任务分析

## 任务概述
实现商品详情内容分区的管理界面，包括分区列表、拖拽排序、模板系统等功能。

## 技术分析

### 技术栈
- **前端框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **拖拽库**: vuedraggable@next
- **工作目录**: `vue-admin/`

### 功能需求

#### 1. 安装拖拽依赖
```bash
cd vue-admin
npm install vuedraggable@next
```

在`vue-admin/package.json`中添加：
```json
{
  "dependencies": {
    "vuedraggable": "^4.1.0"
  }
}
```

#### 2. 创建分区列表组件
**文件**: `vue-admin/src/components/ContentSectionList.vue`

```vue
<template>
  <div class="content-section-list">
    <div class="section-header">
      <h3>内容分区 ({{ sections.length }})</h3>
      <el-button type="primary" @click="handleAdd" :icon="Plus">
        添加分区
      </el-button>
    </div>

    <div class="template-bar" v-if="sections.length === 0">
      <span>快速创建：</span>
      <el-button
        v-for="template in templates"
        :key="template.type"
        link
        type="primary"
        @click="applyTemplate(template)"
      >
        {{ template.name }}
      </el-button>
    </div>

    <draggable
      v-model="sections"
      item-key="id"
      @end="handleDragEnd"
      class="section-list"
    >
      <template #item="{ element: section, index }">
        <el-card class="section-card" :class="`section-${section.section_type}`">
          <div class="section-card-header">
            <div class="section-info">
              <el-icon :size="20" class="type-icon">
                <component :is="getTypeIcon(section.section_type)" />
              </el-icon>
              <span class="section-type">{{ getTypeName(section.section_type) }}</span>
              <el-tag v-if="section.title" size="small">{{ section.title }}</el-tag>
            </div>

            <div class="section-actions">
              <el-button-group>
                <el-button
                  size="small"
                  @click="handleEdit(section)"
                  :icon="Edit"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="handleDelete(section)"
                  :icon="Delete"
                >
                  删除
                </el-button>
              </el-button-group>
            </div>
          </div>

          <div class="section-preview">
            <div class="content-preview" v-html="getPreview(section.content)"></div>
          </div>

          <div class="section-meta">
            <span>顺序: {{ section.display_order }}</span>
            <span v-if="section.updated_at">
              更新: {{ formatDate(section.updated_at) }}
            </span>
          </div>
        </el-card>
      </template>
    </draggable>

    <el-empty v-if="sections.length === 0" description="暂无内容分区">
      <el-button type="primary" @click="handleAdd">创建第一个分区</el-button>
    </el-empty>

    <!-- 编辑对话框 -->
    <ContentSectionForm
      v-model="dialogVisible"
      :section="currentSection"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Edit, Delete, Document, Picture, ShoppingBag, ChatDotRound } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import { ElMessage, ElMessageBox } from 'element-plus'
import ContentSectionForm from './ContentSectionForm.vue'
import type { ContentSection } from '@/types'

interface Props {
  productId: number
  sections: ContentSection[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:sections': [sections: ContentSection[]]
  'add': []
  'edit': [section: ContentSection]
  'delete': [section: ContentSection]
}>()

const dialogVisible = ref(false)
const currentSection = ref<ContentSection | null>(null)

// 分区类型图标映射
const typeIcons: Record<string, any> = {
  story: ChatDotRound,
  nutrition: Document,
  ingredients: ShoppingBag,
  process: Picture,
  tips: ChatDotRound
}

// 分区类型名称
const typeNames: Record<string, string> = {
  story: '故事',
  nutrition: '营养',
  ingredients: '食材',
  process: '工艺',
  tips: '贴士'
}

// 模板列表
const templates = [
  { type: 'story', name: '菜品故事', content: '<p>这是一个关于菜品的故事...</p>' },
  { type: 'nutrition', name: '营养成分', content: '<h3>营养价值</h3><ul><li>蛋白质丰富</li><li>低脂肪</li></ul>' },
  { type: 'ingredients', name: '食材来源', content: '<h3>主要食材</h3><p>精选优质食材...</p>' },
  { type: 'process', name: '制作工艺', content: '<h3>制作步骤</h3><ol><li>准备食材</li><li>开始烹饪</li></ol>' },
  { type: 'tips', name: '食用贴士', content: '<h3>食用建议</h3><p>建议...</p>' }
]

function getTypeIcon(type: string) {
  return typeIcons[type] || Document
}

function getTypeName(type: string) {
  return typeNames[type] || '未知'
}

function getPreview(content: string) {
  // 获取纯文本预览（前100个字符）
  const text = content.replace(/<[^>]*>/g, '')
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function handleAdd() {
  emit('add')
}

function handleEdit(section: ContentSection) {
  currentSection.value = section
  dialogVisible.value = true
  emit('edit', section)
}

async function handleDelete(section: ContentSection) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个分区吗？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    emit('delete', section)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

function handleDragEnd() {
  // 更新display_order
  props.sections.forEach((section, index) => {
    section.display_order = index
  })

  // 通知父组件更新
  emit('update:sections', [...props.sections])
}

function applyTemplate(template: any) {
  const newSection: ContentSection = {
    id: undefined,
    product_id: props.productId,
    section_type: template.type,
    title: template.name,
    content: template.content,
    display_order: props.sections.length
  }

  currentSection.value = newSection
  dialogVisible.value = true
}

function handleSave(section: ContentSection) {
  // 通知父组件保存
  emit('edit', section)
}
</script>

<style scoped>
.content-section-list {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.template-bar {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.template-bar span {
  margin-right: 12px;
  font-weight: bold;
}

.section-list {
  min-height: 200px;
}

.section-card {
  margin-bottom: 16px;
  transition: all 0.3s;
}

.section-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  color: #409eff;
}

.section-type {
  font-weight: bold;
  color: #303133;
}

.section-preview {
  margin-bottom: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 60px;
}

.content-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.section-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

/* 分区类型特定样式 */
.section-story { border-left: 4px solid #67c23a; }
.section-nutrition { border-left: 4px solid #e6a23c; }
.section-ingredients { border-left: 4px solid #f56c6c; }
.section-process { border-left: 4px solid #909399; }
.section-tips { border-left: 4px solid #409eff; }
</style>
```

#### 3. 创建分区表单组件
**文件**: `vue-admin/src/components/ContentSectionForm.vue`

```vue
<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑分区' : '创建分区'"
    width="800px"
    @close="handleClose"
  >
    <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="分区类型" prop="section_type">
        <el-select v-model="formData.section_type" placeholder="选择类型">
          <el-option label="故事" value="story" />
          <el-option label="营养" value="nutrition" />
          <el-option label="食材" value="ingredients" />
          <el-option label="工艺" value="process" />
          <el-option label="贴士" value="tips" />
        </el-select>
      </el-form-item>

      <el-form-item label="标题" prop="title">
        <el-input
          v-model="formData.title"
          placeholder="可选的标题"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="内容" prop="content">
        <QuillEditor
          v-model="formData.content"
          placeholder="请输入内容..."
        />
      </el-form-item>

      <el-form-item label="显示顺序">
        <el-input-number v-model="formData.display_order" :min="0" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import QuillEditor from './QuillEditor.vue'
import type { FormInstance } from 'element-plus'
import type { ContentSection } from '@/types'

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
const formData = ref<ContentSection>({
  id: undefined,
  product_id: 0,
  section_type: 'story',
  title: '',
  content: '',
  display_order: 0
})

const isEdit = computed(() => !!props.section?.id)

const rules = {
  section_type: [
    { required: true, message: '请选择分区类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' }
  ]
}

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

function resetForm() {
  formData.value = {
    id: undefined,
    product_id: 0,
    section_type: 'story',
    title: '',
    content: '',
    display_order: 0
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    emit('save', formData.value)
    handleClose()
  } catch (error) {
    ElMessage.error('表单验证失败')
  }
}

function handleClose() {
  visible.value = false
  formRef.value?.resetFields()
}
</script>
```

#### 4. 集成到商品详情页
在`ProductDetailContent.vue`中集成ContentSectionList组件

#### 5. 实现批量操作
添加全选、批量删除、批量启用/禁用功能

## 实施步骤

### 步骤1: 安装vuedraggable
```bash
cd vue-admin
npm install vuedraggable@next
```

### 步骤2: 创建ContentSectionList组件
拖拽排序、分区列表、模板应用

### 步骤3: 创建ContentSectionForm组件
分区编辑表单、集成QuillEditor

### 步骤4: 实现拖拽排序
使用vuedraggable实现，实时更新display_order

### 步骤5: 创建分区模板
5种分区的预设模板内容

### 步骤6: 集成到商品详情页
在ProductDetailContent中使用

### 步骤7: 测试
测试拖拽、排序、模板应用、批量操作

## 验收标准

| 验收标准 | 测试方法 |
|---------|---------|
| 可以创建5种类型的分区 | 测试所有类型 |
| 拖拽排序流畅无卡顿 | 拖动测试 |
| 模板一键应用成功 | 应用模板 |
| 批量操作功能正常 | 批量删除测试 |
| 与富文本编辑器集成正常 | 编辑测试 |

## 文件清单

**新建文件**:
- `vue-admin/src/components/ContentSectionList.vue`
- `vue-admin/src/components/ContentSectionForm.vue`

**修改文件**:
- `vue-admin/package.json` - 添加vuedraggable
- `vue-admin/src/views/components/ProductDetailContent.vue` - 集成列表

## 技术要点

### vuedraggable配置
- item-key: 'id'
- 动画: transition-group
- 事件处理: @end更新顺序

### 模板系统
- 5种预设模板
- 一键应用
- 可自定义

### 批量操作
- 全选/取消全选
- 批量删除
- 批量修改顺序

## 注意事项

1. **拖拽性能**: 使用虚拟滚动优化大量数据
2. **状态同步**: 拖拽后同步display_order到后端
3. **表单验证**: 必填字段校验
4. **UI反馈**: 拖拽时显示视觉提示
5. **数据一致性**: 确保前后端数据同步

## 与其他任务的集成

- **依赖ADMIN-001**: 使用QuillEditor组件
- **依赖API-001**: 调用后端CRUD API
