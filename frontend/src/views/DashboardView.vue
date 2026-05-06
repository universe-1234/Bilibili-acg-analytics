<template>
  <div>
    <h1 class="text-2xl font-bold text-white mb-6">📊 数据统计分析看板</h1>

    <!-- Overview Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3 mb-8">
      <div v-for="card in overviewCards" :key="card.label"
        class="bg-gradient-to-br from-[#12122a] to-[#0f0f28] rounded-xl p-4 border border-[#1a1a4e] hover:border-pink-500/30 transition-colors">
        <div class="text-2xl font-bold text-pink-400 mb-1">{{ card.value }}</div>
        <div class="text-xs text-gray-500">{{ card.label }}</div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Category Distribution Pie -->
      <div class="bg-[#12122a] rounded-xl p-6 border border-[#1a1a4e]">
        <h3 class="text-lg font-semibold text-white mb-4">视频分类分布</h3>
        <div ref="categoryChartRef" class="h-80"></div>
      </div>

      <!-- Top Videos Bar -->
      <div class="bg-[#12122a] rounded-xl p-6 border border-[#1a1a4e]">
        <h3 class="text-lg font-semibold text-white mb-4">热门视频 TOP15</h3>
        <div ref="topVideosChartRef" class="h-80"></div>
      </div>

      <!-- Daily Trends Line -->
      <div class="bg-[#12122a] rounded-xl p-6 border border-[#1a1a4e]">
        <h3 class="text-lg font-semibold text-white mb-4">数据趋势</h3>
        <div ref="trendChartRef" class="h-80"></div>
      </div>

      <!-- Author Ranking Bar -->
      <div class="bg-[#12122a] rounded-xl p-6 border border-[#1a1a4e]">
        <h3 class="text-lg font-semibold text-white mb-4">UP主影响力排行</h3>
        <div ref="authorChartRef" class="h-80"></div>
      </div>

      <!-- Tag Cloud -->
      <div class="bg-[#12122a] rounded-xl p-6 border border-[#1a1a4e]">
        <h3 class="text-lg font-semibold text-white mb-4">热门标签云</h3>
        <div ref="tagCloudRef" class="h-80"></div>
      </div>

      <!-- Publish Trends -->
      <div class="bg-[#12122a] rounded-xl p-6 border border-[#1a1a4e]">
        <h3 class="text-lg font-semibold text-white mb-4">视频发布时间趋势</h3>
        <div ref="publishTrendRef" class="h-80"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const categoryChartRef = ref(null)
const topVideosChartRef = ref(null)
const trendChartRef = ref(null)
const authorChartRef = ref(null)
const tagCloudRef = ref(null)
const publishTrendRef = ref(null)

let charts = []

const overviewCards = ref([
  { label: '视频总数', value: 0 },
  { label: '用户总数', value: 0 },
  { label: '评论总数', value: 0 },
  { label: '总播放量', value: 0 },
  { label: '总点赞数', value: 0 },
  { label: '总弹幕数', value: 0 },
  { label: '收藏总数', value: 0 },
])

function formatNum(n) {
  if (n >= 100000000) return (n / 100000000).toFixed(1) + '亿'
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return String(n)
}

const chartColors = ['#f472b6', '#a78bfa', '#60a5fa', '#34d399', '#fbbf24', '#f87171', '#818cf8', '#2dd4bf', '#fb923c', '#a3e635']

function makeChart(domRef, option) {
  if (!domRef.value) return null
  const chart = echarts.init(domRef.value)
  chart.setOption(option)
  charts.push(chart)
  return chart
}

