<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import {
  NCard, NButton, NSpace, NIcon, NTag, NModal, NInput, NSelect,
  NEmpty, NPopconfirm, NDropdown
} from 'naive-ui'
import {
  AddOutline, TrashOutline, EllipsisVerticalOutline,
  AlertCircleOutline, CheckmarkCircleOutline
} from '@vicons/ionicons5'
import { h } from 'vue'

const message = useMessage()

const columns = ref([])
const tasks = ref([])
const loading = ref(false)
const showNewColumn = ref(false)
const newColumnName = ref('')
const showNewTask = ref(false)
const newTask = ref({ title: '', description: '', priority: 0, due_date: '', column_id: null })
const showEditTask = ref(false)
const editTask = ref(null)

const priorityOptions = [
  { label: '低', value: 0 },
  { label: '中', value: 1 },
  { label: '高', value: 2 },
  { label: '紧急', value: 3 },
]

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

function getColumnTasks(colId) {
  return tasks.value.filter(t => t.column_id === colId)
}

async function createColumn() {
  if (!newColumnName.value.trim()) return
  try {
    await api.post('/task-columns', { name: newColumnName.value.trim() })
    message.success('创建成功')
    showNewColumn.value = false
    newColumnName.value = ''
    await loadData()
  } catch (err) {
    message.error(err.response?.data?.error || '创建失败')
  }
}

async function deleteColumn(colId) {
  try {
    await api.delete(`/task-columns/${colId}`)
    message.success('已删除')
    await loadData()
  } catch (err) {
    message.error(err.response?.data?.error || '删除失败')
  }
}

function openNewTask(colId) {
  newTask.value = { title: '', description: '', priority: 0, due_date: '', column_id: colId }
  showNewTask.value = true
}

async function createTask() {
  if (!newTask.value.title.trim()) return
  try {
    await api.post('/tasks', newTask.value)
    message.success('创建成功')
    showNewTask.value = false
    await loadData()
  } catch (err) {
    message.error(err.response?.data?.error || '创建失败')
  }
}

function openEditTask(task) {
  editTask.value = { ...task, tag_ids: task.tags?.map(t => t.id) || [] }
  showEditTask.value = true
}

async function saveEditTask() {
  try {
    await api.put(`/tasks/${editTask.value.id}`, {
      title: editTask.value.title,
      description: editTask.value.description,
      priority: editTask.value.priority,
      due_date: editTask.value.due_date,
    })
    message.success('更新成功')
    showEditTask.value = false
    await loadData()
  } catch (err) {
    message.error(err.response?.data?.error || '更新失败')
  }
}

async function deleteTask(taskId) {
  try {
    await api.delete(`/tasks/${taskId}`)
    message.success('已删除')
    await loadData()
  } catch (err) {
    message.error(err.response?.data?.error || '删除失败')
  }
}

