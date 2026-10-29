<template>
  <div class="server-config-overlay" v-if="visible">
    <div class="config-modal">
      <h2>连接服务器</h2>
      <p class="desc">请输入运行 CAD 版本管理器的电脑 IP 地址</p>

      <div class="input-group">
        <label>服务器地址</label>
        <div class="input-row">
          <span class="prefix">http://</span>
          <input
            v-model="serverIP"
            placeholder="例如: 192.168.1.100"
            @keyup.enter="save"
            autofocus
          />
          <span class="suffix">:8000</span>
        </div>
      </div>

      <div class="tips">
        <p>💡 如何获取电脑 IP 地址：</p>
        <ol>
          <li>在电脑上按 Win+R，输入 cmd 回车</li>
          <li>输入 <code>ipconfig</code> 回车</li>
          <li>找到 "IPv4 地址" 即为 IP</li>
        </ol>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <div class="actions">
        <button class="btn-save" @click="save" :disabled="!serverIP.trim()">
          连接
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const visible = ref(false)
const serverIP = ref('')
const error = ref('')

onMounted(() => {
  // 检查是否已配置服务器地址
  const saved = localStorage.getItem('server_url')
  if (saved) {
    // 已配置，直接使用
    window.API_BASE_URL = saved
  } else {
    // 未配置，显示配置界面
    visible.value = true
  }
})

async function save() {
  const ip = serverIP.value.trim()
  if (!ip) return

  error.value = ''
  const url = `http://${ip}:8000`

  try {
    // 测试连接
    const res = await fetch(`${url}/api/health`, { signal: AbortSignal.timeout(5000) })
    const data = await res.json()

    if (data.status === 'ok') {
      // 连接成功，保存配置
      localStorage.setItem('server_url', url)
      window.API_BASE_URL = url
      visible.value = false
      // 刷新页面加载数据
      window.location.reload()
    } else {
      error.value = '服务器响应异常'
    }
  } catch (e) {
    error.value = '无法连接到服务器，请检查 IP 地址和网络'
  }
}
</script>

<style scoped>
.server-config-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 46, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.config-modal {
  background: #fff;
  border-radius: 16px;
  padding: 32px 24px;
  width: 100%;
  max-width: 400px;
}

h2 {
  font-size: 24px;
  margin-bottom: 8px;
  text-align: center;
  color: #1a1a2e;
}

.desc {
  color: #666;
  font-size: 14px;
  text-align: center;
  margin-bottom: 24px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.input-row {
  display: flex;
  align-items: center;
  border: 2px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.input-row:focus-within {
  border-color: #1a1a2e;
}

.prefix, .suffix {
  background: #f5f5f5;
  padding: 12px 8px;
  font-size: 14px;
  color: #666;
}

.input-row input {
  flex: 1;
  border: none;
  padding: 12px;
  font-size: 16px;
  outline: none;
  min-width: 0;
}

.tips {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  font-size: 13px;
  color: #666;
}

.tips p {
  margin-bottom: 8px;
  font-weight: 600;
}

.tips ol {
  margin: 0;
  padding-left: 20px;
}

.tips li {
  margin-bottom: 4px;
}

.tips code {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.error {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  margin-bottom: 16px;
}

.actions {
  display: flex;
  justify-content: center;
}

.btn-save {
  background: #1a1a2e;
  color: #fff;
  border: none;
  padding: 14px 48px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-save:hover:not(:disabled) {
  background: #2a2a4e;
}

.btn-save:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
