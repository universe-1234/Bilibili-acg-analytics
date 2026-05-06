<template>
  <div v-if="video">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Main Content -->
      <div class="lg:col-span-2">
        <!-- Video Player Area -->
        <div class="relative aspect-video rounded-xl overflow-hidden bg-black mb-6 border border-[#1a1a3e]">
          <img :src="video.cover_url" :alt="video.title" class="w-full h-full object-contain" />
          <div class="absolute inset-0 bg-black/50 flex items-center justify-center cursor-pointer group"
            @click="openBilibili">
            <div class="text-center">
              <el-icon :size="64" class="text-white group-hover:text-pink-400 transition-colors"><VideoPlay /></el-icon>
              <p class="text-white mt-4 text-lg group-hover:text-pink-300">点击跳转B站播放</p>
            </div>
          </div>
        </div>

        <!-- Video Info -->
        <h1 class="text-2xl font-bold text-white mb-4">{{ video.title }}</h1>

        <div class="flex flex-wrap items-center gap-4 mb-6">
          <span class="text-pink-400 text-sm">{{ video.author_name }}</span>
          <span class="text-gray-500 text-sm">{{ video.category }}</span>
          <span class="text-gray-500 text-sm">{{ video.publish_date?.split('T')[0] || '未知日期' }}</span>
          <el-button size="small" :type="video.is_favorited ? 'warning' : 'default'" @click="toggleFavorite">
            <el-icon><Star /></el-icon> {{ video.is_favorited ? '已收藏' : '收藏' }}
          </el-button>
          <el-button size="small" @click="openBilibili">
            <el-icon><Link /></el-icon> B站原视频
          </el-button>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-4 sm:grid-cols-7 gap-3 mb-8">
          <div v-for="s in statsCards" :key="s.label" class="bg-[#12122a] rounded-lg p-3 text-center border border-[#1a1a3e]">
            <div class="text-xl font-bold text-pink-400">{{ s.value }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ s.label }}</div>
          </div>
        </div>

        <!-- Tags -->
        <div class="flex flex-wrap gap-2 mb-6" v-if="video.tags">
          <el-tag v-for="tag in video.tags.split(',').filter(Boolean)" :key="tag" size="small" class="cursor-pointer">
            {{ tag.trim() }}
          </el-tag>
        </div>

        <!-- Description -->
        <div class="bg-[#12122a] rounded-xl p-6 mb-8 border border-[#1a1a3e]">
          <h3 class="text-lg font-semibold text-white mb-3">视频简介</h3>
          <p class="text-gray-400 text-sm leading-relaxed">{{ video.description || '暂无简介' }}</p>
        </div>

        <!-- Comment Section -->
        <div class="bg-[#12122a] rounded-xl p-6 border border-[#1a1a3e]">
          <h3 class="text-lg font-semibold text-white mb-4">
            评论 ({{ commentTotal }})
          </h3>

          <!-- Comment Input -->
          <div v-if="auth.isLoggedIn()" class="mb-6">
            <el-input v-model="commentText" type="textarea" :rows="3" placeholder="写下你的评论..." />
            <div class="flex justify-end mt-2">
              <el-button type="primary" size="small" :loading="submitting" @click="submitComment">
                发表评论
              </el-button>
            </div>
          </div>
          <div v-else class="mb-6 text-center py-4 bg-[#0a0a1a] rounded-lg">
            <p class="text-gray-500 text-sm">
              请<router-link to="/login" class="text-pink-400">登录</router-link>后发表评论
            </p>
          </div>

          <!-- Comments List -->
          <div v-if="comments.length > 0" class="space-y-4">
            <div v-for="comment in comments" :key="comment.id" class="border-b border-[#1a1a3e] pb-4 last:border-0">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-pink-400 text-sm font-medium">{{ comment.nickname || comment.username }}</span>
                <span class="text-gray-600 text-xs">{{ formatDate(comment.created_at) }}</span>
              </div>
              <p class="text-gray-300 text-sm">{{ comment.content }}</p>
            </div>
          </div>
          <div v-else class="text-center py-6 text-gray-500 text-sm">暂无评论，快来发表第一条评论吧！</div>

          <div v-if="commentTotal > 20" class="flex justify-center mt-4">
            <el-pagination v-model:current-page="commentPage" :page-size="20" :total="commentTotal"
              layout="prev, pager, next" small background @current-change="fetchComments" />
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="lg:col-span-1">
        <h3 class="text-lg font-semibold text-white mb-4">相关推荐</h3>
        <div class="space-y-3">
          <div v-for="rv in relatedVideos" :key="rv.id"
            class="bg-[#12122a] rounded-lg p-3 flex gap-3 cursor-pointer hover:bg-[#1a1a3e] transition-colors border border-[#1a1a3e]"
            @click="$router.push(`/video/${rv.id}`)">
            <img :src="rv.cover_url" class="w-28 h-18 object-cover rounded flex-shrink-0" />
            <div class="flex-1 min-w-0">
              <h4 class="text-xs text-gray-200 line-clamp-2 mb-1">{{ rv.title }}</h4>
              <p class="text-xs text-gray-500">{{ rv.author_name }}</p>
              <p class="text-xs text-gray-600 mt-1">{{ formatNumber(rv.play_count) }} 播放</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-20 text-gray-500">
    <el-icon :size="64"><VideoCamera /></el-icon>
    <p class="mt-4">视频不存在</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { Star, Link, VideoPlay, VideoCamera } from '@element-plus/icons-vue'

