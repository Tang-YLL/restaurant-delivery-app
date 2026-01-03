import request from '../utils/request'
import type { DashboardStats } from '../types'

// 获取仪表板统计数据
export const getDashboardStats = () => {
  return request.get<any, DashboardStats>('/admin/analytics/today')
}

// 获取订单趋势数据
export const getOrderTrend = (days: number = 7) => {
  return request.get('/admin/analytics/trend', { params: { days } })
}

// 获取热销商品
export const getTopProducts = (limit: number = 10) => {
  return request.get('/admin/analytics/hot-products', { params: { limit } })
}
