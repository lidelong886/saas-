import { login, logout, getUserInfo } from '@/api/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { ElMessage } from 'element-plus'

const state = {
  token: getToken(),
  user: null,
  roles: [],
  permissions: []
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_USER: (state, user) => {
    state.user = user
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  },
  SET_PERMISSIONS: (state, permissions) => {
    state.permissions = permissions
  },
  CLEAR_USER: (state) => {
    state.token = ''
    state.user = null
    state.roles = []
    state.permissions = []
  }
}

const actions = {
  // 用户登录
  async login({ commit }, userInfo) {
    try {
      const { username, password } = userInfo
      const response = await login({ username: username.trim(), password })

      // axios 拦截器已将 axios 响应体 unwrap，直接取 response.data
      // 后端结构：{ code: 0, data: { token, admin } }
      const payload = (response && response.data !== undefined) ? response.data : response
      const token = payload?.token || payload?.access_token
      if (!token) {
        return Promise.reject(new Error('登录响应中未返回有效 token'))
      }

      commit('SET_TOKEN', token)
      setToken(token)

      // admin 字段来自后端 AdminAuthService.login()
      const userData = payload?.admin || payload?.user || payload
      commit('SET_USER', userData)

      return Promise.resolve(userData)
    } catch (error) {
      return Promise.reject(error)
    }
  },

  // 获取用户信息
  async getUserInfo({ commit, state }) {
    try {
      const response = await getUserInfo()
      // axios 拦截器已 unwrap，直接用 response
      const user = (response && response.data !== undefined) ? response.data : response

      commit('SET_USER', user)

      const roles = user?.roles || []
      const permissions = user?.permissions || []

      commit('SET_ROLES', roles)
      commit('SET_PERMISSIONS', permissions)

      return Promise.resolve(user)
    } catch (error) {
      return Promise.reject(error)
    }
  },

  // 用户登出
  async logout({ commit, dispatch }) {
    try {
      // 尝试调用后端登出，忽略 401 等错误（token 已过期时后端返回 401 是正常的）
      await logout().catch(() => {})
    } catch (e) {
      // 忽略后端登出失败
    }

    // 清除本地用户信息（无论后端登出是否成功）
    commit('CLEAR_USER')
    removeToken()

    // 重置路由
    try {
      dispatch('resetRoutes', null, { root: true })
    } catch (e) {
      // 忽略路由重置失败
    }

    return Promise.resolve()
  },

  // 前端登出
  async fedLogout({ commit }) {
    commit('CLEAR_USER')
    removeToken()
    return Promise.resolve()
  },

  // 重置token
  resetToken({ commit }) {
    commit('CLEAR_USER')
    removeToken()
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
