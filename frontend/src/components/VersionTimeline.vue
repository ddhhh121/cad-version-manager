<template>
  <div class="timeline">
    <div class="timeline-header">
      <h3>{{ series?.drawing_number || '请选择图纸' }}</h3>
      <label class="upload-btn">
        上传新版本
        <input type="file" accept=".dwg,.dxf" hidden @change="onUpload" />
      </label>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="versions.length === 0 && series" class="empty">暂无版本，上传第一个图纸开始管理</div>
    <div v-if="!series" class="empty">请从左侧选择一个图纸系列</div>

    <div v-for="v in versions" :key="v.id" class="version-item"
      :class="{ latest: v.version_number === latestVersionNumber }"
      @click="onClickVersion(v)">
      <div class="version-header">
        <span class="version-label">
          v{{ v.version_number }}
          <span v-if="v.version_number === latestVersionNumber" class="latest-tag">当前最新</span>
        </span>
        <span class="version-date">{{ formatDate(v.created_at) }}</span>
      </div>
      <div class="version-body">
        <img v-if="v.thumbnail_path" :src="thumbnailUrl(v.id)" class="version-thumb" />
        <div v-else class="thumb-placeholder">无预览</div>
        <div class="version-info">
          <div>{{ v.filename }}</div>
          <div class="size">{{ formatSize(v.file_size) }}</div>
          <div v-if="v.change_note" class="note">"{{ v.change_note }}"</div>
        </div>
      </div>
      <div class="version-actions">
        <a :href="downloadUrl(v.id)" class="action-link" @click.stop>下载</a>
        <router-link
          v-if="latestVersionId && v.version_number < latestVersionNumber"
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
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { api } from '../api/index.js'
import OldVersionWarning from './OldVersionWarning.vue'

const props = defineProps({ series: Object, projectId: Number })
const emit = defineEmits(['refresh'])

const versions = ref([])
const error = ref('')
const showWarning = ref(false)
const warningData = ref({})

const latestVersionNumber = computed(() =>
  versions.value.length > 0 ? versions.value[0].version_number : 0
)
const latestVersionId = computed(() =>
  versions.value.length > 0 ? versions.value[0].id : null
)

async function loadVersions() {
  if (!props.series) return
  error.value = ''
  try { versions.value = await api.listVersions(props.series.id) }
  catch (e) { error.value = e.message }
}

async function onUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  error.value = ''
  try {
    await api.uploadDrawing(props.projectId, file)
    await loadVersions()
    emit('refresh')
  } catch (e) { error.value = e.message }
  e.target.value = ''
}

function onClickVersion(v) {
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

watch(() => props.series, loadVersions)
</script>

<style scoped>
.timeline { background: #fff; border-radius: 8px; padding: 20px; border: 1px solid #e8e8e8; }
.timeline-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.timeline-header h3 { font-size: 20px; }
.upload-btn { background: #1a1a2e; color: #fff; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.version-item { border-left: 3px solid #ddd; padding: 12px 16px; margin-bottom: 8px; border-radius: 0 6px 6px 0; cursor: pointer; }
.version-item.latest { border-left-color: #27ae60; background: #f0faf4; }
.version-item:hover { background: #f9f9f9; }
.version-item.latest:hover { background: #eafaf1; }
.version-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.version-label { font-weight: 600; }
.latest-tag { background: #27ae60; color: #fff; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; font-weight: 400; }
.version-date { font-size: 13px; color: #999; }
.version-body { display: flex; gap: 12px; }
.version-thumb { width: 120px; height: 90px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; }
.thumb-placeholder { width: 120px; height: 90px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; font-size: 12px; }
.version-info { font-size: 14px; }
.version-info .size { color: #999; font-size: 13px; }
.version-info .note { color: #555; font-style: italic; margin-top: 4px; }
.version-actions { margin-top: 8px; display: flex; gap: 16px; }
.action-link { font-size: 13px; color: #1a1a2e; text-decoration: none; }
.action-link:hover { text-decoration: underline; }
.compare-link { color: #e67e22; }
.empty { color: #999; text-align: center; padding: 40px; }
.error { color: #e74c3c; padding: 8px; margin-bottom: 8px; font-size: 14px; }
</style>
