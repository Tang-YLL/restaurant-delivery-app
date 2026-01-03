import request from '../utils/request'
import type { Category, CategoryForm } from '../types'

// 获取分类列表
export const getCategoryList = () => {
  return request.get<any, Category[]>('/categories')
}

// 获取分类详情
export const getCategoryDetail = (id: number) => {
  return request.get<any, Category>(`/categories/${id}`)
}

// 创建分类
export const createCategory = (data: CategoryForm) => {
  return request.post('/categories', data)
}

// 更新分类
export const updateCategory = (id: number, data: CategoryForm) => {
  return request.put(`/categories/${id}`, data)
}

// 删除分类
export const deleteCategory = (id: number) => {
  return request.delete(`/categories/${id}`)
}
