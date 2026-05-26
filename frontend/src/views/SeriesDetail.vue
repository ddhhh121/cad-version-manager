<template>
  <div ref="rootEl">
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

      <div class="version-list" :class="`zoom-${zoom}`">
        <div v-for="v in versions" :key="v.id" class="version-row"
          :class="{ 'is-latest': v.version_number === latestVersionNumber }"
          @click="onVersionClick(v)">
          <div class="v-label">
            v{{ v.version_number }}
            <span v-if="v.version_number === latestVersionNumber" class="current-badge">当前</span>
          </div>
          <div class="v-body">
            <img v-if="v.thumbnail_path && zoom >= 1" :src="thumbnailUrl(v.id)" class="v-thumb" />
            <div v-else-if="zoom >= 1 && !v.thumbnail_path" class="v-thumb-placeholder">无预览</div>
            <div class="v-info">
              <div class="v-filename">{{ v.filename }}</div>
              <div class="v-meta">{{ formatDate(v.created_at) }} · {{ formatSize(v.file_size) }}</div>
              <div v-if="v.change_note && zoom >= 1" class="v-note">"{{ v.change_note }}"</div>
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
      </div>

      <div v-if="showZoomHint" class="zoom-hint">{{ zoomHint }}</div>

      <OldVersionWarning
        v-bind="warningData"
        :visible="showWarning"
        @dismiss="showWarning = false"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import OldVersionWarning from '../components/OldVersionWarning.vue'

const route = useRoute()
const projectId = route.params.projectId
const seriesId = route.params.seriesId
const series = ref(null)
const versions = ref([])
const rootEl = ref(null)
const loading = ref(true)
const error = ref('')
const uploadError = ref('')
const showWarning = ref(false)
const warningData = ref({})

// Zoom: 0=纯文字, 1=小缩略图, 2=中缩略图, 3=大缩略图
const zoom = ref(1)
const showZoomHint = ref(false)
const zoomHint = ref('')
let hintTimer = null

const zoomLabels = ['纯文字', '小缩略图', '中缩略图', '大缩略图']

function onWheel(e) {
  if (!e.ctrlKey) return
  e.preventDefault()
  if (e.deltaY < 0) {
    zoom.value = Math.min(3, zoom.value + 1)
  } else {
    zoom.value = Math.max(0, zoom.value - 1)
  }
  zoomHint.value = zoomLabels[zoom.value]
  showZoomHint.value = true
  clearTimeout(hintTimer)
  hintTimer = setTimeout(() => { showZoomHint.value = false }, 1000)
}

onMounted(() => {
  load()
  rootEl.value?.addEventListener('wheel', onWheel, { passive: false })
})

onUnmounted(() => {
  clearTimeout(hintTimer)
  rootEl.value?.removeEventListener('wheel', onWheel)
})

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
.v-info { font-size: 13px; }
.v-filename { font-weight: 500; margin-bottom: 2px; }
.v-meta { color: #999; font-size: 12px; }
.v-note { color: #555; font-style: italic; margin-top: 2px; font-size: 12px; }

.v-actions { margin-top: 8px; display: flex; gap: 14px; }
.action-link { font-size: 12px; color: #1a1a2e; text-decoration: none; }
.action-link:hover { text-decoration: underline; }
.compare-link { color: #e67e22; }

/* ── zoom 0: 纯文字 ── */
.zoom-0 .version-row { padding: 6px 12px; margin-bottom: 2px; }
.zoom-0 .v-label { margin-bottom: 0; display: inline; }
.zoom-0 .v-body { display: block; }
.zoom-0 .v-info { font-size: 12px; }
.zoom-0 .v-filename { display: inline; }
.zoom-0 .v-meta { display: inline; margin-left: 8px; }
.zoom-0 .v-actions { margin-top: 2px; }
.zoom-0 .v-thumb, .zoom-0 .v-thumb-placeholder { display: none; }

/* ── zoom 1: 小缩略图 ── */
.zoom-1 .v-thumb { width: 80px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; flex-shrink: 0; }
.zoom-1 .v-thumb-placeholder { width: 80px; height: 60px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; font-size: 10px; flex-shrink: 0; }

/* ── zoom 2: 中缩略图 ── */
.zoom-2 .v-thumb { width: 140px; height: 105px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; flex-shrink: 0; }
.zoom-2 .v-thumb-placeholder { width: 140px; height: 105px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; font-size: 12px; flex-shrink: 0; }

/* ── zoom 3: 大缩略图 ── */
.zoom-3 .version-row { padding: 14px 18px; }
.zoom-3 .v-thumb { width: 200px; height: 150px; object-fit: cover; border-radius: 6px; border: 1px solid #eee; flex-shrink: 0; }
.zoom-3 .v-thumb-placeholder { width: 200px; height: 150px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 6px; color: #999; font-size: 13px; flex-shrink: 0; }
.zoom-3 .v-label { font-size: 14px; }
.zoom-3 .v-info { font-size: 14px; }
.zoom-3 .v-meta { font-size: 13px; }

/* ── zoom hint ── */
.zoom-hint {
  position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,.75); color: #fff; padding: 8px 20px;
  border-radius: 20px; font-size: 13px; z-index: 200;
  pointer-events: none; animation: fade-out .3s .7s forwards;
}
@keyframes fade-out { to { opacity: 0; } }
</style>
