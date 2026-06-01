<script setup>
import { ref, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import {
  NCard, NButton, NSpace, NIcon, NDataTable, NTag, NSelect
} from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'

const message = useMessage()
const tasks = ref([])
const columns = ref([])
const loading = ref(false)
const filterPriority = ref(null)
const filterColumn = ref(null)

const priorityColors = { 0: '#999', 1: '#6366f1', 2: '#f59e0b', 3: '#ef4444' }
const priorityLabels = { 0: '低', 1: '中', 2: '高', 3: '紧急' }

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [colsRes, tasksRes] = await Promise.all([
      api.get('/task-columns'),
      api.get('/tasks'),
    ])
    columns.value = colsRes.data.columns
    tasks.value = tasksRes.data.tasks
  } catch {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

function getColumnName(colId) {
  const col = columns.value.find(c => c.id === colId)
  return col ? col.name : '未分类'
}

function getColumnColor(colId) {
  const col = columns.value.find(c => c.id === colId)
  return col ? col.color : '#999'
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
}

function isOverdue(d) {
  if (!d) return false
  return new Date(d) < new Date(new Date().toDateString())
}

const tableColumns = [
  { title: '标题', key: 'title', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'column_id',
    width: 120,
    render(row) {
      return h(NTag, {
        size: 'small',
        color: { color: getColumnColor(row.column_id) + '20', borderColor: getColumnColor(row.column_id), textColor: getColumnColor(row.column_id) },
      }, { default: () => getColumnName(row.column_id) })
    },
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    render(row) {
      return h(NTag, {
        size: 'small',
        color: { color: priorityColors[row.priority] + '20', borderColor: priorityColors[row.priority], textColor: priorityColors[row.priority] },
      }, { default: () => priorityLabels[row.priority] })
    },
  },
  {
    title: '截止日期',
    key: 'due_date',
    width: 120,
    render(row) {
      return h('span', { style: isOverdue(row.due_date) ? 'color: #ef4444' : '' }, formatDate(row.due_date))
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    render(row) { return new Date(row.created_at).toLocaleString('zh-CN') },
  },
]

async function deleteTask(id) {
  try {
    await api.delete(`/tasks/${id}`)
    message.success('已删除')
    await loadData()
  } catch {
    message.error('删除失败')
  }
}
</script>

<template>
  <n-card title="任务列表">
    <template #header-extra>
      <n-space>
        <n-select
          v-model:value="filterPriority"
          :options="[{label:'全部优先级',value:null},{label:'低',value:0},{label:'中',value:1},{label:'高',value:2},{label:'紧急',value:3}]"
          style="width: 130px"
          size="small"
          clearable
        />
      </n-space>
    </template>

    <n-data-table
      :columns="tableColumns"
      :data="tasks"
      :loading="loading"
      :bordered="false"
      :row-key="(row) => row.id"
      :pagination="{ pageSize: 20 }"
    />
  </n-card>
</template>