const route = useRoute()
const auth = useAuthStore()

const video = ref(null)
const comments = ref([])
const relatedVideos = ref([])
const commentText = ref('')
const submitting = ref(false)
const commentPage = ref(1)
const commentTotal = ref(0)

const statsCards = computed(() => {
  if (!video.value) return []
  return [
    { label: '播放', value: formatNumber(video.value.play_count) },
    { label: '弹幕', value: formatNumber(video.value.danmaku_count) },
    { label: '点赞', value: formatNumber(video.value.like_count) },
    { label: '投币', value: formatNumber(video.value.coin_count) },
    { label: '收藏', value: formatNumber(video.value.favorite_count) },
    { label: '分享', value: formatNumber(video.value.share_count) },
    { label: '评论', value: formatNumber(video.value.reply_count) },
  ]
})

function formatNumber(n) {
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return String(n)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN')
}

function openBilibili() {
  if (video.value?.bilibili_url) {
    window.open(video.value.bilibili_url, '_blank')
  }
}

async function fetchVideo() {
  try {
    const id = route.params.id
    video.value = await api.get(`/videos/${id}`)
    fetchComments()
    fetchRelated()
  } catch {}
}

async function fetchComments() {
  try {
    const res = await api.get(`/videos/${route.params.id}/comments`, {
      params: { page: commentPage.value, page_size: 20 },
    })
    comments.value = res.items
    commentTotal.value = res.total
  } catch {}
}

async function fetchRelated() {
  try {
    const res = await api.get('/videos', {
      params: {
        category: video.value?.category,
        page_size: 6,
        sort_by: 'play_count',
      },
    })
    relatedVideos.value = res.items.filter(v => v.id !== video.value?.id).slice(0, 5)
  } catch {}
}

async function submitComment() {
  if (!commentText.value.trim()) return
  submitting.value = true
  try {
    await api.post(`/videos/${route.params.id}/comments`, {
      content: commentText.value.trim(),
    })
    commentText.value = ''
    ElMessage.success('评论发表成功')
    fetchComments()
  } finally {
    submitting.value = false
  }
}

async function toggleFavorite() {
  if (!auth.isLoggedIn()) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const res = await api.post(`/videos/${route.params.id}/favorite`)
    video.value.is_favorited = res.favorited
    ElMessage.success(res.favorited ? '已加入收藏' : '已取消收藏')
  } catch {}
}

onMounted(fetchVideo)
</script>
