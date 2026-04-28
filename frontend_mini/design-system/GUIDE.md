# PowerNest 设计系统使用指南

> 快速上手统一设计系统

---

## 🚀 快速开始

### 1. 使用 CSS 变量

所有颜色、间距、圆角都已定义为 CSS 变量，直接使用即可：

```css
/* ✅ 推荐写法 */
.my-button {
  background: var(--cta);
  color: #ffffff;
  border-radius: var(--radius-sm);
  padding: var(--space-12);
  height: var(--btn-height);
  transition: all var(--duration) ease;
}

/* ❌ 不推荐写法 */
.my-button {
  background: #F97316;
  color: #ffffff;
  border-radius: 8rpx;
  padding: 24rpx;
  height: 88rpx;
  transition: all 200ms ease;
}
```

---

## 🎨 常用颜色速查

### 主色调（蓝色）
```css
var(--primary)        /* #2563EB - 主蓝色 */
var(--primary-light)  /* #3B82F6 - 浅蓝 */
var(--primary-dark)   /* #1E40AF - 深蓝 */
```

**使用场景：** 导航、链接、次要按钮、图标

### 强调色（橙色）
```css
var(--cta)            /* #F97316 - 行动橙 */
var(--cta-light)      /* #FB923C - 浅橙 */
var(--cta-dark)       /* #EA580C - 深橙 */
```

**使用场景：** 主要按钮、价格、重要提示、换电按钮

### 状态色
```css
var(--success)        /* #10B981 - 成功/可用 */
var(--warning)        /* #F59E0B - 警告/电量不足 */
var(--danger)         /* #EF4444 - 危险/紧急 */
```

### 中性色（灰色）
```css
var(--gray-50)        /* #F8FAFC - 页面背景 */
var(--gray-100)       /* #F1F5F9 - 卡片背景 */
var(--gray-200)       /* #E2E8F0 - 边框 */
var(--gray-400)       /* #94A3B8 - 次要文字 */
var(--gray-500)       /* #64748B - 辅助文字 */
var(--gray-700)       /* #334155 - 标题 */
var(--gray-900)       /* #0F172A - 深色文字 */
```

---

## 📏 常用间距速查

```css
var(--space-4)        /* 8rpx */
var(--space-8)        /* 16rpx */
var(--space-12)       /* 24rpx - 最常用 */
var(--space-16)       /* 32rpx */
var(--space-20)       /* 40rpx */
```

**使用建议：**
- 卡片内边距：`var(--space-12)`
- 卡片间距：`var(--space-8)`
- 元素间距：`var(--space-8)` 或 `var(--space-12)`

---

## 🔘 常用圆角速查

```css
var(--radius-sm)      /* 8rpx - 按钮、输入框 */
var(--radius-md)      /* 12rpx - 普通卡片 */
var(--radius-lg)      /* 16rpx - 大卡片 */
var(--radius-full)    /* 9999rpx - 徽章、标签 */
```

---

## 🎯 常见组件示例

### 1. 标准按钮

```css
.btn-primary {
  background: var(--cta);
  color: #ffffff;
  height: var(--btn-height);
  border-radius: var(--radius-sm);
  font-size: 32rpx;
  font-weight: 700;
  transition: all var(--duration) ease;
}

.btn-primary:active {
  opacity: 0.9;
  transform: translateY(-2rpx);
}
```

### 2. 标准卡片

```css
.card {
  background: #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-12);
  margin-bottom: var(--space-8);
  box-shadow: var(--shadow-md);
  transition: all var(--duration) ease;
}

.card:active {
  opacity: 0.95;
  transform: translateY(-2rpx);
}
```

### 3. 状态标签

```css
.status-tag {
  display: inline-flex;
  padding: 6rpx 16rpx;
  border-radius: var(--radius-full);
  font-size: 22rpx;
  font-weight: 600;
}

.status-available {
  background: var(--success-bg);
  color: #059669;
}
```

### 4. 列表项

