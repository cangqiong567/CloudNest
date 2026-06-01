<script setup>
import { ref, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import {
  NCard, NButton, NSpace, NIcon, NDataTable, NEmpty, NPopconfirm
} from 'naive-ui'
import {
  FolderOutline, DocumentOutline, RefreshOutline, TrashOutline
} from '@vicons/ionicons5'

const message = useMessage()
const files = ref([])
const loading = ref(false)

onMounted(() => loadTrash())

async function loadTrash() {
  loading.value = true
  try {
    const { data } = await api.get('/trash')
    files.value = data.files
  } catch {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function restoreFile(id) {
  try {
    await api.post(`/files/${id}/restore`)
    message.success('已恢复')
    await loadTrash()
  } catch (err) {
    message.error(err.response?.data?.error || '恢复失败')
  }
}

async function permanentDelete(id) {
  try {
    await api.delete(`/files/${id}/permanent`)
    message.success('已永久删除')
    await loadTrash()
  } catch (err) {
    message.error(err.response?.data?.error || '删除失败')
  }
}

async function emptyTrash() {
  try {
    await api.post('/trash/empty')
    message.success('回收站已清空')
    await loadTrash()
  } catch (err) {
    message.error(err.response?.data?.error || '清空失败')
  }
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN')
}

const columns = [
  {
    title: '名称',
    key: 'name',
    render(row) {
      return h('div', { style: 'display: flex; align-items: center; gap: 8px' }, [
        h(NIcon, { size: 20, color: row.is_folder ? '#f59e0b' : '#6366f1' }, { default: () => h(row.is_folder ? FolderOutline : DocumentOutline) }),
        h('span', row.name),
      ])
    },
  },
  {
    title: '大小',
    key: 'file_size',
    width: 100,
    render(row) { return row.is_folder ? '-' : formatSize(row.file_size) },
  },
  {
    title: '删除时间',
    key: 'deleted_at',
    width: 170,
    render(row) { return formatDate(row.deleted_at) },
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render(row) {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, { quaternary: true, size: 'tiny', type: 'success', onClick: () => restoreFile(row.id) }, { icon: () => h(NIcon, { component: RefreshOutline }), default: () => '恢复' }),
          h(NPopconfirm, { onPositiveClick: () => permanentDelete(row.id) }, {
            trigger: () => h(NButton, { quaternary: true, size: 'tiny', type: 'error' }, { icon: () => h(NIcon, { component: TrashOutline }), default: () => '永久删除' }),
            default: () => '确定永久删除？',
          }),
        ]
      })
    },
  },
]
</script>

<template>
  <n-card title="回收站" :bordered="false">
    <template #header-extra>
      <n-popconfirm v-if="files.length > 0" @positive-click="emptyTrash">
        <template #trigger>
          <n-button type="error" size="small">清空回收站</n-button>
        </template>
        确定清空回收站？所有文件将被永久删除。
      </n-popconfirm>
    </template>

    <n-data-table
      :columns="columns"
      :data="files"
      :loading="loading"
      :bordered="false"
      :row-key="(row) => row.id"
    />

    <n-empty v-if="!loading && files.length === 0" description="回收站是空的" style="padding: 40px 0" />
  </n-card>
</template>
