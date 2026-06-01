<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import {
  NCard, NButton, NSpace, NIcon, NList, NListItem, NTag, NEmpty,
  NInput, NSelect, NModal, NForm, NFormItem, NGrid, NGi
} from 'naive-ui'
import {
  AddOutline, SearchOutline, DocumentTextOutline,
  PricetagOutline, FolderOpenOutline
} from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()

const notes = ref([])
const notebooks = ref([])
const tags = ref([])
const loading = ref(false)
const search = ref('')
const activeNotebook = ref(null)
const showNewNotebook = ref(false)
const newNotebookName = ref('')

onMounted(async () => {
  await Promise.all([loadNotes(), loadNotebooks(), loadTags()])
})

async function loadNotes() {
  loading.value = true
  try {
    let url = '/notes'
    const params = []
    if (activeNotebook.value) params.push(`notebook_id=${activeNotebook.value}`)
    if (search.value) params.push(`search=${encodeURIComponent(search.value)}`)
    if (params.length) url += '?' + params.join('&')
    const { data } = await api.get(url)
    notes.value = data.notes
  } catch {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function loadNotebooks() {
  try {
    const { data } = await api.get('/notebooks')
    notebooks.value = data.notebooks
  } catch {}
}

async function loadTags() {
  try {
    const { data } = await api.get('/tags')
    tags.value = data.tags
  } catch {}
}

async function createNotebook() {
  if (!newNotebookName.value.trim()) return
  try {
    await api.post('/notebooks', { name: newNotebookName.value.trim() })
    message.success('创建成功')
    showNewNotebook.value = false
    newNotebookName.value = ''
    await loadNotebooks()
  } catch (err) {
    message.error(err.response?.data?.error || '创建失败')
  }
}

async function createNote() {
  try {
    const { data } = await api.post('/notes', {
      title: '无标题笔记',
      content: '',
      notebook_id: activeNotebook.value,
    })
    router.push(`/dashboard/notes/${data.note.id}`)
  } catch (err) {
    message.error(err.response?.data?.error || '创建失败')
  }
}

async function deleteNote(id) {
  try {
    await api.delete(`/notes/${id}`)
    message.success('已删除')
    await loadNotes()
  } catch (err) {
    message.error(err.response?.data?.error || '删除失败')
  }
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + ' 分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + ' 小时前'
  return d.toLocaleDateString('zh-CN')
}

function handleSearch() {
  loadNotes()
}
</script>

<template>
  <div style="display: flex; gap: 16px; height: calc(100vh - 120px)">
    <!-- 左侧：笔记本列表 -->
    <n-card style="width: 200px; flex-shrink: 0" size="small">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>笔记本</span>
          <n-button quaternary size="tiny" @click="showNewNotebook = true">
            <template #icon><n-icon :component="AddOutline" /></template>
          </n-button>
        </div>
      </template>

      <div
        class="nb-item"
        :class="{ active: !activeNotebook }"
        @click="activeNotebook = null; loadNotes()"
      >
        <n-icon :component="DocumentTextOutline" /> 全部笔记
      </div>
      <div
        v-for="nb in notebooks"
        :key="nb.id"
        class="nb-item"
        :class="{ active: activeNotebook === nb.id }"
        @click="activeNotebook = nb.id; loadNotes()"
      >
        <n-icon :component="FolderOpenOutline" :style="{ color: nb.color }" />
        {{ nb.name }}
        <span class="nb-count">{{ nb.note_count }}</span>
      </div>

      <div v-if="tags.length > 0" style="margin-top: 16px; border-top: 1px solid #eee; padding-top: 12px">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px">标签</div>
        <n-space size="small">
          <n-tag
            v-for="tag in tags"
            :key="tag.id"
            size="small"
            :color="{ color: tag.color + '20', borderColor: tag.color, textColor: tag.color }"
            style="cursor: pointer"
          >
            {{ tag.name }}
          </n-tag>
        </n-space>
      </div>
    </n-card>

    <!-- 右侧：笔记列表 -->
    <n-card style="flex: 1" size="small">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px">
          <n-input
            v-model:value="search"
            placeholder="搜索笔记..."
            clearable
            size="small"
            @keyup.enter="handleSearch"
            @clear="search = ''; loadNotes()"
          >
            <template #prefix><n-icon :component="SearchOutline" /></template>
          </n-input>
          <n-button type="primary" size="small" @click="createNote">
            <template #icon><n-icon :component="AddOutline" /></template>
            新建笔记
          </n-button>
        </div>
      </template>

      <n-list v-if="notes.length > 0" hoverable clickable>
        <n-list-item v-for="note in notes" :key="note.id" @click="router.push(`/dashboard/notes/${note.id}`)">
          <div style="display: flex; justify-content: space-between; align-items: flex-start">
            <div style="flex: 1; min-width: 0">
              <div style="font-weight: 500; font-size: 15px; margin-bottom: 4px">
                <span v-if="note.is_pinned" style="color: #f59e0b; margin-right: 4px">📌</span>
                {{ note.title || '无标题' }}
              </div>
              <div style="font-size: 12px; color: #999">
                {{ formatDate(note.updated_at) }}
                <n-tag v-for="tag in note.tags" :key="tag.id" size="tiny" style="margin-left: 4px"
                  :color="{ color: tag.color + '20', borderColor: tag.color, textColor: tag.color }">
                  {{ tag.name }}
                </n-tag>
              </div>
            </div>
            <n-button quaternary size="tiny" type="error" @click.stop="deleteNote(note.id)">
              删除
            </n-button>
          </div>
        </n-list-item>
      </n-list>

      <n-empty v-else-if="!loading" description="还没有笔记，点击上方按钮创建" style="padding: 60px 0" />
    </n-card>

    <!-- 新建笔记本弹窗 -->
    <n-modal v-model:show="showNewNotebook" preset="dialog" title="新建笔记本" positive-text="创建" negative-text="取消" @positive-click="createNotebook">
      <n-input v-model:value="newNotebookName" placeholder="请输入笔记本名称" @keyup.enter="createNotebook" />
    </n-modal>
  </div>
</template>

<style scoped>
.nb-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  transition: background 0.2s;
}

.nb-item:hover {
  background: #f5f5f5;
}

.nb-item.active {
  background: #ede9fe;
  color: #6366f1;
  font-weight: 500;
}

.nb-count {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}
</style>
