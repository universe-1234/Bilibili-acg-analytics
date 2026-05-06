import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('../views/LayoutView.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/HomeView.vue'),
      },
      {
        path: 'video/:id',
        name: 'VideoDetail',
        component: () => import('../views/VideoDetailView.vue'),
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
      },
      {
        path: 'large-screen',
        name: 'LargeScreen',
        component: () => import('../views/LargeScreenView.vue'),
      },
      {
        path: 'favorites',
        name: 'Favorites',
        component: () => import('../views/FavoritesView.vue'),
        meta: { auth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.auth && !token) {
    return next('/login')
  }
  if (to.meta.guest && token) {
    return next('/')
  }
  next()
})

export default router
