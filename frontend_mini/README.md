# 电池租售平台 - 微信小程序

## 📱 项目说明

这是电池租售平台的微信小程序端，提供用户端的电池租赁、站点查找、订单管理等功能。

## 🚀 快速开始

### 1. 修改API地址（必须）

⚠️ **重要：小程序不支持 localhost，必须修改为你的电脑IP地址**

1. 查看你的电脑IP地址：
   ```bash
   ipconfig
   # 找到 IPv4 地址，例如：192.168.1.100
   ```

2. 修改 `app.js` 第24行：
   ```javascript
   // 修改前
   baseUrl: 'http://localhost:5000/api/v1'
   
   // 修改后（替换成你的IP）
   baseUrl: 'http://192.168.1.100:5000/api/v1'
   ```

### 2. 启动后端服务

确保后端服务正在运行：
```bash
# 在项目根目录运行
start_simple_fixed.bat
```

### 3. 打开微信开发者工具

1. 下载并安装微信开发者工具
   - 下载地址：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

2. 导入项目
   - 打开微信开发者工具
   - 点击"+"号，选择"导入项目"
   - 项目目录：选择 `frontend_mini` 文件夹
   - AppID：选择"测试号"（或使用你自己的AppID）
   - 项目名称：电池租售平台

3. 配置开发设置
   - 点击右上角"详情"
   - 勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"
   - 这样才能访问 http://192.168.x.x 的地址

4. 编译运行
   - 点击"编译"按钮
   - 查看控制台是否有错误

## 📂 项目结构

```
frontend_mini/
├── api/                    # API接口封装
│   ├── auth.js            # 认证相关
│   ├── battery.js         # 电池相关
│   ├── station.js         # 站点相关
│   ├── order.js           # 订单相关
│   └── user.js            # 用户相关
├── pages/                  # 页面
│   ├── index/             # 首页
│   ├── map/               # 地图页
│   ├── station/           # 站点相关
│   │   ├── list/          # 站点列表
│   │   └── detail/        # 站点详情
│   ├── battery/           # 电池相关
│   │   ├── scan/          # 扫码租电
│   │   ├── list/          # 电池列表
│   │   └── detail/        # 电池详情
│   ├── order/             # 订单相关
│   │   ├── list/          # 订单列表
│   │   ├── detail/        # 订单详情
│   │   └── create/        # 创建订单
│   └── profile/           # 个人中心
│       ├── profile/       # 我的页面
│       ├── settings/      # 设置
│       └── balance/       # 余额
├── utils/                  # 工具函数
│   ├── request.js         # 请求封装
│   └── util.js            # 通用工具
├── images/                 # 图片资源
├── app.js                  # 小程序入口
├── app.json                # 小程序配置
└── app.wxss                # 全局样式
```

## ✨ 主要功能

### 已实现功能

1. **首页**
   - 轮播图展示
   - 快捷操作入口
   - 附近站点展示
   - 统计信息展示

2. **地图页**
   - 显示附近站点
   - 地图标记
   - 站点详情弹窗
   - 导航功能

3. **站点功能**
   - 站点列表
   - 站点详情
   - 站点搜索
   - 站点筛选

4. **扫码租电**
   - 扫描二维码
   - 电池信息展示
   - 确认租用
   - 创建订单

5. **订单管理**
   - 订单列表
   - 订单筛选（全部/进行中/已完成/已取消）
   - 订单详情
   - 取消订单
   - 支付订单

6. **个人中心**
   - 用户信息展示
   - 账户余额
   - 统计信息
   - 功能菜单
   - 退出登录

### 待完善功能（占位页面）

以下功能已创建页面框架，显示"功能开发中"：
- 电池列表
- 电池详情
- 订单详情
- 创建订单
- 设置页面
- 余额充值

## 🔧 配置说明

### app.json 配置

```json
{
  "pages": [...],           // 页面路径
  "window": {...},          // 窗口配置
  "tabBar": {...},          // 底部导航栏
  "permission": {...},      // 权限配置
  "networkTimeout": {...}   // 网络超时配置
}
```

### 全局数据（app.js）

