import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark')

  watch(isDark, (val) => {
    localStorage.setItem('theme', val ? 'dark' : 'light')
  })

  function toggle() {
    isDark.value = !isDark.value
  }

  return { isDark, toggle }
})
