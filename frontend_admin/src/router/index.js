import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { getToken } from '@/utils/auth'
import { ElMessage } from 'element-plus'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', noAuth: true }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表板', icon: 'Odometer' }
      },
      {
        path: 'stations',
        name: 'Stations',
        component: () => import('@/views/stations/index.vue'),
        meta: { title: '站点管理', icon: 'Location' }
      },
      {
        path: 'batteries',
        name: 'Batteries',
        component: () => import('@/views/batteries/index.vue'),
        meta: { title: '电池管理', icon: 'Battery' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/orders/index.vue'),
        meta: { title: '订单管理', icon: 'DocumentCopy' }
      },
      {
        path: 'orders/:id',
        name: 'OrderDetail',
        component: () => import('@/views/orders/detail.vue'),
        meta: { title: '订单详情', hidden: true }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/index.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'tenants',
        name: 'Tenants',
        component: () => import('@/views/tenants/index.vue'),
        meta: { title: '租户管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'packages',
        name: 'Packages',
        component: () => import('@/views/packages/index.vue'),
        meta: { title: '套餐管理', icon: 'Tickets' }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/statistics/index.vue'),
        meta: { title: '数据统计', icon: 'TrendCharts' }
      },
      {
        path: 'exchanges',
        name: 'Exchanges',
        component: () => import('@/views/exchanges/index.vue'),
        meta: { title: '换电记录', icon: 'Switch' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/logs/index.vue'),
        meta: { title: '操作日志', icon: 'Document' }
      },
      {
        path: 'rbac/permissions',
        name: 'Permissions',
        component: () => import('@/views/rbac/permissions.vue'),
        meta: { title: '权限管理', icon: 'Lock' }
      },
      {
        path: 'rbac/roles',
        name: 'Roles',
        component: () => import('@/views/rbac/roles.vue'),
        meta: { title: '角色管理', icon: 'UserFilled' }
      },
      {
        path: 'rbac/admins',
        name: 'Admins',
        component: () => import('@/views/rbac/admins.vue'),
        meta: { title: '管理员管理', icon: 'Avatar' }
      },
      {
        path: 'faults',
        name: 'Faults',
        component: () => import('@/views/faults/index.vue'),
        meta: { title: '故障报修', icon: 'Tools' }
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('@/views/notifications/index.vue'),
        meta: { title: '消息通知', icon: 'Bell' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', noAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 开始进度条
  NProgress.start()

  // 设置页面标题
  document.title = `${to.meta.title || '电池SaaS平台'} - 管理后台`

  // 检查是否需要登录
  const token = getToken()
  const isLoginPage = to.path === '/login'
  const noAuth = to.meta.noAuth

  if (!noAuth && !token) {
    // 未登录且不是登录页面，跳转到登录页
    ElMessage.warning('请先登录')
    next('/login')
    NProgress.done()
    return
  }

  if (token && isLoginPage) {
    // 已登录且访问登录页面，跳转到首页
    next('/')
    NProgress.done()
    return
  }

  next()
})

router.afterEach(() => {
  // 完成进度条
  NProgress.done()
})

export default router
