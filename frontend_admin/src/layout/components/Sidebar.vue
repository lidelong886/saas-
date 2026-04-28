<template>
  <div class="sidebar">
    <!-- Logo区域 -->
    <div class="sidebar-logo">
      <div class="logo-icon">
        <svg width="28" height="28" viewBox="0 0 56 56" fill="none">
          <rect width="56" height="56" rx="14" fill="rgba(99,102,241,0.2)"/>
          <path d="M28 10L14 20V36L28 46L42 36V20L28 10Z" stroke="#818cf8" stroke-width="2" stroke-linejoin="round"/>
          <circle cx="28" cy="28" r="5" fill="#818cf8"/>
        </svg>
      </div>
      <div class="logo-text-wrap">
        <span class="logo-text">PowerNest</span>
        <span class="logo-sub">Battery SaaS</span>
      </div>
    </div>

    <!-- 用户信息 -->
    <div class="user-info-bar">
      <el-avatar :size="36" class="user-avatar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </el-avatar>
      <div class="user-detail">
        <span class="user-name">管理员</span>
        <span class="user-role">Super Admin</span>
      </div>
    </div>

    <!-- 菜单区域 -->
    <div class="menu-scroll">
      <div class="menu-section-label">主菜单</div>
      <el-menu
        :default-active="$route.path"
        class="sidebar-menu"
        :collapse="!sidebar.opened"
        :collapse-transition="false"
        mode="vertical"
        background-color="transparent"
        text-color="#64748b"
        active-text-color="#f8fafc"
      >
        <template v-for="item in menuItems" :key="item.path">
          <el-menu-item
            v-if="!item.children"
            :index="item.path"
            @click="handleMenuClick(item)"
          >
            <div class="menu-item-inner">
              <div class="menu-icon" v-html="item.icon"></div>
              <span class="menu-label">{{ item.meta.title }}</span>
            </div>
          </el-menu-item>

          <el-sub-menu v-else :index="item.path">
            <template #title>
              <div class="menu-item-inner">
                <div class="menu-icon" v-html="item.icon"></div>
                <span class="menu-label">{{ item.meta.title }}</span>
              </div>
            </template>
            <el-menu-item
              v-for="child in item.children"
              :key="child.path"
              :index="child.path"
              @click="handleMenuClick(child)"
            >
              <div class="menu-item-inner sub">
                <span class="menu-label">{{ child.meta.title }}</span>
              </div>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>

      <div class="menu-section-label" style="margin-top: 24px">系统</div>
      <el-menu
        :default-active="$route.path"
        class="sidebar-menu"
        :collapse="!sidebar.opened"
        :collapse-transition="false"
        mode="vertical"
        background-color="transparent"
        text-color="#64748b"
        active-text-color="#f8fafc"
      >
        <el-menu-item index="/settings" @click="handleMenuClick({ path: '/settings', meta: { title: '系统设置' } })">
          <div class="menu-item-inner">
            <div class="menu-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            </div>
            <span class="menu-label">系统设置</span>
          </div>
        </el-menu-item>
        <el-menu-item index="/logs" @click="handleMenuClick({ path: '/logs', meta: { title: '操作日志' } })">
          <div class="menu-item-inner">
            <div class="menu-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
            </div>
            <span class="menu-label">操作日志</span>
          </div>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 底部：版本信息 -->
    <div class="sidebar-footer">
      <div class="version-info">
        <span class="version-dot"></span>
        <span class="version-text">v1.0.0</span>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Sidebar',
  setup() {
    const router = useRouter()
    const handleMenuClick = (item) => {
      router.push(item.path)
    }
    return { handleMenuClick }
  },
  computed: {
    ...mapGetters(['sidebar']),
    menuItems() {
      return [
        {
          path: '/dashboard',
          meta: { title: '仪表板' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>`
        },
        {
          path: '/stations',
          meta: { title: '站点管理' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>`
        },
        {
          path: '/batteries',
          meta: { title: '电池管理' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="18" height="11" rx="2"/><path d="M22 11v3"/></svg>`
        },
        {
          path: '/orders',
          meta: { title: '订单管理' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>`
        },
        {
          path: '/users',
          meta: { title: '用户管理' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>`
        },
        {
          path: '/tenants',
          meta: { title: '租户管理' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>`
        },
        {
          path: '/statistics',
          meta: { title: '数据统计' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>`
        },
        {
          path: '/faults',
          meta: { title: '故障报修' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`
        },
        {
          path: '/notifications',
          meta: { title: '消息通知' },
          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0f172a;
  width: 240px;
  border-right: 1px solid rgba(255,255,255,0.06);
  position: relative;
}

// Logo
.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

.logo-icon {
  flex-shrink: 0;
}

.logo-text-wrap {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.logo-text {
  font-size: 16px;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -0.3px;
  line-height: 1.2;
}

.logo-sub {
  font-size: 10px;
  color: #64748b;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

// 用户信息
.user-info-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

.user-avatar {
  background: rgba(100,116,139,0.2) !important;
  border: 1px solid rgba(100,116,139,0.3) !important;
  color: #64748B !important;
  flex-shrink: 0;
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #f1f5f9;
}

.user-role {
  font-size: 11px;
  color: #F97316;
  font-weight: 500;
}

// 菜单滚动区
.menu-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px 12px 0;
  scrollbar-width: thin;
  scrollbar-color: #1e293b transparent;

  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
}

.menu-section-label {
  font-size: 10px;
  font-weight: 700;
  color: #334155;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 0 8px;
  margin-bottom: 6px;
}

// 菜单
.sidebar-menu {
  border: none !important;
  background: transparent !important;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 42px;
    line-height: 42px;
    margin-bottom: 2px;
    border-radius: 10px;
    padding: 0 12px !important;
    color: #64748b;
    transition: all 0.2s;
    background: transparent !important;
    cursor: pointer;

    &:hover {
      background: rgba(255,255,255,0.06) !important;
      color: #94a3b8;
    }

    &.is-active {
      background: rgba(249,115,22,0.15) !important;
      color: #F97316 !important;

      .menu-icon svg { stroke: #F97316; }
    }
  }

  :deep(.el-sub-menu) {
    .el-menu {
      background: transparent !important;
      padding: 0 0 4px 0;
    }

    .el-menu-item {
      height: 36px;
      line-height: 36px;
      padding-left: 44px !important;
      font-size: 13px;
    }
  }
}

.menu-item-inner {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;

  .menu-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .menu-label {
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
  }

  &.sub .menu-label {
    font-size: 13px;
    font-weight: 400;
  }
}

// 底部
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
  cursor: default;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 6px;

  .version-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 6px #10b981;
    animation: pulse 2s ease-in-out infinite;
  }

  .version-text {
    font-size: 11px;
    color: #334155;
    font-weight: 500;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
