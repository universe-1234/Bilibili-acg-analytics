<template>
  <div class="large-screen" :class="{ 'fullscreen': isFullscreen }">
    <!-- Header -->
    <div class="screen-header">
      <div class="header-left">
        <span class="text-cyan-400 text-sm">ACG Data Visualization</span>
      </div>
      <h1 class="text-2xl md:text-3xl font-bold tracking-wider bg-gradient-to-r from-cyan-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
        B站ACG视频数据可视化大屏
      </h1>
      <div class="header-right">
        <span class="text-gray-400 text-sm">{{ currentTime }}</span>
        <el-button text size="small" class="text-white ml-2" @click="toggleFullscreen">
          <el-icon><FullScreen v-if="!isFullscreen" /><Rank v-else /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="screen-grid">
      <!-- Left Column -->
      <div class="left-col">
        <!-- Overview Stats -->
        <div class="screen-card">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-cyan-400 rounded-full inline-block mr-2"></span>
            核心指标概览
          </h3>
          <div class="grid grid-cols-2 gap-2">
            <div v-for="s in overviewStats" :key="s.label" class="stat-item">
              <div class="text-cyan-400 text-lg font-bold">{{ s.value }}</div>
              <div class="text-gray-500 text-xs">{{ s.label }}</div>
            </div>
          </div>
        </div>

        <!-- Category Distribution -->
        <div class="screen-card flex-1">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-pink-400 rounded-full inline-block mr-2"></span>
            视频分类占比
          </h3>
          <div ref="pieChart1" class="chart-box"></div>
        </div>

        <!-- Tag Cloud -->
        <div class="screen-card flex-1">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-yellow-400 rounded-full inline-block mr-2"></span>
            热门标签
          </h3>
          <div ref="barChart1" class="chart-box"></div>
        </div>
      </div>

      <!-- Center Column -->
      <div class="center-col">
        <!-- Main Map / Center Chart -->
        <div class="screen-card flex-1">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-purple-400 rounded-full inline-block mr-2"></span>
            视频播放量TOP20
          </h3>
          <div ref="centerChart" class="chart-box-lg"></div>
        </div>

        <!-- Bottom: Daily Trends -->
        <div class="screen-card" style="height: 300px;">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-green-400 rounded-full inline-block mr-2"></span>
            30日数据趋势
          </h3>
          <div ref="trendChart" class="chart-box"></div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="right-col">
        <!-- Top Authors -->
        <div class="screen-card flex-1">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-orange-400 rounded-full inline-block mr-2"></span>
            UP主影响力排行
          </h3>
          <div ref="rightChart1" class="chart-box"></div>
        </div>

        <!-- Publish Trend -->
        <div class="screen-card flex-1">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-blue-400 rounded-full inline-block mr-2"></span>
            发布时间热力分布
          </h3>
          <div ref="rightChart2" class="chart-box"></div>
        </div>

        <!-- Engagement Radar -->
        <div class="screen-card flex-1">
          <h3 class="card-title">
            <span class="w-2 h-2 bg-red-400 rounded-full inline-block mr-2"></span>
            互动数据概览
          </h3>
          <div ref="rightChart3" class="chart-box"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import api from '../api'
import { FullScreen, Rank } from '@element-plus/icons-vue'

const isFullscreen = ref(false)
const currentTime = ref('')
let timeTimer = null
let charts = []

const overviewStats = ref([
  { label: '视频总数', value: '0' },
  { label: '总播放量', value: '0' },
  { label: '总点赞数', value: '0' },
  { label: '总弹幕数', value: '0' },
])

const colors = ['#00d4ff', '#f472b6', '#a78bfa', '#34d399', '#fbbf24', '#f87171', '#60a5fa']

function formatNum(n) {
  if (n >= 100000000) return (n / 100000000).toFixed(1) + '亿'
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return String(n)
}

function makeChart(dom, option) {
  if (!dom.value) return null
  const c = echarts.init(dom.value)
  c.setOption(option)
  charts.push(c)
  return c
}

function baseOpt() {
  return {
    tooltip: {
      backgroundColor: 'rgba(10,10,30,0.9)',
      borderColor: '#333366',
      textStyle: { color: '#e0e0e0', fontSize: 12 },
    },
    grid: { left: '5%', right: '5%', top: 15, bottom: 5, containLabel: true },
  }
}

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN')
}

