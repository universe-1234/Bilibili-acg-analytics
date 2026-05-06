<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0a0a1a] via-[#1a1040] to-[#0a0a2e]">
    <div class="w-full max-w-md px-4">
      <div class="text-center mb-8">
        <div class="text-pink-400 text-5xl mb-4">🎬</div>
        <h1 class="text-2xl font-bold text-white mb-2">创建新账号</h1>
        <p class="text-gray-400">加入B站ACG数据分析社区</p>
      </div>

      <div class="bg-[#12122a]/80 backdrop-blur rounded-2xl p-8 border border-[#1a1a4e]">
        <div class="mb-4">
          <el-input v-model="username" placeholder="用户名" size="large" />
        </div>
        <div class="mb-4">
          <el-input v-model="email" placeholder="邮箱" size="large" />
        </div>
        <div class="mb-4">
          <el-input v-model="nickname" placeholder="昵称（选填）" size="large" />
        </div>
        <div class="mb-4">
          <el-input v-model="password" type="password" placeholder="密码" size="large" show-password />
        </div>
        <div class="mb-4">
          <el-input v-model="confirmPassword" type="password" placeholder="确认密码" size="large" show-password />
        </div>
        <div class="mb-4">
          <el-button type="primary" size="large" class="w-full" :loading="loading" @click="doRegister">
            注 册
          </el-button>
        </div>
        <div class="text-center text-gray-400 text-sm">
          已有账号？
          <router-link to="/login" class="text-pink-400 hover:text-pink-300">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)

const username = ref('')
const email = ref('')
const nickname = ref('')
const password = ref('')
const confirmPassword = ref('')

async function doRegister() {
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    ElMessage.warning('请填写所有必填项')
    return
  }
  if (password.value !== confirmPassword.value) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (password.value.length < 6) {
    ElMessage.warning('密码长度至少6位')
    return
  }
  loading.value = true
  try {
    await auth.register({
      username: username.value,
      email: email.value,
      nickname: nickname.value || username.value,
      password: password.value,
    })
    ElMessage.success('注册成功！')
    router.push('/')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>
