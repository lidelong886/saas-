# 图标文件说明

## 需要的图标文件

小程序需要以下8个图标文件（每个功能需要普通和选中两个状态）：

### 1. 首页图标
- `home.png` - 普通状态（灰色）
- `home-active.png` - 选中状态（绿色）

### 2. 地图图标
- `map.png` - 普通状态（灰色）
- `map-active.png` - 选中状态（绿色）

### 3. 订单图标
- `order.png` - 普通状态（灰色）
- `order-active.png` - 选中状态（绿色）

### 4. 我的图标
- `profile.png` - 普通状态（灰色）
- `profile-active.png` - 选中状态（绿色）

## 图标规格

- 尺寸：81px × 81px（推荐）
- 格式：PNG（支持透明背景）
- 颜色：
  - 普通状态：#7A7E83（灰色）
  - 选中状态：#3cc51f（绿色）

## 获取图标的方法

### 方法1：使用iconfont（推荐）
1. 访问 https://www.iconfont.cn/
2. 搜索关键词：home、map、order、user
3. 下载PNG格式，尺寸选择81px
4. 使用图片编辑工具修改颜色

### 方法2：使用在线图标生成器
1. 访问 https://icon-icons.com/
2. 搜索并下载对应图标
3. 调整尺寸和颜色

### 方法3：临时方案（开发测试用）
在微信开发者工具中，可以暂时注释掉 app.json 中的 tabBar 配置，
使用文字导航代替图标。

## 临时解决方案

如果暂时没有图标，可以修改 `app.json`，将 tabBar 的 iconPath 和 selectedIconPath 删除，
只保留 text 文字导航。

```json
"tabBar": {
  "color": "#7A7E83",
  "selectedColor": "#3cc51f",
  "list": [
    {
      "pagePath": "pages/index/index",
      "text": "首页"
    },
    {
      "pagePath": "pages/map/map",
      "text": "地图"
    },
    {
      "pagePath": "pages/order/list",
      "text": "订单"
    },
    {
      "pagePath": "pages/profile/profile",
      "text": "我的"
    }
  ]
}
```
