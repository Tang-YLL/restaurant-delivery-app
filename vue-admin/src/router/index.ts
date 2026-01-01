import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../views/layout/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '数据统计', icon: 'DataAnalysis' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/Orders.vue'),
        meta: { title: '订单管理', icon: 'ShoppingCart' }
      },
      {
        path: 'orders/:id',
        name: 'OrderDetail',
        component: () => import('../views/OrderDetail.vue'),
        meta: { title: '订单详情', hidden: true }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/Products.vue'),
        meta: { title: '商品管理', icon: 'Goods' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/Categories.vue'),
        meta: { title: '分类管理', icon: 'Menu' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import('../views/Reviews.vue'),
        meta: { title: '评价管理', icon: 'ChatDotRound' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth !== false) {
    if (userStore.isLoggedIn) {
      next()
    } else {
      next('/login')
    }
  } else {
    if (to.path === '/login' && userStore.isLoggedIn) {
      next('/')
    } else {
      next()
    }
  }
})

export default router
