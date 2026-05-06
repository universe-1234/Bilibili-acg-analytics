<template>
  <div>
    <h1 class="text-2xl font-bold text-white mb-6">
      <el-icon class="mr-2"><Star /></el-icon> 我的收藏
    </h1>

    <div v-if="videos.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <div v-for="video in videos" :key="video.id"
        class="bg-[#12122a] rounded-xl overflow-hidden border border-[#1a1a3e] hover:border-pink-500/30 hover:shadow-lg transition-all cursor-pointer group"
        @click="$router.push(`/video/${video.id}`)">
        <div class="relative aspect-video overflow-hidden bg-[#0a0a1a]">
          <img :src="video.cover_url" :alt="video.title" class="w-full h-full object-cover group-hover:scale-105 transition-transform" loading="lazy" />
          <span class="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-0.5 rounded">{{ video.duration }}</span>
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <el-icon :size="48" class="text-white/80"><VideoPlay /></el-icon>
          </div>
        </div>
        <div class="p-4">
          <h3 class="text-sm font-medium text-gray-100 line-clamp-2 mb-2 min-h-[40px] group-hover:text-pink-400 transition-colors">
            {{ video.title }}
          </h3>
          <div class="text-xs text-gray-500">{{ video.author_name }}</div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20 text-gray-500">
      <el-icon :size="64"><Star /></el-icon>
      <p class="mt-4 text-lg">还没有收藏任何视频</p>
      <el-button type="primary" class="mt-4" @click="$router.push('/')">去发现视频</el-button>
    </div>

    <div v-if="total > pageSize" class="flex justify-center mt-8">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="prev, pager, next" background @current-change="fetchFavorites" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { Star, VideoPlay } from '@element-plus/icons-vue'

const videos = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20

async function fetchFavorites() {
  try {
    const res = await api.get('/user/favorites', {
      params: { page: page.value, page_size: pageSize },
    })
    videos.value = res.items
    total.value = res.total
  } catch {}
}

onMounted(fetchFavorites)
</script>
