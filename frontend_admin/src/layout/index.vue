<template>
  <div class="app-wrapper">
    <Sidebar
      v-if="sidebar.opened"
      class="sidebar-container"
    />

    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <Navbar class="navbar-container" />

      <!-- 主体内容 -->
      <div class="app-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'

export default {
  name: 'Layout',
  components: {
    Sidebar,
    Navbar
  },
  computed: {
    ...mapGetters(['sidebar'])
  }
}
</script>

<style lang="scss" scoped>
.app-wrapper {
  height: 100vh;
  display: flex;
}

.sidebar-container {
  width: 240px;
  height: 100%;
  flex-shrink: 0;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
}

.navbar-container {
  height: 64px;
  flex-shrink: 0;
  background-color: #ffffff;
}

.app-main {
  flex: 1;
  overflow: auto;
  background-color: #f8fafc;
  padding: 0;
}
</style>
