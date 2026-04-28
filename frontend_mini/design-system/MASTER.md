# PowerNest 小程序设计系统 - Master

> 电车电池租售换电小程序 · 统一设计规范
> 适用于：外卖骑手、配送员等高频使用场景

---

## 🎨 核心配色方案

### 主色调（Primary）
```css
--primary: #2563EB;        /* 蓝色 - 信任、专业、科技 */
--primary-light: #3B82F6;  /* 浅蓝 */
--primary-dark: #1E40AF;   /* 深蓝 */
```

### 强调色（CTA / Action）
```css
--cta: #F97316;           /* 橙色 - 行动、紧急、换电 */
--cta-light: #FB923C;     /* 浅橙 */
--cta-dark: #EA580C;      /* 深橙 */
```

### 成功/可用（Success）
```css
--success: #10B981;       /* 绿色 - 电量充足、可用 */
--success-light: #34D399;
--success-bg: #ECFDF5;    /* 绿色背景 */
```

### 警告（Warning）
```css
--warning: #F59E0B;       /* 黄色 - 电量不足 */
--warning-light: #FBBF24;
--warning-bg: #FFFBEB;    /* 黄色背景 */
```

### 危险/紧急（Danger）
```css
--danger: #EF4444;        /* 红色 - 电量危险 */
--danger-light: #F87171;
--danger-bg: #FEF2F2;     /* 红色背景 */
```

### 中性色（Neutral）
```css
--gray-50: #F8FAFC;       /* 页面背景 */
--gray-100: #F1F5F9;      /* 卡片背景 */
--gray-200: #E2E8F0;      /* 边框 */
--gray-300: #CBD5E1;      /* 分隔线 */
--gray-400: #94A3B8;      /* 次要文字 */
--gray-500: #64748B;      /* 辅助文字 */
--gray-600: #475569;      /* 正文 */
--gray-700: #334155;      /* 标题 */
--gray-800: #1E293B;      /* 深色标题 */
--gray-900: #0F172A;      /* 最深文字 */
```

### 背景色
```css
--bg-page: #F8FAFC;       /* 页面背景 */
--bg-card: #FFFFFF;       /* 卡片背景 */
--bg-hover: #F1F5F9;      /* 悬停背景 */
```

---

## 📐 间距系统（Spacing）

```css
--space-4: 8rpx;
--space-8: 16rpx;
--space-12: 24rpx;
--space-16: 32rpx;
--space-20: 40rpx;
--space-24: 48rpx;
--space-32: 64rpx;
```

**使用规则：**
- 卡片内边距：24rpx (--space-12)
- 卡片间距：16rpx (--space-8)
- 页面边距：24rpx (--space-12)
- 元素间距：12rpx / 16rpx

---

## 🔤 字体系统（Typography）

### 字体家族
```css
font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
```

### 字号规范
```css
--text-xs: 20rpx;    /* 极小文字（徽章） */
--text-sm: 24rpx;    /* 小文字（辅助信息） */
--text-base: 28rpx;  /* 正文（默认） */
--text-lg: 32rpx;    /* 大文字（卡片标题） */
--text-xl: 36rpx;    /* 超大文字（价格、数字） */
--text-2xl: 40rpx;   /* 特大文字（页面标题） */
--text-3xl: 48rpx;   /* 巨大文字（电量百分比） */
```

### 字重规范
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### 行高
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

---

## 🎯 圆角系统（Border Radius）

```css
--radius-sm: 8rpx;     /* 小圆角（按钮、输入框） */
--radius-md: 12rpx;    /* 中圆角（卡片） */
--radius-lg: 16rpx;    /* 大圆角（大卡片） */
--radius-xl: 24rpx;    /* 超大圆角（特殊卡片） */
--radius-full: 9999rpx; /* 完全圆角（徽章、头像） */
```

**使用规则：**
- 普通卡片：12rpx
- 大卡片：16rpx
- 按钮：8rpx
- 徽章/标签：9999rpx（完全圆角）

---

## 🎭 阴影系统（Shadow）

```css
--shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);   /* 轻微阴影 */
--shadow-md: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);  /* 中等阴影（卡片） */
--shadow-lg: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);  /* 大阴影（浮动按钮） */
--shadow-xl: 0 12rpx 32rpx rgba(0, 0, 0, 0.16); /* 超大阴影（模态框） */
```

---

## 🔘 按钮规范（Buttons）

### 高度统一
```css
--btn-height: 88rpx;  /* 所有按钮统一高度（符合触摸标准 44px） */
```

### 按钮类型

#### 1. 主要按钮（Primary）
```css
background: #F97316;  /* 橙色 CTA */
color: #FFFFFF;
border-radius: 8rpx;
height: 88rpx;
font-size: 32rpx;
font-weight: 700;
box-shadow: 0 4rpx 12rpx rgba(249, 115, 22, 0.3);
```

#### 2. 次要按钮（Secondary）
```css
background: transparent;
color: #2563EB;
border: 2rpx solid #2563EB;
border-radius: 8rpx;
height: 88rpx;
font-size: 32rpx;
font-weight: 600;
```

