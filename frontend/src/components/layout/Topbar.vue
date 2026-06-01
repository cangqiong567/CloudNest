<script setup>
import { h } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../../stores/auth'
import { useThemeStore } from '../../stores/theme'
import { NButton, NIcon, NSpace, NAvatar, NDropdown } from 'naive-ui'
import { SunnyOutline, MoonOutline, LogOutOutline, PersonOutline, MenuOutline } from '@vicons/ionicons5'

const emit = defineEmits(['toggle-sidebar'])
const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()
const themeStore = useThemeStore()

function renderIcon(icon) {
  return () => h('span', { style: 'display: flex; align-items: center' }, [
    h(NIcon, null, { default: () => h(icon) })
  ])
}

const userDropdownOptions = [
  { label: '个人资料', key: 'profile', icon: renderIcon(PersonOutline) },
  { type: 'divider', key: 'd1' },
  { label: '退出登录', key: 'logout', icon: renderIcon(LogOutOutline) },
]

function handleUserDropdown(key) {
  if (key === 'profile') {
    router.push('/dashboard/settings/profile')
  } else if (key === 'logout') {
    authStore.logout()
    message.success('已退出登录')
    router.push('/login')
  }
}
</script>

<template>
  <div class="topbar">
    <n-button quaternary circle class="mobile-menu" @click="emit('toggle-sidebar')">
      <template #icon><n-icon :component="MenuOutline" /></template>
    </n-button>
    <div></div>
    <n-space align="center" size="medium">
      <n-button quaternary circle @click="themeStore.toggle()">
        <template #icon>
          <n-icon :component="themeStore.isDark ? SunnyOutline : MoonOutline" />
        </template>
      </n-button>

      <n-dropdown :options="userDropdownOptions" @select="handleUserDropdown">
        <n-button quaternary>
          <n-space align="center" size="small">
            <n-avatar :size="28" round style="background: #6366f1">
              {{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}
            </n-avatar>
            <span class="username-text">{{ authStore.user?.username || '用户' }}</span>
          </n-space>
        </n-button>
      </n-dropdown>
    </n-space>
  </div>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--n-border-color, #efeff5);
  background: var(--n-color, #fff);
}

.mobile-menu {
  display: none;
}

@media (max-width: 768px) {
  .mobile-menu {
    display: flex;
  }
  .username-text {
    display: none;
  }
}
</style>
