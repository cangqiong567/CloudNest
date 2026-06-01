<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import {
  NCard, NButton, NSpace, NIcon, NDataTable, NGrid, NGi, NEmpty,
  NModal, NInput, NBreadcrumb, NBreadcrumbItem, NUpload,
  NProgress, NSkeleton
} from 'naive-ui'
import {
  FolderOutline, DocumentOutline, CloudUploadOutline, AddOutline,
  DownloadOutline, TrashOutline, ShareOutline,
  FolderOpenOutline, ListOutline, GridOutline
} from '@vicons/ionicons5'
import { h } from 'vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const files = ref([])
const loading = ref(false)
const viewMode = ref('list')
const breadcrumbs = ref([{ id: null, name: '根目录' }])
const showNewFolder = ref(false)
const newFolderName = ref('')
const showShareModal = ref(false)
const shareUrl = ref('')
const sharePassword = ref('')
const shareExpiry = ref(24)
const uploadProgress = ref(0)
const uploading = ref(false)

const currentParentId = computed(() => {
  const fid = route.params.folderId
  return fid ? parseInt(fid) : null
})

onMounted(() => loadFiles())
watch(currentParentId, () => loadFiles())

async function loadFiles() {
  loading.value = true
  try {
    const params = currentParentId.value ? `?parent_id=${currentParentId.value}` : ''
    const { data } = await api.get(`/files${params}`)
    files.value = data.files

    // 构建面包屑
    if (currentParentId.value) {
      await buildBreadcrumbs(currentParentId.value)
    } else {
      breadcrumbs.value = [{ id: null, name: '根目录' }]
    }
  } catch {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function buildBreadcrumbs(folderId) {
  const crumbs = [{ id: null, name: '根目录' }]
  let currentId = folderId
  const maxDepth = 20
  let depth = 0

  while (currentId && depth < maxDepth) {
    try {
      const { data } = await api.get(`/files/${currentId}`)
      crumbs.push({ id: data.file.id, name: data.file.name })
      currentId = data.file.parent_id
    } catch { break }
    depth++
  }

  breadcrumbs.value = crumbs.reverse()
}

async function createFolder() {
  if (!newFolderName.value.trim()) return
  try {
    await api.post('/files/folder', {
      name: newFolderName.value.trim(),
      parent_id: currentParentId.value,
    })
    message.success('文件夹创建成功')
    showNewFolder.value = false
    newFolderName.value = ''
    await loadFiles()
  } catch (err) {
    message.error(err.response?.data?.error || '创建失败')
  }
}

function openFolder(id) {
  router.push(`/dashboard/files/${id}`)
}

async function handleUpload({ file }) {
  uploading.value = true
  uploadProgress.value = 0
  const formData = new FormData()
  formData.append('file', file.file)
  if (currentParentId.value) formData.append('parent_id', currentParentId.value)
  try {
    await api.post('/files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (e.total) uploadProgress.value = Math.round((e.loaded / e.total) * 100)
      },
    })
    message.success('上传成功')
    await loadFiles()
  } catch (err) {
    message.error(err.response?.data?.error || '上传失败')
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

async function downloadFile(file) {
  try {
    const response = await api.get(`/files/${file.id}/download`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = file.name
    a.click()
    window.URL.revokeObjectURL(url)
  } catch { message.error('下载失败') }
}

async function deleteFile(file) {
  try {
    await api.delete(`/files/${file.id}`)
    message.success('已移入回收站')
    await loadFiles()
  } catch (err) {
    message.error(err.response?.data?.error || '删除失败')
  }
}

async function shareFile(file) {
  try {
    const payload = { expires_hours: shareExpiry.value }
    if (sharePassword.value) payload.password = sharePassword.value
    const { data } = await api.post(`/files/${file.id}/share`, payload)
    shareUrl.value = `${window.location.origin}/dashboard/share/${data.share.share_code}`
    showShareModal.value = true
  } catch (err) {
    message.error(err.response?.data?.error || '分享失败')
  }
}

function getFileIcon(file) {
  return file.is_folder ? FolderOutline : DocumentOutline
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
      return h('div', {
        style: 'display:flex;align-items:center;gap:8px;cursor:pointer',
        onClick: () => row.is_folder ? openFolder(row.id) : null,
      }, [
        h(NIcon, { size: 20, color: row.is_folder ? '#f59e0b' : '#6366f1' }, { default: () => h(getFileIcon(row)) }),
        h('span', { style: row.is_folder ? 'color:#333;font-weight:500' : '' }, row.name),
      ])
    },
  },
  { title: '大小', key: 'file_size', width: 100, render(row) { return row.is_folder ? '-' : formatSize(row.file_size) } },
  { title: '修改时间', key: 'updated_at', width: 170, render(row) { return formatDate(row.updated_at) } },
  {
    title: '操作', key: 'actions', width: 220,
    render(row) {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          !row.is_folder ? h(NButton, { quaternary: true, size: 'tiny', onClick: () => downloadFile(row) }, { icon: () => h(NIcon, { component: DownloadOutline }), default: () => '下载' }) : null,
          !row.is_folder ? h(NButton, { quaternary: true, size: 'tiny', onClick: () => shareFile(row) }, { icon: () => h(NIcon, { component: ShareOutline }), default: () => '分享' }) : null,
          h(NButton, { quaternary: true, size: 'tiny', type: 'error', onClick: () => deleteFile(row) }, { icon: () => h(NIcon, { component: TrashOutline }), default: () => '删除' }),
        ],
      })
    },
  },
]
</script>

