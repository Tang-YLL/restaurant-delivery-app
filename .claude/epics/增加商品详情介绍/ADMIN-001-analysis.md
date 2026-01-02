# ADMIN-001 任务分析

## 任务概述
在Vue3管理后台集成Quill.js富文本编辑器，实现商品详情内容的可视化编辑功能。

## 技术分析

### 技术栈
- **前端框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **富文本编辑器**: Quill.js（@vueup/vue-quill）
- **工作目录**: `vue-admin/`

### 功能需求

#### 1. 安装依赖
```bash
cd vue-admin
npm install @vueup/vue-quill quill
```

在`vue-admin/package.json`中添加：
```json
{
  "dependencies": {
    "@vueup/vue-quill": "^1.2.0",
    "quill": "^1.3.7"
  }
}
```

#### 2. 创建富文本编辑器组件
**文件**: `vue-admin/src/components/QuillEditor.vue`

```vue
<template>
  <div class="quill-editor-wrapper">
    <QuillEditor
      v-model:content="content"
      contentType="html"
      :modules="modules"
      :toolbar="toolbar"
      theme="snow"
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

interface Props {
  modelValue: string
  placeholder?: string
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入内容...',
  readonly: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'imageUpload': [file: File, callback: (url: string) => void]
}>()

const content = ref(props.modelValue)

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

function handleReady() {
  console.log('Quill editor ready')
}

// 自定义图片上传
async function handleImageUpload() {
  const input = document.createElement('input')
  input.setAttribute('type', 'file')
  input.setAttribute('accept', 'image/*')
  input.click()

  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return

    try {
      // 调用父组件的上传方法
      const url = await uploadImage(file)
      // 插入图片到编辑器
      const quill = (this as any).quill
      const range = quill.getSelection()
      quill.insertEmbed(range.index, 'image', url)
    } catch (error) {
      console.error('Image upload failed:', error)
      ElMessage.error('图片上传失败')
    }
  }
}

async function uploadImage(file: File): Promise<string> {
  // 调用后端API上传图片
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/v1/admin/products/1/details/images/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: formData
  })

  const result = await response.json()
  return result.data.url
}

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
}

:deep(.ql-toolbar) {
  border-radius: 4px 4px 0 0;
}

:deep(.ql-container) {
  border-radius: 0 0 4px 4px;
}
</style>
```

#### 3. 集成到商品详情页
**文件**: `vue-admin/src/views/ProductDetail.vue`

在商品编辑页面中添加富文本编辑器：

```vue
<template>
  <el-tabs v-model="activeTab">
    <el-tab-pane label="基本信息" name="basic">
      <!-- 现有的基本信息表单 -->
    </el-tab-pane>

    <el-tab-pane label="详情内容" name="details">
      <el-form :model="form" label-width="120px">
        <!-- 内容分区列表 -->
        <div v-for="(section, index) in form.contentSections" :key="section.id || index">
          <el-form-item :label="`分区 ${index + 1}`">
            <el-card>
              <el-select v-model="section.section_type" placeholder="选择类型">
                <el-option label="故事" value="story" />
                <el-option label="营养" value="nutrition" />
                <el-option label="食材" value="ingredients" />
                <el-option label="工艺" value="process" />
                <el-option label="贴士" value="tips" />
              </el-select>

              <el-input v-model="section.title" placeholder="标题" />

              <QuillEditor
                v-model="section.content"
                :placeholder="'请输入内容...'"
              />

              <el-button @click="removeSection(index)">删除</el-button>
            </el-card>
          </el-form-item>
        </div>

        <el-button @click="addSection">添加分区</el-button>
        <el-button type="primary" @click="saveDetails">保存</el-button>
      </el-form>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import QuillEditor from '@/components/QuillEditor.vue'
import { createContentSection, updateContentSection } from '@/api/product'

const activeTab = ref('details')

const form = ref({
  contentSections: []
})

function addSection() {
  form.value.contentSections.push({
    section_type: 'story',
    title: '',
    content: '',
    display_order: form.value.contentSections.length
  })
}

function removeSection(index: number) {
  form.value.contentSections.splice(index, 1)
}

async function saveDetails() {
  try {
    for (const section of form.value.contentSections) {
      if (section.id) {
        await updateContentSection(section.id, section)
      } else {
        await createContentSection(productId, section)
      }
    }
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}
</script>
```