async function moveTask(taskId, newColId) {
  try {
    await api.put(`/tasks/${taskId}/move`, { column_id: newColId, position: 0 })
    await loadData()
  } catch {
    message.error('移动失败')
  }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function isOverdue(d) {
  if (!d) return false
  return new Date(d) < new Date(new Date().toDateString())
}

function getMoveOptions(task) {
  return columns.value
    .filter(c => c.id !== task.column_id)
    .map(c => ({ label: `移到 ${c.name}`, key: c.id }))
}

function handleMoveSelect(key, task) {
  moveTask(task.id, key)
}
</script>

<template>
  <div>
    <!-- 工具栏 -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="font-size: 20px; margin: 0">任务看板</h2>
      <n-button @click="showNewColumn = true">
        <template #icon><n-icon :component="AddOutline" /></template>
        新建列
      </n-button>
    </div>

    <!-- 看板 -->
    <div style="display: flex; gap: 16px; overflow-x: auto; padding-bottom: 16px; min-height: calc(100vh - 200px)">
      <n-card
        v-for="col in columns"
        :key="col.id"
        style="min-width: 280px; max-width: 320px; flex-shrink: 0"
        size="small"
      >
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center">
            <n-space align="center" size="small">
              <div :style="{ width: '8px', height: '8px', borderRadius: '50%', background: col.color }"></div>
              <span>{{ col.name }}</span>
              <n-tag size="tiny" :bordered="false">{{ getColumnTasks(col.id).length }}</n-tag>
            </n-space>
            <n-space size="small">
              <n-button quaternary size="tiny" @click="openNewTask(col.id)">
                <template #icon><n-icon :component="AddOutline" /></template>
              </n-button>
              <n-popconfirm @positive-click="deleteColumn(col.id)">
                <template #trigger>
                  <n-button quaternary size="tiny" type="error">
                    <template #icon><n-icon :component="TrashOutline" /></template>
                  </n-button>
                </template>
                确定删除此列？列下任务将变为无列状态。
              </n-popconfirm>
            </n-space>
          </div>
        </template>

        <!-- 任务卡片 -->
        <div style="display: flex; flex-direction: column; gap: 8px">
          <div
            v-for="task in getColumnTasks(col.id)"
            :key="task.id"
            class="task-card"
            @click="openEditTask(task)"
          >
            <div style="display: flex; justify-content: space-between; align-items: flex-start">
              <div style="font-weight: 500; font-size: 14px; flex: 1">{{ task.title }}</div>
              <n-dropdown :options="getMoveOptions(task)" @select="(key) => handleMoveSelect(key, task)" size="small">
                <n-button quaternary size="tiny" @click.stop>
                  <template #icon><n-icon :component="EllipsisVerticalOutline" /></template>
                </n-button>
              </n-dropdown>
            </div>

            <div v-if="task.description" style="font-size: 12px; color: #666; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">
              {{ task.description }}
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px">
              <n-tag :color="{ color: priorityColors[task.priority] + '20', borderColor: priorityColors[task.priority], textColor: priorityColors[task.priority] }" size="tiny">
                {{ priorityLabels[task.priority] }}
              </n-tag>
              <span v-if="task.due_date" :style="{ fontSize: '11px', color: isOverdue(task.due_date) ? '#ef4444' : '#999' }">
                {{ isOverdue(task.due_date) ? '⚠️ ' : '' }}{{ formatDate(task.due_date) }}
              </span>
            </div>
          </div>

          <n-empty v-if="getColumnTasks(col.id).length === 0" description="暂无任务" size="small" style="padding: 20px 0" />
        </div>
      </n-card>

      <!-- 添加列占位 -->
      <n-card
        v-if="columns.length === 0"
        style="min-width: 280px; text-align: center; cursor: pointer"
        hoverable
        @click="showNewColumn = true"
      >
        <n-empty description="点击创建第一个看板列" />
      </n-card>
    </div>

    <!-- 新建列弹窗 -->
    <n-modal v-model:show="showNewColumn" preset="dialog" title="新建看板列" positive-text="创建" negative-text="取消" @positive-click="createColumn">
      <n-input v-model:value="newColumnName" placeholder="列名称（如：待办、进行中）" @keyup.enter="createColumn" />
    </n-modal>

    <!-- 新建任务弹窗 -->
    <n-modal v-model:show="showNewTask" preset="dialog" title="新建任务" positive-text="创建" negative-text="取消" @positive-click="createTask" style="max-width: 500px">
      <n-input v-model:value="newTask.title" placeholder="任务标题" style="margin-bottom: 12px" />
      <n-input v-model:value="newTask.description" type="textarea" placeholder="任务描述（可选）" :rows="2" style="margin-bottom: 12px" />
      <div style="display: flex; gap: 12px">
        <n-select v-model:value="newTask.priority" :options="priorityOptions" placeholder="优先级" style="flex: 1" />
        <n-input v-model:value="newTask.due_date" type="date" style="flex: 1" />
      </div>
    </n-modal>

    <!-- 编辑任务弹窗 -->
    <n-modal v-model:show="showEditTask" preset="dialog" title="编辑任务" positive-text="保存" negative-text="取消" @positive-click="saveEditTask" style="max-width: 500px">
      <template v-if="editTask">
        <n-input v-model:value="editTask.title" placeholder="任务标题" style="margin-bottom: 12px" />
        <n-input v-model:value="editTask.description" type="textarea" placeholder="任务描述" :rows="3" style="margin-bottom: 12px" />
        <div style="display: flex; gap: 12px; margin-bottom: 12px">
          <n-select v-model:value="editTask.priority" :options="priorityOptions" placeholder="优先级" style="flex: 1" />
          <n-input v-model:value="editTask.due_date" type="date" style="flex: 1" />
        </div>
        <n-popconfirm @positive-click="deleteTask(editTask.id); showEditTask = false">
          <template #trigger>
            <n-button type="error" size="small">删除任务</n-button>
          </template>
          确定删除此任务？
        </n-popconfirm>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.task-card {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
  background: #fff;
}

.task-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-color: #6366f1;
}
</style>
