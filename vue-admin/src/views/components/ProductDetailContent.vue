<template>
  <el-dialog
    v-model="visible"
    title="商品详情内容"
    width="900px"
    @close="handleClose"
  >
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 编辑模式 -->
      <el-tab-pane label="编辑内容" name="edit">
        <div class="content-sections">
          <div v-if="sections.length === 0" class="empty-state">
            <el-empty description="暂无内容分区，请点击下方按钮添加" />
          </div>

          <div v-for="(section, index) in sections" :key="section.id || index" class="section-card">
            <el-card>
              <template #header>
                <div class="section-header">
                  <span>分区 {{ index + 1 }}</span>
                  <div class="section-actions">
                    <el-button type="danger" size="small" @click="removeSection(index)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                </div>
              </template>

              <el-form :model="section" label-width="100px">
                <el-form-item label="分区类型" required>
                  <el-select v-model="section.section_type" placeholder="选择类型" style="width: 100%">
                    <el-option label="故事介绍" value="story" />
                    <el-option label="营养成分" value="nutrition" />
                    <el-option label="食材说明" value="ingredients" />
                    <el-option label="制作工艺" value="process" />
                    <el-option label="食用贴士" value="tips" />
                  </el-select>
                </el-form-item>

                <el-form-item label="标题" required>
                  <el-input v-model="section.title" placeholder="请输入标题" />
                </el-form-item>

                <el-form-item label="显示顺序">
                  <el-input-number v-model="section.display_order" :min="0" />
                </el-form-item>

                <el-form-item label="内容">
                  <QuillEditor
                    v-model="section.content"
                    :product-id="productId"
                    placeholder="请输入内容..."
                  />
                </el-form-item>
              </el-form>
            </el-card>
          </div>

          <div class="add-section-btn">
            <el-button type="primary" @click="addSection">
              <el-icon><Plus /></el-icon>
              添加内容分区
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- 预览模式 -->
      <el-tab-pane label="预览" name="preview">
        <div class="preview-container">
          <div v-if="sections.length === 0" class="empty-state">
            <el-empty description="暂无内容预览" />
          </div>
          <div v-for="(section, index) in sections" :key="index" class="section-preview">
            <div class="section-type-badge">{{ getSectionTypeName(section.section_type) }}</div>
            <h3>{{ section.title || '无标题' }}</h3>
            <ContentPreview :content="section.content" />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import QuillEditor from '../components/QuillEditor.vue'
import ContentPreview from '../components/ContentPreview.vue'
import {
  getProductContentSections,
  createContentSection,
  updateContentSection,
  deleteContentSection
} from '../api/product'

interface Props {
  modelValue: boolean
  productId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = ref(props.modelValue)
const activeTab = ref('edit')
const sections = ref<any[]>([])
const saving = ref(false)

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

// 添加新分区
const addSection = () => {
  sections.value.push({
    section_type: 'story',
    title: '',
    content: '',
    display_order: sections.value.length
  })
}

// 删除分区
const removeSection = async (index: number) => {
  const section = sections.value[index]
  if (section.id) {
    // 如果是已保存的分区，调用删除API
    try {
      await deleteContentSection(props.productId, section.id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败')
      return
    }
  }
  sections.value.splice(index, 1)
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

// 保存所有分区
const handleSave = async () => {
  // 验证
  for (const section of sections.value) {
    if (!section.section_type) {
      ElMessage.error('请选择分区类型')
      return
    }
    if (!section.title) {
      ElMessage.error('请输入标题')
      return
    }
  }

  saving.value = true
  try {
    // 逐个保存分区
    for (const section of sections.value) {
      if (section.id) {
        // 更新现有分区
        await updateContentSection(props.productId, section.id, {
          section_type: section.section_type,
          title: section.title,
          content: section.content,
          display_order: section.display_order
        })
      } else {
        // 创建新分区
        const result: any = await createContentSection(props.productId, {
          section_type: section.section_type,
          title: section.title,
          content: section.content,
          display_order: section.display_order
        })
        // 更新ID
        section.id = result.id
      }
    }

    ElMessage.success('保存成功')
    visible.value = false
  } catch (error) {
    console.error('Failed to save sections:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
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
.content-sections {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.section-card {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.section-actions {
  display: flex;
  gap: 10px;
}

.add-section-btn {
  margin-top: 20px;
  text-align: center;
}

.preview-container {
  padding: 20px;
  max-height: 600px;
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
}

.section-preview h3 {
  margin: 10px 0;
  color: #303133;
}

:deep(.el-card__header) {
  padding: 12px 20px;
  background-color: #f5f7fa;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}
</style>
