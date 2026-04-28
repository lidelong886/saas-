# PowerNest 小程序设计系统

> 统一、现代、生产级的 UI 设计系统

---

## 📚 文档导航

| 文档 | 用途 | 适合人群 |
|------|------|----------|
| [MASTER.md](./MASTER.md) | 完整设计规范（颜色、字体、间距、组件） | 设计师、开发者 |
| [GUIDE.md](./GUIDE.md) | 快速上手指南（常用示例、工具类） | 开发者 |
| [MIGRATION.md](./MIGRATION.md) | 页面迁移指南（旧代码改造） | 开发者 |
| [migrate.sh](./migrate.sh) | 自动迁移脚本（批量替换） | 开发者 |

---

## 🎯 设计原则

### 1. 统一性（Consistency）
- 所有页面使用相同的颜色、圆角、间距
- 统一的按钮高度（88rpx）
- 统一的过渡动画（200ms）

### 2. 可访问性（Accessibility）
- 颜色对比度符合 WCAG AA 标准（4.5:1）
- 触摸目标 ≥ 88rpx × 88rpx（44px × 44px）
- 清晰的焦点状态

### 3. 性能优先（Performance）
- 使用 CSS 变量减少重复代码
- 统一的过渡时间避免卡顿
- 轻量级阴影和动画

### 4. 场景适配（Context）
- 为外卖骑手优化（大按钮、清晰状态）
- 快速操作优先（扫码、导航）
- 电量状态一目了然

---

## 🎨 核心配色

```
主色调（蓝色）：#2563EB - 信任、专业、科技
强调色（橙色）：#F97316 - 行动、紧急、换电
成功色（绿色）：#10B981 - 电量充足、可用
警告色（黄色）：#F59E0B - 电量不足
危险色（红色）：#EF4444 - 电量危险
```

**为什么选择这套配色？**
- **蓝色**：传递信任感，适合物流配送场景
- **橙色**：醒目的行动色，引导用户快速操作
- **绿色**：直观表示电量充足、站点可用
- **黄/红**：清晰的警告层级，避免电量耗尽

---

## 📐 设计令牌（Design Tokens）

### 颜色
```css
--primary: #2563EB
--cta: #F97316
--success: #10B981
--warning: #F59E0B
--danger: #EF4444
--gray-50 ~ --gray-900
```

### 间距
```css
--space-4: 8rpx
--space-8: 16rpx
--space-12: 24rpx  /* 最常用 */
--space-16: 32rpx
```

### 圆角
```css
--radius-sm: 8rpx   /* 按钮 */
--radius-md: 12rpx  /* 卡片 */
--radius-lg: 16rpx  /* 大卡片 */
--radius-full: 9999rpx  /* 徽章 */
```

### 阴影
```css
--shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.04)
--shadow-md: 0 4rpx 12rpx rgba(0, 0, 0, 0.08)  /* 最常用 */
--shadow-lg: 0 8rpx 24rpx rgba(0, 0, 0, 0.12)
```

### 其他
```css
--btn-height: 88rpx  /* 统一按钮高度 */
--duration: 200ms    /* 统一过渡时间 */
```

---

## 🧩 核心组件

### 按钮（Button）
- **主要按钮**：橙色背景，白色文字
- **次要按钮**：透明背景，蓝色边框
- **危险按钮**：红色背景，白色文字
- **统一高度**：88rpx

### 卡片（Card）
- **背景**：白色
- **圆角**：12rpx
- **阴影**：0 4rpx 12rpx rgba(0, 0, 0, 0.08)
- **顶部色条**：可选 4rpx 色条表示状态

### 状态标签（Status Tag）
- **圆角**：完全圆角（9999rpx）
- **颜色**：根据状态使用对应背景色
- **字重**：600（semibold）

### 列表项（List Item）
- **最小高度**：88rpx
- **点击反馈**：opacity 0.95 + translateY(-2rpx)
- **过渡**：200ms

---