async function fetchOverview() {
  try {
    const d = await api.get('/dashboard/overview')
    overviewStats.value = [
      { label: '视频总数', value: String(d.total_videos) },
      { label: '总播放量', value: formatNum(d.total_plays) },
      { label: '总点赞数', value: formatNum(d.total_likes) },
      { label: '总弹幕数', value: formatNum(d.total_danmaku) },
    ]
  } catch {}
}

// Left charts
const pieChart1 = ref(null)
const barChart1 = ref(null)
// Center
const centerChart = ref(null)
const trendChart = ref(null)
// Right
const rightChart1 = ref(null)
const rightChart2 = ref(null)
const rightChart3 = ref(null)

async function initLeftCharts() {
  try {
    const cats = await api.get('/dashboard/category-stats')
    makeChart(pieChart1, {
      ...baseOpt(),
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '50%'],
        label: { color: '#aaa', fontSize: 10, formatter: '{b}\n{d}%' },
        emphasis: { label: { fontSize: 14 } },
        data: cats.map(c => ({ name: c.category, value: c.count })),
      }],
      color: colors,
    })
  } catch {}

  try {
    const tags = await api.get('/dashboard/tag-cloud')
    const topTags = tags.slice(0, 12)
    makeChart(barChart1, {
      ...baseOpt(),
      grid: { left: '3%', right: '10%', top: 5, bottom: 5, containLabel: true },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#555', fontSize: 9 },
        splitLine: { lineStyle: { color: '#151530' } },
      },
      yAxis: {
        type: 'category',
        data: topTags.map(t => t.name).reverse(),
        axisLabel: { color: '#888', fontSize: 10 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [{
        type: 'bar',
        data: topTags.map(t => t.value).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#f472b6' },
            { offset: 1, color: '#fbbf24' },
          ]),
          borderRadius: [0, 3, 3, 0],
        },
      }],
    })
  } catch {}
}

