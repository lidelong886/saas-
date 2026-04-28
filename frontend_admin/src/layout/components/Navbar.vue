<template>
  <div class="navbar">
    <!-- 左侧 -->
    <div class="navbar-left">
      <el-button
        text
        class="toggle-btn"
        @click="toggleSidebar"
        :icon="sidebar.opened ? 'Fold' : 'Expand'"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <line v-if="sidebar.opened" x1="3" y1="12" x2="21" y2="12"/>
          <line v-if="sidebar.opened" x1="3" y1="6" x2="21" y2="6"/>
          <line v-if="sidebar.opened" x1="3" y1="18" x2="21" y2="18"/>
          <line v-if="!sidebar.opened" x1="3" y1="12" x2="21" y2="12"/>
          <line v-if="!sidebar.opened" x1="3" y1="6" x2="21" y2="6"/>
          <line v-if="!sidebar.opened" x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </el-button>

      <Breadcrumb />
    </div>

    <!-- 右侧 -->
    <div class="navbar-right">
      <!-- 搜索 -->
      <el-button text class="nav-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      </el-button>

      <!-- 通知 -->
      <el-dropdown trigger="click" placement="bottom-end">
        <el-button text class="nav-btn notif-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span class="notif-dot"></span>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu class="notif-menu">
            <div class="notif-header">
              <span class="notif-title">通知</span>
              <span class="notif-count">3</span>
            </div>
            <el-dropdown-item v-for="n in notifications" :key="n.id" class="notif-item">
              <div class="notif-dot-sm" :class="n.type"></div>
              <div class="notif-content">
                <div class="notif-text">{{ n.text }}</div>
                <div class="notif-time">{{ n.time }}</div>
              </div>
            </el-dropdown-item>
            <div class="notif-footer">查看全部</div>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- 全屏 -->
      <el-button text class="nav-btn" @click="toggleFullscreen">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
      </el-button>

      <!-- 用户 -->
      <el-dropdown trigger="click" placement="bottom-end">
        <div class="user-trigger">
          <el-avatar :size="32" class="user-avatar">管</el-avatar>
          <div class="user-info">
            <span class="user-name">管理员</span>
            <span class="user-role">Super Admin</span>
          </div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="chevron"><path d="m6 9 6 6 6-6"/></svg>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleProfile">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item @click="handleSettings">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>
              系统设置
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout" class="logout-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import Breadcrumb from './Breadcrumb'

export default {
  name: 'Navbar',
  components: { Breadcrumb },
  setup() {
    const store = useStore()
    const router = useRouter()
    const handleProfile = () => router.push('/profile')
    const handleSettings = () => router.push('/settings')
    const handleLogout = async () => {
      await ElMessageBox.confirm('确定退出登录？', '提示', { type: 'warning' })
      await store.dispatch('user/logout')
      router.push('/login')
    }
    const toggleSidebar = () => store.dispatch('app/toggleSideBar')
    const toggleFullscreen = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen()
      } else {
        document.exitFullscreen()
      }
    }
    return { handleProfile, handleSettings, handleLogout, toggleSidebar, toggleFullscreen }
  },
  computed: {
    ...mapGetters(['sidebar'])
  },
  data() {
    return {
      notifications: [
        { id: 1, type: 'info', text: '新用户注册：李明', time: '3分钟前' },
        { id: 2, type: 'success', text: '订单完成：#10086', time: '15分钟前' },
        { id: 3, type: 'warn', text: '电池电量低：B-008', time: '1小时前' }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px 0 16px;
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  &:hover { background: #f1f5f9; color: #0f172a; }
  cursor: pointer;
}

.nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  position: relative;
  cursor: pointer;
  &:hover { background: #f1f5f9; color: #0f172a; }
}

.notif-btn { position: relative; }
.notif-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid #fff;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 6px;

  &:hover { background: #f1f5f9; }
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
  border: none !important;
  color: #fff !important;
  font-size: 13px !important;
  font-weight: 700 !important;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  text-align: left;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.2;
}

.user-role {
  font-size: 11px;
  color: #94a3b8;
}

.chevron { color: #94a3b8; flex-shrink: 0; }

// 下拉菜单样式
:deep(.notif-menu) {
  width: 300px;
  padding: 0;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 40px rgba(0,0,0,0.12);
}

.notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid #f1f5f9;

  .notif-title { font-size: 14px; font-weight: 700; color: #0f172a; }
  .notif-count {
    background: #F97316;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.notif-item {
  display: flex !important;
  align-items: flex-start !important;
  gap: 10px;
  padding: 12px 16px !important;
  border-radius: 0 !important;
  height: auto !important;
  line-height: 1.5 !important;
}

.notif-dot-sm {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
  &.info { background: #64748B; }
  &.success { background: #10b981; }
  &.warn { background: #F97316; }
}

.notif-content {
  flex: 1;
}

.notif-text { font-size: 13px; color: #334155; font-weight: 500; }
.notif-time { font-size: 11px; color: #94a3b8; margin-top: 2px; }

.notif-footer {
  text-align: center;
  padding: 12px;
  font-size: 13px;
  color: #F97316;
  font-weight: 600;
  cursor: pointer;
  border-top: 1px solid #f1f5f9;
  &:hover { background: #f8fafc; }
}

.logout-item { color: #ef4444 !important; }
</style>