```javascript
globalData: {
  userInfo: null,           // 用户信息
  token: null,              // 登录令牌
  code: null,               // 微信登录code
  baseUrl: '...',           // API地址（需要修改）
  tenantId: 1               // 租户ID
}
```

## 🎨 样式说明

### 全局样式（app.wxss）

- 容器样式：`.container`, `.page-container`
- 按钮样式：`.btn-primary`, `.btn-secondary`, `.btn-danger`
- 卡片样式：`.card`, `.card-header`, `.card-title`
- 表单样式：`.form-item`, `.form-input`
- 状态标签：`.status-tag`, `.status-available`
- 列表样式：`.list-item`, `.list-item-title`
- 工具类：`.text-center`, `.flex`, `.mb-16`

### 颜色规范

- 主色：`#07c160`（绿色）
- 成功：`#52c41a`
- 警告：`#faad14`
- 危险：`#ff4d4f`
- 信息：`#1890ff`
- 文字：`#333333`（主要）、`#666666`（次要）、`#999999`（辅助）

## 📝 开发注意事项

### 1. API请求

所有API请求都通过 `utils/request.js` 封装，自动处理：
- Token认证
- 租户ID
- 错误提示
- 登录过期跳转

使用示例：
```javascript
const request = require('../../utils/request')

// GET请求
request.get('/station/list', { page: 1 })

// POST请求
request.post('/order/create', { battery_id: 1 })
```

### 2. 登录状态

检查登录状态：
```javascript
const token = wx.getStorageSync('token')
if (!token) {
  // 未登录，跳转登录页
}
```

### 3. 位置权限

使用地图和定位功能需要用户授权：
```javascript
wx.getLocation({
  type: 'gcj02',
  success: (res) => {
    // 获取位置成功
  },
  fail: () => {
    // 获取位置失败，引导用户授权
  }
})
```

### 4. 扫码功能

扫码功能需要在真机上测试：
```javascript
wx.scanCode({
  onlyFromCamera: true,
  success: (res) => {
    const code = res.result
    // 处理扫码结果
  }
})
```

## 🐛 常见问题

### Q1: 小程序提示"不在以下 request 合法域名列表中"

**解决**：
- 开发阶段：勾选"不校验合法域名"
- 正式发布：需要在微信公众平台配置服务器域名

### Q2: 小程序无法连接后端

**检查**：
1. 后端是否正在运行？
2. IP地址是否正确？
3. 手机和电脑是否在同一局域网？
4. 防火墙是否阻止了5000端口？

**解决**：
```bash
# Windows防火墙允许5000端口
netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=TCP localport=5000
```

### Q3: 底部导航栏没有图标

**说明**：
- 当前版本使用纯文字导航
- 如需图标，参考 `images/README.md` 添加图标文件

### Q4: 地图不显示

**原因**：需要配置地图key

**解决**：
1. 注册腾讯位置服务账号
2. 创建应用，获取key
3. 在小程序中配置key

## 📱 真机调试

1. 点击微信开发者工具的"预览"按钮
2. 用手机微信扫描二维码
3. 在真机上测试功能

**注意**：
- 扫码功能必须在真机上测试
- 定位功能在真机上更准确
- 真机需要和电脑在同一局域网

## 🎯 答辩演示建议

### 演示流程

1. **展示首页**
   - 轮播图
   - 快捷操作
   - 附近站点

2. **展示地图功能**
   - 查看附近站点
   - 点击站点标记
   - 导航功能

3. **展示扫码租电**
   - 扫描二维码
   - 查看电池信息
   - 确认租用

4. **展示订单管理**
   - 查看订单列表
   - 筛选订单
   - 订单操作

5. **展示个人中心**
   - 用户信息
   - 账户余额
   - 功能菜单

### 准备工作

- ✅ 提前测试所有功能
- ✅ 准备好演示数据
- ✅ 截图保存关键界面
- ✅ 准备好备用方案

## 📞 技术支持

如有问题，请查看：
1. `小程序运行指南.md` - 详细的运行指南
2. `images/README.md` - 图标文件说明
3. 微信开发者工具的控制台错误信息

## 📄 许可证

本项目仅用于学习和毕业设计，不用于商业用途。