<template>
  <div>
    <!-- 面包屑 + 工具栏 -->
    <n-card size="small" style="margin-bottom: 16px">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px">
        <n-breadcrumb>
          <n-breadcrumb-item
            v-for="(crumb, idx) in breadcrumbs"
            :key="idx"
            @click="crumb.id === null ? router.push('/dashboard/files') : router.push(`/dashboard/files/${crumb.id}`)"
            :clickable="idx < breadcrumbs.length - 1"
          >
            <n-icon v-if="idx === 0" :component="FolderOpenOutline" style="margin-right: 4px" />
            {{ crumb.name }}
          </n-breadcrumb-item>
        </n-breadcrumb>

        <n-space>
          <n-upload :show-file-list="false" :custom-request="handleUpload" multiple>
            <n-button type="primary" :loading="uploading">
              <template #icon><n-icon :component="CloudUploadOutline" /></template>
              上传文件
            </n-button>
          </n-upload>
          <n-button @click="showNewFolder = true">
            <template #icon><n-icon :component="AddOutline" /></template>
            新建文件夹
          </n-button>
          <n-button quaternary @click="viewMode = viewMode === 'list' ? 'grid' : 'list'">
            <template #icon><n-icon :component="viewMode === 'list' ? GridOutline : ListOutline" /></template>
          </n-button>
        </n-space>
      </div>

      <n-progress v-if="uploading" :percentage="uploadProgress" style="margin-top: 8px" />
    </n-card>

    <!-- 加载骨架屏 -->
    <n-card v-if="loading">
      <n-skeleton v-for="i in 5" :key="i" style="margin-bottom: 12px" height="40px" />
    </n-card>

    <!-- 文件列表 -->
    <n-card v-else>
      <n-data-table
        v-if="viewMode === 'list'"
        :columns="columns"
        :data="files"
        :bordered="false"
        :row-key="(row) => row.id"
      />

      <n-grid v-else :cols="4" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true">
        <n-gi v-for="file in files" :key="file.id" span="2 m:1">
          <n-card hoverable style="cursor: pointer" @click="file.is_folder ? openFolder(file.id) : null">
            <div style="text-align: center">
              <n-icon :size="40" :color="file.is_folder ? '#f59e0b' : '#6366f1'">
                <component :is="getFileIcon(file)" />
              </n-icon>
              <div style="margin-top: 8px; font-weight: 500; word-break: break-all">{{ file.name }}</div>
              <div style="font-size: 12px; color: #999; margin-top: 4px">
                {{ file.is_folder ? '文件夹' : formatSize(file.file_size) }}
              </div>
            </div>
          </n-card>
        </n-gi>
      </n-grid>

      <n-empty v-if="!loading && files.length === 0" description="这里还没有文件，点击上传开始吧" style="padding: 60px 0" />
    </n-card>

    <!-- 新建文件夹弹窗 -->
    <n-modal v-model:show="showNewFolder" preset="dialog" title="新建文件夹" positive-text="创建" negative-text="取消" @positive-click="createFolder">
      <n-input v-model:value="newFolderName" placeholder="请输入文件夹名称" @keyup.enter="createFolder" />
    </n-modal>

    <!-- 分享弹窗 -->
    <n-modal v-model:show="showShareModal" preset="card" title="分享文件" style="max-width: 420px">
      <n-space vertical>
        <n-input :value="shareUrl" readonly placeholder="分享链接" />
        <n-button type="primary" block @click="navigator.clipboard.writeText(shareUrl); message.success('已复制到剪贴板')">
          复制链接
        </n-button>
      </n-space>
    </n-modal>
  </div>
</template>
