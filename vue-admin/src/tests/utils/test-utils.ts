import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { config, flushPromises } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'

// 创建测试用的Pinia实例
export function createTestingPinia() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

// 创建测试用的Router实例
export function createTestingRouter() {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      {
        path: '/login',
        name: 'Login',
        component: { template: '<div>Login</div>' },
      },
      {
        path: '/',
        component: { template: '<div><router-view /></div>' },
        children: [
          {
            path: 'dashboard',
            name: 'Dashboard',
            component: { template: '<div>Dashboard</div>' },
          },
          {
            path: 'orders',
            name: 'Orders',
            component: { template: '<div>Orders</div>' },
          },
        ],
      },
    ],
  })
  return router
}

// Mock API响应
export function mockApiResponse<T>(data: T, delay = 0): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(data)
    }, delay)
  })
}

// Mock API错误
export function mockApiError(message: string, delay = 0): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject(new Error(message))
    }, delay)
  })
}

// 清除所有mock
export function clearAllMocks() {
  vi.clearAllMocks()
  localStorage.clear()
}

// 等待所有Promise完成
export { flushPromises }

// 导出vitest全局对象
export { describe, it, expect, beforeEach, vi }
