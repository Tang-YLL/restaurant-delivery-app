import axios from 'axios'
import type { AxiosInstance, AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { useUserStore } from '../stores/user'
import mockApi from '../mock'

// 是否使用Mock数据
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Mock请求适配器
const mockAdapter = async (config: InternalAxiosRequestConfig) => {
  const { method, url, params, data } = config

  // 路由到对应的Mock方法
  if (url?.includes('/auth/login') && method === 'post') {
    return await mockApi.login(data.username, data.password)
  }

  if (url?.includes('/orders') && method === 'get') {
    return await mockApi.getOrders(params)
  }

  if (url?.match(/\/orders\/\d+/) && method === 'get') {
    const id = Number(url.split('/').pop())
    return await mockApi.getOrderDetail(id)
  }

  if (url?.includes('/orders/') && method === 'put') {
    const id = Number(url.split('/')[3])
    return await mockApi.updateOrderStatus(id, data.status)
  }

  if (url?.includes('/products') && method === 'get') {
    return await mockApi.getProducts(params)
  }

  if (url?.includes('/products/categories') && method === 'get') {
    return await mockApi.getCategories()
  }

  if (url?.includes('/users') && method === 'get') {
    return await mockApi.getUsers(params)
  }

  if (url?.includes('/reviews') && method === 'get') {
    return await mockApi.getReviews(params)
  }

  if (url?.includes('/dashboard/stats') && method === 'get') {
    return await mockApi.getDashboardStats()
  }

  throw new Error('Mock API not implemented')
}

// 请求拦截器
service.interceptors.request.use(
  async (config) => {
    // 如果启用Mock，使用Mock适配器
    if (USE_MOCK) {
      try {
        const mockData = await mockAdapter(config)
        return Promise.resolve({ ...config, adapter: () => Promise.resolve({ data: mockData }) } as any)
      } catch (error: any) {
        return Promise.reject(error)
      }
    }

    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 如果是Mock模式，直接返回data
    if (USE_MOCK) {
      return response.data
    }

    // 检查响应数据格式
    // 如果响应中有 code 字段，说明是标准格式响应
    if ('code' in response.data) {
      const { code, message, data } = response.data

      // 根据业务状态码判断
      if (code === 200) {
        return data
      } else if (code === 401) {
        // token过期或未登录
        ElMessage.error('登录已过期，请重新登录')
        const userStore = useUserStore()
        userStore.logout()
        router.push('/login')
        return Promise.reject(new Error(message || '登录已过期'))
      } else {
        // 其他错误
        ElMessage.error(message || '请求失败')
        return Promise.reject(new Error(message || '请求失败'))
      }
    } else {
      // 否则直接返回响应数据（如登录响应的token）
      return response.data
    }
  },
  (error: AxiosError) => {
    // 如果是Mock模式，直接抛出错误
    if (USE_MOCK) {
      ElMessage.error(error.message || '请求失败')
      return Promise.reject(error)
    }

    // HTTP错误状态码处理
    if (error.response) {
      switch (error.response.status) {
        case 400:
          ElMessage.error('请求参数错误')
          break
        case 401:
          ElMessage.error('未授权，请登录')
          const userStore = useUserStore()
          userStore.logout()
          router.push('/login')
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        case 502:
          ElMessage.error('网关错误')
          break
        case 503:
          ElMessage.error('服务不可用')
          break
        case 504:
          ElMessage.error('网关超时')
          break
        default:
          ElMessage.error(`请求失败: ${error.message}`)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error(error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default service
