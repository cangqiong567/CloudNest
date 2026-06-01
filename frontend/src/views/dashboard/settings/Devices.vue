<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import {
  NCard, NList, NListItem, NButton, NTag, NSpace, NIcon, NEmpty, NPopconfirm
} from 'naive-ui'
import { DesktopOutline, PhonePortraitOutline, TrashOutline } from '@vicons/ionicons5'

const message = useMessage()
const devices = ref([])
const loginHistory = ref([])

onMounted(async () => {
  await loadDevices()
  await loadHistory()
})

async function loadDevices() {
  try {
    const { data } = await api.get('/users/devices')
    devices.value = data.devices
  } catch {}
}

async function loadHistory() {
  try {
    const { data } = await api.get('/users/login-history')
    loginHistory.value = data.records
  } catch {}
}

async function removeDevice(id) {
  try {
    await api.delete(`/users/devices/${id}`)
    message.success('设备已移除')
    await loadDevices()
  } catch (err) {
    message.error(err.response?.data?.error || '移除失败')
  }
}

function getDeviceIcon(name) {
  if (name && (name.includes('Android') || name.includes('iOS'))) return PhonePortraitOutline
  return DesktopOutline
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN')
}
</script>

<template>
  <n-space vertical size="large">
    <n-card title="信任设备">
      <n-list v-if="devices.length > 0" bordered>
        <n-list-item v-for="device in devices" :key="device.id">
          <template #prefix>
            <n-icon :component="getDeviceIcon(device.device_name)" size="24" />
          </template>
          <template #default>
            <div>
              <div style="font-weight: 500">{{ device.device_name }}</div>
              <div style="font-size: 12px; color: #999">
                最后使用：{{ formatTime(device.last_used_at) }}
              </div>
            </div>
          </template>
          <template #suffix>
            <n-popconfirm @positive-click="removeDevice(device.id)">
              <template #trigger>
                <n-button quaternary type="error" size="small">
                  <template #icon>
                    <n-icon :component="TrashOutline" />
                  </template>
                </n-button>
              </template>
              确定移除此设备？
            </n-popconfirm>
          </template>
        </n-list-item>
      </n-list>
      <n-empty v-else description="暂无信任设备" />
    </n-card>

    <n-card title="登录历史">
      <n-list v-if="loginHistory.length > 0" bordered>
        <n-list-item v-for="record in loginHistory" :key="record.id">
          <template #prefix>
            <n-icon :component="getDeviceIcon(record.user_agent)" size="24" />
          </template>
          <template #default>
            <div>
              <div style="font-weight: 500">
                {{ record.ip_address }}
                <n-tag v-if="record.is_new_device" type="warning" size="small" style="margin-left: 8px">
                  新设备
                </n-tag>
              </div>
              <div style="font-size: 12px; color: #999">
                {{ formatTime(record.login_at) }}
              </div>
            </div>
          </template>
        </n-list-item>
      </n-list>
      <n-empty v-else description="暂无登录记录" />
    </n-card>
  </n-space>
</template>
