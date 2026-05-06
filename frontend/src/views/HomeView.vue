<template>
  <div>
    <!-- Hero Banner -->
    <div class="relative overflow-hidden rounded-2xl mb-8 p-8 md:p-12 bg-gradient-to-r from-[#1a1040] via-[#0f0f30] to-[#1a1030] border border-[#1a1a4e]">
      <div class="relative z-10">
        <h1 class="text-2xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">
          🎬 B站ACG视频数据统计与分析
        </h1>
        <p class="text-gray-400 text-sm md:text-base max-w-xl">
          探索B站ACG频道热门视频数据，涵盖动画、漫画、游戏、轻小说等多种类型。发现最受欢迎的创作者，追踪视频趋势。
        </p>
        <div class="flex gap-4 mt-6">
          <el-button type="primary" size="large" @click="$router.push('/dashboard')">
            <el-icon><DataAnalysis /></el-icon> 数据分析
          </el-button>
          <el-button size="large" @click="$router.push('/large-screen')">
            <el-icon><Monitor /></el-icon> 可视化大屏
          </el-button>
        </div>
      </div>
      <div class="absolute right-4 top-1/2 -translate-y-1/2 text-8xl opacity-10 select-none pointer-events-none">
        🎌
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="flex flex-wrap items-center gap-4 mb-6">
      <el-input v-model="keyword" placeholder="搜索视频标题、作者、标签..." class="max-w-md" clearable
        :prefix-icon="Search" @keyup.enter="searchVideos" @clear="searchVideos" />
      <el-select v-model="category" placeholder="全部分类" clearable class="w-36" @change="searchVideos">
        <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
      </el-select>
      <el-select v-model="sortBy" class="w-36" @change="searchVideos">
        <el-option label="播放最多" value="play_count" />
        <el-option label="点赞最多" value="like_count" />
        <el-option label="弹幕最多" value="danmaku_count" />
        <el-option label="最新发布" value="publish_date" />
      </el-select>
      <el-button type="primary" @click="searchVideos">搜索</el-button>
      <span class="text-gray-500 text-sm ml-auto">共 {{ total }} 个视频</span>
    </div>

    <!-- Video Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <div v-for="video in videos" :key="video.id"
        class="bg-[#12122a] rounded-xl overflow-hidden border border-[#1a1a3e] hover:border-pink-500/30 hover:shadow-lg hover:shadow-pink-500/5 transition-all duration-300 cursor-pointer group"
        @click="$router.push(`/video/${video.id}`)">
        <!-- Cover -->
        <div class="relative aspect-video overflow-hidden bg-[#0a0a1a]">
          <img :src="video.cover_url" :alt="video.title" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" />
          <span class="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-0.5 rounded">
            {{ video.duration }}
          </span>
          <span class="absolute top-2 left-2 bg-pink-500/80 text-white text-xs px-2 py-0.5 rounded">
            {{ video.category || 'ACG' }}
          </span>
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <el-icon :size="48" class="text-white/80"><VideoPlay /></el-icon>
          </div>
        </div>
        <!-- Info -->
        <div class="p-4">
          <h3 class="text-sm font-medium text-gray-100 line-clamp-2 mb-2 min-h-[40px] group-hover:text-pink-400 transition-colors">
            {{ video.title }}
          </h3>
          <div class="text-xs text-gray-500 mb-3">{{ video.author_name }}</div>
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span class="flex items-center gap-1"><el-icon><VideoPlay /></el-icon> {{ formatNumber(video.play_count) }}</span>
            <span class="flex items-center gap-1"><el-icon><ChatDotSquare /></el-icon> {{ formatNumber(video.danmaku_count) }}</span>
            <span class="flex items-center gap-1"><el-icon><Star /></el-icon> {{ formatNumber(video.like_count) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="videos.length === 0 && !loading" class="text-center py-20 text-gray-500">
      <el-icon :size="64"><VideoCamera /></el-icon>
      <p class="mt-4 text-lg">暂无视频数据</p>
    </div>

    <!-- Pagination -->
    <div class="flex justify-center mt-8" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="prev, pager, next" background @current-change="fetchVideos" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { Search, VideoPlay, ChatDotSquare, Star, VideoCamera, DataAnalysis, Monitor } from '@element-plus/icons-vue'

const videos = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const keyword = ref('')
const category = ref('')
const sortBy = ref('play_count')
const categories = ref([])

function formatNumber(n) {
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}

async function fetchVideos() {
  loading.value = true
  try {
    const res = await api.get('/videos', {
      params: {
        keyword: keyword.value || undefined,
        category: category.value || undefined,
        sort_by: sortBy.value,
        page: page.value,
        page_size: pageSize,
      },
    })
    videos.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const res = await api.get('/videos/categories')
    categories.value = res
  } catch {}
}

function searchVideos() {
  page.value = 1
  fetchVideos()
}

onMounted(() => {
  fetchVideos()
  fetchCategories()
})
</script>
