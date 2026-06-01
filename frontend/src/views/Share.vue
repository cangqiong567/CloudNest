<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import axios from 'axios'
import { NCard, NButton, NIcon, NInput, NSpace, NResult } from 'naive-ui'
import { DownloadOutline, DocumentOutline, FolderOutline } from '@vicons/ionicons5'

const route = useRoute()
const message = useMessage()

const file = ref(null)
const share = ref(null)
const loading = ref(true)
const error = ref('')
const needPassword = ref(false)
const password = ref('')

onMounted(() => loadShare())

async function loadShare() {
  loading.value = true
  error.value = ''
  try {
    const code = route.params.code
    const pw = password.value ? `?password=${password.value}` : ''
    const { data } = await axios.get(`/api/v1/share/${code}${pw}`)
    file.value = data.file
    share.value = data.share
    needPassword.value = false
  } catch (err) {
    if (err.response?.data?.need_password) {
      needPassword.value = true
      error.value = ''
    } else {
      error.value = err.response?.data?.error || '加载失败'
    }
  } finally {
    loading.value = false
  }
}

async function downloadFile() {
  try {
    const response = await axios.get(`/api/v1/files/${file.value.id}/download`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = file.value.name
    a.click()
    window.URL.revokeObjectURL(url)
  } catch {
    message.error('下载失败')
  }
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>

<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f5f5; padding: 20px">
    <n-card style="max-width: 480px; width: 100%">
      <!-- 加载中 -->
      <div v-if="loading" style="text-align: center; padding: 40px 0; color: #999">加载中...</div>

      <!-- 需要密码 -->
      <div v-else-if="needPassword" style="text-align: center">
        <n-icon :size="48" color="#6366f1" style="margin-bottom: 16px">
          <DocumentOutline />
        </n-icon>
        <h3>此文件需要密码访问</h3>
        <n-input v-model:value="password" placeholder="请输入提取密码" style="margin: 16px 0" @keyup.enter="loadShare" />
        <n-button type="primary" block @click="loadShare">确认</n-button>
      </div>

      <!-- 错误 -->
      <n-result v-else-if="error" status="error" :title="error" style="padding: 20px 0" />

      <!-- 文件信息 -->
      <div v-else-if="file" style="text-align: center">
        <n-icon :size="48" :color="file.is_folder ? '#f59e0b' : '#6366f1'" style="margin-bottom: 16px">
          <component :is="file.is_folder ? FolderOutline : DocumentOutline" />
        </n-icon>
        <h2 style="margin-bottom: 8px">{{ file.name }}</h2>
        <p style="color: #999; margin-bottom: 24px">
          {{ file.is_folder ? '文件夹' : formatSize(file.file_size) }}
          <span v-if="share"> · {{ share.view_count }} 次查看</span>
        </p>
        <n-button v-if="!file.is_folder" type="primary" size="large" block @click="downloadFile">
          <template #icon><n-icon :component="DownloadOutline" /></template>
          下载文件
        </n-button>
      </div>
    </n-card>
  </div>
</template>
