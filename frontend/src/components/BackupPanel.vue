<template>
  <div class="backup-panel">
    <div class="panel-header">
      <h3>数据备份</h3>
      <div class="header-actions">
        <label class="restore-btn">
          恢复备份
          <input type="file" accept=".zip" hidden @change="onRestore" />
        </label>
        <button class="create-btn" @click="doCreate" :disabled="creating">
          {{ creating ? '创建中...' : '创建备份' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="backups.length === 0" class="empty">暂无备份</div>

    <div v-else class="backup-list">
      <div v-for="backup in backups" :key="backup.id" class="backup-item">
        <div class="backup-info">
          <div class="backup-name">{{ backup.name }}</div>
          <div class="backup-meta">
            {{ formatSize(backup.size) }} · {{ formatDate(backup.created_at) }}
          </div>
        </div>
        <div class="backup-actions">
          <a :href="downloadUrl(backup.id)" class="action-link">下载</a>
          <button class="action-link delete-link" @click="confirmDelete(backup)">删除</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :visible="deleteTarget.visible"
      title="删除备份"
      :message="`确定要删除备份「${deleteTarget.item?.name || ''}」吗？`"
      @confirm="doDelete"
      @cancel="deleteTarget.visible = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api/index.js'
import ConfirmDialog from './ConfirmDialog.vue'

const backups = ref([])
const loading = ref(true)
const creating = ref(false)
const error = ref('')
const success = ref('')
const deleteTarget = ref({ visible: false, item: null })

onMounted(() => load())

async function load() {
  loading.value = true
  error.value = ''
  try {
    backups.value = await api.listBackups()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function doCreate() {
  creating.value = true
  error.value = ''
  success.value = ''
  try {
    await api.createBackup()
    success.value = '备份创建成功'
    await load()
    setTimeout(() => { success.value = '' }, 3000)
  } catch (e) {
    error.value = e.message
  } finally {
    creating.value = false
  }
}

async function onRestore(e) {
  const file = e.target.files[0]
  if (!file) return

  if (!confirm('恢复备份将覆盖当前数据，确定继续吗？')) {
    e.target.value = ''
    return
  }

  error.value = ''
  success.value = ''
  try {
    await api.restoreBackup(file)
    success.value = '恢复成功，请刷新页面'
    setTimeout(() => { success.value = '' }, 5000)
  } catch (e) {
    error.value = e.message
  }
  e.target.value = ''
}

function confirmDelete(backup) {
  deleteTarget.value = { visible: true, item: backup }
}

async function doDelete() {
  const backup = deleteTarget.value.item
  deleteTarget.value.visible = false
  if (!backup) return
  try {
    await api.deleteBackup(backup.id)
    await load()
  } catch (e) {
    error.value = e.message
  }
}

function downloadUrl(backupId) {
  return api.getBackupDownloadUrl(backupId)
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB'
  return (bytes / 1073741824).toFixed(2) + ' GB'
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}
</script>

<style scoped>
.backup-panel {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 {
  font-size: 18px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.create-btn {
  background: #27ae60;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.create-btn:hover {
  background: #219a52;
}

.create-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.restore-btn {
  background: #1a1a2e;
  color: #fff;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.restore-btn:hover {
  background: #2a2a4e;
}

.error {
  color: #e74c3c;
  padding: 8px 0;
  margin-bottom: 12px;
  font-size: 14px;
}

.success {
  color: #27ae60;
  padding: 8px 0;
  margin-bottom: 12px;
  font-size: 14px;
}

.loading {
  color: #999;
  text-align: center;
  padding: 40px;
}

.empty {
  color: #999;
  text-align: center;
  padding: 40px;
}

.backup-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.backup-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.backup-item:hover {
  background: #f0f1f2;
}

.backup-name {
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 4px;
}

.backup-meta {
  font-size: 12px;
  color: #888;
}

.backup-actions {
  display: flex;
  gap: 16px;
}

.action-link {
  font-size: 13px;
  color: #1a1a2e;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.action-link:hover {
  text-decoration: underline;
}

.delete-link {
  color: #e74c3c;
}
</style>
