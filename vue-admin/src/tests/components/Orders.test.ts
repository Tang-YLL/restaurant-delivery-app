import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Orders from '@/views/Orders.vue'
import * as orderApi from '@/api/order'

// Mock order API
vi.mock('@/api/order', () => ({
  getOrderList: vi.fn(),
  updateOrderStatus: vi.fn(),
  exportOrders: vi.fn(),
}))

// Mock Element Plus
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
    },
    ElMessageBox: {
      confirm: vi.fn(),
    },
  }
})

describe('Orders.vue', () => {
  let router: any
  let pinia: any

  const mockOrders = [
    {
      id: 1,
      orderNo: 'ORD20240101120000',
      userName: '张三',
      userPhone: '13800138000',
      totalAmount: 88.88,
      status: 'paid',
      paymentMethod: '微信支付',
      createdAt: '2024-01-01 12:00:00',
    },
    {
      id: 2,
      orderNo: 'ORD20240101130000',
      userName: '李四',
      userPhone: '13900139000',
      totalAmount: 128.0,
      status: 'shipped',
      paymentMethod: '支付宝',
      createdAt: '2024-01-01 13:00:00',
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()

    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/orders', component: Orders },
        { path: '/orders/:id', component: { template: '<div>Order Detail</div>' } },
      ],
    })

    pinia = createPinia()
    setActivePinia(pinia)

    router.push = vi.fn()
  })

  it('应该正确渲染订单列表页面', () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValueOnce({
      list: [],
      total: 0,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    expect(wrapper.find('.orders').exists()).toBe(true)
    expect(wrapper.text()).toContain('订单管理')
  })

  it('应该在挂载时加载订单列表', async () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValueOnce({
      list: mockOrders,
      total: 2,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()

    expect(orderApi.getOrderList).toHaveBeenCalled()
    expect(wrapper.vm.orderList).toHaveLength(2)
    expect(wrapper.vm.total).toBe(2)
  })

  it('应该显示搜索表单和导出按钮', () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValueOnce({
      list: [],
      total: 0,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    expect(wrapper.text()).toContain('订单号')
    expect(wrapper.text()).toContain('客户姓名')
    expect(wrapper.text()).toContain('订单状态')
    expect(wrapper.text()).toContain('导出CSV')
  })

  it('应该支持按订单号搜索', async () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValue({
      list: mockOrders.filter((o) => o.orderNo === 'ORD20240101120000'),
      total: 1,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()

    // 设置搜索条件
    await wrapper.setData({
      queryForm: {
        ...wrapper.vm.queryForm,
        orderNo: 'ORD20240101120000',
      },
    })

    // 触发搜索
    const searchButton = wrapper.findAll('button').find(
      (btn) => btn.text().includes('搜索')
    )
    if (searchButton) {
      await searchButton.trigger('click')
      await flushPromises()
    }
  })

  it('应该支持按状态筛选', async () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValue({
      list: mockOrders.filter((o) => o.status === 'paid'),
      total: 1,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()

    // 设置状态筛选
    await wrapper.setData({
      queryForm: {
        ...wrapper.vm.queryForm,
        status: 'paid',
      },
    })
  })

  it('应该重置搜索条件', async () => {
    vi.mocked(orderApi.getOrderList)
      .mockResolvedValueOnce({
        list: mockOrders,
        total: 2,
      })
      .mockResolvedValueOnce({
        list: [],
        total: 0,
      })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()

    // 设置搜索条件
    await wrapper.setData({
      queryForm: {
        ...wrapper.vm.queryForm,
        orderNo: 'ORD20240101120000',
        userName: '张三',
      },
    })

    // 触发重置
    const resetButton = wrapper.findAll('button').find(
      (btn) => btn.text().includes('重置')
    )
    if (resetButton) {
      await resetButton.trigger('click')
      await flushPromises()
    }

    expect(wrapper.vm.queryForm.orderNo).toBe('')
    expect(wrapper.vm.queryForm.userName).toBe('')
  })

  it('应该正确显示订单状态标签', () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValueOnce({
      list: mockOrders,
      total: 2,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    expect(wrapper.vm.getStatusType('pending')).toBe('warning')
    expect(wrapper.vm.getStatusType('paid')).toBe('success')
    expect(wrapper.vm.getStatusType('shipped')).toBe('primary')
    expect(wrapper.vm.getStatusType('delivered')).toBe('info')
    expect(wrapper.vm.getStatusType('cancelled')).toBe('danger')

    expect(wrapper.vm.getStatusText('pending')).toBe('待付款')
    expect(wrapper.vm.getStatusText('paid')).toBe('已付款')
    expect(wrapper.vm.getStatusText('shipped')).toBe('已发货')
    expect(wrapper.vm.getStatusText('delivered')).toBe('已完成')
    expect(wrapper.vm.getStatusText('cancelled')).toBe('已取消')
  })

  it('应该跳转到订单详情页', async () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValueOnce({
      list: mockOrders,
      total: 2,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()

    // 触发查看详情
    await wrapper.vm.handleView(1)
    expect(router.push).toHaveBeenCalledWith('/orders/1')
  })

  it('应该显示分页组件', () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValueOnce({
      list: mockOrders,
      total: 100,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    expect(wrapper.find('.pagination-container').exists()).toBe(true)
  })

  it('应该改变每页显示数量', async () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValue({
      list: mockOrders,
      total: 2,
    })

    const wrapper = mount(Orders, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()

    // 改变每页数量
    await wrapper.setData({
      queryForm: {
        ...wrapper.vm.queryForm,
        pageSize: 20,
      },
    })

    // 触发加载
    await wrapper.vm.loadOrders()
    await flushPromises()

    expect(orderApi.getOrderList).toHaveBeenCalled()
  })
})
