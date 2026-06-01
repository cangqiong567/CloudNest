<script setup>
import { computed } from 'vue'
import { darkTheme, NConfigProvider, NMessageProvider, NDialogProvider } from 'naive-ui'
import { useThemeStore } from './stores/theme'

const themeStore = useThemeStore()
const theme = computed(() => themeStore.isDark ? darkTheme : null)
</script>

<template>
  <NConfigProvider :theme="theme">
    <NMessageProvider>
      <NDialogProvider>
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 页面过渡动画 */
.page-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* 深色模式变量 */
.dark body {
  background: #1a1a2e;
  color: #e0e0e0;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.dark ::-webkit-scrollbar-thumb {
  background: #555;
}
</style>
