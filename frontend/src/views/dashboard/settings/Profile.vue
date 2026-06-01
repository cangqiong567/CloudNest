<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../../../stores/auth'
import api from '../../../api'
import {
  NCard, NForm, NFormItem, NInput, NButton, NAvatar, NSpace, NUpload, NIcon
} from 'naive-ui'
import { CameraOutline } from '@vicons/ionicons5'

const message = useMessage()
const authStore = useAuthStore()
const loading = ref(false)
const form = ref({ username: '', bio: '' })

onMounted(async () => {
  try {
    const { data } = await api.get('/users/profile')
    form.value.username = data.user.username
    form.value.bio = data.user.bio || ''
  } catch {}
})

async function handleUpdate() {
  loading.value = true
  try {
    const { data } = await api.put('/users/profile', form.value)
    authStore.user = data.user
    message.success('更新成功')
  } catch (err) {
    message.error(err.response?.data?.error || '更新失败')
  } finally {
    loading.value = false
  }
}

async function handleAvatarUpload({ file }) {
  const formData = new FormData()
  formData.append('avatar', file.file)
  try {
    const { data } = await api.post('/users/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    authStore.user.avatar_url = data.avatar_url
    message.success('头像上传成功')
  } catch (err) {
    message.error(err.response?.data?.error || '上传失败')
  }
}
</script>

<template>
  <n-card title="个人资料">
    <div style="display: flex; gap: 32px; flex-wrap: wrap">
      <div style="text-align: center">
        <n-avatar
          round
          :size="96"
          :src="authStore.user?.avatar_url || ''"
          style="background: #6366f1; font-size: 36px"
        >
          {{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}
        </n-avatar>
        <n-upload
          :show-file-list="false"
          :custom-request="handleAvatarUpload"
          accept="image/*"
          style="margin-top: 12px"
        >
          <n-button size="small" quaternary>
            <template #icon>
              <n-icon :component="CameraOutline" />
            </template>
            更换头像
          </n-button>
        </n-upload>
      </div>

      <div style="flex: 1; min-width: 280px">
        <n-form label-placement="left" label-width="80">
          <n-form-item label="用户名">
            <n-input v-model:value="form.username" placeholder="请输入用户名" />
          </n-form-item>
          <n-form-item label="邮箱">
            <n-input :value="authStore.user?.email" disabled />
          </n-form-item>
          <n-form-item label="个人简介">
            <n-input
              v-model:value="form.bio"
              type="textarea"
              placeholder="介绍一下自己..."
              :rows="3"
              :maxlength="500"
              show-count
            />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" :loading="loading" @click="handleUpdate">
              保存修改
            </n-button>
          </n-form-item>
        </n-form>
      </div>
    </div>
  </n-card>
</template>
