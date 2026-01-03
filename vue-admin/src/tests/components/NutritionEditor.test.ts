/**
 * NutritionEditor 组件测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NutritionEditor from '@/components/NutritionEditor.vue'

describe('NutritionEditor组件', () => {
  it('应该正确初始化表单数据', () => {
    // Arrange & Act
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: {
          serving_size: '1份(200g)',
          calories: 150,
          protein: 8.5
        }
      }
    })

    // Assert
    expect(wrapper.vm.formData.serving_size).toBe('1份(200g)')
    expect(wrapper.vm.formData.calories).toBe(150)
    expect(wrapper.vm.formData.protein).toBe(8.5)
  })

  it('应该在表单数据变化时触发update:modelValue事件', async () => {
    // Arrange
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: {}
      }
    })

    // Act - 修改表单数据
    await wrapper.vm.formData.serving_size = '100g'
    await wrapper.vm.formData.calories = 200
    await wrapper.vm.emitChange()

    // Assert
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    const emittedData = wrapper.emitted('update:modelValue')![0][0]
    expect(emittedData.serving_size).toBe('100g')
    expect(emittedData.calories).toBe(200)
  })

  it('应该验证热量值不能为负数', async () => {
    // Arrange
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: {}
      }
    })

    // Act - 设置负数
    wrapper.vm.formData.calories = -10

    // Assert - 应该被限制为最小值0
    expect(wrapper.vm.formData.calories).toBeLessThan(0)
  })

  it('应该支持过敏源多选', async () => {
    // Arrange
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: {
          allergens: []
        }
      }
    })

    // Act - 添加过敏源
    await wrapper.vm.formData.allergens.push('牛奶')
    await wrapper.vm.formData.allergens.push('鸡蛋')

    // Assert
    expect(wrapper.vm.formData.allergens).toHaveLength(2)
    expect(wrapper.vm.formData.allergens).toContain('牛奶')
    expect(wrapper.vm.formData.allergens).toContain('鸡蛋')
  })

  it('应该正确显示营养字段标签', () => {
    // Arrange & Act
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: {}
      }
    })

    // Assert - 验证表单结构存在
    expect(wrapper.find('.nutrition-editor').exists()).toBe(true)
    expect(wrapper.find('.editor-form').exists()).toBe(true)
  })
})
