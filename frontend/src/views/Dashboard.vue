<script setup>
import { NLayout, NLayoutSider, NLayoutContent } from 'naive-ui'
import { ref } from 'vue'
import Sidebar from '../components/layout/Sidebar.vue'
import Topbar from '../components/layout/Topbar.vue'

const collapsed = ref(false)
const mobileShow = ref(false)

function toggleSidebar() {
  if (window.innerWidth <= 768) {
    mobileShow.value = !mobileShow.value
  } else {
    collapsed.value = !collapsed.value
  }
}
</script>

<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider
      bordered
      :collapsed="collapsed"
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      :native-scrollbar="false"
      :style="{
        background: 'var(--n-color, #fff)',
        position: 'fixed',
        zIndex: 100,
        height: '100vh',
        left: mobileShow ? '0' : undefined,
        transform: mobileShow ? 'translateX(0)' : undefined,
      }"
      class="layout-sider"
    >
      <Sidebar :collapsed="collapsed" />
    </n-layout-sider>

    <n-layout :style="{ marginLeft: collapsed ? '64px' : '220px' }" class="main-layout">
      <n-layout-content :native-scrollbar="false" content-style="height: 100vh; display: flex; flex-direction: column;">
        <Topbar @toggle-sidebar="toggleSidebar" />
        <div style="flex: 1; padding: 20px; overflow: auto">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style>
/* 移动端遮罩 */
@media (max-width: 768px) {
  .layout-sider {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  .layout-sider.show {
    transform: translateX(0);
  }
  .main-layout {
    margin-left: 0 !important;
  }
}
</style>
