const getters = {
  sidebar: state => state.app.sidebar,
  device: state => state.app.device,
  size: state => state.app.size,
  language: state => state.app.language,
  token: state => state.user.token,
  user: state => state.user.user,
  roles: state => state.user.roles,
  permissions: state => state.user.permissions,
  avatar: state => state.user.user?.avatar,
  nickname: state => state.user.user?.nickname || state.user.user?.username
}

export default getters
