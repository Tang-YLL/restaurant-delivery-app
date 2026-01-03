import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import * as userApi from '@/api/user'

// Mock API
vi.mock('@/api/user', () => ({
  login: vi.fn(),
  getUserInfo: vi.fn(),
}))

describe('User Store', () => {
  beforeEach(() => {
    // 清除localStorage
    localStorage.clear()
    vi.clearAllMocks()

    // 创建新的pinia实例
    const pinia = createPinia()
    setActivePinia(pinia)
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态（无token）', () => {
      const userStore = useUserStore()

      expect(userStore.token).toBe('')
      expect(userStore.user).toBeNull()
      expect(userStore.isLoggedIn).toBe(false)
    })

    it('应该从localStorage恢复已登录状态', () => {
      // 设置localStorage BEFORE importing store
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))

      // 重新创建pinia和store
      const pinia = createPinia()
      setActivePinia(pinia)
      const userStore = useUserStore()

      expect(userStore.token).toBe('test-token')
      expect(userStore.user).toEqual({ id: 1, username: 'admin', role: 'admin' })
      expect(userStore.isLoggedIn).toBe(true)
    })
  })

  describe('登录功能', () => {
    it('应该成功登录', async () => {
      const mockLoginData = {
        access_token: 'test-token-123',
        refresh_token: 'refresh-token-123',
      }

      const mockUser = {
        id: 1,
        username: 'admin',
        role: 'admin',
      }

      vi.mocked(userApi.login).mockResolvedValueOnce(mockLoginData)
      vi.mocked(userApi.getUserInfo).mockResolvedValueOnce(mockUser)

      const userStore = useUserStore()
      const result = await userStore.login('admin', 'admin123')

      expect(userApi.login).toHaveBeenCalledWith({
        username: 'admin',
        password: 'admin123',
      })

      expect(userStore.token).toBe('test-token-123')
      expect(userStore.user).toEqual(mockUser)
      expect(userStore.isLoggedIn).toBe(true)
      expect(localStorage.getItem('token')).toBe('test-token-123')
      expect(localStorage.getItem('refresh_token')).toBe('refresh-token-123')
      expect(result).toEqual(mockLoginData)
    })

    it('应该处理localStorage中的无效用户数据', () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', 'invalid json')

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // 重新创建store
      const pinia = createPinia()
      setActivePinia(pinia)
      const userStore = useUserStore()

      expect(userStore.token).toBe('test-token')
      expect(userStore.user).toBeNull()
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })
  })

  describe('登出功能', () => {
    it('应该成功登出', () => {
      // 先登录
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin' }))

      const pinia = createPinia()
      setActivePinia(pinia)

      const userStore = useUserStore()
      expect(userStore.isLoggedIn).toBe(true)

      // 登出
      userStore.logout()

      expect(userStore.token).toBe('')
      expect(userStore.user).toBeNull()
      expect(userStore.isLoggedIn).toBe(false)
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })
  })

  describe('获取用户信息', () => {
    it('应该成功获取用户信息', async () => {
      const mockUser = {
        id: 1,
        username: 'admin',
        role: 'admin',
        email: 'admin@example.com',
      }

      vi.mocked(userApi.getUserInfo).mockResolvedValueOnce(mockUser)

      const userStore = useUserStore()
      const result = await userStore.getUser()

      expect(userApi.getUserInfo).toHaveBeenCalled()
      expect(userStore.user).toEqual(mockUser)
      expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser))
      expect(result).toEqual(mockUser)
    })

    it('应该在未登录时抛出错误', async () => {
      vi.mocked(userApi.getUserInfo).mockRejectedValueOnce(new Error('未登录'))

      const userStore = useUserStore()

      await expect(userStore.getUser()).rejects.toThrow('未登录')
    })
  })
})
