import request from '../utils/request'
import type { Product, ProductForm, ProductQuery, PageResponse, Nutrition, NutritionFormData } from '../types'

// 分类缓存
let categoriesCache: Array<{ id: number; name: string; code: string }> | null = null

// 获取分类列表（带缓存）
const getCategoriesWithCache = async () => {
  if (categoriesCache) {
    return categoriesCache
  }

  categoriesCache = await request.get<any, Array<{ id: number; name: string; code: string }>>('/categories')
  return categoriesCache
}

// 清除分类缓存（用于添加/删除分类后）
export const clearCategoriesCache = () => {
  categoriesCache = null
}

// 获取商品列表
export const getProductList = async (params: ProductQuery) => {
  // 如果有category参数，需要转换为category_id
  const requestParams: any = {
    page: params.page,
    pageSize: params.pageSize,
    keyword: params.keyword,
  }

  // 处理status参数
  if (params.status !== undefined && params.status !== null && params.status !== '') {
    requestParams.is_active = params.status === 'active'
  }

  // 处理category参数（如果有值才请求分类列表）
  if (params.category && params.category !== '') {
    try {
      const categories = await getCategoriesWithCache()
      const category = categories.find((cat: any) => cat.name === params.category)
      if (category) {
        requestParams.category_id = category.id
      }
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  }

  return request.get<any, PageResponse<Product>>('/admin/products', { params: requestParams })
}

// 获取商品详情
export const getProductDetail = (id: number) => {
  return request.get<any, Product>(`/products/${id}`)
}

// 创建商品
export const createProduct = async (data: ProductForm) => {
  // 获取分类列表以找到category_id（使用缓存）
  const categories = await getCategoriesWithCache()
  const category = categories.find((cat: any) => cat.name === data.category)

  if (!category) {
    throw new Error('分类不存在')
  }

  // 字段映射：前端字段 -> 后端字段
  const payload = {
    title: data.name,
    description: data.description,
    price: data.price,
    stock: data.stock,
    category_id: category.id,
    local_image_path: data.image || '/images/default.png',
    image_url: data.image || '/images/default.png',
    is_active: data.status === 'active'
  }
  return request.post('/admin/products', payload)
}

// 更新商品
export const updateProduct = async (id: number, data: ProductForm) => {
  // 获取分类列表以找到category_id（使用缓存）
  const categories = await getCategoriesWithCache()
  const category = categories.find((cat: any) => cat.name === data.category)

  if (!category) {
    throw new Error('分类不存在')
  }

  // 字段映射：前端字段 -> 后端字段
  // 只传递非空字段，避免覆盖已有数据
  const payload: any = {}

  if (data.name) payload.title = data.name
  if (data.description !== undefined && data.description !== null) payload.description = data.description
  if (data.price !== undefined && data.price !== null) payload.price = data.price
  if (data.stock !== undefined && data.stock !== null) payload.stock = data.stock
  if (data.category) payload.category_id = category.id
  if (data.image) {
    payload.local_image_path = data.image
    payload.image_url = data.image
  }
  if (data.status) payload.is_active = data.status === 'active'

  return request.put(`/admin/products/${id}`, payload)
}

// 删除商品
export const deleteProduct = (id: number) => {
  return request.delete(`/admin/products/${id}`)
}

// 获取商品分类（使用缓存）
export const getCategories = () => {
  return getCategoriesWithCache()
}

// 更新商品库存
// 参数 adjustment 是库存调整量（正数增加，负数减少）
export const updateStock = (id: number, adjustment: number) => {
  return request.patch(`/admin/products/${id}/stock`, { stock_adjustment: adjustment })
}

// 获取商品营养成分
export const getProductNutrition = (id: number) => {
  return request.get<any, Nutrition>(`/admin/products/${id}/details/nutrition`)
}

// 保存商品营养成分
export const saveProductNutrition = (id: number, data: NutritionFormData) => {
  // 清理null值和undefined值
  const payload: any = {
    serving_size: data.serving_size || '',
    calories: data.calories ?? 0,
    protein: data.protein ?? 0,
    fat: data.fat ?? 0,
    carbohydrates: data.carbohydrates ?? 0,
    sodium: data.sodium ?? 0,
    allergens: data.allergens || []
  }

  // 可选字段，只有有值时才添加
  if (data.dietary_fiber !== null && data.dietary_fiber !== undefined) {
    payload.dietary_fiber = data.dietary_fiber
  }
  if (data.sugar !== null && data.sugar !== undefined) {
    payload.sugar = data.sugar
  }

  return request.put(`/admin/products/${id}/details/nutrition`, payload)
}

// ========== 商品详情内容相关 API ==========

// 获取商品详情的所有内容分区
export const getProductContentSections = (productId: number) => {
  return request.get(`/admin/products/${productId}/details`)
}

// 创建内容分区
export const createContentSection = (productId: number, data: any) => {
  return request.post(`/admin/products/${productId}/details/sections`, data)
}

// 更新内容分区
export const updateContentSection = (productId: number, sectionId: number, data: any) => {
  return request.put(`/admin/products/${productId}/details/sections/${sectionId}`, data)
}

// 删除内容分区
export const deleteContentSection = (productId: number, sectionId: number) => {
  return request.delete(`/admin/products/${productId}/details/sections/${sectionId}`)
}

// 批量更新内容分区
export const batchUpdateContentSections = (productId: number, sections: any[]) => {
  return request.put(`/admin/products/${productId}/details/sections/batch`, { sections })
}

// 上传商品详情图片
export const uploadProductDetailImage = (productId: number, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/admin/products/${productId}/details/images/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
