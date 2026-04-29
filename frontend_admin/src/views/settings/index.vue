<template>
  <div class="settings-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">系统设置</h1>
        <p class="page-subtitle">管理支付密钥与地图服务</p>
      </div>
    </div>

    <!-- 快捷统计卡片 -->
    <div class="status-chips">
      <div class="chip" :class="mapStatusClass">
        <span class="chip-dot"></span>
        <span class="chip-label">高德地图</span>
        <span class="chip-value">{{ mapSettings.amapKey ? '已配置' : '未配置' }}</span>
      </div>
      <div class="chip" :class="paymentStatusClass">
        <span class="chip-dot"></span>
        <span class="chip-label">微信支付</span>
        <span class="chip-value">{{ paymentSettings.wechatAppId ? '已配置' : '未配置' }}</span>
      </div>
    </div>

    <!-- 设置卡片 -->
    <div class="settings-grid">
      <!-- 支付设置 -->
      <div class="settings-card">
        <div class="card-header">
          <div class="card-icon payment-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
          </div>
          <div>
            <h3 class="card-title">支付设置</h3>
            <p class="card-desc">微信支付商户凭证（安全存储于数据库）</p>
          </div>
        </div>

        <div class="card-body">
          <div class="secure-note">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            凭证信息已加密存储，重启服务后依然有效
          </div>

          <div class="field-row">
            <label class="field-label">微信 AppID</label>
            <el-input
              v-model="paymentSettings.wechatAppId"
              :type="showAppId ? 'text' : 'password'"
              placeholder="wx 开头的应用唯一标识"
              class="modern-input"
            >
              <template #suffix>
                <button class="visibility-btn" @click="showAppId = !showAppId" type="button">
                  <svg v-if="!showAppId" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </template>
            </el-input>
          </div>

          <div class="field-row">
            <label class="field-label">微信商户号</label>
            <el-input
              v-model="paymentSettings.wechatMchId"
              :type="showMchId ? 'text' : 'password'"
              placeholder="微信支付商户号"
              class="modern-input"
            >
              <template #suffix>
                <button class="visibility-btn" @click="showMchId = !showMchId" type="button">
                  <svg v-if="!showMchId" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </template>
            </el-input>
          </div>
        </div>

        <div class="card-footer">
          <el-button type="primary" class="btn-primary" @click="savePaymentSettings" :loading="saving.payment">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            保存支付设置
          </el-button>
        </div>
      </div>

      <!-- 地图设置 -->
      <div class="settings-card">
        <div class="card-header">
          <div class="card-icon map-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
          </div>
          <div>
            <h3 class="card-title">地图设置</h3>
            <p class="card-desc">高德地图 API Key（控制站点地址解析）</p>
          </div>
        </div>

        <div class="card-body">
          <div class="secure-note">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Key 存储于数据库，重启服务不会丢失
          </div>

          <div class="field-row">
            <label class="field-label">高德地图 Key</label>
            <el-input
              v-model="mapSettings.amapKey"
              :type="showMapKey ? 'text' : 'password'"
              placeholder="请输入高德地图 Web API Key"
              class="modern-input"
            >
              <template #prefix>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </template>
              <template #suffix>
                <button class="visibility-btn" @click="showMapKey = !showMapKey" type="button">
                  <svg v-if="!showMapKey" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </template>
            </el-input>
          </div>

          <div class="tip-box">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <span>Key 需前往 <a href="https://console.amap.com/dev/key/app" target="_blank" class="tip-link">高德开放平台控制台</a> 申请 Web API Key，申请时需绑定 JS API 服务</span>
          </div>
        </div>

        <div class="card-footer">
          <el-button type="primary" class="btn-primary" @click="saveMapSettings" :loading="saving.map">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            保存地图设置
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '@/api/system'

