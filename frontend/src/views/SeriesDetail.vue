<template>
  <div>
    <router-link :to="`/project/${projectId}`" class="back-link">← 返回项目</router-link>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="series">
      <div class="page-header">
        <h1>{{ series.drawing_number }}</h1>
        <label class="upload-btn">
          上传新版本
          <input type="file" accept=".dwg,.dxf" hidden @change="onUpload" />
        </label>
      </div>

      <div v-if="uploadError" class="error">{{ uploadError }}</div>
      <div v-if="versions.length === 0" class="empty">暂无版本</div>

      <div v-for="v in versions" :key="v.id" class="version-row"
        :class="{ 'is-latest': v.version_number === latestVersionNumber }"
        @click="onVersionClick(v)">
        <div class="v-label">
          v{{ v.version_number }}
          <span v-if="v.version_number === latestVersionNumber" class="current-badge">当前最新</span>
        </div>
        <div class="v-body">
          <img v-if="v.thumbnail_path" :src="thumbnailUrl(v.id)" class="v-thumb" />
          <div v-else class="v-thumb-placeholder">无预览</div>
          <div class="v-info">
            <div class="v-filename">{{ v.filename }}</div>
            <div class="v-meta">{{ formatDate(v.created_at) }} · {{ formatSize(v.file_size) }}</div>
            <div v-if="v.change_note" class="v-note">"{{ v.change_note }}"</div>
          </div>
        </div>
        <div class="v-actions">
          <a :href="downloadUrl(v.id)" class="action-link" @click.stop>下载</a>
          <router-link
            v-if="v.version_number < latestVersionNumber && latestVersionId"
            :to="`/compare/${v.id}/${latestVersionId}`"
            class="action-link compare-link"
            @click.stop
          >与最新对比</router-link>
        </div>
      </div>

      <OldVersionWarning
        v-bind="warningData"
        :visible="showWarning"
        @dismiss="showWarning = false"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import OldVersionWarning from '../components/OldVersionWarning.vue'

const route = useRoute()
const projectId = route.params.projectId
const seriesId = route.params.seriesId
const series = ref(null)
const versions = ref([])
const loading = ref(true)
const error = ref('')
const uploadError = ref('')
const showWarning = ref(false)
const warningData = ref({})

const latestVersionNumber = computed(() =>
  versions.value.length > 0 ? versions.value[0].version_number : 0
)
const latestVersionId = computed(() =>
  versions.value.length > 0 ? versions.value[0].id : null
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    series.value = await api.getSeries(seriesId)
    versions.value = await api.listVersions(seriesId)
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

function onVersionClick(v) {
  if (v.version_number < latestVersionNumber.value) {
    warningData.value = {
      currentVersion: v.version_number,
      latestVersion: latestVersionNumber.value,
      latestVersionId: latestVersionId.value,
      latestNote: versions.value[0]?.change_note || '',
      latestDate: formatDate(versions.value[0]?.created_at),
      targetPath: `/compare/${v.id}/${latestVersionId.value}`,
    }
    showWarning.value = true
  }
}

async function onUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadError.value = ''
  try {
    await api.uploadDrawing(projectId, file)
    versions.value = await api.listVersions(seriesId)
    series.value = await api.getSeries(seriesId)
  } catch (e) { uploadError.value = e.message }
  e.target.value = ''
}

function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }
function downloadUrl(vid) { return api.getDownloadUrl(vid) }
function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

onMounted(load)
</script>

<style scoped>
.back-link { color: #1a1a2e; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h1 { font-size: 24px; }
.upload-btn { background: #1a1a2e; color: #fff; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.upload-btn:hover { background: #2a2a4e; }

.empty { color: #999; text-align: center; padding: 60px; }
.error { color: #e74c3c; padding: 8px 0; margin-bottom: 8px; font-size: 14px; }

.version-row { background: #fff; border-radius: 6px; padding: 10px 14px; margin-bottom: 6px; border: 1px solid #e8e8e8; cursor: pointer; }
.version-row:hover { background: #fcfcfc; }
.version-row.is-latest { border-color: #27ae60; background: #f0faf4; }
.version-row.is-latest:hover { background: #e8f6ec; }

.v-label { font-weight: 600; font-size: 12px; margin-bottom: 6px; }
.current-badge { background: #27ae60; color: #fff; font-size: 10px; padding: 1px 7px; border-radius: 8px; margin-left: 6px; }

.v-body { display: flex; gap: 10px; }
.v-thumb { width: 100px; height: 75px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; flex-shrink: 0; }
.v-thumb-placeholder { width: 100px; height: 75px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; font-size: 11px; flex-shrink: 0; }
.v-info { font-size: 13px; }
.v-filename { font-weight: 500; margin-bottom: 2px; }
.v-meta { color: #999; font-size: 12px; }
.v-note { color: #555; font-style: italic; margin-top: 2px; font-size: 12px; }

.v-actions { margin-top: 8px; display: flex; gap: 14px; }
.action-link { font-size: 12px; color: #1a1a2e; text-decoration: none; }
.action-link:hover { text-decoration: underline; }
.compare-link { color: #e67e22; }
</style>
