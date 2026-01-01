import request from '../utils/request'
import type { Order, OrderQuery, PageResponse } from '../types'

// 获取订单列表
export const getOrderList = (params: OrderQuery) => {
  return request.get<any, PageResponse<Order>>('/admin/orders', { params })
}

// 获取订单详情
export const getOrderDetail = (id: number) => {
  return request.get<any, Order>(`/admin/orders/${id}`)
}

// 更新订单状态
export const updateOrderStatus = (id: number, status: string) => {
  return request.patch(`/admin/orders/${id}/status`, { status })
}

// 删除订单
export const deleteOrder = (id: number) => {
  return request.delete(`/orders/${id}`)
}

// 导出订单CSV
export const exportOrders = (params: OrderQuery) => {
  return request.get('/orders/export', {
    params,
    responseType: 'blob'
  })
}

// 获取订单统计数据
export const getOrderStats = (days: number = 7) => {
  return request.get('/orders/stats', { params: { days } })
}
