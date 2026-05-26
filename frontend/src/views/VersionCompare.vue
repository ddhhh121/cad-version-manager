<template>
  <div>
    <router-link :to="projectId ? `/project/${projectId}` : '/'" class="back-link">← 返回项目</router-link>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="vNew && vOld">
      <h2>{{ drawingNumber }} · 版本对比</h2>

      <!-- 新版卡片 -->
      <div class="version-card new-card">
        <div class="card-badge">v{{ vNew.version_number }} · 当前（新）</div>
        <div class="card-body">
          <img v-if="vNew.thumbnail_path" :src="thumbnailUrl(vNew.id)" class="compare-thumb" />
          <div v-else class="thumb-placeholder">无预览</div>
          <div class="card-info">
            <div>文件名: {{ vNew.filename }}</div>
            <div>上传: {{ formatDate(vNew.created_at) }}</div>
            <div v-if="vNew.change_note">变更: "{{ vNew.change_note }}"</div>
          </div>
        </div>
      </div>

      <!-- 旧版卡片 -->
      <div class="version-card old-card">
        <div class="card-badge old-badge">v{{ vOld.version_number }} · 上一个（旧）</div>
        <div class="card-body">
          <img v-if="vOld.thumbnail_path" :src="thumbnailUrl(vOld.id)" class="compare-thumb" />
          <div v-else class="thumb-placeholder">无预览</div>
          <div class="card-info">
            <div>文件名: {{ vOld.filename }}</div>
            <div>上传: {{ formatDate(vOld.created_at) }}</div>
          </div>
        </div>
      </div>

      <DiffTable :diffs="diffs" :oldVersionNumber="vOld.version_number" :newVersionNumber="vNew.version_number" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import DiffTable from '../components/DiffTable.vue'

const route = useRoute()
const vOld = ref(null)
const vNew = ref(null)
const diffs = ref([])
const drawingNumber = ref('')
const projectId = ref(null)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.compareVersions(route.params.vid1, route.params.vid2)
    vOld.value = data.version_old
    vNew.value = data.version_new
    diffs.value = data.diffs

    // Get the drawing number and project ID from the series
    const series = await api.getSeries(vNew.value.series_id)
    drawingNumber.value = series.drawing_number
    projectId.value = series.project_id
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }
function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}

onMounted(load)
</script>

<style scoped>
.back-link { color: #1a1a2e; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }
h2 { font-size: 22px; margin-bottom: 20px; }
.version-card { border-radius: 8px; padding: 0; margin-bottom: 16px; overflow: hidden; }
.new-card { border: 2px solid #27ae60; }
.old-card { border: 2px dashed #ccc; }
.card-badge { padding: 8px 16px; font-weight: 600; font-size: 14px; background: #27ae60; color: #fff; }
.old-badge { background: #bbb; }
.card-body { display: flex; gap: 16px; padding: 16px; }
.compare-thumb { width: 200px; height: 150px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; flex-shrink: 0; }
.thumb-placeholder { width: 200px; height: 150px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; }
.card-info { font-size: 14px; }
.error { color: #e74c3c; }
</style>
