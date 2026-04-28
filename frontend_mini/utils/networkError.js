/**
 * 将微信 wx.request 失败信息转为用户可读文案（答辩演示 / 真机联调）
 */

function formatRequestFail(err) {
  const raw = err && err.errMsg ? String(err.errMsg) : ''
  const lower = raw.toLowerCase()

  if (
    raw.indexOf('url not in domain list') !== -1 ||
    raw.indexOf('合法域名') !== -1 ||
    lower.indexOf('not in domain') !== -1
  ) {
    return {
      toast: '域名校验：请见弹窗说明',
      modal: {
        title: '请求被微信拦截（域名）',
        content:
          '【开发者工具】右上角「详情」→「本地设置」→ 勾选「不校验合法域名、web-view…」。\n\n【真机】须在小程序后台配置 request 合法域名，或使用已备案 HTTPS 域名；本地调试可让老师用手机连热点 + 内网穿透（可选）。'
      }
    }
  }

  if (lower.indexOf('timeout') !== -1 || raw.indexOf('超时') !== -1) {
    return {
      toast: '请求超时',
      modal: {
        title: '请求超时',
        content: '请检查 Wi-Fi、后端是否卡顿，或稍后在「我的」页查看当前接口地址是否正确。'
      }
    }
  }

  if (
    lower.indexOf('fail') !== -1 ||
    lower.indexOf('connect') !== -1 ||
    lower.indexOf('refused') !== -1 ||
    lower.indexOf('aborted') !== -1 ||
    lower.indexOf('reset') !== -1
  ) {
    return {
      toast: '无法连接服务器',
      modal: {
        title: '连不上后端服务',
        content:
          '1. 演示电脑上运行「启动后端.bat」，浏览器能打开健康检查地址。\n\n2. 老师手机扫码预览时：把 frontend_mini/config.js 里的 apiBase 改成你电脑的局域网 IP（如 http://192.168.1.5:5000/api/v1），不要用 127.0.0.1。\n\n3. 手机与电脑同一 Wi-Fi；Windows 防火墙放行 5000 端口。'
      }
    }
  }

  const short = raw.length > 36 ? '网络异常(详见控制台)' : raw || '网络异常'
  return { toast: short, modal: null }
}

function formatHttpError(statusCode, data) {
  let msg = ''
  if (data && typeof data === 'object' && data.message) {
    msg = String(data.message)
  }
  const toast = msg ? (msg.length > 18 ? msg.slice(0, 18) + '…' : msg) : `请求失败(${statusCode})`
  return {
    toast,
    modal:
      msg && msg.length > 18
        ? { title: `HTTP ${statusCode}`, content: msg }
        : {
            title: `HTTP ${statusCode}`,
            content: msg || '服务器未返回说明。请确认后端已启动，且小程序 config.js 中端口与后端一致。'
          }
  }
}

function showDemoNetworkHelp(apiBase) {
  const base = apiBase || '（未读取到，请检查 app 是否已启动）'
  wx.showModal({
    title: '答辩演示 · 网络说明',
    content:
      `当前接口地址：\n${base}\n\n` +
      '【开发者工具】详情 → 本地设置 → 勾选「不校验合法域名…」\n\n' +
      '【老师手机预览】config.js 必须把 127.0.0.1 改成你电脑的局域网 IP（与后端端口一致），手机和电脑同一 Wi-Fi；电脑需运行后端并放行防火墙端口。\n\n' +
      '若仍失败，在电脑浏览器访问：\nhttp://你的IP:5000/api/v1/health\n确认返回 healthy。',
    showCancel: false,
    confirmText: '知道了'
  })
}

module.exports = {
  formatRequestFail,
  formatHttpError,
  showDemoNetworkHelp
}
