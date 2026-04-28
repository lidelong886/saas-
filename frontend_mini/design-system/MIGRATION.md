# 页面样式迁移指南

> 如何将现有页面迁移到统一设计系统

---

## 🎯 迁移步骤

### 1. 颜色替换

| 旧颜色 | 新颜色 | 用途 |
|--------|--------|------|
| `#64748B` | `var(--primary)` 或 `#2563EB` | 主色调 |
| `#F97316` | `var(--cta)` 或 `#F97316` | CTA按钮（保持不变） |
| `#00ff88` | `var(--success)` 或 `#10B981` | 成功/可用状态 |
| `#4f46e5`, `#6366f1` | `var(--primary)` 或 `#2563EB` | 统一为主蓝色 |
| `#0f172a` | `var(--gray-900)` 或 `#0F172A` | 深色文字 |
| `#1a1a1a` | `var(--gray-50)` 或 `#F8FAFC` | 背景色（不要用纯黑） |
| `#f0f2f8`, `#f4f6f9` | `var(--gray-50)` 或 `#F8FAFC` | 统一页面背景 |

### 2. 圆角替换

| 旧圆角 | 新圆角 | 用途 |
|--------|--------|------|
| `32rpx` | `12rpx` | 普通卡片 |
| `24rpx` | `16rpx` | 大卡片 |
| `16rpx` | `12rpx` | 普通卡片 |
| `12rpx` | `12rpx` | 保持不变 |
| `8rpx` | `8rpx` | 按钮（保持不变） |
| `50rpx`, `999rpx` | `9999rpx` | 完全圆角 |

### 3. 按钮高度统一

**所有按钮统一为 88rpx**

```css
/* ❌ 旧代码 */
.btn { height: 96rpx; }
.btn { height: 128rpx; }
.btn { height: 160rpx; }

/* ✅ 新代码 */
.btn { height: 88rpx; min-height: 88rpx; }
```

### 4. 阴影替换

```css
/* ❌ 旧代码 */
box-shadow: 0 4rpx 6rpx rgba(0, 0, 0, 0.1);
box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.04);
box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);

/* ✅ 新代码 */
box-shadow: var(--shadow-md);  /* 统一使用 */
```

### 5. 过渡动画统一

```css
/* ❌ 旧代码 */
transition: all 0.3s;
transition: all 200ms ease;
transition: color 0.3s;

/* ✅ 新代码 */
transition: all var(--duration) ease;  /* 统一 200ms */
```

---

## 📝 具体页面迁移示例

### 首页 (index/index.wxss)

#### 需要修改的地方：

1. **送单模式背景色**
```css
/* ❌ 旧代码 */
.container.delivery-mode {
  background: #1a1a1a;  /* 纯黑太刺眼 */
}

/* ✅ 新代码 */
.container.delivery-mode {
  background: var(--gray-900);  /* 使用深灰 #0F172A */
}
```

2. **荧光绿改为标准绿**
```css
/* ❌ 旧代码 */
color: #00ff88;
border: 2rpx solid #00ff88;
background: #00ff88;

/* ✅ 新代码 */
color: var(--success);
border: 2rpx solid var(--success);
background: var(--success);
```

3. **按钮高度统一**
```css
/* ❌ 旧代码 */
.scan-button-delivery {
  height: 160rpx;
}

/* ✅ 新代码 */
.scan-button-delivery {
  height: 120rpx;  /* 特殊大按钮可以保留，但不要超过 120rpx */
}
```

---

### 换电页面 (exchange/exchange.wxss)

#### 需要修改的地方：

1. **紫色渐变改为蓝色**
```css
/* ❌ 旧代码 */
background: linear-gradient(135deg, #4f46e5, #7c3aed);

/* ✅ 新代码 */
background: linear-gradient(135deg, var(--primary), var(--primary-light));
/* 或 */
background: linear-gradient(135deg, #2563EB, #3B82F6);
```

2. **步骤点颜色**
```css
/* ❌ 旧代码 */
.step-item.active .step-dot {
  background: linear-gradient(135deg, #6366f1, #7c3aed);
}

/* ✅ 新代码 */
.step-item.active .step-dot {
  background: var(--primary);
}
```

3. **确认按钮**
```css
/* ❌ 旧代码 */
.confirm-btn {
  height: 88rpx;  /* 这个是对的 */
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
}

/* ✅ 新代码 */
.confirm-btn {
  height: 88rpx;
  background: var(--cta);  /* 使用橙色 CTA */
}
```

---

### 电池列表 (battery/list.wxss)

#### 需要修改的地方：

1. **卡片圆角**
```css
/* ❌ 旧代码 */
.card {
  border-radius: 32rpx;  /* 太大 */
}

/* ✅ 新代码 */
.card {
  border-radius: var(--radius-md);  /* 12rpx */
}
```

2. **背景色统一**
```css
/* ❌ 旧代码 */
.container {
  background: #f4f6f9;
}

/* ✅ 新代码 */
.container {
  background: var(--gray-50);  /* #F8FAFC */
}
```

3. **状态标签颜色**
```css
/* ❌ 旧代码 */
.active-st { background: #eef2ff; color: #6366f1; }

/* ✅ 新代码 */
.active-st { background: #EFF6FF; color: var(--primary); }
```

---

## 🔧 快速查找替换

使用 VS Code 全局查找替换（Ctrl+Shift+H）：

### 颜色替换
```
查找: #00ff88
替换: var(--success)

查找: #4f46e5|#6366f1|#7c3aed
替换: var(--primary)
(使用正则表达式)

查找: #1a1a1a
替换: var(--gray-900)

查找: #f0f2f8|#f4f6f9
替换: var(--gray-50)
(使用正则表达式)
```

### 圆角替换
```
查找: border-radius: 32rpx
替换: border-radius: 12rpx

查找: border-radius: 24rpx
替换: border-radius: 16rpx
```

### 按钮高度
```
查找: height: (96|128|160)rpx
替换: height: 88rpx
(使用正则表达式)
```

---

## ✅ 迁移检查清单

每个页面迁移后检查：

- [ ] 所有颜色使用 CSS 变量或设计系统颜色
- [ ] 没有使用 `#00ff88`（荧光绿）
- [ ] 没有使用 `#4f46e5`、`#6366f1`（紫色）
- [ ] 没有使用 `#1a1a1a`（纯黑背景）
- [ ] 所有按钮高度为 88rpx
- [ ] 所有卡片圆角为 12rpx 或 16rpx
- [ ] 所有阴影使用 `var(--shadow-md)`
- [ ] 所有过渡动画为 `var(--duration)`
- [ ] 触摸目标 ≥ 88rpx × 88rpx

---

## 📱 测试建议

迁移后在真机测试：

1. **颜色对比度**：确保文字清晰可读
2. **触摸反馈**：所有按钮有明确的点击反馈
3. **动画流畅**：过渡动画不卡顿
4. **一致性**：所有页面视觉风格统一

---

**优先级：**
1. 首页（index）- 最高优先级
2. 换电页面（exchange）- 高优先级
3. 电池列表（battery/list）- 中优先级
4. 其他页面 - 逐步迁移
