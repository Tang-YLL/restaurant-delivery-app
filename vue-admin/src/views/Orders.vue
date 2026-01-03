<template>
  <div class="orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <el-button type="primary" @click="handleExport" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出CSV
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="订单号">
          <el-input
            v-model="queryForm.orderNo"
            placeholder="请输入订单号"
            clearable
            style="width: 200px"
            @keyup.enter="loadOrders"
          />
        </el-form-item>

        <el-form-item label="客户姓名">
          <el-input
            v-model="queryForm.userName"
            placeholder="请输入客户姓名"
            clearable
            style="width: 150px"
            @keyup.enter="loadOrders"
          />
        </el-form-item>

        <el-form-item label="联系电话">
          <el-input
            v-model="queryForm.userPhone"
            placeholder="请输入联系电话"
            clearable
            style="width: 150px"
            @keyup.enter="loadOrders"
          />
        </el-form-item>

        <el-form-item label="订单状态">
          <el-select v-model="queryForm.status" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="全部状态" value="" />
            <el-option label="待付款" value="pending">
              <el-tag type="warning" size="small">待付款</el-tag>
            </el-option>
            <el-option label="已付款" value="paid">
              <el-tag type="info" size="small">已付款</el-tag>
            </el-option>
            <el-option label="制作中" value="preparing">
              <el-tag type="primary" size="small">制作中</el-tag>
            </el-option>
            <el-option label="待取餐" value="ready">
              <el-tag type="success" size="small">待取餐</el-tag>
            </el-option>
            <el-option label="已完成" value="completed">
              <el-tag type="info" size="small">已完成</el-tag>
            </el-option>
            <el-option label="已取消" value="cancelled">
              <el-tag type="danger" size="small">已取消</el-tag>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="配送方式">
          <el-select v-model="queryForm.deliveryType" placeholder="全部" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="外卖配送" value="delivery" />
            <el-option label="到店自取" value="pickup" />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadOrders">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 订单列表 -->
      <el-table :data="orderList" border stripe v-loading="loading" class="orders-table">
        <el-table-column type="index" label="#" width="50" align="center" />

        <el-table-column prop="orderNo" label="订单号" width="170" fixed>
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row.id)" :underline="false">
              {{ row.orderNo }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column label="客户信息" width="150">
          <template #default="{ row }">
            <div class="customer-info">
              <div class="customer-name">{{ row.userName || '-' }}</div>
              <div class="customer-phone">{{ row.userPhone || '-' }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="totalAmount" label="订单金额" width="110" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.totalAmount }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="订单状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" :icon="getStatusIcon(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="deliveryType" label="配送方式" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.deliveryType === 'delivery' ? 'success' : 'warning'" size="small">
              {{ row.deliveryType === 'delivery' ? '外卖' : '自取' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="createdAt" label="下单时间" width="170" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.createdAt) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" fixed="right" width="180" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row.id)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-dropdown @command="(cmd) => handleStatusChange(row.id, cmd)">
              <el-button type="success" link>
                <el-icon><Edit /></el-icon>
                状态<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="paid">
                    <el-icon><Money /></el-icon>
                    已付款
                  </el-dropdown-item>
                  <el-dropdown-item command="preparing">
                    <el-icon><Loading /></el-icon>
                    制作中
                  </el-dropdown-item>
                  <el-dropdown-item command="ready">
                    <el-icon><Van /></el-icon>
                    待取餐
                  </el-dropdown-item>
                  <el-dropdown-item command="completed">
                    <el-icon><CircleCheck /></el-icon>
                    已完成
                  </el-dropdown-item>
                  <el-dropdown-item command="cancelled" divided>
                    <el-icon><CircleClose /></el-icon>
                    已取消
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryForm.page"
          v-model:page-size="queryForm.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="loadOrders"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download, Search, RefreshLeft, ArrowDown,
  View, Edit, Money, Loading, Van,
  CircleCheck, CircleClose, Clock,
  ShoppingBag, TakeawayBox, Bell
} from '@element-plus/icons-vue'
import { getOrderList, updateOrderStatus, exportOrders } from '../api/order'
import type { Order, OrderQuery } from '../types'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const exporting = ref(false)
const orderList = ref<Order[]>([])
const total = ref(0)
const dateRange = ref<[string, string]>([])

const queryForm = reactive<OrderQuery>({
  page: 1,
  pageSize: 10,
  orderNo: '',
  userName: '',
  userPhone: '',
  status: '',
  deliveryType: '',
  startDate: undefined,
  endDate: undefined
})

const loadOrders = async () => {
  loading.value = true
  try {
    const params = { ...queryForm }

    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.startDate = dateRange.value[0]
      params.endDate = dateRange.value[1]
    }

    // 移除空字符串参数
    Object.keys(params).forEach(key => {
      if (params[key as string] === '' || params[key as string] === undefined) {
        delete params[key as string]
      }
    })

    console.log('🔍 加载订单列表，参数:', params)

    const data = await getOrderList(params)

    console.log('✅ 订单列表响应:', data)
    console.log('📦 订单数量:', data.list?.length)
    console.log('📊 总数:', data.total)

    orderList.value = data.list
    total.value = data.total
  } catch (error) {
    console.error('❌ 加载订单失败:', error)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  Object.assign(queryForm, {
    page: 1,
    pageSize: 10,
    orderNo: '',
    userName: '',
    userPhone: '',
    status: '',
    deliveryType: '',
    startDate: undefined,
    endDate: undefined
  })
  dateRange.value = []
  loadOrders()
}

const handleView = (id: number) => {
  router.push(`/orders/${id}`)
}

const handleStatusChange = async (id: number, status: string) => {
  try {
    const statusText = getStatusText(status)
    await ElMessageBox.confirm(
      `确定要将订单状态更改为"${statusText}"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await updateOrderStatus(id, status)
    ElMessage.success('状态更新成功')
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '状态更新失败')
    }
  }
}

const handleExport = async () => {
  exporting.value = true
  try {
    const params = { ...queryForm }
    if (dateRange.value && dateRange.value.length === 2) {
      params.startDate = dateRange.value[0]
      params.endDate = dateRange.value[1]
    }

    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key as string] === '' || params[key as string] === undefined) {
        delete params[key as string]
      }
    })

    const blob = await exportOrders(params)

    // 创建下载链接
    const url = window.URL.createObjectURL(blob as any)
    const link = document.createElement('a')
    link.href = url
    link.download = `订单列表_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Failed to export orders:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const handlePageSizeChange = (pageSize: number) => {
  queryForm.page = 1
  queryForm.pageSize = pageSize
  loadOrders()
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'warning',
    paid: 'info',
    preparing: 'primary',
    ready: 'success',
    completed: 'info',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusIcon = (status: string) => {
  const iconMap: Record<string, any> = {
    pending: Clock,
    paid: Money,
    preparing: Loading,
    ready: Bell,
    completed: CircleCheck,
    cancelled: CircleClose
  }
  return iconMap[status]
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待付款',
    paid: '已付款',
    preparing: '制作中',
    ready: '待取餐',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.search-form .el-form-item {
  margin-bottom: 10px;
}

.orders-table {
  width: 100%;
}

.customer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.customer-name {
  font-weight: 500;
  color: #303133;
}

.customer-phone {
  font-size: 12px;
  color: #909399;
}

.amount {
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
