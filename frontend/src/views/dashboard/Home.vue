<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NGrid, NGi, NCard, NStatistic, NIcon, NSpace, NTag, NButton, NList, NListItem, NThing, NSkeleton, NEmpty } from 'naive-ui'
import {
  FolderOutline, DocumentTextOutline, CheckmarkDoneOutline,
  CloudOutline, TimeOutline, AddOutline
} from '@vicons/ionicons5'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const fileStats = ref({ file_count: 0, folder_count: 0, total_size: 0 })
const taskStats = ref({ total: 0, today: 0, overdue: 0, by_status: {} })
const noteCount = ref(0)
const recentNotes = ref([])
const todayTasks = ref([])

onMounted(async () => {
  try {
    const [filesRes, tasksRes, notesRes, todayRes] = await Promise.all([
      api.get('/files/stats'),
      api.get('/tasks/stats'),
      api.get('/notes'),
      api.get('/tasks?due_date=today'),
    ])
    fileStats.value = filesRes.data
    taskStats.value = tasksRes.data
    noteCount.value = notesRes.data.notes?.length || 0
    recentNotes.value = (notesRes.data.notes || []).slice(0, 5)
    todayTasks.value = (todayRes.data.tasks || []).slice(0, 5)
  } catch {} finally {
    loading.value = false
  }
})

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function priorityLabel(p) {
  return ['', '中', '高', '紧急'][p] || '低'
}
function priorityType(p) {
  return ['', 'warning', 'error', 'error'][p] || 'info'
}
</script>

<template>
  <div>
    <h2 style="margin-bottom: 20px; font-size: 24px; color: var(--n-text-color)">
      欢迎回来，{{ authStore.user?.username || '用户' }} 👋
    </h2>

    <!-- 统计卡片 -->
    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true">
      <n-gi span="4 m:1">
        <n-card hoverable style="cursor:pointer" @click="router.push('/dashboard/files')">
          <n-statistic label="文件数">
            <template #prefix><n-icon :component="FolderOutline" color="#6366f1" /></template>
            <n-skeleton v-if="loading" :width="40" :height="28" style="display:inline-block" />
            <template v-else>{{ fileStats.file_count }}</template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:1">
        <n-card hoverable style="cursor:pointer" @click="router.push('/dashboard/notes')">
          <n-statistic label="笔记数">
            <template #prefix><n-icon :component="DocumentTextOutline" color="#10b981" /></template>
            <n-skeleton v-if="loading" :width="40" :height="28" style="display:inline-block" />
            <template v-else>{{ noteCount }}</template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:1">
        <n-card hoverable style="cursor:pointer" @click="router.push('/dashboard/tasks')">
          <n-statistic label="任务数">
            <template #prefix><n-icon :component="CheckmarkDoneOutline" color="#f59e0b" /></template>
            <n-skeleton v-if="loading" :width="40" :height="28" style="display:inline-block" />
            <template v-else>
              {{ taskStats.total }}
              <n-tag v-if="taskStats.overdue > 0" type="error" size="tiny" :bordered="false" style="margin-left:8px">
                {{ taskStats.overdue }} 逾期
              </n-tag>
            </template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:1">
        <n-card hoverable>
          <n-statistic label="存储用量">
            <template #prefix><n-icon :component="CloudOutline" color="#ef4444" /></template>
            <n-skeleton v-if="loading" :width="60" :height="28" style="display:inline-block" />
            <template v-else>{{ formatSize(fileStats.total_size) }}</template>
          </n-statistic>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- 快速操作 + 今日待办 -->
    <n-grid :cols="2" :x-gap="16" style="margin-top:24px" responsive="screen" :item-responsive="true">
      <n-gi span="2 m:1">
        <n-card title="⚡ 快速操作" size="small">
          <n-space>
            <n-button type="primary" @click="router.push('/dashboard/files')">
              <template #icon><n-icon :component="AddOutline" /></template>
              上传文件
            </n-button>
            <n-button @click="router.push('/dashboard/notes/new')">
              <template #icon><n-icon :component="AddOutline" /></template>
              新建笔记
            </n-button>
            <n-button @click="router.push('/dashboard/tasks')">
              <template #icon><n-icon :component="AddOutline" /></template>
              新建任务
            </n-button>
          </n-space>
        </n-card>
      </n-gi>
      <n-gi span="2 m:1">
        <n-card title="📋 今日待办" size="small">
          <n-skeleton v-if="loading" :repeat="3" />
          <n-empty v-else-if="todayTasks.length === 0" description="今天没有待办任务" />
          <n-list v-else bordered>
            <n-list-item v-for="task in todayTasks" :key="task.id">
              <n-thing :title="task.title">
                <template #header-extra>
                  <n-tag v-if="task.priority" :type="priorityType(task.priority)" size="small" :bordered="false">
                    {{ priorityLabel(task.priority) }}
                  </n-tag>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- 最近笔记 -->
    <n-card title="📝 最近笔记" size="small" style="margin-top:16px">
      <n-skeleton v-if="loading" :repeat="3" />
      <n-empty v-else-if="recentNotes.length === 0" description="还没有笔记" />
      <n-list v-else bordered clickable>
        <n-list-item v-for="note in recentNotes" :key="note.id" @click="router.push(`/dashboard/notes/${note.id}`)">
          <n-thing :title="note.title" :description="note.updated_at?.slice(0, 10)" />
        </n-list-item>
      </n-list>
    </n-card>
  </div>
</template>
