import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('../views/Landing.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/share/:code',
    name: 'share',
    component: () => import('../views/Share.vue'),
  },
  {
    path: '/dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/dashboard/Home.vue'),
      },
      {
        path: 'files',
        name: 'files',
        component: () => import('../views/dashboard/files/FileList.vue'),
      },
      {
        path: 'files/:folderId',
        name: 'files-folder',
        component: () => import('../views/dashboard/files/FileList.vue'),
      },
      {
        path: 'files/trash',
        name: 'trash',
        component: () => import('../views/dashboard/files/Trash.vue'),
      },
      {
        path: 'notes',
        name: 'notes',
        component: () => import('../views/dashboard/notes/NoteList.vue'),
      },
      {
        path: 'notes/:id',
        name: 'note-edit',
        component: () => import('../views/dashboard/notes/NoteEditor.vue'),
      },
      {
        path: 'tasks',
        name: 'tasks',
        redirect: '/dashboard/tasks/board',
      },
      {
        path: 'tasks/board',
        name: 'tasks-board',
        component: () => import('../views/dashboard/tasks/BoardView.vue'),
      },
      {
        path: 'tasks/list',
        name: 'tasks-list',
        component: () => import('../views/dashboard/tasks/ListView.vue'),
      },
      {
        path: 'tasks/calendar',
        name: 'tasks-calendar',
        component: () => import('../views/dashboard/tasks/CalendarView.vue'),
      },
      {
        path: 'settings',
        redirect: '/dashboard/settings/profile',
      },
      {
        path: 'settings/profile',
        name: 'settings-profile',
        component: () => import('../views/dashboard/settings/Profile.vue'),
      },
      {
        path: 'settings/account',
        name: 'settings-account',
        component: () => import('../views/dashboard/settings/Account.vue'),
      },
      {
        path: 'settings/devices',
        name: 'settings-devices',
        component: () => import('../views/dashboard/settings/Devices.vue'),
      },
      {
        path: 'settings/appearance',
        name: 'settings-appearance',
        component: () => import('../views/dashboard/settings/Appearance.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if ((to.name === 'login' || to.name === 'register') && authStore.isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
