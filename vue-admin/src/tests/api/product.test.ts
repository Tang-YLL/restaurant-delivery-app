/**
 * 商品API测试
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import {
  getProductDetails,
  createContentSection,
  updateContentSection,
  deleteContentSection,
  updateNutritionFacts
} from '@/api/product'

// Mock axios
vi.mock('axios')

describe('商品详情API', () => {
  beforeEach(() => {
    // 清除所有mock
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getProductDetails', () => {
    it('应该成功获取商品完整详情', async () => {
      // Arrange
      const mockProductDetails = {
        product_id: 1,
        content_sections: [
          {
            id: 1,
            section_type: 'story',
            title: '品牌故事',
            content: '<p>故事内容</p>'
          }
        ],
        nutrition_facts: {
          id: 1,
          calories: 150,
          protein: 8.5
        }
      }

      vi.mocked(axios.get).mockResolvedValue({
        data: mockProductDetails
      })

      // Act
      const result = await getProductDetails(1)

      // Assert
      expect(axios.get).toHaveBeenCalledWith('/api/v1/products/1/full-details')
      expect(result).toEqual(mockProductDetails)
    })

    it('应该处理API错误', async () => {
      // Arrange
      const mockError = new Error('Network Error')
      vi.mocked(axios.get).mockRejectedValue(mockError)

      // Act & Assert
      await expect(getProductDetails(1)).rejects.toThrow('Network Error')
    })
  })

  describe('createContentSection', () => {
    it('应该成功创建内容区块', async () => {
      // Arrange
      const newSection = {
        section_type: 'story',
        title: '品牌故事',
        content: '<p>内容</p>',
        display_order: 1
      }

      const mockResponse = {
        id: 1,
        ...newSection
      }

      vi.mocked(axios.post).mockResolvedValue({
        data: mockResponse
      })

      // Act
      const result = await createContentSection(1, newSection)

      // Assert
      expect(axios.post).toHaveBeenCalledWith(
        '/api/v1/admin/products/1/detail-sections',
        newSection
      )
      expect(result).toEqual(mockResponse)
    })

    it('应该处理创建失败的情况', async () => {
      // Arrange
      const newSection = {
        section_type: 'story',
        content: '<p>内容</p>'
      }

      vi.mocked(axios.post).mockRejectedValue({
        response: {
          status: 400,
          data: { message: '无效的section_type' }
        }
      })

      // Act & Assert
      await expect(createContentSection(1, newSection)).rejects.toThrow()
    })
  })

  describe('updateContentSection', () => {
    it('应该成功更新内容区块', async () => {
      // Arrange
      const updateData = {
        title: '更新的标题',
        content: '<p>更新的内容</p>'
      }

      const mockResponse = {
        id: 1,
        section_type: 'story',
        ...updateData
      }

      vi.mocked(axios.put).mockResolvedValue({
        data: mockResponse
      })

      // Act
      const result = await updateContentSection(1, updateData)

      // Assert
      expect(axios.put).toHaveBeenCalledWith(
        '/api/v1/admin/products/detail-sections/1',
        updateData
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('deleteContentSection', () => {
    it('应该成功删除内容区块', async () => {
      // Arrange
      vi.mocked(axios.delete).mockResolvedValue({
        data: { message: '删除成功' }
      })

      // Act
      const result = await deleteContentSection(1)

      // Assert
      expect(axios.delete).toHaveBeenCalledWith(
        '/api/v1/admin/products/detail-sections/1'
      )
      expect(result).toEqual({ message: '删除成功' })
    })
  })

  describe('updateNutritionFacts', () => {
    it('应该成功更新营养数据', async () => {
      // Arrange
      const nutritionData = {
        serving_size: '1份(200g)',
        calories: 150,
        protein: 8.5,
        fat: 5.2
      }

      const mockResponse = {
        id: 1,
        product_id: 1,
        ...nutritionData
      }

      vi.mocked(axios.put).mockResolvedValue({
        data: mockResponse
      })

      // Act
      const result = await updateNutritionFacts(1, nutritionData)

      // Assert
      expect(axios.put).toHaveBeenCalledWith(
        '/api/v1/admin/products/1/nutrition',
        nutritionData
      )
      expect(result).toEqual(mockResponse)
    })

    it('应该处理营养数据验证失败', async () => {
      // Arrange
      const invalidData = {
        calories: -100  // 负数
      }

      vi.mocked(axios.put).mockRejectedValue({
        response: {
          status: 422,
          data: { message: '热量值不能为负数' }
        }
      })

      // Act & Assert
      await expect(updateNutritionFacts(1, invalidData)).rejects.toThrow()
    })
  })

  describe('批量操作API', () => {
    it('应该支持批量上传内容区块图片', async () => {
      // Arrange
      const files = [
        new File([''], 'image1.jpg'),
        new File([''], 'image2.jpg')
      ]

      const mockResponse = {
        uploaded: [
          { url: '/images/products/img1.jpg' },
          { url: '/images/products/img2.jpg' }
        ]
      }

      vi.mocked(axios.post).mockResolvedValue({
        data: mockResponse
      })

      const formData = new FormData()
      files.forEach(file => formData.append('images', file))

      // Act
      const result = await axios.post('/api/v1/admin/products/upload-detail-images', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      // Assert
      expect(axios.post).toHaveBeenCalled()
      expect(result.data.uploaded).toHaveLength(2)
    })
  })
})
