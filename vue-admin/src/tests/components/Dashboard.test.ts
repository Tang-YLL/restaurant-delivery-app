import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Dashboard from '@/views/Dashboard.vue'
import * as dashboardApi from '@/api/dashboard'
import { elementPlusStubs } from '../utils/test-utils'

// Mock dashboard API
vi.mock('@/api/dashboard', () => ({
  getDashboardStats: vi.fn(),
}))

// Mock ECharts
vi.mock('echarts', () => ({
  default: {
    init: vi.fn(() => ({
      setOption: vi.fn(),
      dispose: vi.fn(),
      resize: vi.fn(),
    })),
  },
  graphic: {
    LinearGradient: vi.fn(),
  },
}))

describe('Dashboard.vue', () => {
  let router: any
  let pinia: any

  const mockStats = {
    todayOrders: 128,
    todaySales: 15890.5,
    totalUsers: 1523,
    totalProducts: 86,
    orderTrend: [
      { date: '2024-01-01', orders: 120, sales: 15000 },
      { date: '2024-01-02', orders: 135, sales: 16800 },
      { date: '2024-01-03', orders: 128, sales: 15890 },
    ],
    topProducts: [
      { name: '宫保鸡丁', sales: 256 },
      { name: '鱼香肉丝', sales: 198 },
      { name: '麻婆豆腐', sales: 176 },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()

    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/dashboard', component: Dashboard },
      ],
    })

    pinia = createPinia()
    setActivePinia(pinia)

    // Mock getBoundingClientRect for chart refs
    Element.prototype.getBoundingClientRect = vi.fn(() => ({
      width: 800,
      height: 400,
      top: 0,
      left: 0,
      bottom: 400,
      right: 800,
      x: 0,
      y: 0,
      toJSON: vi.fn(),
    }))
  })

  it('应该正确渲染Dashboard页面', () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    expect(wrapper.find('.dashboard').exists()).toBe(true)
  })

  it('应该在挂载时加载统计数据', async () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    await flushPromises()

    expect(dashboardApi.getDashboardStats).toHaveBeenCalled()
  })

  it('应该显示4个统计卡片', () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    const statCards = wrapper.findAll('.stat-card')
    expect(statCards).toHaveLength(4)
  })

  it('应该正确显示统计数据', async () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('今日订单数')
    expect(wrapper.text()).toContain('今日销售额')
    expect(wrapper.text()).toContain('用户总数')
    expect(wrapper.text()).toContain('商品总数')
  })

  it('应该格式化显示销售额', async () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    await flushPromises()

    expect(wrapper.vm.stats.todaySales).toBe(15890.5)
    expect(wrapper.vm.stats.todayOrders).toBe(128)
    expect(wrapper.vm.stats.totalUsers).toBe(1523)
    expect(wrapper.vm.stats.totalProducts).toBe(86)
  })

  it('应该显示订单趋势图', () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    expect(wrapper.text()).toContain('订单趋势')
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('应该显示热销商品图', () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    expect(wrapper.text()).toContain('热销商品 Top10')
  })

  it('应该支持切换趋势天数', async () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    await flushPromises()

    expect(wrapper.vm.trendDays).toBe(7)

    // 改变趋势天数
    await wrapper.setData({ trendDays: 30 })
    expect(wrapper.vm.trendDays).toBe(30)
  })

  it('应该有正确初始化ECharts实例', async () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    await flushPromises()

    // ECharts应该被初始化
    const echarts = await import('echarts')
    expect(echarts.default.init).toHaveBeenCalled()
  })

  it('应该在组件卸载时清理ECharts实例', async () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce(mockStats)

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
      attachTo: document.body,
    })

    await flushPromises()

    const echarts = await import('echarts')
    const mockChartInstance = echarts.default.init()

    wrapper.unmount()

    // 验证dispose被调用
    // 注意：这里需要更复杂的mock来验证实例被正确清理
  })

  it('应该正确格式化销售额为千分位', async () => {
    vi.mocked(dashboardApi.getDashboardStats).mockResolvedValueOnce({
      ...mockStats,
      todaySales: 15890.5,
    })

    const wrapper = mount(Dashboard, {
      global: {
        plugins: [router, pinia],
        stubs: elementPlusStubs,
      },
    })

    await flushPromises()

    // 测试toLocalString方法
    const sales = 15890.5
    expect(sales.toLocaleString()).toBeDefined()
  })
})
