import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '../types'
import { login as loginApi, getUserInfo } from '../api/user'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)
  const isLoggedIn = ref<boolean>(!!token.value)

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const data = await loginApi({ username, password })
      token.value = data.access_token
      isLoggedIn.value = true
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      // 登录成功后获取用户信息
      try {
        const userInfo = await getUserInfo()
        user.value = userInfo
        localStorage.setItem('user', JSON.stringify(userInfo))
      } catch (error) {
        // 如果获取用户信息失败，仍然登录成功，但没有用户详情
        console.warn('获取用户信息失败，但登录成功', error)
      }

      return data
    } catch (error) {
      throw error
    }
  }

  // 获取用户信息
  const getUser = async () => {
    try {
      const data = await getUserInfo()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    } catch (error) {
      throw error
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    user.value = null
    isLoggedIn.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // 从本地存储恢复用户信息
  const restoreUser = () => {
    const savedToken = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')

    // 恢复token
    if (savedToken) {
      token.value = savedToken
      isLoggedIn.value = true
    } else {
      token.value = ''
      isLoggedIn.value = false
    }

    // 恢复user信息
    if (userStr) {
      try {
        user.value = JSON.parse(userStr)
      } catch (e) {
        console.error('Failed to parse user from localStorage', e)
        // 清除无效数据
        localStorage.removeItem('user')
        user.value = null
      }
    } else {
      user.value = null
    }
  }

  // 初始化时恢复用户信息
  restoreUser()

  return {
    token,
    user,
    isLoggedIn,
    login,
    getUser,
    logout,
    restoreUser  // 导出restoreUser以便测试使用
  }
})
