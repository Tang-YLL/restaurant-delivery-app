import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { config, flushPromises } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'

/**
 * Element Plus 组件的通用 stub
 * 用于测试时避免加载完整的 Element Plus 组件
 */
export const elementPlusStubs = {
  'el-card': {
    template: '<div class="el-card"><div class="el-card__header" v-if="$slots.header"><slot name="header" /></div><div class="el-card__body"><slot /></div></div>'
  },
  'el-row': { template: '<div class="el-row"><slot /></div>' },
  'el-col': { template: '<div class="el-col"><slot /></div>' },
  'el-button': { template: '<button class="el-button"><slot /></button>' },
  'el-input': { template: '<input class="el-input" />' },
  'el-form': {
    template: '<form class="el-form"><slot /></form>',
    methods: {
      validate: () => Promise.resolve(false),
      resetFields: () => {},
      clearValidate: () => {},
    }
  },
  'el-form-item': {
    template: '<div class="el-form-item"><slot /></div>',
  },
  'el-select': {
    template: '<select class="el-select"><slot /></select>',
  },
  'el-option': { template: '<option class="el-option"><slot /></option>' },
  'el-date-picker': {
    template: '<input type="date" class="el-date-picker" />',
  },
  'el-table': { template: '<table class="el-table"><slot /></table>' },
  'el-table-column': {
    template: '<td class="el-table-column"><slot /></td>',
  },
  'el-tag': { template: '<span class="el-tag"><slot /></span>' },
  'el-dropdown': {
    template: '<div class="el-dropdown"><slot /></div>',
  },
  'el-dropdown-menu': {
    template: '<div class="el-dropdown-menu"><slot /></div>',
  },
  'el-dropdown-item': {
    template: '<div class="el-dropdown-item"><slot /></div>',
  },
  'el-pagination': {
    template: '<div class="el-pagination"><slot /></div>',
  },
  'el-radio-group': {
    template: '<div class="el-radio-group"><slot /></div>',
  },
  'el-radio-button': {
    template: '<button class="el-radio-button"><slot /></button>',
  },
  'el-icon': { template: '<i class="el-icon"><slot /></i>' },
  'el-dialog': {
    template: '<div class="el-dialog" v-if="visible"><slot /></div>',
    props: ['modelValue', 'title'],
  },
  'el-upload': {
    template: '<div class="el-upload"><slot /></div>',
  },
  'el-image': {
    template: '<img class="el-image" />',
    props: ['src'],
  },
}

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

// 创建带有 Element Plus stub 的全局配置
export function createTestGlobalConfig(plugins: any[] = []) {
  return {
    plugins,
    stubs: elementPlusStubs,
  }
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
