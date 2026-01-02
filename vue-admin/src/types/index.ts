// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  avatar?: string
  createdAt: string
}

export interface LoginForm {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// 订单相关类型
export type OrderStatus = 'pending' | 'paid' | 'preparing' | 'ready' | 'completed' | 'cancelled'

export interface OrderItem {
  id: number
  productId: number
  productName: string
  productImage: string
  price: number
  quantity: number
  subtotal: number
}

export interface Order {
  id: number
  orderNo: string
  userId: number
  userName: string
  userPhone: string
  userAddress: string
  items: OrderItem[]
  totalAmount: number
  status: OrderStatus
  deliveryType: string
  paymentMethod: string
  remark?: string
  createdAt: string
  updatedAt: string
}

export interface OrderQuery {
  page: number
  pageSize: number
  status?: OrderStatus
  orderNo?: string
  userName?: string
  userPhone?: string
  deliveryType?: string
  startDate?: string
  endDate?: string
}

// 商品相关类型
export interface Product {
  id: number
  name: string
  description: string
  price: number
  stock: number
  category: string
  image: string
  images: string[]
  status: 'active' | 'inactive'
  sales: number
  createdAt: string
  updatedAt: string
}

export interface ProductForm {
  name: string
  description: string
  price: number
  stock: number
  category: string
  image: string
  images: string[]
  status: 'active' | 'inactive'
}

export interface ProductQuery {
  page: number
  pageSize: number
  category?: string
  status?: string
  keyword?: string
}

// 统计数据类型
export interface DashboardStats {
  todayOrders: number
  todaySales: number
  totalUsers: number
  totalProducts: number
  orderTrend: Array<{ date: string; orders: number; sales: number }>
  topProducts: Array<{ id: number; name: string; sales: number; revenue: number }>
}

// 评价类型
export interface Review {
  id: number
  user_id: number
  user_phone?: string
  user_nickname?: string
  product_id: number
  product_name?: string
  rating: number
  content: string
  images?: string[]
  admin_reply?: string
  is_visible: boolean
  created_at: string
  updated_at?: string
}

export interface ReviewQuery {
  page: number
  pageSize: number
  productId?: number
  rating?: number
  isVisible?: boolean
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PageResponse<T = any> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// 分类相关类型
export interface Category {
  id: number
  name: string
  code: string
  description?: string
  sort_order: number
  is_active: boolean
  created_at: string
}

export interface CategoryForm {
  name: string
  code: string
  description?: string
  sort_order: number
  is_active: boolean
}
