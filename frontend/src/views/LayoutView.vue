<template>
  <div class="min-h-screen flex flex-col">
    <header class="fixed top-0 left-0 right-0 z-50 bg-[#0a0a1a]/95 backdrop-blur border-b border-[#1a1a3e]">
      <div class="max-w-screen-2xl mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-8">
          <router-link to="/" class="flex items-center gap-2 text-xl font-bold text-pink-400 no-underline">
            🎬 <span class="hidden sm:inline">B站ACG数据分析</span>
          </router-link>
          <nav class="hidden md:flex items-center gap-1">
            <router-link to="/" class="nav-link" active-class="nav-link-active">
              🏠 首页
            </router-link>
            <router-link to="/dashboard" class="nav-link" active-class="nav-link-active">
              📊 数据看板
            </router-link>
            <router-link to="/large-screen" class="nav-link" active-class="nav-link-active">
              🖥️ 可视化大屏
            </router-link>
            <router-link v-if="auth.isLoggedIn()" to="/favorites" class="nav-link" active-class="nav-link-active">
              ⭐ 我的收藏
            </router-link>
          </nav>
        </div>
        <div class="flex items-center gap-3">
          <template v-if="auth.isLoggedIn() && auth.user">
            <span class="text-gray-400 text-sm hidden sm:inline">{{ auth.user.nickname || auth.user.username }}</span>
            <el-button text type="danger" @click="handleLogout">退出</el-button>
          </template>
          <template v-else>
            <el-button text @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" size="small" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </header>
    <main class="flex-1 pt-20 pb-8 px-4 max-w-screen-2xl mx-auto w-full">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 8px;
  color: #a0a0b8;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}
.nav-link:hover {
  color: #e0e0f0;
  background: rgba(255, 255, 255, 0.05);
}
.nav-link-active {
  color: #f472b6 !important;
  background: rgba(244, 114, 182, 0.1);
}
</style>