#### 3. 危险按钮（Danger）
```css
background: #EF4444;
color: #FFFFFF;
border-radius: 8rpx;
height: 88rpx;
font-size: 32rpx;
font-weight: 700;
```

#### 4. 禁用按钮（Disabled）
```css
background: #E2E8F0;
color: #94A3B8;
border-radius: 8rpx;
height: 88rpx;
opacity: 0.6;
```

---

## 📦 卡片规范（Cards）

### 标准卡片
```css
background: #FFFFFF;
border-radius: 12rpx;
padding: 24rpx;
margin-bottom: 16rpx;
box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
```

### 卡片顶部色条（可选）
```css
/* 在卡片顶部添加 4rpx 色条表示状态 */
border-top: 4rpx solid #2563EB;  /* 蓝色 - 普通 */
border-top: 4rpx solid #F97316;  /* 橙色 - 重要 */
border-top: 4rpx solid #10B981;  /* 绿色 - 成功 */
border-top: 4rpx solid #F59E0B;  /* 黄色 - 警告 */
```

---

## 🏷️ 状态标签（Status Tags）

```css
/* 可用 */
.status-available {
  background: #ECFDF5;
  color: #059669;
  padding: 6rpx 16rpx;
  border-radius: 9999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

/* 使用中 */
.status-in-use {
  background: #EFF6FF;
  color: #2563EB;
}

/* 充电中 */
.status-charging {
  background: #FFFBEB;
  color: #D97706;
}

/* 维护中 */
.status-maintenance {
  background: #FEF2F2;
  color: #DC2626;
}

/* 离线 */
.status-offline {
  background: #F1F5F9;
  color: #64748B;
}
```

---

## 🎬 动画规范（Animation）

### 过渡时间
```css
--duration-fast: 150ms;    /* 快速交互 */
--duration-normal: 200ms;  /* 标准过渡 */
--duration-slow: 300ms;    /* 慢速过渡 */
```

### 缓动函数
```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
```

### 标准过渡
```css
transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
```

### 点击反馈
```css
.clickable:active {
  opacity: 0.9;
  transform: translateY(-2rpx);
}
```

---

## ♿ 无障碍规范（Accessibility）

### 触摸目标
- 最小触摸区域：88rpx × 88rpx（44px × 44px）
- 所有按钮、可点击元素必须满足此标准

### 颜色对比度
- 正文文字：4.5:1（WCAG AA）
- 大文字（≥32rpx）：3:1
- 使用的颜色组合已通过对比度测试

### 焦点状态
```css
.focusable:focus {
  outline: 4rpx solid rgba(37, 99, 235, 0.5);
  outline-offset: 2rpx;
}
```

---

## 📱 响应式规范

### 安全区域
```css
/* 顶部安全区域 */
padding-top: constant(safe-area-inset-top);
padding-top: env(safe-area-inset-top);

/* 底部安全区域 */
padding-bottom: constant(safe-area-inset-bottom);
padding-bottom: env(safe-area-inset-bottom);
```

### 固定底部按钮
```css
.fixed-bottom-btn {
  position: fixed;
  bottom: 32rpx;
  left: 24rpx;
  right: 24rpx;
  height: 88rpx;
  z-index: 100;
}
```

---

## 🚫 禁止使用（Anti-patterns）

### ❌ 不要使用的颜色
- ~~#00ff88~~（荧光绿 - 太刺眼）
- ~~#4f46e5~~（紫色 - 与品牌不符）
- ~~#1a1a1a~~（纯黑背景 - 对比度过高）

### ❌ 不要使用的圆角
- ~~32rpx~~（太大）
- ~~24rpx~~（除非特殊大卡片）

### ❌ 不要使用的按钮高度
- ~~96rpx、128rpx、160rpx~~（不统一）
- 统一使用 **88rpx**

### ❌ 不要使用 emoji 作为图标
- ❌ 📷、⚡、🔋
- ✅ 使用 SVG 图标或 iconfont

---

## ✅ 设计检查清单

在发布前检查：

- [ ] 所有颜色使用设计系统中的颜色
- [ ] 所有按钮高度为 88rpx
- [ ] 所有卡片圆角为 12rpx 或 16rpx
- [ ] 所有触摸目标 ≥ 88rpx × 88rpx
- [ ] 所有文字大小符合字体系统
- [ ] 所有过渡动画为 200ms
- [ ] 所有卡片使用统一阴影
- [ ] 没有使用 emoji 作为图标
- [ ] 颜色对比度符合 WCAG AA 标准

---

## 📚 参考资源

- **配色灵感**：蓝色（信任）+ 橙色（行动）适合物流配送场景
- **字体系统**：基于 iOS Human Interface Guidelines
- **触摸标准**：Apple iOS 44pt / Android 48dp
- **对比度检查**：WebAIM Contrast Checker

---

**版本**：v1.0  
**更新日期**：2026-04-23  
**适用范围**：PowerNest 小程序所有页面
