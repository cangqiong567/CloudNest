<script setup>
import { NCard, NRadioGroup, NRadioButton, NSpace, NText, NDivider } from 'naive-ui'
import { useTheme } from '../../../composables/useTheme'
import { useI18n } from '../../../locales'

const { isDark, toggle, themeMode, setTheme } = useTheme()
const { locale, setLocale, localeOptions } = useI18n()

const themeOptions = [
  { label: '☀️ 浅色', value: 'light' },
  { label: '🌙 深色', value: 'dark' },
  { label: '💻 跟随系统', value: 'system' },
]

function handleThemeChange(val) {
  setTheme(val)
}
</script>

<template>
  <n-space vertical size="large">
    <n-card title="主题">
      <n-text depth="3" style="display: block; margin-bottom: 12px">选择你喜欢的界面主题</n-text>
      <n-radio-group :value="themeMode" @update:value="handleThemeChange">
        <n-space>
          <n-radio-button v-for="opt in themeOptions" :key="opt.value" :value="opt.value" :label="opt.label" />
        </n-space>
      </n-radio-group>
    </n-card>

    <n-card title="语言 / Language">
      <n-text depth="3" style="display: block; margin-bottom: 12px">切换界面语言</n-text>
      <n-radio-group :value="locale" @update:value="setLocale">
        <n-space>
          <n-radio-button v-for="opt in localeOptions" :key="opt.value" :value="opt.value" :label="opt.label" />
        </n-space>
      </n-radio-group>
    </n-card>
  </n-space>
</template>
