import request from '../utils/request'
import type { Review, ReviewQuery, PageResponse } from '../types'

// 获取评价列表
export const getReviewList = (params: ReviewQuery) => {
  return request.get<any, PageResponse<Review>>('/admin/reviews', { params })
}

// 删除评价
export const deleteReview = (id: number) => {
  return request.delete(`/admin/reviews/${id}`)
}

// 回复评价
export const replyReview = (id: number, reply: string) => {
  return request.post(`/admin/reviews/${id}/reply`, { reply })
}

// 设置评价可见性
export const setReviewVisibility = (id: number, is_visible: boolean) => {
  return request.put(`/admin/reviews/${id}/visibility`, { is_visible })
}