## 🚀 快速开始

### 1. 查看示例
最佳实践示例：`pages/index/index.wxss`

### 2. 使用 CSS 变量
```css
.my-button {
  background: var(--cta);
  height: var(--btn-height);
  border-radius: var(--radius-sm);
  transition: all var(--duration) ease;
}
```

### 3. 使用工具类
```html
<view class="flex justify-between align-center gap-8">
  <text class="text-lg text-bold text-dark">标题</text>
  <text class="text-sm text-muted">描述</text>
</view>
```

---

## 🔄 迁移现有页面

### 方法 1：自动迁移（推荐）
```bash
bash design-system/migrate.sh
```

### 方法 2：手动迁移
参考 [MIGRATION.md](./MIGRATION.md) 逐步替换

---

## ✅ 设计检查清单

开发新页面前，确保：

- [ ] 阅读 [GUIDE.md](./GUIDE.md) 快速上手指南
- [ ] 使用 CSS 变量而不是硬编码颜色
- [ ] 按钮高度统一为 88rpx
- [ ] 卡片圆角统一为 12rpx
- [ ] 触摸目标 ≥ 88rpx × 88rpx
- [ ] 过渡动画统一为 200ms
- [ ] 颜色对比度符合 WCAG AA
- [ ] 在真机上测试

---

## 🎯 设计目标

### 已解决的问题
✅ 颜色混乱（4种不同配色方案）  
✅ 圆角不统一（12rpx、16rpx、24rpx、32rpx）  
✅ 按钮高度不统一（88rpx、96rpx、128rpx、160rpx）  
✅ 字体大小随意使用  
✅ 阴影样式不一致  
✅ 过渡动画时间不统一  

### 设计系统优势
✅ **统一性**：所有页面视觉风格一致  
✅ **可维护性**：修改一处，全局生效  
✅ **开发效率**：使用工具类快速开发  
✅ **用户体验**：清晰的视觉层级和交互反馈  
✅ **可访问性**：符合无障碍标准  

---

## 📊 设计系统覆盖范围

### 已统一
- ✅ 全局样式（app.wxss）
- ✅ 首页（pages/index/index.wxss）
- ⏳ 换电页面（待迁移）
- ⏳ 电池列表（待迁移）
- ⏳ 其他页面（待迁移）

### 迁移优先级
1. **高优先级**：首页、换电页面、电池列表
2. **中优先级**：订单、支付、个人中心
3. **低优先级**：设置、帮助、关于

---

## 🛠️ 工具和资源

### 开发工具
- **VS Code**：推荐使用查找替换功能
- **微信开发者工具**：实时预览
- **真机调试**：测试颜色对比度和触摸反馈

### 设计工具
- **Figma**：可导出设计令牌
- **WebAIM Contrast Checker**：检查颜色对比度

### 参考资源
- **iOS Human Interface Guidelines**：触摸标准
- **Material Design**：组件设计参考
- **Tailwind CSS**：工具类命名参考

---

## 📝 更新日志

### v1.0 (2026-04-23)
- ✅ 创建完整设计系统
- ✅ 统一全局样式（app.wxss）
- ✅ 更新首页样式
- ✅ 创建迁移脚本和文档

---

## 🤝 贡献指南

### 添加新组件
1. 在 `MASTER.md` 中添加组件规范
2. 在 `app.wxss` 中添加全局样式
3. 在 `GUIDE.md` 中添加使用示例
4. 更新此文档的更新日志

### 修改设计令牌
1. 在 `app.wxss` 中修改 CSS 变量
2. 更新 `MASTER.md` 文档
3. 测试所有页面是否正常显示
4. 更新此文档的更新日志

---

## 📞 联系方式

有问题或建议？

- 查看文档：`design-system/` 目录
- 参考示例：`pages/index/index.wxss`
- 提交 Issue：项目仓库

---

**版本**：v1.0  
**更新日期**：2026-04-23  
**维护者**：PowerNest 开发团队