```css
.list-item {
  display: flex;
  align-items: center;
  padding: var(--space-12);
  background: #ffffff;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-8);
  min-height: var(--btn-height);
  transition: all var(--duration) ease;
}

.list-item:active {
  opacity: 0.95;
  transform: translateY(-2rpx);
}
```

---

## 🎭 常用工具类

### Flex 布局
```html
<view class="flex justify-between align-center gap-8">
  <view>左侧内容</view>
  <view>右侧内容</view>
</view>
```

### 文字样式
```html
<text class="text-lg text-bold text-dark">标题</text>
<text class="text-sm text-muted">描述文字</text>
<text class="text-xl text-cta">¥99</text>
```

### 间距
```html
<view class="mt-12 mb-8 px-12">内容</view>
```

### 圆角和阴影
```html
<view class="rounded shadow">卡片</view>
```

---

## 📱 响应式适配

### 安全区域
```html
<view class="safe-area-top">顶部内容</view>
<view class="safe-area-bottom">底部内容</view>
```

### 固定底部按钮
```css
.fixed-bottom-btn {
  position: fixed;
  bottom: var(--space-16);
  left: var(--space-12);
  right: var(--space-12);
  height: var(--btn-height);
  z-index: 100;
}
```

---

## ✅ 开发检查清单

每次开发新页面或组件时，检查：

- [ ] 使用 CSS 变量而不是硬编码颜色
- [ ] 按钮高度为 `var(--btn-height)` (88rpx)
- [ ] 卡片圆角为 `var(--radius-md)` (12rpx)
- [ ] 触摸目标 ≥ 88rpx × 88rpx
- [ ] 过渡动画为 `var(--duration)` (200ms)
- [ ] 点击反馈：`:active { opacity: 0.9; transform: translateY(-2rpx); }`
- [ ] 使用工具类而不是重复写样式

---

## 🚫 常见错误

### ❌ 错误示例

```css
/* 1. 硬编码颜色 */
.btn { background: #F97316; }

/* 2. 不统一的圆角 */
.card { border-radius: 32rpx; }

/* 3. 不统一的按钮高度 */
.btn { height: 96rpx; }

/* 4. 硬编码间距 */
.card { padding: 24rpx; }

/* 5. 不统一的过渡时间 */
.btn { transition: all 0.3s; }
```

### ✅ 正确示例

```css
/* 1. 使用 CSS 变量 */
.btn { background: var(--cta); }

/* 2. 统一圆角 */
.card { border-radius: var(--radius-md); }

/* 3. 统一按钮高度 */
.btn { height: var(--btn-height); }

/* 4. 使用间距变量 */
.card { padding: var(--space-12); }

/* 5. 统一过渡时间 */
.btn { transition: all var(--duration) ease; }
```

---

## 🎨 配色使用建议

### 页面背景
```css
background: var(--gray-50);  /* 浅灰背景 */
```

### 卡片背景
```css
background: #ffffff;  /* 白色卡片 */
```

### 主要按钮
```css
background: var(--cta);  /* 橙色 - 行动按钮 */
```

### 次要按钮
```css
background: transparent;
border: 2rpx solid var(--primary);
color: var(--primary);
```

### 文字颜色
```css
color: var(--gray-700);  /* 标题 */
color: var(--gray-500);  /* 正文 */
color: var(--gray-400);  /* 次要文字 */
```

### 状态颜色
```css
/* 成功/可用 */
color: var(--success);

/* 警告/电量不足 */
color: var(--warning);

/* 危险/紧急 */
color: var(--danger);
```

---

## 📚 更多资源

- **完整设计系统**：`design-system/MASTER.md`
- **迁移指南**：`design-system/MIGRATION.md`
- **全局样式**：`app.wxss`

---

## 💡 提示

1. **优先使用工具类**：避免重复写样式
2. **保持一致性**：所有页面使用相同的设计令牌
3. **测试真机**：确保颜色对比度和触摸反馈
4. **参考首页**：`pages/index/index.wxss` 是最佳实践示例

---

**有问题？** 查看 `design-system/MASTER.md` 获取完整文档
