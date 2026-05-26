<template>
  <div>
    <router-link to="/" class="back-link">← 返回项目列表</router-link>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="project">
      <div class="project-header">
        <h1>{{ project.name }}</h1>
        <label class="upload-btn">
          上传图纸
          <input type="file" accept=".dwg,.dxf" hidden @change="onUpload" />
        </label>
      </div>

      <div v-if="uploadError" class="error">{{ uploadError }}</div>

      <div v-if="seriesList.length === 0" class="empty">还没有图纸，上传第一个开始管理</div>

      <router-link
        v-for="s in seriesList" :key="s.id"
        :to="`/project/${project.id}/series/${s.id}`"
        class="series-card"
      >
        <div class="card-thumb">
          <img v-if="s.latest_version?.thumbnail_path" :src="thumbnailUrl(s.latest_version.id)" />
          <div v-else class="thumb-placeholder">无预览</div>
        </div>
        <div class="card-info">
          <span class="drawing-number">{{ s.drawing_number }}</span>
          <span class="series-meta">v{{ s.latest_version?.version_number || '?' }} · 共{{ s.version_count }}版</span>
        </div>
        <span v-if="s.latest_version" class="latest-tag">当前最新</span>
        <span class="arrow">→</span>
      </router-link>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'

const route = useRoute()
const project = ref(null)
const seriesList = ref([])
const loading = ref(true)
const error = ref('')
const uploadError = ref('')

async function loadProject() {
  loading.value = true
  error.value = ''
  try {
    project.value = await api.getProject(route.params.id)
    seriesList.value = project.value.series_list || []
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function onUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadError.value = ''
  try {
    await api.uploadDrawing(project.value.id, file)
    await loadProject()
  } catch (e) { uploadError.value = e.message }
  e.target.value = ''
}

function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }

onMounted(loadProject)
</script>

<style scoped>
.back-link { color: #1a1a2e; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }

.project-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.project-header h1 { font-size: 24px; }
.upload-btn { background: #1a1a2e; color: #fff; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.upload-btn:hover { background: #2a2a4e; }

.empty { color: #999; text-align: center; padding: 60px; }
.error { color: #e74c3c; padding: 8px 0; margin-bottom: 8px; font-size: 14px; }

.series-card {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border-radius: 6px; padding: 10px 14px; margin-bottom: 6px;
  border: 1px solid #e8e8e8; text-decoration: none; color: inherit;
  transition: box-shadow .15s;
}
.series-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,.06); }

.card-thumb { width: 60px; height: 45px; border-radius: 4px; overflow: hidden; background: #eee; flex-shrink: 0; }
.card-thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #999; font-size: 10px; }

.card-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.drawing-number { font-weight: 600; font-size: 14px; }
.series-meta { font-size: 12px; color: #888; }

.latest-tag { background: #27ae60; color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 8px; flex-shrink: 0; }
.arrow { color: #ccc; font-size: 14px; flex-shrink: 0; }
</style>
