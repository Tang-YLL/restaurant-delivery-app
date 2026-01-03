/**
 * QuillEditor 组件测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import QuillEditor from '@/components/QuillEditor.vue'

// Mock vue-quill组件
vi.mock('@vueup/vue-quill', () => ({
  QuillEditor: {
    name: 'QuillEditor',
    template: '<div class="mock-quill"><slot /></div>',
    props: ['modelValue', 'contentType', 'toolbar', 'theme', 'placeholder', 'readonly']
  }
}))

describe('QuillEditor组件', () => {
  it('应该正确接收modelValue prop', () => {
    // Arrange
    const content = '<p>测试内容</p>'

    // Act
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: content
      }
    })

    // Assert
    expect(wrapper.props('modelValue')).toBe(content)
  })

  it('应该在内容更新时触发update:modelValue事件', async () => {
    // Arrange
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: ''
      }
    })

    const newContent = '<p>新内容</p>'

    // Act - 模拟内容更新
    await wrapper.vm.handleUpdate(newContent)

    // Assert
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([newContent])
  })

  it('应该正确计算内容字符数（不包含HTML标签）', () => {
    // Arrange
    const htmlContent = '<p>这是<b>加粗</b>内容</p>'

    // Act
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: htmlContent
      }
    })

    // Assert - "这是加粗内容" = 6个字符
    expect(wrapper.vm.contentLength).toBe(6)
  })

  it('应该使用默认placeholder', () => {
    // Arrange & Act
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: ''
      }
    })

    // Assert
    expect(wrapper.props('placeholder')).toBe('请输入内容...')
  })

  it('应该支持自定义placeholder', () => {
    // Arrange & Act
    const customPlaceholder = '请输入品牌故事...'
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: '',
        placeholder: customPlaceholder
      }
    })

    // Assert
    expect(wrapper.props('placeholder')).toBe(customPlaceholder)
  })

  it('应该支持readonly模式', () => {
    // Arrange & Act
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: '<p>内容</p>',
        readonly: true
      }
    })

    // Assert
    expect(wrapper.props('readonly')).toBe(true)
  })
})
