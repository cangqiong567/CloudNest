import { ref, computed } from 'vue'
import zh from './zh'
import en from './en'

const messages = { zh, en }
const currentLocale = ref(localStorage.getItem('locale') || 'zh')

export function useI18n() {
  const locale = currentLocale

  const t = (key) => {
    const keys = key.split('.')
    let result = messages[locale.value]
    for (const k of keys) {
      if (result && typeof result === 'object') {
        result = result[k]
      } else {
        return key
      }
    }
    return result || key
  }

  const setLocale = (lang) => {
    locale.value = lang
    localStorage.setItem('locale', lang)
  }

  const localeOptions = [
    { label: '中文', value: 'zh' },
    { label: 'English', value: 'en' },
  ]

  return { locale, t, setLocale, localeOptions }
}