function baseOption() {
  return {
    tooltip: {
      backgroundColor: '#1a1a2e',
      borderColor: '#2a2a4e',
      textStyle: { color: '#e0e0e0' },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  }
}

async function fetchOverview() {
  try {
    const data = await api.get('/dashboard/overview')
    overviewCards.value = [
      { label: '视频总数', value: formatNum(data.total_videos) },
      { label: '用户总数', value: formatNum(data.total_users) },
      { label: '评论总数', value: formatNum(data.total_comments) },
      { label: '总播放量', value: formatNum(data.total_plays) },
      { label: '总点赞数', value: formatNum(data.total_likes) },
      { label: '总弹幕数', value: formatNum(data.total_danmaku) },
      { label: '收藏总数', value: formatNum(data.total_favorites) },
    ]
  } catch {}
}

async function fetchCategoryStats() {
  try {
    const data = await api.get('/dashboard/category-stats')
    makeChart(categoryChartRef, {
      ...baseOption(),
      series: [{
        type: 'pie',
        radius: ['45%', '75%'],
        center: ['50%', '50%'],
        roseType: 'radius',
        itemStyle: {
          borderRadius: 6,
          borderColor: '#1a1a2e',
          borderWidth: 2,
        },
        label: { color: '#a0a0b8' },
        data: data.map(d => ({ name: d.category, value: d.count })),
      }],
      color: chartColors,
    })
  } catch {}
}

async function fetchTopVideos() {
  try {
    const data = await api.get('/dashboard/top-videos', { params: { limit: 15 } })
    const reversed = [...data].reverse()
    makeChart(topVideosChartRef, {
      ...baseOption(),
      grid: { left: '2%', right: '10%', bottom: 5, top: 5, containLabel: true },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#888', fontSize: 10, formatter: v => formatNum(v) },
        splitLine: { lineStyle: { color: '#1a1a2e' } },
      },
      yAxis: {
        type: 'category',
        data: reversed.map(v => v.title.length > 12 ? v.title.slice(0, 12) + '...' : v.title),
        axisLabel: { color: '#aaa', fontSize: 10 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [{
        type: 'bar',
        data: reversed.map((v, i) => ({
          value: v.play_count,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#f472b6' },
              { offset: 1, color: '#a78bfa' },
            ]),
            borderRadius: [0, 4, 4, 0],
          },
        })),
        label: {
          show: true,
          position: 'right',
          color: '#aaa',
          fontSize: 10,
          formatter: p => formatNum(p.value),
        },
      }],
    })
  } catch {}
}

async function fetchTrends() {
  try {
    const data = await api.get('/dashboard/daily-trends', { params: { days: 30 } })
    makeChart(trendChartRef, {
      ...baseOption(),
      xAxis: {
        type: 'category',
        data: data.map(d => d.date),
        axisLabel: { color: '#666', fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#666', formatter: v => formatNum(v) },
        splitLine: { lineStyle: { color: '#1a1a2e' } },
      },
      series: ['plays', 'likes', 'danmaku'].map((key, i) => ({
        name: { plays: '播放', likes: '点赞', danmaku: '弹幕' }[key],
        type: 'line',
        data: data.map(d => d[key]),
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2 },
        color: chartColors[i],
      })),
      legend: {
        textStyle: { color: '#888' },
        top: 0,
      },
    })
  } catch {}
}

async function fetchAuthorRanking() {
  try {
    const data = await api.get('/dashboard/author-ranking')
    makeChart(authorChartRef, {
      ...baseOption(),
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.map(d => d.author),
        axisLabel: { color: '#666', fontSize: 10, rotate: 30 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#666', formatter: v => formatNum(v) },
        splitLine: { lineStyle: { color: '#1a1a2e' } },
      },
      series: [{
        type: 'bar',
        data: data.map(d => d.total_plays),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#60a5fa' },
            { offset: 1, color: '#a78bfa' },
          ]),
          borderRadius: [6, 6, 0, 0],
        },
      }],
    })
  } catch {}
}

async function fetchTagCloud() {
  try {
    const data = await api.get('/dashboard/tag-cloud')
    const topTags = data.slice(0, 15)
    makeChart(tagCloudRef, {
      ...baseOption(),
      grid: { left: '3%', right: '10%', top: 5, bottom: 5, containLabel: true },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#666', fontSize: 10 },
        splitLine: { lineStyle: { color: '#1a1a2e' } },
      },
      yAxis: {
        type: 'category',
        data: topTags.map(t => t.name).reverse(),
        axisLabel: { color: '#888', fontSize: 11 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [{
        type: 'bar',
        data: topTags.map((t, i) => ({
          value: t.value,
          itemStyle: { color: chartColors[i % chartColors.length], borderRadius: [0, 4, 4, 0] },
        })).reverse(),
      }],
    })
  } catch {}
}

async function fetchPublishTrends() {
  try {
    const data = await api.get('/dashboard/publish-trends')
    makeChart(publishTrendRef, {
      ...baseOption(),
      xAxis: {
        type: 'category',
        data: data.map(d => d.date),
        axisLabel: { color: '#666', fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#666' },
        splitLine: { lineStyle: { color: '#1a1a2e' } },
      },
      series: [{
        type: 'bar',
        data: data.map(d => d.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#34d399' },
            { offset: 1, color: '#60a5fa' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
      }],
    })
  } catch {}
}

onMounted(() => {
  fetchOverview()
  fetchCategoryStats()
  fetchTopVideos()
  fetchTrends()
  fetchAuthorRanking()
  fetchTagCloud()
  fetchPublishTrends()
})

onUnmounted(() => {
  charts.forEach(c => c.dispose())
})
</script>