export default {
  name: 'Settings',
  data() {
    return {
      saving: { payment: false, map: false },
      showAppId: false,
      showMchId: false,
      showMapKey: false,
      paymentSettings: {
        wechatAppId: '',
        wechatMchId: ''
      },
      mapSettings: {
        amapKey: ''
      }
    }
  },
  computed: {
    mapStatusClass() {
      return this.mapSettings.amapKey ? 'chip-ok' : 'chip-warn'
    },
    paymentStatusClass() {
      return this.paymentSettings.wechatAppId && this.paymentSettings.wechatMchId ? 'chip-ok' : 'chip-warn'
    }
  },
  mounted() {
    this.loadSettings()
  },
  methods: {
    applySettings(data) {
      if (!data) return
      this.paymentSettings = {
        wechatAppId: data.wechatAppId || '',
        wechatMchId: data.wechatMchId || ''
      }
      this.mapSettings = {
        amapKey: data.amapKey || ''
      }
    },
    async loadSettings() {
      try {
        const res = await getSettings()
        // axios 拦截器已自动 unwrap，外层 code=200，直接用 res
        if (res && (res.code === 0 || res.code === 200)) {
          this.applySettings(res.data || {})
        } else {
          ElMessage.warning('加载设置失败，请刷新页面重试')
        }
      } catch (e) {
        console.error('加载设置失败', e)
        ElMessage.error('加载设置失败: ' + (e?.message || e?.response?.data?.message || ''))
      }
    },
    async savePaymentSettings() {
      this.saving.payment = true
      try {
        const res = await updateSettings(this.paymentSettings)
        if (res && (res.code === 0 || res.code === 200)) {
          this.applySettings(res.data || {})
        }
        ElMessage.success('支付设置保存成功')
      } catch (e) {
        ElMessage.error('保存失败: ' + (e?.message || ''))
      } finally {
        this.saving.payment = false
      }
    },
    async saveMapSettings() {
      this.saving.map = true
      try {
        const res = await updateSettings(this.mapSettings)
        if (res && (res.code === 0 || res.code === 200)) {
          this.applySettings(res.data || {})
        }
        ElMessage.success('地图设置保存成功')
      } catch (e) {
        ElMessage.error('保存失败: ' + (e?.message || ''))
      } finally {
        this.saving.map = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.settings-page {
  padding: 28px 32px;
  max-width: 1100px;
}

/* ── 头部 ──────────────────────────────────────── */
.page-header {
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.3px;
  margin-bottom: 4px;
}
.page-subtitle { font-size: 14px; color: #94a3b8; }

/* ── 状态芯片 ─────────────────────────────────── */
.status-chips {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 50px;
  padding: 8px 16px;
  font-size: 13px;
}
.chip-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #cbd5e1;
  flex-shrink: 0;
}
.chip-ok .chip-dot { background: #10b981; box-shadow: 0 0 6px rgba(16,185,129,0.4); }
.chip-warn .chip-dot { background: #f59e0b; }
.chip-label { font-weight: 600; color: #64748b; }
.chip-value { font-weight: 600; color: #334155; }

/* ── 设置卡片网格 ──────────────────────────────── */
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.settings-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  transition: box-shadow 0.2s;
  &:hover { box-shadow: 0 8px 30px rgba(0,0,0,0.08); }
}

/* 地图卡全宽 */
.settings-card:last-child {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px 28px 20px;
  border-bottom: 1px solid #f1f5f9;
}
.card-icon {
  width: 44px; height: 44px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.payment-icon { background: #d1fae5; color: #10b981; }
.map-icon { background: #fef3c7; color: #f59e0b; }
.card-title { font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
.card-desc { font-size: 12px; color: #94a3b8; }

.card-body {
  padding: 20px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-footer {
  padding: 16px 28px 24px;
  border-top: 1px solid #f1f5f9;
}

/* ── 字段行 ──────────────────────────────────────── */
.field-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.field-unit-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.field-unit {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
  white-space: nowrap;
}

/* ── 输入框样式 ─────────────────────────────────── */
:deep(.el-input__wrapper),
:deep(.el-input__wrapper.is-focus) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0 !important;
  background: #f8fafc;
  padding: 8px 14px;
  &:hover { box-shadow: 0 0 0 1px #cbd5e1 !important; }
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}
:deep(.el-input-number) {
  .el-input__wrapper {
    padding: 0 12px;
  }
}
.visibility-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: #94a3b8;
  display: flex;
  &:hover { color: #64748b; }
}

/* ── 安全提示 ─────────────────────────────────── */
.secure-note {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 12px;
  color: #059669;
  font-weight: 500;
}

/* ── 提示框 ───────────────────────────────────── */
.tip-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 12px;
  color: #92400e;
  svg { flex-shrink: 0; margin-top: 2px; }
}
.tip-link {
  color: #6366f1;
  text-decoration: underline;
  font-weight: 600;
}

/* ── 主按钮 ───────────────────────────────────── */
.btn-primary {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
  &:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.4); transform: translateY(-1px); }
}

/* ── 响应式 ───────────────────────────────────── */
@media (max-width: 900px) {
  .settings-grid { grid-template-columns: 1fr; }
  .settings-card:last-child { grid-column: auto; }
  .settings-page { padding: 20px 16px; }
}
</style>
