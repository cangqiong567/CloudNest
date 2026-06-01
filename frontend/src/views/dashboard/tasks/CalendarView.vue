<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../../../api'
import { NCard, NButton, NIcon, NSpace, NTag } from 'naive-ui'
import { ChevronBackOutline, ChevronForwardOutline } from '@vicons/ionicons5'

const message = useMessage()
const tasks = ref([])
const currentDate = ref(new Date())

const priorityColors = { 0: '#999', 1: '#6366f1', 2: '#f59e0b', 3: '#ef4444' }
const priorityLabels = { 0: '低', 1: '中', 2: '高', 3: '紧急' }

onMounted(async () => {
  await loadTasks()
})

async function loadTasks() {
  try {
    const { data } = await api.get('/tasks')
    tasks.value = data.tasks
  } catch {
    message.error('加载失败')
  }
}

const year = computed(() => currentDate.value.getFullYear())
const month = computed(() => currentDate.value.getMonth())

const monthName = computed(() => {
  return `${year.value}年${month.value + 1}月`
})

const calendarDays = computed(() => {
  const firstDay = new Date(year.value, month.value, 1)
  const lastDay = new Date(year.value, month.value + 1, 0)
  const startDay = firstDay.getDay() // 0=周日

  const days = []

  // 上月填充
  const prevMonthLastDay = new Date(year.value, month.value, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    days.push({ day: prevMonthLastDay - i, currentMonth: false, date: null })
  }

  // 本月
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const date = `${year.value}-${String(month.value + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ day: d, currentMonth: true, date })
  }

  // 下月填充
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    days.push({ day: d, currentMonth: false, date: null })
  }

  return days
})

function getTasksForDate(dateStr) {
  if (!dateStr) return []
  return tasks.value.filter(t => t.due_date === dateStr)
}

function prevMonth() {
  currentDate.value = new Date(year.value, month.value - 1, 1)
}

function nextMonth() {
  currentDate.value = new Date(year.value, month.value + 1, 1)
}

function isToday(dateStr) {
  if (!dateStr) return false
  return dateStr === new Date().toISOString().split('T')[0]
}

const weekDays = ['日', '一', '二', '三', '四', '五', '六']
</script>

<template>
  <n-card>
    <template #header>
      <n-space align="center">
        <n-button quaternary @click="prevMonth">
          <template #icon><n-icon :component="ChevronBackOutline" /></template>
        </n-button>
        <span style="font-size: 18px; font-weight: 600; min-width: 120px; text-align: center">{{ monthName }}</span>
        <n-button quaternary @click="nextMonth">
          <template #icon><n-icon :component="ChevronForwardOutline" /></template>
        </n-button>
      </n-space>
    </template>

    <div class="calendar">
      <!-- 星期头部 -->
      <div class="calendar-header">
        <div v-for="wd in weekDays" :key="wd" class="calendar-weekday">{{ wd }}</div>
      </div>

      <!-- 日期格子 -->
      <div class="calendar-body">
        <div
          v-for="(day, idx) in calendarDays"
          :key="idx"
          class="calendar-cell"
          :class="{ 'other-month': !day.currentMonth, 'today': isToday(day.date) }"
        >
          <div class="cell-day">{{ day.day }}</div>
          <div class="cell-tasks">
            <div
              v-for="task in getTasksForDate(day.date).slice(0, 3)"
              :key="task.id"
              class="cell-task"
              :style="{ borderLeftColor: priorityColors[task.priority] }"
            >
              {{ task.title }}
            </div>
            <div v-if="getTasksForDate(day.date).length > 3" class="cell-more">
              +{{ getTasksForDate(day.date).length - 3 }} 更多
            </div>
          </div>
        </div>
      </div>
    </div>
  </n-card>
</template>

<style scoped>
.calendar {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.calendar-weekday {
  padding: 8px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: #666;
}

.calendar-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.calendar-cell {
  min-height: 100px;
  padding: 4px 6px;
  border-right: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}

.calendar-cell:nth-child(7n) {
  border-right: none;
}

.calendar-cell.other-month {
  background: #fafafa;
  color: #ccc;
}

.calendar-cell.today {
  background: #ede9fe;
}

.cell-day {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  color: inherit;
}

.cell-tasks {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cell-task {
  font-size: 11px;
  padding: 2px 4px;
  border-left: 3px solid #6366f1;
  background: #fff;
  border-radius: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-more {
  font-size: 10px;
  color: #999;
  padding: 2px 4px;
}
</style>
