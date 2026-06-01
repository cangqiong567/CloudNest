import { ref, watch, onMounted } from 'vue'

const themeMode = ref(localStorage.getItem('theme') || 'light')
const isDark = ref(false)

function applyTheme(mode) {
  if (mode === 'system') {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  } else {
    isDark.value = mode === 'dark'
  }
  document.documentElement.classList.toggle('dark', isDark.value)
}

// 初始化
applyTheme(themeMode.value)

// 监听系统主题变化
if (window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (themeMode.value === 'system') {
      applyTheme('system')
    }
  })
}

export function useTheme() {
  const setTheme = (mode) => {
    themeMode.value = mode
    localStorage.setItem('theme', mode)
    applyTheme(mode)
  }

  const toggle = () => {
    const newMode = isDark.value ? 'light' : 'dark'
    setTheme(newMode)
  }

  return { isDark, themeMode, setTheme, toggle }
}
