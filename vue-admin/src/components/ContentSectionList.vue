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
      v-model="localSections"
      item-key="id"
      class="section-list"
      :class="{ 'is-dragging': isDragging }"
      @start="isDragging = true"
      @end="handleDragEnd"
    >
      <template #item="{ element: section, index }">
        <el-card
          class="section-card"
          :class="`section-${section.section_type}`"
          :data-index="index"
        >
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
const isDragging = ref(false)

// 本地排序副本
const localSections = computed({
  get: () => props.sections,
  set: (value) => {
    emit('update:sections', value)
  }
})

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
  {
    type: 'story',
    name: '菜品故事',
    content: '<h3>菜品故事</h3><p>这是一个关于菜品的精彩故事...</p>'
  },
  {
    type: 'nutrition',
    name: '营养成分',
    content: '<h3>营养价值</h3><ul><li>蛋白质含量丰富</li><li>低脂肪健康之选</li><li>富含维生素和矿物质</li></ul>'
  },
  {
    type: 'ingredients',
    name: '食材来源',
    content: '<h3>主要食材</h3><p>我们精选优质食材，确保每一道菜品的新鲜与美味。</p><ul><li>主料：新鲜采购</li><li>辅料：严格筛选</li></ul>'
  },
  {
    type: 'process',
    name: '制作工艺',
    content: '<h3>制作步骤</h3><ol><li>精心准备食材</li><li>按照传统工艺烹饪</li><li>严格控制火候和时间</li></ol>'
  },
  {
    type: 'tips',
    name: '食用贴士',
    content: '<h3>食用建议</h3><p>建议趁热食用，口感更佳。可搭配饮品一起享用。</p>'
  }
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
  currentSection.value = null
  dialogVisible.value = true
  emit('add')
}

function handleEdit(section: ContentSection) {
  currentSection.value = { ...section }
  dialogVisible.value = true
  emit('edit', section)
}

async function handleDelete(section: ContentSection) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个分区吗？此操作不可恢复。',
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
  isDragging.value = false

  // 更新display_order
  const updatedSections = localSections.value.map((section, index) => ({
    ...section,
    display_order: index
  }))

  // 通知父组件更新
  emit('update:sections', updatedSections)
  ElMessage.success('排序已更新')
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
  dialogVisible.value = false
  ElMessage.success('保存成功')
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

.section-list.is-dragging .section-card {
  cursor: move;
}

.section-card {
  margin-bottom: 16px;
  transition: all 0.3s;
  cursor: grab;
}

.section-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.section-card:active {
  cursor: grabbing;
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
.section-story {
  border-left: 4px solid #67c23a;
}

.section-nutrition {
  border-left: 4px solid #e6a23c;
}

.section-ingredients {
  border-left: 4px solid #f56c6c;
}

.section-process {
  border-left: 4px solid #909399;
}

.section-tips {
  border-left: 4px solid #409eff;
}

/* 拖拽时的动画效果 */
.sortable-ghost {
  opacity: 0.5;
  background: #f0f9ff;
}

.sortable-drag {
  opacity: 1;
  transform: rotate(3deg);
}
</style>
