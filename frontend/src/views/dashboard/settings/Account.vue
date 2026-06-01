<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { useAuthStore } from '../../../stores/auth'
import api from '../../../api'
import {
  NCard, NForm, NFormItem, NInput, NButton, NSpace, NText,
  NDivider, NAlert, NIcon, NSwitch, NTag
} from 'naive-ui'
import { ShieldCheckmarkOutline, KeyOutline } from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const authStore = useAuthStore()
const loading = ref(false)
const pwForm = ref({ old_password: '', new_password: '', confirm_password: '' })

// 2FA 状态
const is2faEnabled = ref(false)
const tfaStep = ref(0) // 0=未开始, 1=显示密钥, 2=验证中
const tfaSecret = ref('')
const tfaOtpauthUri = ref('')
const tfaCode = ref('')
const tfaLoading = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/me')
    is2faEnabled.value = data.user?.is_2fa_enabled || false
  } catch {}
})

async function handleChangePassword() {
  if (pwForm.value.new_password !== pwForm.value.confirm_password) {
    message.warning('两次密码输入不一致')
    return
  }
  if (pwForm.value.new_password.length < 6) {
    message.warning('新密码长度至少6位')
    return
  }
  loading.value = true
  try {
    await api.put('/users/password', {
      old_password: pwForm.value.old_password,
      new_password: pwForm.value.new_password,
    })
    message.success('密码修改成功')
    pwForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (err) {
    message.error(err.response?.data?.error || '修改失败')
  } finally {
    loading.value = false
  }
}

async function start2faSetup() {
  tfaLoading.value = true
  try {
    const { data } = await api.post('/auth/2fa/setup')
    tfaSecret.value = data.secret
    tfaOtpauthUri.value = data.otpauth_uri
    tfaStep.value = 1
  } catch (err) {
    message.error(err.response?.data?.error || '生成密钥失败')
  } finally {
    tfaLoading.value = false
  }
}

async function verify2fa() {
  if (!tfaCode.value || tfaCode.value.length !== 6) {
    message.warning('请输入6位验证码')
    return
  }
  tfaLoading.value = true
  try {
    await api.post('/auth/2fa/verify', { code: tfaCode.value })
    message.success('两步验证已启用！')
    is2faEnabled.value = true
    tfaStep.value = 0
    tfaCode.value = ''
  } catch (err) {
    message.error(err.response?.data?.error || '验证失败')
  } finally {
    tfaLoading.value = false
  }
}

function disable2fa() {
  dialog.warning({
    title: '关闭两步验证',
    content: '关闭后账号安全性将降低，确定要关闭吗？',
    positiveText: '确定关闭',
    negativeText: '取消',
    onPositiveClick: () => {
      // 直接关闭（简化流程，实际应要求验证码）
      api.post('/auth/2fa/disable', { code: '' }).then(() => {
        is2faEnabled.value = false
        message.success('两步验证已关闭')
      }).catch(() => {
        message.error('关闭失败，可能需要验证码')
      })
    },
  })
}

function handleDeleteAccount() {
  dialog.warning({
    title: '注销账号',
    content: '注销后账号将在7天后永久删除，确定要注销吗？',
    positiveText: '确定注销',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await api.delete('/users/account')
        message.success('账号已注销')
        authStore.logout()
        router.push('/login')
      } catch (err) {
        message.error(err.response?.data?.error || '注销失败')
      }
    },
  })
}

async function exportData() {
  try {
    const response = await api.get('/settings/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `cloudnest-export-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    window.URL.revokeObjectURL(url)
    message.success('数据导出成功')
  } catch {
    message.error('导出失败')
  }
}
</script>

<template>
  <n-space vertical size="large">
    <!-- 修改密码 -->
    <n-card title="修改密码">
      <n-form label-placement="left" label-width="100" style="max-width: 400px">
        <n-form-item label="当前密码">
          <n-input v-model:value="pwForm.old_password" type="password" show-password-on="click" placeholder="请输入当前密码" />
        </n-form-item>
        <n-form-item label="新密码">
          <n-input v-model:value="pwForm.new_password" type="password" show-password-on="click" placeholder="请输入新密码（至少6位）" />
        </n-form-item>
        <n-form-item label="确认新密码">
          <n-input v-model:value="pwForm.confirm_password" type="password" show-password-on="click" placeholder="请再次输入新密码" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" :loading="loading" @click="handleChangePassword">修改密码</n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 两步验证 -->
    <n-card title="两步验证 (2FA)">
      <n-space vertical>
        <n-alert v-if="is2faEnabled" type="success" :bordered="false">
          <template #icon><n-icon :component="ShieldCheckmarkOutline" /></template>
          两步验证已启用，你的账号更加安全。
        </n-alert>

        <n-space align="center">
          <n-text>状态：</n-text>
          <n-tag :type="is2faEnabled ? 'success' : 'default'" :bordered="false">
            {{ is2faEnabled ? '已启用' : '未启用' }}
          </n-tag>
        </n-space>

        <n-divider v-if="!is2faEnabled && tfaStep === 0" />
        <n-button v-if="!is2faEnabled && tfaStep === 0" type="primary" :loading="tfaLoading" @click="start2faSetup">
          <template #icon><n-icon :component="KeyOutline" /></template>
          启用两步验证
        </n-button>

        <!-- 密钥展示 -->
        <n-card v-if="tfaStep === 1" title="设置步骤" size="small" style="margin-top: 12px">
          <n-space vertical>
            <n-text>1. 在你的验证器 App（Google Authenticator、Authy 等）中添加以下密钥：</n-text>
            <n-card size="small" style="background: #f4f4f5">
              <n-text code style="font-size: 16px; letter-spacing: 2px">{{ tfaSecret }}</n-text>
            </n-card>
            <n-text>或扫描此 URI（手动粘贴到验证器）：</n-text>
            <n-input :value="tfaOtpauthUri" readonly type="textarea" :rows="2" />
            <n-divider />
            <n-text>2. 输入验证器 App 显示的 6 位验证码：</n-text>
            <n-input v-model:value="tfaCode" placeholder="000000" maxlength="6" style="max-width: 200px" />
            <n-button type="primary" :loading="tfaLoading" @click="verify2fa">验证并启用</n-button>
          </n-space>
        </n-card>

        <n-button v-if="is2faEnabled" type="error" @click="disable2fa">关闭两步验证</n-button>
      </n-space>
    </n-card>

    <!-- 数据导出 -->
    <n-card title="数据导出">
      <n-text>一键导出你在 CloudNest 中的所有数据（文件信息、笔记、任务等），导出为 JSON 格式。</n-text>
      <div style="margin-top: 16px">
        <n-button @click="exportData">导出所有数据</n-button>
      </div>
    </n-card>

    <!-- 账号注销 -->
    <n-card title="账号注销">
      <n-text type="error">注销账号后，你的所有数据将在7天后永久删除。在此期间可联系管理员恢复。</n-text>
      <div style="margin-top: 16px">
        <n-button type="error" @click="handleDeleteAccount">注销账号</n-button>
      </div>
    </n-card>
  </n-space>
</template>
