<template>
  <div class="quill-editor-wrapper">
    <QuillEditor
      v-model:content="content"
      contentType="html"
      :modules="modules"
      :toolbar="toolbar"
      theme="snow"
      :placeholder="placeholder"
      :readonly="readonly"
      @update:content="handleUpdate"
      @ready="handleReady"
    />
    <div class="char-count">{{ contentLength }} 字符</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { ElMessage } from 'element-plus'

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

const contentLength = computed(() => {
  return content.value.replace(/<[^>]*>/g, '').length
})

// 工具栏配置
const toolbar = [
  ['bold', 'italic', 'underline', 'strike'],
  ['blockquote', 'code-block'],
  [{ 'header': 1 }, { 'header': 2 }],
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],
  [{ 'indent': '-1'}, { 'indent': '+1' }],
  [{ 'direction': 'rtl' }],
  [{ 'size': ['small', false, 'large', 'huge'] }],
  [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
  [{ 'color': [] }, { 'background': [] }],
  [{ 'align': [] }],
  ['link', 'image'],
  ['clean']
]

// 自定义图片上传handler
const handleImageUpload = async () => {
  const input = document.createElement('input')
  input.setAttribute('type', 'file')
  input.setAttribute('accept', 'image/*')
  input.click()

  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return

    // 验证文件大小（5MB）
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过5MB')
      return
    }

    // 验证文件类型
    if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
      ElMessage.error('只支持JPG和PNG格式')
      return
    }

    try {
      // 显示上传进度
      const loading = ElMessage({
        message: '图片上传中...',
        type: 'info',
        duration: 0
      })

      // 调用上传API
      const url = await uploadImage(file)

      // 关闭loading
      loading.close()

      // 插入图片到编辑器
      if (quillInstance.value) {
        const range = quillInstance.value.getSelection()
        quillInstance.value.insertEmbed(range.index, 'image', url)
      }

      ElMessage.success('图片上传成功')
    } catch (error) {
      console.error('Image upload failed:', error)
      ElMessage.error('图片上传失败')
    }
  }
}

// 上传图片到后端
async function uploadImage(file: File): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)

  // 获取token
  const token = localStorage.getItem('token')

  const response = await fetch(
    `${import.meta.env.VITE_API_BASE_URL || ''}/api/v1/admin/products/${props.productId}/details/images/upload`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  )

  if (!response.ok) {
    throw new Error('Upload failed')
  }

  const result = await response.json()
  return result.data.url
}

// 模块配置
const modules = {
  toolbar: {
    container: toolbar,
    handlers: {
      image: handleImageUpload
    }
  }
}

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
</script>

<style scoped>
.quill-editor-wrapper {
  position: relative;
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
</style>