#### 4. 实现图片上传功能
在QuillEditor组件中添加自定义图片上传handler，调用后端API：
- `POST /admin/products/{product_id}/details/images/upload`

#### 5. 添加预览功能
**文件**: `vue-admin/src/components/ContentPreview.vue`

```vue
<template>
  <div class="content-preview" v-html="content"></div>
</template>

<script setup lang="ts">
interface Props {
  content: string
}

defineProps<Props>()
</script>

<style scoped>
.content-preview {
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 200px;
}

.content-preview img {
  max-width: 100%;
  height: auto;
}

.content-preview h1, .content-preview h2, .content-preview h3 {
  margin-top: 1em;
  margin-bottom: 0.5em;
}
</style>
```

## 实施步骤

### 步骤1: 安装Quill.js
```bash
cd vue-admin
npm install @vueup/vue-quill quill
```

### 步骤2: 创建QuillEditor组件
创建`vue-admin/src/components/QuillEditor.vue`

### 步骤3: 配置工具栏
- 标题（H1-H6）
- 文本格式（加粗、斜体、下划线）
- 列表（有序、无序）
- 图片上传
- 链接
- 对齐方式
- 颜色和背景色

### 步骤4: 集成到商品详情页
在ProductDetail.vue中添加"详情内容"Tab

### 步骤5: 实现图片上传
自定义图片handler，调用后端API上传

### 步骤6: 添加预览功能
创建ContentPreview组件显示渲染效果

### 步骤7: 测试
- 测试所有格式化选项
- 测试图片上传
- 测试内容保存和加载
- 测试移动端预览

## 验收标准

| 验收标准 | 测试方法 |
|---------|---------|
| 编辑器正常显示和工作 | 打开编辑页面 |
| 支持10种以上格式化选项 | 测试工具栏所有按钮 |
| 图片上传成功显示在编辑器中 | 上传测试图片 |
| 预览功能正常 | 切换到预览模式 |
| 内容正确保存到数据库 | 保存后刷新页面 |

## 文件清单

**新建文件**:
- `vue-admin/src/components/QuillEditor.vue`
- `vue-admin/src/components/ContentPreview.vue`

**修改文件**:
- `vue-admin/package.json` - 添加依赖
- `vue-admin/src/views/ProductDetail.vue` - 添加详情内容Tab
- `vue-admin/src/api/product.ts` - 添加API方法（如果需要）

## 技术要点

### Quill.js配置
- **主题**: snow（白色简洁主题）
- **contentType**: html（返回HTML字符串）
- **modules**: 自定义工具栏和图片handler

### 图片上传流程
1. 用户点击图片按钮
2. 创建文件选择input
3. 选择文件后调用后端API
4. 上传成功获取URL
5. 插入图片到编辑器

### v-model绑定
使用Vue 3的v-model实现双向绑定
父组件传递modelValue，编辑器触发update:modelValue事件

## 注意事项

1. **CSS导入**: 确保导入Quill的CSS文件
2. **TypeScript支持**: 使用@vueup/vue-quill的TypeScript定义
3. **图片base64**: 不要使用base64存储图片，应该上传到服务器
4. **XSS防护**: 后端已过滤HTML，前端可以显示
5. **移动端预览**: 使用iframe或移动设备模拟器

## 与其他任务的集成

- **依赖API-001**: 调用后端CRUD API保存内容
- **依赖API-002**: 调用后端图片上传API
- **为ADMIN-002准备**: 提供富文本编辑组件供分区管理使用
