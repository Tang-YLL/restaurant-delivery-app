import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Login from '@/views/Login.vue'
import { useUserStore } from '@/stores/user'
import ElMessage from 'element-plus'

// Mock Element Plus Message
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
    },
  }
})

describe('Login.vue', () => {
  let router: any
  let pinia: any

  beforeEach(() => {
    // 清除localStorage
    localStorage.clear()
    vi.clearAllMocks()

    // 创建测试用router
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/login', component: Login },
        { path: '/', component: { template: '<div>Home</div>' } },
      ],
    })

    // 创建测试用pinia
    pinia = createPinia()
    setActivePinia(pinia)

    // Mock push
    router.push = vi.fn()
  })

  it('应该正确渲染登录表单', () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    expect(wrapper.find('.login-container').exists()).toBe(true)
    expect(wrapper.find('.login-card').exists()).toBe(true)
    expect(wrapper.text()).toContain('管理后台登录')
    expect(wrapper.text()).toContain('默认账号: admin / admin123')
  })

  it('应该显示用户名和密码输入框', () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    const inputs = wrapper.findAll('input')
    expect(inputs).toHaveLength(2)
  })

  it('应该验证必填字段', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    const loginButton = wrapper.find('button')
    await loginButton.trigger('click')
    await flushPromises()

    // 验证错误消息应该显示
    await wrapper.vm.$nextTick()
  })

  it('应该在输入为空时显示验证错误', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    const formRef = wrapper.vm.$refs.formRef as any
    expect(formRef).toBeDefined()

    // 触发验证
    if (formRef) {
      const valid = await formRef.validate()
      expect(valid).toBe(false)
    }
  })

  it('应该在密码少于6位时显示验证错误', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    // 设置表单值
    await wrapper.setData({
      loginForm: {
        username: 'admin',
        password: '12345',
      },
    })

    const formRef = wrapper.vm.$refs.formRef as any
    if (formRef) {
      const valid = await formRef.validate()
      expect(valid).toBe(false)
    }
  })

  it('应该成功登录并跳转', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    // Mock userStore.login
    const userStore = useUserStore()
    vi.spyOn(userStore, 'login').mockResolvedValueOnce({
      token: 'test-token',
      user: { id: 1, username: 'admin', role: 'admin' },
    })

    // 设置表单值
    await wrapper.setData({
      loginForm: {
        username: 'admin',
        password: 'admin123',
      },
    })

    // 触发登录
    const loginButton = wrapper.find('button')
    await loginButton.trigger('click')
    await flushPromises()

    // 验证登录成功
    expect(ElMessage.success).toHaveBeenCalledWith('登录成功')
    expect(router.push).toHaveBeenCalledWith('/')
  })

  it('应该在登录失败时显示错误消息', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    // Mock userStore.login抛出错误
    const userStore = useUserStore()
    vi.spyOn(userStore, 'login').mockRejectedValueOnce(
      new Error('用户名或密码错误')
    )

    // 设置表单值
    await wrapper.setData({
      loginForm: {
        username: 'wrong',
        password: 'wrong',
      },
    })

    // 触发登录
    const loginButton = wrapper.find('button')
    await loginButton.trigger('click')
    await flushPromises()

    // 验证错误消息
    expect(ElMessage.error).toHaveBeenCalledWith('用户名或密码错误')
  })

  it('应该在登录过程中显示loading状态', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    // Mock一个延迟的登录请求
    const userStore = useUserStore()
    vi.spyOn(userStore, 'login').mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              token: 'test-token',
              user: { id: 1, username: 'admin', role: 'admin' },
            })
          }, 100)
        })
    )

    // 设置表单值
    await wrapper.setData({
      loginForm: {
        username: 'admin',
        password: 'admin123',
      },
    })

    // 触发登录
    const loginButton = wrapper.find('button')
    await loginButton.trigger('click')

    // 检查loading状态
    expect(wrapper.vm.loading).toBe(true)
    expect(wrapper.find('button').text()).toContain('登录中...')

    await flushPromises()

    // 登录完成后loading应该为false
    expect(wrapper.vm.loading).toBe(false)
  })

  it('应该在按回车键时触发登录', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, pinia],
      },
    })

    const userStore = useUserStore()
    const loginSpy = vi
      .spyOn(userStore, 'login')
      .mockResolvedValueOnce({
        token: 'test-token',
        user: { id: 1, username: 'admin', role: 'admin' },
      })

    // 设置表单值
    await wrapper.setData({
      loginForm: {
        username: 'admin',
        password: 'admin123',
      },
    })

    // 找到密码输入框并触发回车事件
    const passwordInput = wrapper.findAll('input')[1]
    await passwordInput.trigger('keyup.enter')

    await flushPromises()

    // 验证login被调用
    expect(loginSpy).toHaveBeenCalled()
  })
})
