// Mock API 数据

// 模拟延迟
const delay = (ms: number = 300) => new Promise(resolve => setTimeout(resolve, ms))

// 生成随机数据
const randomDate = (start: Date, end: Date) => {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime())).toISOString()
}

const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min

// Mock 数据
const mockUsers = [
  { id: 1, username: 'admin', email: 'admin@example.com', role: 'admin', createdAt: '2024-01-01T00:00:00Z' },
  { id: 2, username: 'user1', email: 'user1@example.com', role: 'user', createdAt: '2024-01-02T00:00:00Z' },
  { id: 3, username: 'user2', email: 'user2@example.com', role: 'user', createdAt: '2024-01-03T00:00:00Z' },
  { id: 4, username: 'user3', email: 'user3@example.com', role: 'user', createdAt: '2024-01-04T00:00:00Z' },
  { id: 5, username: 'user4', email: 'user4@example.com', role: 'user', createdAt: '2024-01-05T00:00:00Z' }
]

const mockProducts = [
  {
    id: 1,
    name: 'iPhone 15 Pro Max',
    description: '苹果最新旗舰手机，搭载A17 Pro芯片',
    price: 9999,
    stock: 50,
    category: '手机',
    image: '/images/iphone.jpg',
    images: ['/images/iphone1.jpg', '/images/iphone2.jpg'],
    status: 'active',
    sales: 128,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: 'MacBook Pro 16英寸',
    description: 'M3 Max芯片，专业级性能',
    price: 19999,
    stock: 30,
    category: '电脑',
    image: '/images/macbook.jpg',
    images: ['/images/macbook1.jpg', '/images/macbook2.jpg'],
    status: 'active',
    sales: 85,
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z'
  },
  {
    id: 3,
    name: 'AirPods Pro 2',
    description: '主动降噪，空间音频',
    price: 1899,
    stock: 100,
    category: '耳机',
    image: '/images/airpods.jpg',
    images: ['/images/airpods1.jpg'],
    status: 'active',
    sales: 256,
    createdAt: '2024-01-03T00:00:00Z',
    updatedAt: '2024-01-03T00:00:00Z'
  },
  {
    id: 4,
    name: 'iPad Air 5',
    description: 'M1芯片，10.9英寸 Liquid 视网膜显示屏',
    price: 4399,
    stock: 45,
    category: '平板',
    image: '/images/ipad.jpg',
    images: ['/images/ipad1.jpg', '/images/ipad2.jpg'],
    status: 'active',
    sales: 98,
    createdAt: '2024-01-04T00:00:00Z',
    updatedAt: '2024-01-04T00:00:00Z'
  },
  {
    id: 5,
    name: 'Apple Watch Series 9',
    description: '健康监测，智能运动',
    price: 3199,
    stock: 60,
    category: '手表',
    image: '/images/watch.jpg',
    images: ['/images/watch1.jpg'],
    status: 'active',
    sales: 167,
    createdAt: '2024-01-05T00:00:00Z',
    updatedAt: '2024-01-05T00:00:00Z'
  }
]

const mockOrders: any[] = []
for (let i = 1; i <= 50; i++) {
  const statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
  const status = statuses[randomInt(0, 4)]
  const product = mockProducts[randomInt(0, mockProducts.length - 1)]

  mockOrders.push({
    id: i,
    orderNo: `ORD${String(i).padStart(6, '0')}`,
    userId: randomInt(1, 5),
    userName: `用户${randomInt(1, 100)}`,
    userPhone: `138${String(randomInt(10000000, 99999999))}`,
    userAddress: `北京市朝阳区某街道${randomInt(1, 100)}号`,
    items: [{
      id: 1,
      productId: product.id,
      productName: product.name,
      productImage: product.image,
      price: product.price,
      quantity: randomInt(1, 3),
      subtotal: product.price * randomInt(1, 3)
    }],
    totalAmount: product.price * randomInt(1, 3),
    status,
    paymentMethod: ['微信支付', '支付宝', '银行卡'][randomInt(0, 2)],
    remark: randomInt(0, 1) ? '' : '请尽快发货',
    createdAt: randomDate(new Date(2024, 0, 1), new Date()),
    updatedAt: randomDate(new Date(2024, 0, 1), new Date())
  })
}

const mockReviews: any[] = []
for (let i = 1; i <= 30; i++) {
  const statuses = ['pending', 'approved', 'rejected']
  const status = statuses[randomInt(0, 2)]
  const product = mockProducts[randomInt(0, mockProducts.length - 1)]

  mockReviews.push({
    id: i,
    productId: product.id,
    productName: product.name,
    userId: randomInt(1, 5),
    userName: `用户${randomInt(1, 100)}`,
    userAvatar: '',
    rating: randomInt(3, 5),
    content: '商品质量很好，物流也很快，非常满意！',
    images: randomInt(0, 1) ? ['/images/review1.jpg'] : [],
    status,
    createdAt: randomDate(new Date(2024, 0, 1), new Date())
  })
}

