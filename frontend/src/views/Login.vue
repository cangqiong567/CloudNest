<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { NCard, NForm, NFormItem, NInput, NButton, NSpace, NIcon } from 'naive-ui'
import { CloudOutline, MailOutline, LockClosedOutline } from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const form = ref({ email: '', password: '' })
const loading = ref(false)

async function handleLogin() {
  if (!form.value.email || !form.value.password) {
    message.warning('请填写邮箱和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(form.value.email, form.value.password)
    message.success('登录成功')
    router.push('/dashboard')
  } catch (err) {
    message.error(err.response?.data?.error || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <n-card class="auth-card" :bordered="false">
      <div class="auth-header">
        <n-icon size="36" color="#6366f1">
          <CloudOutline />
        </n-icon>
        <h2>登录 CloudNest</h2>
      </div>

      <n-form @submit.prevent="handleLogin">
        <n-form-item label="邮箱">
          <n-input
            v-model:value="form.email"
            placeholder="请输入邮箱"
            size="large"
          >
            <template #prefix>
              <n-icon :component="MailOutline" />
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="密码">
          <n-input
            v-model:value="form.password"
            type="password"
            placeholder="请输入密码"
            show-password-on="click"
            size="large"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <n-icon :component="LockClosedOutline" />
            </template>
          </n-input>
        </n-form-item>

        <n-button
          type="primary"
          block
          size="large"
          :loading="loading"
          @click="handleLogin"
          style="margin-top: 8px"
        >
          登录
        </n-button>
      </n-form>

      <div class="auth-footer">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.auth-card {
  width: 400px;
  padding: 20px;
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
}

.auth-header h2 {
  margin-top: 12px;
  font-size: 22px;
  color: #333;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.auth-footer a {
  color: #6366f1;
  text-decoration: none;
}
</style>
