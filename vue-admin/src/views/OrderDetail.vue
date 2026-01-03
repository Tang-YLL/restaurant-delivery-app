<template>
  <div class="order-detail">
    <el-page-header @back="goBack" content="订单详情" />

    <el-card class="detail-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag :type="getStatusType(order.status)">
            {{ getStatusText(order.status) }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ order.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(order.status)">
            {{ getStatusText(order.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户姓名">{{ order.userName }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ order.userPhone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ order.userAddress }}</el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ order.paymentMethod }}</el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ order.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="订单金额" :span="2">
          <span class="amount">¥{{ order.totalAmount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2" v-if="order.remark">
          {{ order.remark }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="actions">
        <el-button type="primary" @click="showStatusDialog">更新状态</el-button>
      </div>
    </el-card>

    <el-card class="items-card">
      <template #header>
        <span>商品列表</span>
      </template>

      <el-table :data="order.items" border>
        <el-table-column prop="productName" label="商品名称" />
        <el-table-column label="商品图片" width="100">
          <template #default="{ row }">
            <el-image
              :src="row.productImage"
              fit="cover"
              style="width: 60px; height: 60px"
              :preview-src-list="[row.productImage]"
            />
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价" width="120">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="subtotal" label="小计" width="120">
          <template #default="{ row }">
            ¥{{ row.subtotal }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 状态更新对话框 -->
    <el-dialog v-model="statusDialogVisible" title="更新订单状态" width="400px">
      <el-form :model="statusForm">
        <el-form-item label="订单状态">
          <el-select v-model="statusForm.status" placeholder="请选择状态">
            <el-option label="待付款" value="pending" />
            <el-option label="已付款" value="paid" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="delivered" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateStatus">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrderDetail, updateOrderStatus } from '../api/order'
import type { Order } from '../types'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const order = ref<Order>({
  id: 0,
  orderNo: '',
  userId: 0,
  userName: '',
  userPhone: '',
  userAddress: '',
  items: [],
  totalAmount: 0,
  status: 'pending',
  paymentMethod: '',
  createdAt: '',
  updatedAt: ''
})

const statusDialogVisible = ref(false)
const statusForm = reactive({
  status: ''
})

const loadOrderDetail = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const data = await getOrderDetail(id)
    order.value = data
    statusForm.status = data.status
  } catch (error) {
    console.error('Failed to load order detail:', error)
    ElMessage.error('加载订单详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const showStatusDialog = () => {
  statusForm.status = order.value.status
  statusDialogVisible.value = true
}

const handleUpdateStatus = async () => {
  try {
    await updateOrderStatus(order.value.id, statusForm.status)
    ElMessage.success('状态更新成功')
    statusDialogVisible.value = false
    loadOrderDetail()
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'warning',
    paid: 'success',
    shipped: 'primary',
    delivered: 'info',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待付款',
    paid: '已付款',
    shipped: '已发货',
    delivered: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

onMounted(() => {
  loadOrderDetail()
})
</script>

<style scoped>
.order-detail {
  padding: 20px;
}

.detail-card,
.items-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
}

.actions {
  margin-top: 20px;
}
</style>
