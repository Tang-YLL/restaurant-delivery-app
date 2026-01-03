<template>
  <div class="content-preview">
    <div v-if="!content" class="empty-placeholder">
      暂无内容预览
    </div>
    <div v-else v-html="sanitizedContent" class="preview-content"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  content: string
}

const props = defineProps<Props>()

// 简单的HTML清理（基本XSS防护）
const sanitizedContent = computed(() => {
  if (!props.content) return ''

  // 只移除script标签，其他HTML保留
  let html = props.content

  // 移除script标签及其内容
  html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')

  // 移除危险的属性
  html = html.replace(/on\w+="[^"]*"/gi, '')
  html = html.replace(/on\w+='[^']*'/gi, '')
  html = html.replace(/javascript:/gi, '')

  return html
})
</script>

<style scoped>
.content-preview {
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 200px;
  background-color: #ffffff;
}

.empty-placeholder {
  color: #909399;
  text-align: center;
  padding: 60px 0;
  font-size: 14px;
}

.preview-content {
  line-height: 1.6;
  color: #303133;
  font-size: 14px;
}

/* 标题样式 */
.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3),
.preview-content :deep(h4),
.preview-content :deep(h5),
.preview-content :deep(h6) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: bold;
  line-height: 1.4;
}

.preview-content :deep(h1) {
  font-size: 2em;
  border-bottom: 2px solid #e4e7ed;
  padding-bottom: 0.3em;
}

.preview-content :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 0.3em;
}

.preview-content :deep(h3) {
  font-size: 1.25em;
}

/* 段落样式 */
.preview-content :deep(p) {
  margin: 0.5em 0;
}

/* 列表样式 */
.preview-content :deep(ul),
.preview-content :deep(ol) {
  padding-left: 2em;
  margin: 0.5em 0;
}

.preview-content :deep(li) {
  margin: 0.25em 0;
}

/* 引用样式 */
.preview-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 1em;
  margin: 1em 0;
  color: #606266;
  background-color: #f4f4f5;
  padding: 0.5em 1em;
}

/* 代码块样式 */
.preview-content :deep(pre) {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 1em;
  overflow-x: auto;
  margin: 1em 0;
}

.preview-content :deep(code) {
  background-color: #f5f7fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.preview-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

/* 图片样式 */
.preview-content :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1em auto;
  border-radius: 4px;
}

/* 链接样式 */
.preview-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

/* 表格样式 */
.preview-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.preview-content :deep(table th),
.preview-content :deep(table td) {
  border: 1px solid #dcdfe6;
  padding: 0.5em;
  text-align: left;
}

.preview-content :deep(table th) {
  background-color: #f5f7fa;
  font-weight: bold;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .content-preview {
    padding: 15px;
  }

  .preview-content {
    font-size: 13px;
  }

  .preview-content :deep(img) {
    max-width: 100%;
  }

  .preview-content :deep(h1) {
    font-size: 1.5em;
  }

  .preview-content :deep(h2) {
    font-size: 1.25em;
  }
}
</style>
