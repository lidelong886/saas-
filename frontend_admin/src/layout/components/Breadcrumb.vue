<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item v-for="(item, index) in breadcrumbList" :key="item.path">
      <router-link v-if="index < breadcrumbList.length - 1" :to="item.path">
        {{ item.meta.title }}
      </router-link>
      <span v-else>{{ item.meta.title }}</span>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'Breadcrumb',
  setup() {
    const route = useRoute()

    const breadcrumbList = computed(() => {
      const matched = route.matched.filter(item => item.meta && item.meta.title)
      return matched
    })

    return {
      breadcrumbList
    }
  }
}
</script>

<style lang="scss" scoped>
.el-breadcrumb {
  font-size: 14px;
  color: #606266;

  :deep(.el-breadcrumb__item) {
    .el-breadcrumb__inner {
      color: #606266;

      &:hover {
        color: #409eff;
      }
    }

    &:last-child .el-breadcrumb__inner {
      color: #303133;
      font-weight: 500;
    }
  }
}
</style>
