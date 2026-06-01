<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { NButton, NSpace, NIcon } from 'naive-ui'
import { CloudOutline } from '@vicons/ionicons5'

const router = useRouter()
const authStore = useAuthStore()

if (authStore.isLoggedIn) {
  router.replace('/dashboard')
}
</script>

<template>
  <div class="landing">
    <div class="landing-content">
      <div class="logo">
        <n-icon size="48" color="#6366f1">
          <CloudOutline />
        </n-icon>
        <h1>CloudNest</h1>
      </div>
      <p class="tagline">你的个人云端工作台</p>
      <p class="desc">文件管理 · 笔记系统 · 任务看板 — 一站式管理你的数字生活</p>
      <n-space justify="center" size="large" style="margin-top: 32px">
        <n-button type="primary" size="large" @click="router.push('/register')">
          免费注册
        </n-button>
        <n-button size="large" @click="router.push('/login')">
          登录
        </n-button>
      </n-space>
    </div>
  </div>
</template>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.landing-content {
  text-align: center;
  color: white;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo h1 {
  font-size: 42px;
  font-weight: 700;
}

.tagline {
  font-size: 24px;
  font-weight: 300;
  margin-bottom: 8px;
}

.desc {
  font-size: 16px;
  opacity: 0.85;
}
</style>
