<script setup>
import { h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NMenu, NIcon } from 'naive-ui'
import {
  HomeOutline,
  FolderOutline,
  DocumentTextOutline,
  CheckmarkDoneOutline,
  SettingsOutline,
  CloudOutline,
  PersonOutline,
  ShieldOutline,
  PhonePortraitOutline,
  TrashOutline,
  ListOutline,
  CalendarOutline,
  GridOutline,
  ColorPaletteOutline,
} from '@vicons/ionicons5'

defineProps({ collapsed: Boolean })

const router = useRouter()
const route = useRoute()

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = [
  {
    label: '仪表盘',
    key: 'home',
    icon: renderIcon(HomeOutline),
  },
  {
    label: '文件管理',
    key: 'files',
    icon: renderIcon(FolderOutline),
    children: [
      { label: '全部文件', key: 'files', icon: renderIcon(FolderOutline) },
      { label: '回收站', key: 'files/trash', icon: renderIcon(TrashOutline) },
    ],
  },
  {
    label: '笔记系统',
    key: 'notes',
    icon: renderIcon(DocumentTextOutline),
  },
  {
    label: '任务看板',
    key: 'tasks',
    icon: renderIcon(CheckmarkDoneOutline),
    children: [
      { label: '看板视图', key: 'tasks/board', icon: renderIcon(GridOutline) },
      { label: '列表视图', key: 'tasks/list', icon: renderIcon(ListOutline) },
      { label: '日历视图', key: 'tasks/calendar', icon: renderIcon(CalendarOutline) },
    ],
  },
  {
    label: '设置',
    key: 'settings',
    icon: renderIcon(SettingsOutline),
    children: [
      { label: '个人资料', key: 'settings/profile', icon: renderIcon(PersonOutline) },
      { label: '账号安全', key: 'settings/account', icon: renderIcon(ShieldOutline) },
      { label: '设备管理', key: 'settings/devices', icon: renderIcon(PhonePortraitOutline) },
      { label: '界面偏好', key: 'settings/appearance', icon: renderIcon(ColorPaletteOutline) },
    ],
  },
]

function handleMenuUpdate(key) {
  if (key === 'home') {
    router.push('/dashboard')
  } else {
    router.push(`/dashboard/${key}`)
  }
}

function getActiveKey() {
  const path = route.path
  if (path === '/dashboard') return 'home'
  return path.replace('/dashboard/', '')
}
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-logo" :class="{ collapsed }">
      <n-icon size="28" color="#6366f1">
        <CloudOutline />
      </n-icon>
      <span v-if="!collapsed" class="logo-text">CloudNest</span>
    </div>

    <n-menu
      :collapsed="collapsed"
      :collapsed-width="64"
      :collapsed-icon-size="22"
      :options="menuOptions"
      :value="getActiveKey()"
      :default-expanded-keys="['files', 'tasks', 'settings']"
      @update:value="handleMenuUpdate"
    />
  </div>
</template>

<style scoped>
.sidebar {
  padding: 8px 0;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  margin-bottom: 8px;
}

.sidebar-logo.collapsed {
  justify-content: center;
  padding: 16px 0;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}
</style>
