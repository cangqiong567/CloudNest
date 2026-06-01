<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import {
  NCard, NButton, NSpace, NIcon, NInput, NTag, NSelect,
  NModal, NList, NListItem, NDivider, NDropdown
} from 'naive-ui'
import {
  ArrowBackOutline, SaveOutline, TimeOutline,
  DownloadOutline, EllipsisVerticalOutline
} from '@vicons/ionicons5'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const note = ref(null)
const title = ref('')
const content = ref('')
const saving = ref(false)
const showVersions = ref(false)
const versions = ref([])
const saveTimer = ref(null)
const lastSaved = ref('')

const noteId = ref(route.params.id)

onMounted(async () => {
  await loadNote()
})

onBeforeUnmount(() => {
  if (saveTimer.value) clearTimeout(saveTimer.value)
  autoSave()
})

async function loadNote() {
  try {
    const { data } = await api.get(`/notes/${noteId.value}`)
    note.value = data.note
    title.value = data.note.title
    content.value = data.note.content || ''
    lastSaved.value = data.note.updated_at
  } catch {
    message.error('加载失败')
    router.push('/dashboard/notes')
  }
}

// 内容变更时自动保存（防抖 2 秒）
watch([title, content], () => {
  if (saveTimer.value) clearTimeout(saveTimer.value)
  saveTimer.value = setTimeout(autoSave, 2000)
})

async function autoSave() {
  if (!note.value) return
  if (title.value === note.value.title && content.value === note.value.content) return

  saving.value = true
  try {
    const { data } = await api.put(`/notes/${noteId.value}`, {
      title: title.value,
      content: content.value,
    })
    note.value = data.note
    lastSaved.value = data.note.updated_at
  } catch {} finally {
    saving.value = false
  }
}

async function loadVersions() {
  try {
    const { data } = await api.get(`/notes/${noteId.value}/versions`)
    versions.value = data.versions
    showVersions.value = true
  } catch {
    message.error('加载版本历史失败')
  }
}

async function restoreVersion(versionId) {
  try {
    const { data } = await api.post(`/notes/${noteId.value}/versions/${versionId}/restore`)
    note.value = data.note
    title.value = data.note.title
    content.value = data.note.content || ''
    showVersions.value = false
    message.success('已恢复到历史版本')
  } catch {
    message.error('恢复失败')
  }
}

async function exportNote(fmt) {
  try {
    const response = await api.get(`/notes/${noteId.value}/export/${fmt}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `${title.value || '笔记'}.${fmt === 'html' ? 'html' : 'md'}`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch {
    message.error('导出失败')
  }
}

const moreOptions = [
  { label: '版本历史', key: 'versions', icon: () => h('span', '🕐') },
  { label: '导出 Markdown', key: 'export-md', icon: () => h('span', '📄') },
  { label: '导出 HTML', key: 'export-html', icon: () => h('span', '🌐') },
]

import { h } from 'vue'

function handleMore(key) {
  if (key === 'versions') loadVersions()
  else if (key === 'export-md') exportNote('markdown')
  else if (key === 'export-html') exportNote('html')
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN')
}
</script>

<template>
  <div style="display: flex; flex-direction: column; height: calc(100vh - 120px)">
    <!-- 顶栏 -->
    <n-card size="small" style="margin-bottom: 12px">
      <div style="display: flex; justify-content: space-between; align-items: center">
        <n-space align="center">
          <n-button quaternary @click="router.push('/dashboard/notes')">
            <template #icon><n-icon :component="ArrowBackOutline" /></template>
            返回
          </n-button>
          <span style="font-size: 12px; color: #999">
            {{ saving ? '保存中...' : (lastSaved ? `上次保存：${formatTime(lastSaved)}` : '') }}
          </span>
        </n-space>

        <n-dropdown :options="moreOptions" @select="handleMore">
          <n-button quaternary>
            <template #icon><n-icon :component="EllipsisVerticalOutline" /></template>
          </n-button>
        </n-dropdown>
      </div>
    </n-card>

    <!-- 标题 -->
    <n-input
      v-model:value="title"
      placeholder="笔记标题"
      :bordered="false"
      size="large"
      style="font-size: 24px; font-weight: 700; margin-bottom: 12px"
    />

    <!-- 编辑器区域 -->
    <n-card style="flex: 1; overflow: hidden" :bordered="false">
      <div style="display: flex; gap: 16px; height: 100%">
        <!-- 编辑区 -->
        <div style="flex: 1; display: flex; flex-direction: column">
          <div style="font-size: 12px; color: #999; margin-bottom: 8px">Markdown 编辑</div>
          <n-input
            v-model:value="content"
            type="textarea"
            placeholder="开始写作..."
            :autosize="false"
            style="flex: 1"
            :input-props="{ style: 'height: 100%; resize: none; font-family: monospace; font-size: 14px; line-height: 1.6' }"
          />
        </div>

        <!-- 预览区 -->
        <div style="flex: 1; border-left: 1px solid #eee; padding-left: 16px; overflow: auto">
          <div style="font-size: 12px; color: #999; margin-bottom: 8px">预览</div>
          <div class="markdown-preview" v-html="renderMarkdown(content)" />
        </div>
      </div>
    </n-card>

    <!-- 版本历史弹窗 -->
    <n-modal v-model:show="showVersions" preset="card" title="版本历史" style="max-width: 500px">
      <n-list v-if="versions.length > 0">
        <n-list-item v-for="v in versions" :key="v.id">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <div>
              <div style="font-weight: 500">版本 {{ v.version_num }}</div>
              <div style="font-size: 12px; color: #999">{{ formatTime(v.created_at) }}</div>
            </div>
            <n-button size="small" @click="restoreVersion(v.id)">恢复</n-button>
          </div>
        </n-list-item>
      </n-list>
      <div v-else style="text-align: center; color: #999; padding: 20px">暂无版本历史</div>
    </n-modal>
  </div>
</template>

<script>
// 简单的 Markdown 渲染（基础实现）
function renderMarkdown(text) {
  if (!text) return '<p style="color: #999">预览区域</p>'
  let html = text
    // 代码块
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="lang-$1">$2</code></pre>')
    // 行内代码
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 标题
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // 粗体/斜体
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 链接
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>')
    // 图片
    .replace(/!\[(.+?)\]\((.+?)\)/g, '<img src="$2" alt="$1" style="max-width:100%">')
    // 列表
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    // 引用
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // 分割线
    .replace(/^---$/gm, '<hr>')
    // 换行
    .replace(/\n/g, '<br>')

  return html
}
</script>

<style scoped>
.markdown-preview {
  font-size: 14px;
  line-height: 1.7;
  color: #333;
}

.markdown-preview :deep(h1) {
  font-size: 24px;
  margin: 16px 0 8px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.markdown-preview :deep(h2) {
  font-size: 20px;
  margin: 14px 0 6px;
}

.markdown-preview :deep(h3) {
  font-size: 16px;
  margin: 12px 0 4px;
}

.markdown-preview :deep(pre) {
  background: #f4f4f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-preview :deep(code) {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.markdown-preview :deep(blockquote) {
  border-left: 3px solid #6366f1;
  padding-left: 12px;
  margin: 8px 0;
  color: #666;
}

.markdown-preview :deep(li) {
  margin: 4px 0;
  padding-left: 4px;
}

.markdown-preview :deep(hr) {
  border: none;
  border-top: 1px solid #eee;
  margin: 16px 0;
}

.markdown-preview :deep(a) {
  color: #6366f1;
}

.markdown-preview :deep(img) {
  max-width: 100%;
  border-radius: 6px;
  margin: 8px 0;
}
</style>
