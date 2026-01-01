import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import * as userApi from '@/api/user'

// Mock user API
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

  it('应该有初始状态', () => {
    const userStore = useUserStore()

    expect(userStore.token).toBe('')
    expect(userStore.user).toBeNull()
    expect(userStore.isLoggedIn).toBe(false)
  })

  it('应该从localStorage恢复token', () => {
    localStorage.setItem('token', 'test-token')

    const pinia = createPinia()
    setActivePinia(pinia)

    const userStore = useUserStore()
    expect(userStore.token).toBe('test-token')
    expect(userStore.isLoggedIn).toBe(true)
  })

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
    expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser))
    expect(result).toEqual(mockLoginData)
  })

  it('登录失败应该抛出错误', async () => {
    const error = new Error('用户名或密码错误')
    vi.mocked(userApi.login).mockRejectedValueOnce(error)

    const userStore = useUserStore()

    await expect(userStore.login('wrong', 'wrong')).rejects.toThrow(
      '用户名或密码错误'
    )

    expect(userStore.token).toBe('')
    expect(userStore.user).toBeNull()
    expect(userStore.isLoggedIn).toBe(false)
  })

  it('应该成功登出', () => {
    const mockUser = { id: 1, username: 'admin' }
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify(mockUser))

    const pinia = createPinia()
    setActivePinia(pinia)

    const userStore = useUserStore()
    userStore.user = mockUser as any
    expect(userStore.isLoggedIn).toBe(true)

    userStore.logout()

    expect(userStore.token).toBe('')
    expect(userStore.user).toBeNull()
    expect(userStore.isLoggedIn).toBe(false)
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  it('应该成功获取用户信息', async () => {
    const mockUser = {
      id: 1,
      username: 'admin',
      role: 'admin',
      email: 'admin@example.com',
    }

    // Mock getUserInfo
    userApi.getUserInfo = vi.fn().mockResolvedValueOnce(mockUser) as any

    const userStore = useUserStore()
    const result = await userStore.getUser()

    expect(userApi.getUserInfo).toHaveBeenCalled()
    expect(userStore.user).toEqual(mockUser)
    expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser))
    expect(result).toEqual(mockUser)
  })

  it('获取用户信息失败应该抛出错误', async () => {
    const error = new Error('未登录')
    vi.mocked(userApi.getUserInfo).mockRejectedValueOnce(error)

    const userStore = useUserStore()

    await expect(userStore.getUser()).rejects.toThrow('未登录')
  })

  it('应该从localStorage恢复用户信息', () => {
    const mockUser = {
      id: 1,
      username: 'admin',
      role: 'admin',
    }

    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify(mockUser))

    // 重新创建pinia实例以触发restoreUser
    const pinia = createPinia()
    setActivePinia(pinia)

    const userStore = useUserStore()

    expect(userStore.token).toBe('test-token')
    expect(userStore.user).toEqual(mockUser)
    expect(userStore.isLoggedIn).toBe(true)
  })

  it('应该处理localStorage中的无效用户数据', () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', 'invalid json')

    const pinia = createPinia()
    setActivePinia(pinia)

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    const userStore = useUserStore()

    expect(userStore.token).toBe('test-token')
    expect(userStore.user).toBeNull()
    expect(consoleSpy).toHaveBeenCalled()

    consoleSpy.mockRestore()
  })

  it('应该处理localStorage中无用户数据的情况', () => {
    localStorage.setItem('token', 'test-token')

    const pinia = createPinia()
    setActivePinia(pinia)

    const userStore = useUserStore()

    expect(userStore.token).toBe('test-token')
    expect(userStore.user).toBeNull()
    expect(userStore.isLoggedIn).toBe(true)
  })
})
