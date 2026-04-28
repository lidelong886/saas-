import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@/styles/index.scss'
import websocket from '@/utils/websocket'

// 创建应用实例
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(router)
app.use(store)
app.use(ElementPlus, {
  size: 'medium',
  zIndex: 3000
})

// 初始化 WebSocket 连接
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (token && to.path !== '/login') {
    websocket.connect()
  }
  next()
})

// 挂载应用
app.mount('#app')
