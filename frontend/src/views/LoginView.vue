<template>
  <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0a0a1a;color:#fff;font-family:sans-serif">
    <div style="width:380px;padding:32px;background:#12122a;border-radius:12px;border:1px solid #1a1a4e">
      <h2 style="text-align:center;color:#f472b6;margin-bottom:24px">登录</h2>
      <div v-if="errorMsg" style="color:#f87171;text-align:center;margin-bottom:12px;font-size:14px">{{ errorMsg }}</div>
      <div v-if="successMsg" style="color:#34d399;text-align:center;margin-bottom:12px;font-size:14px">{{ successMsg }}</div>
      <input v-model="username" placeholder="用户名" style="width:100%;padding:12px;margin:8px 0;background:#0a0a1a;border:1px solid #333;border-radius:6px;color:#fff;font-size:16px;box-sizing:border-box" />
      <input v-model="password" type="password" placeholder="密码" style="width:100%;padding:12px;margin:8px 0;background:#0a0a1a;border:1px solid #333;border-radius:6px;color:#fff;font-size:16px;box-sizing:border-box" @keyup.enter="doLogin" />
      <button @click="doLogin" :disabled="loading" style="width:100%;padding:12px;margin:12px 0;background:#f472b6;color:#fff;border:none;border-radius:6px;font-size:16px;cursor:pointer">
        {{ loading ? '登录中...' : '登 录' }}
      </button>
      <p style="text-align:center;font-size:13px;color:#888">
        <router-link to="/register" style="color:#f472b6">注册</router-link> | 默认账号: admin / admin123
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

async function doLogin() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!username.value || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  try {
    await auth.login(username.value, password.value)
    successMsg.value = '登录成功! 跳转中...'
    setTimeout(() => router.push('/'), 500)
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>
