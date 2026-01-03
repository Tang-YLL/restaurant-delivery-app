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

// 营养成分相关类型
export interface Nutrition {
  serving_size: string  // 份量（如：100g、1份）
  calories: number      // 热量 (kJ)
  protein: number       // 蛋白质 (g)
  fat: number          // 脂肪 (g)
  carbohydrates: number // 碳水化合物 (g)
  sodium: number       // 钠 (mg)
  dietary_fiber?: number // 膳食纤维 (g)，可选
  sugar?: number       // 糖 (g)，可选
  allergens?: string[] // 过敏源列表，可选
}

export interface NutritionFormData {
  serving_size: string
  calories: number | null
  protein: number | null
  fat: number | null
  carbohydrates: number | null
  sodium: number | null
  dietary_fiber?: number | null
  sugar?: number | null
  allergens?: string[]
}

// NRV标准值（中国营养标签标准）
export const NRV_VALUES = {
  protein: 60,      // 蛋白质 60g
  fat: 60,         // 脂肪 60g
  carbohydrates: 300, // 碳水化合物 300g
  sodium: 2000     // 钠 2000mg
} as const

// 过敏源列表
export const ALLERGEN_LIST = [
  '含麸质谷物',
  '甲壳纲类动物',
  '蛋类',
  '鱼类',
  '花生',
  '大豆',
  '乳制品',
  '坚果'
] as const

// 内容分区相关类型
export type SectionType = 'story' | 'nutrition' | 'ingredients' | 'process' | 'tips'

export interface ContentSection {
  id?: number
  product_id: number
  section_type: SectionType
  title?: string
  content: string
  display_order: number
  created_at?: string
  updated_at?: string
}

export interface ContentSectionFormData {
  section_type: SectionType
  title?: string
  content: string
  display_order: number
}
