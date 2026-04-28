#!/bin/bash

# PowerNest 小程序样式统一迁移脚本
# 用途：批量替换所有页面的颜色、圆角、按钮高度等

echo "🎨 开始统一 PowerNest 小程序 UI 设计..."

# 定义要处理的目录
TARGET_DIR="c:/Users/lidelong/battery_saas_platform/frontend_mini/pages"

# 1. 颜色替换
echo "📝 步骤 1/5: 替换颜色..."

# 荧光绿 -> 标准绿
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#00ff88/var(--success)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#00cc6a/var(--success-light)/g' {} +

# 紫色 -> 蓝色
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#4f46e5/var(--primary)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#6366f1/var(--primary)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#7c3aed/var(--primary-light)/g' {} +

# 纯黑背景 -> 深灰
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#1a1a1a/var(--gray-900)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#2a2a2a/var(--gray-800)/g' {} +

# 背景色统一
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#f0f2f8/var(--gray-50)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#f4f6f9/var(--gray-50)/g' {} +

# 文字颜色
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#0f172a/var(--gray-900)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#1e293b/var(--gray-800)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#334155/var(--gray-700)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#475569/var(--gray-600)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#64748b/var(--gray-500)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#94a3b8/var(--gray-400)/g' {} +

# 边框颜色
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#e2e8f0/var(--gray-200)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#f1f5f9/var(--gray-100)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#F8FAFC/var(--gray-50)/g' {} +

# 成功色
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#10b981/var(--success)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#34d399/var(--success-light)/g' {} +

# 警告色
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#f59e0b/var(--warning)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#fbbf24/var(--warning-light)/g' {} +

# 危险色
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#ef4444/var(--danger)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#f87171/var(--danger-light)/g' {} +

# CTA 橙色（保持不变，但统一写法）
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/#F97316/var(--cta)/g' {} +

echo "✅ 颜色替换完成"

# 2. 圆角替换
echo "📝 步骤 2/5: 统一圆角..."

find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/border-radius: 32rpx/border-radius: var(--radius-md)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/border-radius: 24rpx/border-radius: var(--radius-lg)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/border-radius: 16rpx/border-radius: var(--radius-lg)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/border-radius: 12rpx/border-radius: var(--radius-md)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/border-radius: 8rpx/border-radius: var(--radius-sm)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/border-radius: 50rpx/border-radius: var(--radius-full)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/border-radius: 999rpx/border-radius: var(--radius-full)/g' {} +

echo "✅ 圆角统一完成"

# 3. 按钮高度统一
echo "📝 步骤 3/5: 统一按钮高度..."

find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/height: 96rpx/height: var(--btn-height)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/height: 128rpx/height: 120rpx/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/height: 160rpx/height: 120rpx/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/min-height: 88rpx/min-height: var(--btn-height)/g' {} +

echo "✅ 按钮高度统一完成"

# 4. 过渡动画统一
echo "📝 步骤 4/5: 统一过渡动画..."

find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/transition: all 0\.3s/transition: all var(--duration) ease/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/transition: all 200ms ease/transition: all var(--duration) ease/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/transition: color 0\.3s/transition: all var(--duration) ease/g' {} +

echo "✅ 过渡动画统一完成"

# 5. 间距统一
echo "📝 步骤 5/5: 统一间距..."

find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/padding: 24rpx/padding: var(--space-12)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/margin: 24rpx/margin: var(--space-12)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/margin-bottom: 24rpx/margin-bottom: var(--space-12)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/margin-bottom: 16rpx/margin-bottom: var(--space-8)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/gap: 16rpx/gap: var(--space-8)/g' {} +
find "$TARGET_DIR" -name "*.wxss" -type f -exec sed -i 's/gap: 24rpx/gap: var(--space-12)/g' {} +

echo "✅ 间距统一完成"

echo ""
echo "🎉 UI 统一迁移完成！"
echo ""
echo "📋 迁移总结："
echo "  ✅ 颜色已统一为设计系统配色"
echo "  ✅ 圆角已统一（12rpx/16rpx）"
echo "  ✅ 按钮高度已统一（88rpx）"
echo "  ✅ 过渡动画已统一（200ms）"
echo "  ✅ 间距已统一"
echo ""
echo "⚠️  请注意："
echo "  1. 检查所有页面是否正常显示"
echo "  2. 在真机上测试颜色对比度"
echo "  3. 确认所有按钮触摸反馈正常"
echo ""
echo "📚 参考文档："
echo "  - 设计系统: frontend_mini/design-system/MASTER.md"
echo "  - 迁移指南: frontend_mini/design-system/MIGRATION.md"
