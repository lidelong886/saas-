<template>
  <div class="login-page">
    <!-- 动态背景 -->
    <div class="bg-animation">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 左侧品牌区 -->
      <div class="brand-side">
        <div class="brand-content">
          <div class="brand-icon">
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
              <rect width="56" height="56" rx="16" fill="white" fill-opacity="0.15"/>
              <path d="M28 10L14 20V36L28 46L42 36V20L28 10Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
              <path d="M28 10V46M14 20L42 36M42 20L14 36" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>
              <circle cx="28" cy="28" r="5" fill="white" fill-opacity="0.8"/>
            </svg>
          </div>
          <h1 class="brand-title">PowerNest</h1>
          <p class="brand-subtitle">智能电池租赁 · SaaS 云平台</p>
          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-dot"></div>
              <span>实时电池监控</span>
            </div>
            <div class="feature-item">
              <div class="feature-dot"></div>
              <span>智能站点管理</span>
            </div>
            <div class="feature-item">
              <div class="feature-dot"></div>
              <span>多租户 SaaS 架构</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="form-side">
        <div class="form-header">
          <h2>欢迎回来 👋</h2>
          <p>请登录您的管理账户</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          size="large"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <div class="input-group">
              <div class="input-label">用户名</div>
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                :prefix-icon="UserIcon"
                class="modern-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-group">
              <div class="input-label">密码</div>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="LockIcon"
                show-password
                class="modern-input"
              />
            </div>
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            native-type="submit"
          >
            <span v-if="!loading">登 录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { h } from 'vue'

const UserIcon = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  width: '16', height: '16', viewBox: '0 0 24 24',
  fill: 'none', stroke: 'currentColor', 'stroke-width': '2',
  'stroke-linecap': 'round', 'stroke-linejoin': 'round'
}, [
  h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: '12', cy: '7', r: '4' })
])

const LockIcon = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  width: '16', height: '16', viewBox: '0 0 24 24',
  fill: 'none', stroke: 'currentColor', 'stroke-width': '2',
  'stroke-linecap': 'round', 'stroke-linejoin': 'round'
}, [
  h('rect', { x: '3', y: '11', width: '18', height: '11', rx: '2', ry: '2' }),
  h('path', { d: 'M7 11V7a5 5 0 0 1 10 0v4' })
])

export default {
  name: 'Login',
  components: { UserIcon, LockIcon },
  setup() {
    const store = useStore()
    const router = useRouter()
    return { store, router }
  },
  data() {
    return {
      loading: false,
      rememberMe: false,
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    async handleLogin() {
      try {
        await this.$refs.loginFormRef.validate()
        this.loading = true
        const { username, password } = this.loginForm
        await this.store.dispatch('user/login', { username, password })
        ElMessage.success({ message: '登录成功，欢迎回来！', duration: 2000 })
        this.router.push('/')
      } catch (error) {
        if (error !== 'validation_failed') {
          ElMessage.error('登录失败，请检查用户名和密码')
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
  position: relative;
  overflow: hidden;
  padding: 20px;
}

// 动态光球背景
.bg-animation {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;

  .orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.4;
    animation: float 20s ease-in-out infinite;
  }

  .orb-1 {
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, #6366f1 0%, transparent 70%);
    top: -150px;
    left: -100px;
    animation-delay: 0s;
  }

  .orb-2 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, #10b981 0%, transparent 70%);
    bottom: -100px;
    right: -50px;
    animation-delay: -7s;
    opacity: 0.3;
  }

  .orb-3 {
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, #f59e0b 0%, transparent 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-delay: -14s;
    opacity: 0.2;
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25%       { transform: translate(30px, -40px) scale(1.05); }
  50%       { transform: translate(-20px, 20px) scale(0.95); }
  75%       { transform: translate(40px, 30px) scale(1.02); }
}

// 登录卡片
.login-card {
  position: relative;
  z-index: 10;
  display: flex;
  width: 920px;
  max-width: 100%;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

// 左侧品牌区
.brand-side {
  width: 380px;
  flex-shrink: 0;
  background: linear-gradient(160deg, #6366f1 0%, #4f46e5 50%, #7c3aed 100%);
  padding: 60px 48px;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -30%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -40%;
    left: -20%;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
  }
}

.brand-content {
  position: relative;
  z-index: 2;
  color: #fff;
}

.brand-icon {
  margin-bottom: 24px;
}

.brand-title {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 15px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 48px;
  line-height: 1.6;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(255,255,255,0.85);
  font-weight: 500;

  .feature-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255,255,255,0.7);
    box-shadow: 0 0 8px rgba(255,255,255,0.5);
    flex-shrink: 0;
  }
}

// 右侧表单区
.form-side {
  flex: 1;
  padding: 56px 52px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.97);
}

.form-header {
  margin-bottom: 40px;

  h2 {
    font-size: 26px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
    letter-spacing: -0.3px;
  }

  p {
    font-size: 14px;
    color: #64748b;
  }
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;
  }
}

.input-group {
  width: 100%;
}

.input-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
  display: block;
}

.modern-input {
  :deep(.el-input__wrapper) {
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 0 0 1px #e2e8f0;
    background: #f8fafc;
    transition: all 0.2s;

    &:hover {
      box-shadow: 0 0 0 1px #cbd5e1;
      background: #fff;
    }

    &.is-focus {
      box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
      background: #fff;
    }
  }

  :deep(.el-input__inner) {
    font-size: 15px;
    &::placeholder { color: #94a3b8; }
  }
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;

  .forgot-link {
    font-size: 13px;
    color: #6366f1;
    font-weight: 500;
    &:hover { color: #4f46e5; }
  }
}

.login-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  color: #fff;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5);
  }

  &:active {
    transform: translateY(0);
  }
}

// 响应式
@media (max-width: 768px) {
  .login-card {
    flex-direction: column;
    width: 100%;
  }

  .brand-side {
    width: 100%;
    padding: 40px 32px;
    .brand-features { display: none; }
  }

  .form-side {
    padding: 40px 32px;
  }
}
</style>
