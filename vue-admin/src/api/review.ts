import request from '../utils/request'
import type { Review, ReviewQuery, PageResponse } from '../types'

// 获取评价列表
export const getReviewList = (params: ReviewQuery) => {
  return request.get<any, PageResponse<Review>>('/reviews', { params })
}

// 审核评价
export const approveReview = (id: number) => {
  return request.put(`/reviews/${id}/approve`)
}

// 拒绝评价
export const rejectReview = (id: number) => {
  return request.put(`/reviews/${id}/reject`)
}

// 删除评价
export const deleteReview = (id: number) => {
  return request.delete(`/reviews/${id}`)
}
