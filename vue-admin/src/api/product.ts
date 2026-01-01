import request from '../utils/request'
import type { Product, ProductForm, ProductQuery, PageResponse } from '../types'

// 获取商品列表
export const getProductList = (params: ProductQuery) => {
  return request.get<any, PageResponse<Product>>('/admin/products', { params })
}

// 获取商品详情
export const getProductDetail = (id: number) => {
  return request.get<any, Product>(`/products/${id}`)
}

// 创建商品
export const createProduct = async (data: ProductForm) => {
  // 获取分类列表以找到category_id
  const categories = await request.get<any, Array<{ id: number; name: string; code: string }>>('/categories')
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
  // 获取分类列表以找到category_id
  const categories = await request.get<any, Array<{ id: number; name: string; code: string }>>('/categories')
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

// 获取商品分类
export const getCategories = () => {
  return request.get<any, Array<{ id: number; name: string; code: string }>>('/categories')
}

// 更新商品库存
export const updateStock = (id: number, stock: number) => {
  return request.patch(`/admin/products/${id}/stock`, { stock })
}