async function initCenterCharts() {
  try {
    const top = await api.get('/dashboard/top-videos', { params: { limit: 20 } })
    const topData = [...top].reverse()
    const maxPlay = Math.max(...topData.map(v => v.play_count))
    makeChart(centerChart, {
      ...baseOpt(),
      grid: { left: '2%', right: '12%', top: 10, bottom: 5, containLabel: true },
      yAxis: {
        type: 'category',
        data: topData.map(v => v.title.length > 10 ? v.title.slice(0, 10) + '…' : v.title),
        axisLabel: { color: '#aaa', fontSize: 10 },
        axisLine: { show: false },
        axisTick: { show: false },
        inverse: true,
      },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#888', fontSize: 9, formatter: formatNum },
        splitLine: { lineStyle: { color: '#151530' } },
      },
      series: [{
        type: 'bar',
        data: topData.map(v => ({
          value: v.play_count,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#a78bfa' },
              { offset: 1, color: '#00d4ff' },
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

  try {
    const trend = await api.get('/dashboard/daily-trends', { params: { days: 30 } })
    makeChart(trendChart, {
      ...baseOpt(),
      grid: { left: '5%', right: '5%', top: 20, bottom: 5, containLabel: true },
      xAxis: {
        type: 'category',
        data: trend.map(d => d.date.slice(5)),
        axisLabel: { color: '#555', fontSize: 9 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#555', fontSize: 9, formatter: formatNum },
        splitLine: { lineStyle: { color: '#151530' } },
      },
      legend: { textStyle: { color: '#888', fontSize: 10 }, top: 0 },
      series: ['plays', 'likes', 'danmaku'].map((k, i) => ({
        name: { plays: '播放', likes: '点赞', danmaku: '弹幕' }[k],
        type: 'line',
        data: trend.map(d => d[k]),
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2 },
        color: colors[i],
      })),
    })
  } catch {}
}

async function initRightCharts() {
  try {
    const authors = await api.get('/dashboard/author-ranking')
    makeChart(rightChart1, {
      ...baseOpt(),
      grid: { left: '3%', right: '10%', top: 5, bottom: 5, containLabel: true },
      yAxis: {
        type: 'category',
        data: [...authors.slice(0, 10)].reverse().map(a => a.author),
        axisLabel: { color: '#888', fontSize: 9 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#555', fontSize: 9, formatter: formatNum },
        splitLine: { lineStyle: { color: '#151530' } },
      },
      series: [{
        type: 'bar',
        data: [...authors.slice(0, 10)].reverse().map(a => a.total_plays),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#f97316' },
            { offset: 1, color: '#fbbf24' },
          ]),
          borderRadius: [0, 3, 3, 0],
        },
      }],
    })
  } catch {}

  try {
    const pub = await api.get('/dashboard/publish-trends')
    makeChart(rightChart2, {
      ...baseOpt(),
      grid: { left: '3%', right: '5%', top: 5, bottom: 5, containLabel: true },
      xAxis: {
        type: 'category',
        data: pub.map(d => d.date.slice(5)),
        axisLabel: { color: '#555', fontSize: 8 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#555', fontSize: 9 },
        splitLine: { lineStyle: { color: '#151530' } },
      },
      series: [{
        type: 'bar',
        data: pub.map(d => d.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#60a5fa' },
            { offset: 1, color: '#34d399' },
          ]),
          borderRadius: [3, 3, 0, 0],
        },
      }],
    })
  } catch {}

  try {
    const engage = await api.get('/dashboard/video-engagement')
    const totals = { plays: 0, likes: 0, danmaku: 0, favorites: 0, shares: 0, coins: 0 }
    engage.forEach(v => {
      totals.plays += v.plays
      totals.likes += v.likes
      totals.danmaku += v.danmaku
      totals.favorites += v.favorites
      totals.shares += v.shares
      totals.coins += v.coins
    })
    makeChart(rightChart3, {
      ...baseOpt(),
      radar: {
        center: ['50%', '50%'],
        radius: '65%',
        indicator: [
          { name: '播放', max: totals.plays },
          { name: '点赞', max: totals.likes },
          { name: '弹幕', max: totals.danmaku },
          { name: '收藏', max: totals.favorites },
          { name: '分享', max: totals.shares },
          { name: '投币', max: totals.coins },
        ],
        axisName: { color: '#888', fontSize: 10 },
      },
      series: [{
        type: 'radar',
        data: [{
          value: [totals.plays, totals.likes, totals.danmaku, totals.favorites, totals.shares, totals.coins],
          name: '互动数据',
          areaStyle: { color: 'rgba(244, 114, 182, 0.3)' },
          itemStyle: { color: '#f472b6' },
          lineStyle: { color: '#f472b6' },
        }],
      }],
    })
  } catch {}
}

function toggleFullscreen() {
  if (isFullscreen.value) {
    document.exitFullscreen?.()
  } else {
    document.querySelector('.large-screen')?.requestFullscreen?.()
  }
  isFullscreen.value = !isFullscreen.value
}

onMounted(() => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  fetchOverview()
  initLeftCharts()
  initCenterCharts()
  initRightCharts()
})

onUnmounted(() => {
  clearInterval(timeTimer)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
.large-screen {
  min-height: calc(100vh - 6rem);
  background: linear-gradient(135deg, #0a0a1e 0%, #0d0d2b 50%, #0a0a20 100%);
  padding: 16px;
}

.screen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  margin-bottom: 16px;
  background: rgba(10, 10, 30, 0.8);
  border: 1px solid #1a1a4e;
  border-radius: 8px;
}

.header-left, .header-right {
  width: 200px;
}
.header-right {
  text-align: right;
}

.screen-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr 1fr;
  gap: 14px;
  min-height: calc(100vh - 10rem);
}

.left-col, .right-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.center-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.screen-card {
  background: rgba(15, 15, 35, 0.8);
  border: 1px solid #1a1a4e;
  border-radius: 10px;
  padding: 14px;
  backdrop-filter: blur(10px);
}

.card-title {
  font-size: 14px;
  color: #e0e0e0;
  margin-bottom: 10px;
  font-weight: 600;
  letter-spacing: 1px;
}

.chart-box {
  height: 200px;
  width: 100%;
}

.chart-box-lg {
  height: 100%;
  width: 100%;
  min-height: 350px;
}

.stat-item {
  background: rgba(10, 10, 30, 0.6);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  border: 1px solid #1a1a3e;
}

@media (max-width: 1200px) {
  .screen-grid {
    grid-template-columns: 1fr 1fr;
  }
  .right-col {
    grid-column: span 2;
    flex-direction: row;
    flex-wrap: wrap;
  }
  .right-col .screen-card {
    flex: 1 1 200px;
  }
}

@media (max-width: 768px) {
  .screen-grid {
    grid-template-columns: 1fr;
  }
  .right-col {
    grid-column: span 1;
  }
}
</style>
