import request from '../utils/request'
import type { Product, ProductForm, ProductQuery, PageResponse } from '../types'

// 获取商品列表
export const getProductList = (params: ProductQuery) => {
  return request.get<any, PageResponse<Product>>('/products', { params })
}

// 获取商品详情
export const getProductDetail = (id: number) => {
  return request.get<any, Product>(`/products/${id}`)
}

// 创建商品
export const createProduct = (data: ProductForm) => {
  // 字段映射：前端字段 -> 后端字段
  const payload = {
    title: data.name,
    description: data.description,
    price: data.price,
    stock: data.stock,
    category_id: parseInt(data.category),
    local_image_path: data.image || '/images/default.png',
    status: data.status === 'active' ? 'ACTIVE' : 'INACTIVE',
    is_active: true
  }
  return request.post('/admin/products', payload)
}

// 更新商品
export const updateProduct = (id: number, data: ProductForm) => {
  // 字段映射：前端字段 -> 后端字段
  const payload = {
    title: data.name,
    description: data.description,
    price: data.price,
    stock: data.stock,
    category_id: parseInt(data.category),
    local_image_path: data.image || '/images/default.png',
    status: data.status === 'active' ? 'ACTIVE' : 'INACTIVE',
    is_active: true
  }
  return request.put(`/admin/products/${id}`, payload)
}

// 删除商品
export const deleteProduct = (id: number) => {
  return request.delete(`/admin/products/${id}`)
}

// 获取商品分类
export const getCategories = () => {
  return request.get<any, string[]>('/categories')
}

// 更新商品库存
export const updateStock = (id: number, stock: number) => {
  return request.patch(`/admin/products/${id}/stock`, { stock })
}
