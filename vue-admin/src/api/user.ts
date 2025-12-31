import request from '../utils/request'
import type { LoginForm, LoginResponse, User } from '../types'

// 登录
export const login = (data: LoginForm) => {
  return request.post<any, LoginResponse>('/auth/login', data)
}

// 获取用户信息
export const getUserInfo = () => {
  return request.get<any, User>('/auth/userinfo')
}

// 登出
export const logout = () => {
  return request.post('/auth/logout')
}

// 获取用户列表
export const getUserList = (params: { page: number; pageSize: number; keyword?: string }) => {
  return request.get<any, any>('/users', { params })
}

// 更新用户状态
export const updateUserStatus = (id: number, status: string) => {
  return request.put(`/users/${id}/status`, { status })
}

// 删除用户
export const deleteUser = (id: number) => {
  return request.delete(`/users/${id}`)
}
