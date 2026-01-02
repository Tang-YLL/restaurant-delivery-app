import request from '../utils/request'
import type { Order, OrderQuery, PageResponse } from '../types'

/**
 * 将后端返回的订单数据转换为前端格式
 */
const transformOrder = (backendOrder: any): Order => {
  return {
    id: backendOrder.id,
    orderNo: backendOrder.order_number || '',
    userId: backendOrder.user_id || 0,
    userName: backendOrder.user_nickname || backendOrder.user_name || '',
    userPhone: backendOrder.user_phone || '',
    userAddress: backendOrder.delivery_address || '',
    items: backendOrder.order_items || [],
    totalAmount: backendOrder.total_amount || 0,
    status: backendOrder.status || 'pending',
    deliveryType: backendOrder.delivery_type || '',
    paymentMethod: backendOrder.payment_method || 'wechat',
    remark: backendOrder.remark || '',
    createdAt: backendOrder.created_at || '',
    updatedAt: backendOrder.updated_at || ''
  }
}

// 获取订单列表
export const getOrderList = async (params: OrderQuery): Promise<PageResponse<Order>> => {
  console.log('📡 API: 请求订单列表', params)

  // 转换参数名以匹配后端API
  const requestParams: any = {
    page: params.page,
    page_size: params.pageSize,  // pageSize -> page_size
  }

  // 可选参数 - 添加详细日志
  console.log('📡 API: 处理参数前的值:', {
    status: params.status,
    orderNo: params.orderNo,
    userName: params.userName,
    userPhone: params.userPhone,
    deliveryType: params.deliveryType
  })

  if (params.status !== undefined && params.status !== null && params.status !== '') {
    requestParams.status = params.status
    console.log('✅ 添加 status 参数:', params.status)
  }

  if (params.orderNo) {
    requestParams.order_no = params.orderNo  // orderNo -> order_no
    console.log('✅ 添加 order_no 参数:', params.orderNo)
  }

  if (params.userName) {
    requestParams.user_name = params.userName  // userName -> user_name
    console.log('✅ 添加 user_name 参数:', params.userName)
  }

  if (params.userPhone) {
    requestParams.user_phone = params.userPhone  // userPhone -> user_phone
    console.log('✅ 添加 user_phone 参数:', params.userPhone)
  }

  if (params.deliveryType) {
    requestParams.delivery_type = params.deliveryType  // deliveryType -> delivery_type
    console.log('✅ 添加 delivery_type 参数:', params.deliveryType)
  }

  if (params.startDate) {
    requestParams.start_date = params.startDate  // startDate -> start_date
  }

  if (params.endDate) {
    requestParams.end_date = params.endDate  // endDate -> end_date
  }

  console.log('📡 API: 实际请求参数', requestParams)

  const response = await request.get<any, any>('/admin/orders', { params: requestParams })

  console.log('📡 API: 原始响应', response)

  // 转换响应数据格式
  const result = {
    list: (response.orders || []).map(transformOrder),
    total: response.pagination?.total || 0,
    page: response.pagination?.page || params.page,
    pageSize: response.pagination?.page_size || params.pageSize
  }

  console.log('📡 API: 转换后结果', result)

  return result
}

// 获取订单详情
export const getOrderDetail = async (id: number): Promise<Order> => {
  const response = await request.get<any, any>(`/admin/orders/${id}`)
  return transformOrder(response)
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
