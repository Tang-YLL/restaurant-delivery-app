<template>
  <el-dialog
    v-model="visible"
    title="商品详情内容管理"
    width="90%"
    :style="{ maxWidth: '1400px' }"
    @close="handleClose"
    :close-on-click-modal="false"
    draggable
  >
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 列表管理模式 -->
      <el-tab-pane label="分区管理" name="list">
        <ContentSectionList
          :product-id="productId"
          :sections="sections"
          @update:sections="handleSectionsUpdate"
          @add="handleAddSection"
          @edit="handleEditSection"
          @delete="handleDeleteSection"
        />
      </el-tab-pane>

      <!-- 预览模式 -->
      <el-tab-pane label="预览" name="preview">
        <div class="preview-container">
          <div v-if="sections.length === 0" class="empty-state">
            <el-empty description="暂无内容预览" />
          </div>
          <div v-for="(section, index) in sortedSections" :key="section.id || index" class="section-preview">
            <div class="section-type-badge" :class="`type-${section.section_type}`">
              {{ getSectionTypeName(section.section_type) }}
            </div>
            <h3>{{ section.title || '无标题' }}</h3>
            <ContentPreview :content="section.content" />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import ContentSectionList from '@/components/ContentSectionList.vue'
import ContentPreview from '@/components/ContentPreview.vue'
import {
  getProductContentSections,
  createContentSection,
  updateContentSection,
  deleteContentSection
} from '@/api/product'
import type { ContentSection } from '@/types'

interface Props {
  modelValue: boolean
  productId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'refresh': []
}>()

const visible = ref(props.modelValue)
const activeTab = ref('list')
const sections = ref<ContentSection[]>([])
const saving = ref(false)

// 排序后的分区列表
const sortedSections = computed(() => {
  return [...sections.value].sort((a, b) => a.display_order - b.display_order)
})

// 分区类型名称映射
const getSectionTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    story: '故事介绍',
    nutrition: '营养成分',
    ingredients: '食材说明',
    process: '制作工艺',
    tips: '食用贴士'
  }
  return typeMap[type] || type
}

// 加载内容分区
const loadSections = async () => {
  try {
    const data: any = await getProductContentSections(props.productId)
    sections.value = data.sections || []
  } catch (error) {
    console.error('Failed to load content sections:', error)
    ElMessage.error('加载内容分区失败')
  }
}

// 处理分区更新（拖拽排序）
const handleSectionsUpdate = async (updatedSections: ContentSection[]) => {
  sections.value = updatedSections

  // 批量更新display_order
  try {
    for (const section of updatedSections) {
      if (section.id) {
        await updateContentSection(props.productId, section.id, {
          section_type: section.section_type,
          title: section.title || '',
          content: section.content,
          display_order: section.display_order
        })
      }
    }
    ElMessage.success('排序已更新')
  } catch (error) {
    console.error('Failed to update sections order:', error)
    ElMessage.error('更新排序失败')
  }
}

// 添加新分区（由ContentSectionForm中的save事件触发）
const handleAddSection = async () => {
  // 这个方法实际上不需要做什么，因为表单会通过handleEditSection来处理
  // ContentSectionList会自己管理对话框的显示
}

// 编辑分区
const handleEditSection = async (section: ContentSection) => {
  try {
    if (section.id) {
      // 更新现有分区
      await updateContentSection(props.productId, section.id, {
        section_type: section.section_type,
        title: section.title || '',
        content: section.content,
        display_order: section.display_order
      })

      // 更新本地数据
      const index = sections.value.findIndex(s => s.id === section.id)
      if (index !== -1) {
        sections.value[index] = { ...section }
      }

      ElMessage.success('更新成功')
    } else {
      // 创建新分区
      const result: any = await createContentSection(props.productId, {
        section_type: section.section_type,
        title: section.title || '',
        content: section.content,
        display_order: section.display_order
      })

      // 更新ID并添加到列表
      section.id = result.id
      section.product_id = props.productId
      sections.value.push({ ...section })

      ElMessage.success('创建成功')
    }

    // 通知父组件刷新
    emit('refresh')
  } catch (error) {
    console.error('Failed to save section:', error)
    ElMessage.error('保存失败')
  }
}

// 删除分区
const handleDeleteSection = async (section: ContentSection) => {
  if (!section.id) {
    // 如果是新创建的分区（没有ID），直接从本地移除
    const index = sections.value.findIndex(s => s === section)
    if (index !== -1) {
      sections.value.splice(index, 1)
    }
    return
  }

  try {
    await deleteContentSection(props.productId, section.id)

    // 从本地移除
    const index = sections.value.findIndex(s => s.id === section.id)
    if (index !== -1) {
      sections.value.splice(index, 1)
    }

    ElMessage.success('删除成功')
    emit('refresh')
  } catch (error) {
    console.error('Failed to delete section:', error)
    ElMessage.error('删除失败')
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 监听visible变化
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
  if (newValue && props.productId > 0) {
    loadSections()
  }
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>

<style scoped>
/* 确保对话框主体有最大高度并可滚动 */
:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.preview-container {
  padding: 20px;
  max-height: 650px;
  overflow-y: auto;
}

.section-preview {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.section-preview:last-child {
  border-bottom: none;
}

.section-type-badge {
  display: inline-block;
  padding: 4px 12px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 10px;
  font-weight: 500;
}

/* 分区类型特定样式 */
.section-type-badge.type-story {
  background-color: #f0f9ff;
  color: #67c23a;
}

.section-type-badge.type-nutrition {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.section-type-badge.type-ingredients {
  background-color: #fef0f0;
  color: #f56c6c;
}

.section-type-badge.type-process {
  background-color: #f4f4f5;
  color: #909399;
}

.section-type-badge.type-tips {
  background-color: #ecf5ff;
  color: #409eff;
}

.section-preview h3 {
  margin: 10px 0;
  color: #303133;
  font-size: 18px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
