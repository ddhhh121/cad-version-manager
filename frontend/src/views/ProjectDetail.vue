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

      <div v-for="s in seriesList" :key="s.id" class="series-card">
        <div class="series-header" @click="toggleSeries(s.id)">
          <div class="series-title">
            <span class="drawing-number">{{ s.drawing_number }}</span>
            <span class="series-meta">v{{ s.latest_version?.version_number || '?' }} · 共{{ s.version_count }}版</span>
            <span v-if="s.latest_version" class="latest-tag">当前最新</span>
          </div>
          <span class="expand-icon">{{ expandedId === s.id ? '▼' : '▶' }}</span>
        </div>

        <div v-if="expandedId === s.id" class="series-body">
          <div v-if="versionsLoading[s.id]">加载中...</div>
          <div v-else v-for="v in versionsMap[s.id]" :key="v.id" class="version-row"
            :class="{ 'is-latest': v.version_number === getLatestVersionNumber(s.id) }"
            @click="onVersionClick(v, s.id)">
            <div class="v-label">
              v{{ v.version_number }}
              <span v-if="v.version_number === getLatestVersionNumber(s.id)" class="current-badge">当前</span>
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
                v-if="v.version_number < getLatestVersionNumber(s.id)"
                :to="`/compare/${v.id}/${getLatestVersionId(s.id)}`"
                class="action-link compare-link"
                @click.stop
              >与最新对比</router-link>
            </div>
          </div>
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
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import OldVersionWarning from '../components/OldVersionWarning.vue'

const route = useRoute()
const project = ref(null)
const seriesList = ref([])
const loading = ref(true)
const error = ref('')
const uploadError = ref('')

// Accordion state
const expandedId = ref(null)
const versionsMap = reactive({})
const versionsLoading = reactive({})

// Warning dialog state
const showWarning = ref(false)
const warningData = ref({})

async function loadProject() {
  loading.value = true
  error.value = ''
  try {
    project.value = await api.getProject(route.params.id)
    seriesList.value = project.value.series_list || []
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function toggleSeries(seriesId) {
  if (expandedId.value === seriesId) {
    expandedId.value = null
    return
  }
  expandedId.value = seriesId
  if (!versionsMap[seriesId]) {
    versionsLoading[seriesId] = true
    try {
      versionsMap[seriesId] = await api.listVersions(seriesId)
    } catch (e) {
      versionsMap[seriesId] = []
    }
    versionsLoading[seriesId] = false
  }
}

function getLatestVersionNumber(seriesId) {
  const vers = versionsMap[seriesId]
  return vers && vers.length > 0 ? vers[0].version_number : 0
}

function getLatestVersionId(seriesId) {
  const vers = versionsMap[seriesId]
  return vers && vers.length > 0 ? vers[0].id : null
}

function onVersionClick(v, seriesId) {
  const latestNum = getLatestVersionNumber(seriesId)
  if (v.version_number < latestNum) {
    warningData.value = {
      currentVersion: v.version_number,
      latestVersion: latestNum,
      latestVersionId: getLatestVersionId(seriesId),
      latestNote: versionsMap[seriesId]?.[0]?.change_note || '',
      latestDate: formatDate(versionsMap[seriesId]?.[0]?.created_at),
      targetPath: `/compare/${v.id}/${getLatestVersionId(seriesId)}`,
    }
    showWarning.value = true
  }
}

async function onUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadError.value = ''
  try {
    const result = await api.uploadDrawing(project.value.id, file)
    await loadProject()
    // Auto-expand the series that got the new version
    const sid = result.series_id
    versionsLoading[sid] = true
    versionsMap[sid] = await api.listVersions(sid)
    versionsLoading[sid] = false
    expandedId.value = sid
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

/* Series card */
.series-card { background: #fff; border-radius: 8px; margin-bottom: 12px; border: 1px solid #e8e8e8; overflow: hidden; }
.series-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; cursor: pointer; user-select: none; }
.series-header:hover { background: #fafafa; }
.series-title { display: flex; align-items: center; gap: 12px; }
.drawing-number { font-weight: 700; font-size: 18px; }
.series-meta { font-size: 13px; color: #888; }
.latest-tag { background: #27ae60; color: #fff; font-size: 11px; padding: 2px 10px; border-radius: 10px; }
.expand-icon { color: #999; font-size: 12px; }

/* Version rows inside expanded card */
.series-body { border-top: 1px solid #eee; }
.version-row { padding: 14px 20px; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.version-row:last-child { border-bottom: none; }
.version-row:hover { background: #fcfcfc; }
.version-row.is-latest { background: #f0faf4; }
.version-row.is-latest:hover { background: #e8f6ec; }

.v-label { font-weight: 600; font-size: 14px; margin-bottom: 8px; }
.current-badge { background: #27ae60; color: #fff; font-size: 10px; padding: 1px 8px; border-radius: 8px; margin-left: 6px; }

.v-body { display: flex; gap: 14px; }
.v-thumb { width: 140px; height: 105px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; flex-shrink: 0; }
.v-thumb-placeholder { width: 140px; height: 105px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; font-size: 12px; flex-shrink: 0; }
.v-info { font-size: 14px; }
.v-filename { font-weight: 500; margin-bottom: 4px; }
.v-meta { color: #999; font-size: 13px; }
.v-note { color: #555; font-style: italic; margin-top: 4px; font-size: 13px; }

.v-actions { margin-top: 10px; display: flex; gap: 18px; }
.action-link { font-size: 13px; color: #1a1a2e; text-decoration: none; }
.action-link:hover { text-decoration: underline; }
.compare-link { color: #e67e22; }
</style>
