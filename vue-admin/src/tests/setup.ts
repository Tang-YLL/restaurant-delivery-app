/**
 * Vitest 测试环境配置
 */
import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// 全局mock Element Plus的消息组件
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}

global.ElMessageBox = {
  confirm: vi.fn()
}

// 配置Vue Test Utils
config.global.stubs = {
  'el-button': true,
  'el-input': true,
  'el-input-number': true,
  'el-form': true,
  'el-form-item': true,
  'el-checkbox': true,
  'el-checkbox-group': true,
  'el-table': true,
  'el-table-column': true,
  'el-dialog': true,
  'el-upload': true
}

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn()
})) as any

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})