// Mock API
export const mockApi = {
  // 登录
  async login(username: string, password: string) {
    await delay()
    if (username === 'admin' && password === 'admin123') {
      return {
        token: 'mock-token-' + Date.now(),
        user: mockUsers[0]
      }
    }
    throw new Error('用户名或密码错误')
  },

  // 获取订单列表
  async getOrders(params: any) {
    await delay()
    let filtered = [...mockOrders]

    if (params.status) {
      filtered = filtered.filter(o => o.status === params.status)
    }
    if (params.orderNo) {
      filtered = filtered.filter(o => o.orderNo.includes(params.orderNo))
    }
    if (params.userName) {
      filtered = filtered.filter(o => o.userName.includes(params.userName))
    }
    if (params.startDate && params.endDate) {
      filtered = filtered.filter(o => {
        const date = o.createdAt.split('T')[0]
        return date >= params.startDate && date <= params.endDate
      })
    }

    const start = (params.page - 1) * params.pageSize
    const end = start + params.pageSize

    return {
      list: filtered.slice(start, end),
      total: filtered.length,
      page: params.page,
      pageSize: params.pageSize
    }
  },

  // 获取订单详情
  async getOrderDetail(id: number) {
    await delay()
    const order = mockOrders.find(o => o.id === id)
    if (!order) throw new Error('订单不存在')
    return order
  },

  // 更新订单状态
  async updateOrderStatus(id: number, status: string) {
    await delay()
    const order = mockOrders.find(o => o.id === id)
    if (!order) throw new Error('订单不存在')
    order.status = status
    return { success: true }
  },

  // 获取商品列表
  async getProducts(params: any) {
    await delay()
    let filtered = [...mockProducts]

    if (params.category) {
      filtered = filtered.filter(p => p.category === params.category)
    }
    if (params.status) {
      filtered = filtered.filter(p => p.status === params.status)
    }
    if (params.keyword) {
      filtered = filtered.filter(p => p.name.includes(params.keyword))
    }

    const start = (params.page - 1) * params.pageSize
    const end = start + params.pageSize

    return {
      list: filtered.slice(start, end),
      total: filtered.length,
      page: params.page,
      pageSize: params.pageSize
    }
  },

  // 获取分类
  async getCategories() {
    await delay()
    return ['手机', '电脑', '耳机', '平板', '手表']
  },

  // 获取用户列表
  async getUsers(params: any) {
    await delay()
    let filtered = [...mockUsers]

    if (params.keyword) {
      filtered = filtered.filter(u =>
        u.username.includes(params.keyword) ||
        u.email.includes(params.keyword)
      )
    }

    const start = (params.page - 1) * params.pageSize
    const end = start + params.pageSize

    return {
      list: filtered.slice(start, end),
      total: filtered.length,
      page: params.page,
      pageSize: params.pageSize
    }
  },

  // 获取评价列表
  async getReviews(params: any) {
    await delay()
    let filtered = [...mockReviews]

    if (params.status) {
      filtered = filtered.filter(r => r.status === params.status)
    }
    if (params.rating) {
      filtered = filtered.filter(r => r.rating === params.rating)
    }
    if (params.keyword) {
      filtered = filtered.filter(r =>
        r.productName.includes(params.keyword) ||
        r.userName.includes(params.keyword)
      )
    }

    const start = (params.page - 1) * params.pageSize
    const end = start + params.pageSize

    return {
      list: filtered.slice(start, end),
      total: filtered.length,
      page: params.page,
      pageSize: params.pageSize
    }
  },

  // 获取仪表板统计
  async getDashboardStats() {
    await delay()

    // 生成最近7天的数据
    const orderTrend = []
    for (let i = 6; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      orderTrend.push({
        date: date.toISOString().split('T')[0],
        orders: randomInt(10, 50),
        sales: randomInt(10000, 50000)
      })
    }

    // 热销商品
    const topProducts = mockProducts.map(p => ({
      id: p.id,
      name: p.name,
      sales: p.sales,
      revenue: p.price * p.sales
    })).sort((a, b) => b.sales - a.sales).slice(0, 10)

    return {
      todayOrders: randomInt(20, 50),
      todaySales: randomInt(30000, 80000),
      totalUsers: mockUsers.length,
      totalProducts: mockProducts.length,
      orderTrend,
      topProducts
    }
  }
}

export default mockApi
