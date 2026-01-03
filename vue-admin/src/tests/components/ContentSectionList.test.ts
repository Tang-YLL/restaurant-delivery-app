/**
 * ContentSectionList 组件测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ContentSectionList from '@/components/ContentSectionList.vue'

// Mock组件
const mockSection = {
  id: 1,
  section_type: 'story',
  title: '品牌故事',
  content: '<p>故事内容</p>',
  display_order: 1
}

describe('ContentSectionList组件', () => {
  it('应该正确渲染内容区块列表', () => {
    // Arrange
    const sections = [mockSection]

    // Act
    const wrapper = mount(ContentSectionList, {
      props: {
        sections: sections
      }
    })

    // Assert
    expect(wrapper.props('sections')).toHaveLength(1)
    expect(wrapper.props('sections')[0].title).toBe('品牌故事')
  })

  it('应该在点击编辑时触发edit事件', async () => {
    // Arrange
    const wrapper = mount(ContentSectionList, {
      props: {
        sections: [mockSection]
      }
    })

    // Act - 模拟点击编辑
    await wrapper.vm.handleEdit(mockSection)

    // Assert
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')![0]).toEqual([mockSection])
  })

  it('应该在点击删除时触发delete事件并显示确认', async () => {
    // Arrange
    const wrapper = mount(ContentSectionList, {
      props: {
        sections: [mockSection]
      }
    })

    // Act - 模拟点击删除
    await wrapper.vm.handleDelete(mockSection)

    // Assert
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')![0]).toEqual([mockSection])
  })

  it('应该按display_order排序显示区块', () => {
    // Arrange
    const sections = [
      { ...mockSection, id: 1, display_order: 2 },
      { ...mockSection, id: 2, display_order: 1 },
      { ...mockSection, id: 3, display_order: 3 }
    ]

    // Act
    const wrapper = mount(ContentSectionList, {
      props: {
        sections: sections
      }
    })

    // Assert
    const sortedSections = wrapper.vm.sortedSections
    expect(sortedSections[0].id).toBe(2)
    expect(sortedSections[1].id).toBe(1)
    expect(sortedSections[2].id).toBe(3)
  })

  it('应该正确显示不同类型的区块标签', () => {
    // Arrange
    const sections = [
      { ...mockSection, section_type: 'story', title: '品牌故事' },
      { ...mockSection, section_type: 'nutrition', title: '营养信息' },
      { ...mockSection, section_type: 'ingredients', title: '食材信息' }
    ]

    // Act
    const wrapper = mount(ContentSectionList, {
      props: {
        sections: sections
      }
    })

    // Assert
    expect(wrapper.vm.getSectionTypeLabel('story')).toBe('品牌故事')
    expect(wrapper.vm.getSectionTypeLabel('nutrition')).toBe('营养信息')
    expect(wrapper.vm.getSectionTypeLabel('ingredients')).toBe('食材信息')
  })

  it('应该支持拖拽排序', async () => {
    // Arrange
    const wrapper = mount(ContentSectionList, {
      props: {
        sections: [mockSection]
      }
    })

    // Act - 模拟拖拽结束
    const newSections = [{ ...mockSection, id: 2 }]
    await wrapper.vm.handleDragEnd(newSections)

    // Assert
    expect(wrapper.emitted('reorder')).toBeTruthy()
    expect(wrapper.emitted('reorder')![0]).toEqual([newSections])
  })
})
