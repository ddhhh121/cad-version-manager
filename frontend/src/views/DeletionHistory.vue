<template>
  <div>
    <router-link to="/" class="back-link">← 返回首页</router-link>

    <div class="page-header">
      <h1>删除历史</h1>
      <div class="filters">
        <select v-model="entityType" @change="load" class="filter-select">
          <option value="">全部类型</option>
          <option value="project">项目</option>
          <option value="series">系列</option>
          <option value="version">版本</option>
        </select>
      </div>
    </div>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="logs.length === 0" class="empty">暂无删除记录</div>

    <table v-else class="log-table">
      <thead>
        <tr>
          <th>类型</th>
          <th>名称</th>
          <th>删除时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in logs" :key="log.id">
          <td>
            <span class="type-badge" :class="log.entity_type">{{ typeLabels[log.entity_type] }}</span>
          </td>
          <td class="name-cell">{{ log.entity_name }}</td>
          <td class="time-cell">{{ formatDate(log.deleted_at) }}</td>
          <td>
            <button class="restore-btn" @click="confirmRestore(log)">恢复</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="logs.length >= 50" class="load-more">
      <button @click="loadMore" :disabled="loadingMore">
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>

    <ConfirmDialog
      :visible="restoreTarget.visible"
      title="恢复记录"
      :message="`确定要恢复「${restoreTarget.item?.entity_name || ''}」吗？`"
      @confirm="doRestore"
      @cancel="restoreTarget.visible = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api/index.js'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const logs = ref([])
const loading = ref(true)
const error = ref('')
const entityType = ref('')
const offset = ref(0)
const loadingMore = ref(false)
const restoreTarget = ref({ visible: false, item: null })

const typeLabels = {
  project: '项目',
  series: '系列',
  version: '版本',
}

onMounted(() => load())

async function load() {
  loading.value = true
  error.value = ''
  offset.value = 0
  try {
    const params = { limit: 50, offset: 0 }
    if (entityType.value) params.entity_type = entityType.value
    logs.value = await api.listDeletions(params)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  loadingMore.value = true
  try {
    offset.value += 50
    const params = { limit: 50, offset: offset.value }
    if (entityType.value) params.entity_type = entityType.value
    const more = await api.listDeletions(params)
    logs.value.push(...more)
  } catch (e) {
    // ignore
  } finally {
    loadingMore.value = false
  }
}

function confirmRestore(log) {
  restoreTarget.value = { visible: true, item: log }
}

async function doRestore() {
  const log = restoreTarget.value.item
  restoreTarget.value.visible = false
  if (!log) return
  try {
    await api.restoreDeletion(log.id)
    logs.value = logs.value.filter(l => l.id !== log.id)
  } catch (e) {
    error.value = e.message
  }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}
</script>

<style scoped>
.back-link { color: #1a1a2e; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h1 { font-size: 24px; }

.filter-select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }

.empty { color: #999; text-align: center; padding: 60px; }
.error { color: #e74c3c; padding: 8px 0; margin-bottom: 8px; font-size: 14px; }

.log-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.log-table th, .log-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }
.log-table th { background: #f8f9fa; font-weight: 600; font-size: 13px; color: #666; }
.log-table tr:last-child td { border-bottom: none; }
.log-table tr:hover { background: #fafafa; }

.type-badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }
.type-badge.project { background: #e3f2fd; color: #1565c0; }
.type-badge.series { background: #f3e5f5; color: #7b1fa2; }
.type-badge.version { background: #e8f5e9; color: #2e7d32; }

.name-cell { font-weight: 500; }
.time-cell { color: #999; font-size: 13px; }

.restore-btn { background: #1a1a2e; color: #fff; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; font-size: 13px; }
.restore-btn:hover { background: #2a2a4e; }

.load-more { text-align: center; margin-top: 20px; }
.load-more button { background: #f5f5f5; border: 1px solid #ddd; padding: 10px 24px; border-radius: 6px; cursor: pointer; }
.load-more button:hover { background: #eee; }
.load-more button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
