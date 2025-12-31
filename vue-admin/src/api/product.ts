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
  return request.post('/products', data)
}

// 更新商品
export const updateProduct = (id: number, data: ProductForm) => {
  return request.put(`/products/${id}`, data)
}

// 删除商品
export const deleteProduct = (id: number) => {
  return request.delete(`/products/${id}`)
}

// 获取商品分类
export const getCategories = () => {
  return request.get<any, string[]>('/products/categories')
}

// 更新商品库存
export const updateStock = (id: number, stock: number) => {
  return request.put(`/products/${id}/stock`, { stock })
}
