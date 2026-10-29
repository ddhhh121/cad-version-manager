<template>
  <div
    class="drop-zone"
    :class="{ 'drag-over': isDragOver }"
    @dragover.prevent="isDragOver = true"
    @dragleave.prevent="isDragOver = false"
    @drop.prevent="onDrop"
  >
    <!-- 拖拽提示 -->
    <div v-if="isDragOver" class="drop-overlay">
      <div class="drop-icon">📄</div>
      <div class="drop-text">松开鼠标上传文件</div>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <div class="progress-text">正在上传 {{ uploadedCount }}/{{ totalFiles }}...</div>
    </div>

    <!-- 上传结果 -->
    <div v-if="uploadResults.length > 0" class="upload-results">
      <div class="results-header">
        <h3>上传结果</h3>
        <button class="btn-close" @click="uploadResults = []">×</button>
      </div>
      <div v-for="(result, i) in uploadResults" :key="i" class="result-item" :class="result.status">
        <span class="result-icon">
          {{ result.status === 'new_series' ? '🆕' : result.status === 'new_version' ? '📎' : result.status === 'duplicate' ? '⚠️' : '❌' }}
        </span>
        <span class="result-file">{{ result.filename }}</span>
        <span class="result-message">{{ result.message }}</span>
      </div>
    </div>

    <div class="page-header">
      <h1>项目</h1>
      <div class="header-actions">
        <label class="btn-upload">
          📁 上传文件
          <input type="file" accept=".dwg,.dxf" multiple hidden @change="onFileSelect" />
        </label>
        <button class="btn-primary" @click="showCreate = true">+ 新建项目</button>
      </div>
    </div>

    <div v-if="showCreate" class="create-form">
      <input v-model="newName" placeholder="项目名称" @keyup.enter="create" />
      <input v-model="newDesc" placeholder="描述（可选）" />
      <button class="btn-primary" @click="create">创建</button>
      <button class="btn-ghost" @click="showCreate = false">取消</button>
    </div>

    <div class="toolbar">
      <input v-model="searchQuery" placeholder="搜索项目名称..." class="search-input" @input="onSearchInput" />
      <select v-model="sortBy" class="sort-select" @change="load">
        <option value="created_at">创建时间</option>
        <option value="name">名称</option>
        <option value="series_count">图纸数</option>
      </select>
      <button class="btn-icon" @click="orderAsc = !orderAsc; load()">
        {{ orderAsc ? '↑' : '↓' }}
      </button>
    </div>

    <!-- 拖拽提示文字 -->
    <div class="drag-hint">
      💡 拖拽 DWG/DXF 文件到此处，自动识别并归类
    </div>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="card-grid">
      <ProjectCard
        v-for="p in projects" :key="p.id" :project="p"
        @deleted="load" @renamed="load"
      />
      <div v-if="projects.length === 0" class="empty">
        {{ searchQuery ? '没有匹配的项目' : '还没有项目，新建一个吧' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api/index.js'
import ProjectCard from '../components/ProjectCard.vue'

const projects = ref([])
const loading = ref(true)
const error = ref('')
const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')
const searchQuery = ref('')
const sortBy = ref('created_at')
const orderAsc = ref(false)

// 拖拽上传相关
const isDragOver = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadedCount = ref(0)
const totalFiles = ref(0)
const uploadResults = ref([])

let searchTimer = null

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(load, 300)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    projects.value = await api.listProjects({
      search: searchQuery.value || undefined,
      sort_by: sortBy.value,
      order: orderAsc.value ? 'asc' : 'desc',
    })
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function create() {
  if (!newName.value.trim()) return
  await api.createProject({ name: newName.value.trim(), description: newDesc.value.trim() })
  showCreate.value = false
  newName.value = ''
  newDesc.value = ''
  await load()
}

// 处理拖拽上传
async function onDrop(e) {
  isDragOver.value = false
  const files = Array.from(e.dataTransfer.files).filter(f =>
    f.name.toLowerCase().endsWith('.dwg') || f.name.toLowerCase().endsWith('.dxf')
  )
  if (files.length === 0) {
    error.value = '请上传 DWG 或 DXF 文件'
    return
  }
  await uploadFiles(files)
}

// 处理文件选择上传
async function onFileSelect(e) {
  const files = Array.from(e.target.files)
  if (files.length === 0) return
  await uploadFiles(files)
  e.target.value = ''
}

// 上传文件
async function uploadFiles(files) {
  uploading.value = true
  uploadResults.value = []
  uploadedCount.value = 0
  totalFiles.value = files.length
  uploadProgress.value = 0

  const results = []
  for (let i = 0; i < files.length; i++) {
    try {
      const result = await api.smartUpload(files[i])
      results.push({ ...result, filename: files[i].name })
    } catch (e) {
      results.push({
        status: 'error',
        message: e.message,
        filename: files[i].name,
      })
    }
    uploadedCount.value = i + 1
    uploadProgress.value = ((i + 1) / files.length) * 100
  }

  uploadResults.value = results
  uploading.value = false
  await load() // 刷新项目列表
}

onMounted(load)
</script>

<style scoped>
.drop-zone { position: relative; min-height: calc(100vh - 100px); }
.drop-zone.drag-over { background: rgba(26, 26, 46, 0.05); }

.drop-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(26, 26, 46, 0.9); z-index: 1000;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.drop-icon { font-size: 80px; margin-bottom: 20px; }
.drop-text { color: #fff; font-size: 24px; font-weight: 600; }

.upload-progress {
  background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.progress-bar { height: 8px; background: #eee; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: #27ae60; transition: width 0.3s; }
.progress-text { margin-top: 8px; font-size: 14px; color: #666; text-align: center; }

.upload-results {
  background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.results-header h3 { font-size: 16px; margin: 0; }
.btn-close { background: none; border: none; font-size: 20px; cursor: pointer; color: #999; }
.result-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 0;
  border-bottom: 1px solid #f0f0f0; font-size: 13px;
}
.result-item:last-child { border-bottom: none; }
.result-icon { font-size: 16px; }
.result-file { font-weight: 500; min-width: 120px; }
.result-message { color: #666; flex: 1; }
.result-item.error .result-message { color: #e74c3c; }
.result-item.duplicate .result-message { color: #f39c12; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { font-size: 24px; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.btn-primary { background: #1a1a2e; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-ghost { background: none; border: 1px solid #ccc; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-left: 8px; }
.btn-upload {
  background: #27ae60; color: #fff; padding: 8px 20px; border-radius: 6px;
  cursor: pointer; font-size: 14px; display: inline-flex; align-items: center; gap: 6px;
}
.btn-upload:hover { background: #219a52; }

.toolbar { display: flex; gap: 8px; margin-bottom: 16px; align-items: center; }
.search-input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; min-width: 0; }
.search-input:focus { outline: none; border-color: #1a1a2e; }
.sort-select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; background: #fff; cursor: pointer; }
.btn-icon { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 8px 12px; cursor: pointer; font-size: 16px; }

.drag-hint {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  border: 2px dashed #ccc; border-radius: 8px;
  padding: 16px; text-align: center; color: #666; font-size: 14px;
  margin-bottom: 16px;
}

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.create-form { background: #fff; padding: 16px; border-radius: 8px; margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.create-form input { flex: 1; min-width: 140px; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
.empty { color: #999; text-align: center; padding: 60px; }
.error { color: #e74c3c; padding: 16px; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 12px; align-items: stretch; }
  .page-header h1 { font-size: 20px; text-align: center; }
  .header-actions { justify-content: center; }
  .toolbar { flex-wrap: wrap; }
  .card-grid { grid-template-columns: 1fr; }
  .result-item { flex-wrap: wrap; }
  .result-file { min-width: 100%; }
}
</style>
