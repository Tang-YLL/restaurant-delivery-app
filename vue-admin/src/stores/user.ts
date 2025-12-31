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
      token.value = data.token
      user.value = data.user
      isLoggedIn.value = true
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
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
    localStorage.removeItem('user')
  }

  // 从本地存储恢复用户信息
  const restoreUser = () => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        user.value = JSON.parse(userStr)
      } catch (e) {
        console.error('Failed to parse user from localStorage', e)
      }
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
    logout
  }
})
