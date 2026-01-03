import { defineStore } from 'pinia'
import { ref, onUnmounted } from 'vue'
import { ElNotification } from 'element-plus'
import type { Order } from '../types'

export const useWebSocketStore = defineStore('websocket', () => {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  let reconnectTimer: number | null = null

  // 连接WebSocket
  const connect = (token: string) => {
    if (ws.value) {
      return
    }

    const wsUrl = `ws://localhost:3000/ws?token=${token}`
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      console.log('WebSocket connected')
      connected.value = true
      reconnectAttempts.value = 0
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleMessage(data)
      } catch (e) {
        console.error('Failed to parse WebSocket message', e)
      }
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.value.onclose = () => {
      console.log('WebSocket disconnected')
      connected.value = false
      ws.value = null

      // 尝试重连
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectTimer = window.setTimeout(() => {
          reconnectAttempts.value++
          console.log(`Reconnecting... Attempt ${reconnectAttempts.value}`)
          connect(token)
        }, 3000)
      }
    }
  }

  // 处理消息
  const handleMessage = (data: any) => {
    if (data.type === 'new_order') {
      const order = data.order as Order
      ElNotification({
        title: '新订单',
        message: `订单号: ${order.orderNo}\n客户: ${order.userName}\n金额: ¥${order.totalAmount}`,
        type: 'success',
        duration: 0,
        onClick: () => {
          // 跳转到订单详情页
          window.location.href = `/orders/${order.id}`
        }
      })
    } else if (data.type === 'order_updated') {
      const order = data.order as Order
      ElNotification({
        title: '订单更新',
        message: `订单 ${order.orderNo} 状态已更新为 ${order.status}`,
        type: 'info',
        duration: 3000
      })
    }
  }

  // 发送消息
  const send = (data: any) => {
    if (ws.value && connected.value) {
      ws.value.send(JSON.stringify(data))
    }
  }

  // 断开连接
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    connected.value = false
  }

  // 组件卸载时断开连接
  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    connect,
    disconnect,
    send
  }
})
