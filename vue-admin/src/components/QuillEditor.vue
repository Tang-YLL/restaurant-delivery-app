<template>
  <div class="quill-editor-wrapper">
    <QuillEditorBase
      v-model:content="content"
      contentType="html"
      :toolbar="toolbarOptions"
      theme="snow"
      :placeholder="placeholder"
      :readonly="readonly"
      @update:content="handleUpdate"
      @ready="handleReady"
    />

    <!-- 图片上传按钮 -->
    <div class="toolbar-actions">
      <el-button
        type="primary"
        size="small"
        @click="showUploadDialog = true"
        :disabled="!productId"
      >
        <el-icon><Picture /></el-icon>
        上传图片
      </el-button>
    </div>

    <div class="char-count">{{ contentLength }} 字符</div>

    <!-- 图片上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传图片"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept="image/jpeg,image/png,image/jpg"
        ref="uploadRef"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽图片到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只支持 JPG/PNG 格式，文件大小不超过 5MB
          </div>
        </template>
      </el-upload>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpload" :loading="uploading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { QuillEditor as QuillEditorBase } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { ElMessage } from 'element-plus'
import { Picture, UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import request from '@/utils/request'

interface Props {
  modelValue: string
  placeholder?: string
  readonly?: boolean
  productId?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入内容...',
  readonly: false,
  productId: 0
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const content = ref(props.modelValue)
const quillInstance = ref<any>(null)
const showUploadDialog = ref(false)
const uploading = ref(false)
const selectedFile = ref<File | null>(null)
const uploadRef = ref<UploadInstance>()

const contentLength = computed(() => {
  return content.value.replace(/<[^>]*>/g, '').length
})

// 工具栏配置（简化版，避免register错误）
const toolbarOptions = [
  ['bold', 'italic', 'underline', 'strike'],
  ['blockquote', 'code-block'],
  [{ 'header': 1 }, { 'header': 2 }],
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],
  [{ 'indent': '-1'}, { 'indent': '+1' }],
  [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
  [{ 'color': [] }, { 'background': [] }],
  [{ 'align': [] }],
  ['link', 'image'],
  ['clean']
]

function handleUpdate(value: string) {
  content.value = value
  emit('update:modelValue', value)
}

function handleReady(quill: any) {
  quillInstance.value = quill
  console.log('Quill editor ready')
}

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== content.value) {
    content.value = newValue
  }
})

// 图片上传相关函数
function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要上传的图片')
    return
  }

  if (!props.productId) {
    ElMessage.error('缺少商品ID，无法上传')
    return
  }

  try {
    uploading.value = true

    // 创建FormData
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    // 上传到后端（使用配置好的request实例）
    const response = await request.post<{
      success: boolean
      message: string
      data: {
        url: string
        filename: string
        size: number
        original_size: number
        compression_ratio: string
      }
    }>(
      `/admin/products/${props.productId}/details/images/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    if (response.success && response.data?.url) {
      const imageUrl = response.data.url

      // 构建完整URL（移除 /api 部分，因为图片是静态文件）
      const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
      const baseURL = apiBaseURL.replace('/api', '')
      const fullUrl = `${baseURL}${imageUrl}`

      console.log('图片URL:', {
        imageUrl,
        apiBaseURL,
        baseURL,
        fullUrl
      })

      // 将图片插入到编辑器中
      if (quillInstance.value) {
        const quill = quillInstance.value
        const range = quill.getSelection() || quill.getLength()
        quill.insertEmbed(range, 'image', fullUrl)
      }

      ElMessage.success('图片上传成功')
      showUploadDialog.value = false
      selectedFile.value = null
      uploadRef.value?.clearFiles()
    } else {
      throw new Error('上传失败')
    }
  } catch (error: any) {
    console.error('Upload error:', error)
    // request拦截器已经处理了错误提示，这里不需要额外提示
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.quill-editor-wrapper {
  position: relative;
}

.toolbar-actions {
  margin: 10px 0;
  display: flex;
  gap: 8px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

:deep(.ql-editor) {
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
}

:deep(.ql-toolbar) {
  border-radius: 4px 4px 0 0;
  border-color: #dcdfe6;
}

:deep(.ql-container) {
  border-radius: 0 0 4px 4px;
  border-color: #dcdfe6;
  font-size: 14px;
}

:deep(.ql-editor.ql-blank::before) {
  color: #c0c4cc;
  font-style: normal;
}

/* 上传组件样式 */
.upload-demo {
  margin: 20px 0;
}

:deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px;
}

:deep(.el-icon--upload) {
  font-size: 48px;
  color: #409eff;
}

.el-upload__tip {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
  text-align: center;
}
</style>
