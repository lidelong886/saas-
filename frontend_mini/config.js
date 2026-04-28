// =====================================================================
// 网络配置说明
// ---------------------------------------------------------------------
// 模式 1 - 开发者工具调试：USE_TUNNEL = false, LAN_IP = 'localhost'
// 模式 2 - 局域网真机调试：USE_TUNNEL = false, LAN_IP = '你的局域网IP'
// 模式 3 - 内网穿透真机调试：USE_TUNNEL = true, TUNNEL_URL = 'cpolar给的地址'
// =====================================================================

// === 在这里切换模式 ===
const USE_TUNNEL = false                 // true = 用内网穿透, false = 用局域网
const TUNNEL_URL = 'https://36343c86.r28.cpolar.top' // cpolar/ngrok 给的公网地址
const LAN_IP     = '127.0.0.1'                 // 局域网模式用的 IP
const PORT       = 5000
// =====================

const apiBase = USE_TUNNEL
  ? `${TUNNEL_URL}/api/v1`
  : `http://${LAN_IP}:${PORT}/api/v1`

// 自动检测提示
const _info = wx && wx.getSystemInfoSync ? wx.getSystemInfoSync() : {}
const _onDevice = _info.platform && _info.platform !== 'devtools'
if (_onDevice && !USE_TUNNEL && (LAN_IP === '127.0.0.1' || LAN_IP === 'localhost')) {
  console.warn('[config] 真机模式下 LAN_IP 仍为 localhost，网络请求可能失败，请修改 config.js')
}

module.exports = {
  apiBase,
  tenantId: 1
}
