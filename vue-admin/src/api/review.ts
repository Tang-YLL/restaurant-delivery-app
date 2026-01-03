import request from '../utils/request'
import type { Review, ReviewQuery } from '../types'

// 获取评价列表
export const getReviewList = async (params: ReviewQuery) => {
  // 转换参数名
  const requestParams: any = {
    page: params.page,
    page_size: params.pageSize,
  }

  if (params.productId !== undefined) {
    requestParams.product_id = params.productId
  }

  if (params.rating !== undefined) {
    requestParams.rating = params.rating
  }

  if (params.isVisible !== undefined) {
    requestParams.is_visible = params.isVisible
  }

  return request.get('/admin/reviews', { params: requestParams })
}

// 删除评价
export const deleteReview = (id: number) => {
  return request.delete(`/admin/reviews/${id}`)
}

// 回复评价
export const replyReview = (id: number, reply: string) => {
  return request.post(`/admin/reviews/${id}/reply`, { reply })
}

// 切换评价显示状态
export const toggleReviewVisibility = (id: number, isVisible: boolean) => {
  return request.put(`/admin/reviews/${id}/visibility`, null, {
    params: { is_visible: isVisible }
  })
}

