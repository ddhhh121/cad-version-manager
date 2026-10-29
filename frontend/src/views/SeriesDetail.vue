<template>
  <div ref="rootEl">
    <router-link :to="`/project/${projectId}`" class="back-link">← 返回项目</router-link>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="series">
      <div class="page-header">
        <h1>{{ series.drawing_number }}</h1>
        <div class="header-actions">
          <div class="export-dropdown" @click.stop="showExportMenu = !showExportMenu">
            <button class="export-btn">导出 ▾</button>
            <div v-if="showExportMenu" class="export-menu">
              <a :href="exportUrl('excel')" class="export-item">导出 Excel</a>
              <a :href="exportUrl('pdf')" class="export-item">导出 PDF</a>
            </div>
          </div>
          <label class="upload-btn">
            上传新版本
            <input type="file" accept=".dwg,.dxf" hidden @change="onUpload" />
          </label>
        </div>
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
              <div v-if="v.tags && v.tags.length > 0 && zoom >= 1" class="v-tags">
                <span v-for="tag in v.tags" :key="tag" class="tag-badge" :class="getTagClass(tag)">{{ tag }}</span>
              </div>
            </div>
          </div>
          <div class="v-actions">
            <button class="action-link" @click.stop="openPreview(v)">预览</button>
            <a :href="downloadUrl(v.id)" class="action-link" @click.stop>下载</a>
            <router-link
              v-if="v.version_number < latestVersionNumber && latestVersionId"
              :to="`/compare/${v.id}/${latestVersionId}`"
              class="action-link compare-link"
              @click.stop
            >与最新对比</router-link>
            <button class="action-link" @click.stop="openTagEditor(v)">标签</button>
            <button class="action-link delete-link" @click.stop="confirmDeleteVersion(v)">删除</button>
          </div>
        </div>
      </div>

      <div v-if="showZoomHint" class="zoom-hint">{{ zoomHint }}</div>

      <OldVersionWarning
        v-bind="warningData"
        :visible="showWarning"
        @dismiss="showWarning = false"
      />

      <ConfirmDialog
        :visible="deleteTarget.visible"
        title="删除版本"
        :message="`确定要删除「v${deleteTarget.item?.version_number || ''}」吗？此操作不可撤销。`"
        @confirm="doDeleteVersion"
        @cancel="deleteTarget.visible = false"
      />

      <!-- 文件预览 -->
      <FilePreview
        :visible="previewVisible"
        :versionId="previewVersion?.id"
        :title="`预览 - v${previewVersion?.version_number || ''}`"
        :downloadUrl="previewVersion ? downloadUrl(previewVersion.id) : ''"
        @close="closePreview"
      />

      <!-- 标签编辑面板 -->
      <div v-if="tagEditor.visible" class="tag-editor-overlay" @click.self="tagEditor.visible = false">
        <div class="tag-editor">
          <h3>编辑标签 - v{{ tagEditor.version?.version_number }}</h3>
          <div class="preset-tags">
            <span class="preset-label">预设标签：</span>
            <button v-for="preset in presetTags" :key="preset"
              class="preset-btn" :class="{ active: tagEditor.tags.includes(preset) }"
              @click="togglePresetTag(preset)">
              {{ preset }}
            </button>
          </div>
          <div class="custom-tag-input">
            <input v-model="tagEditor.newTag" placeholder="输入自定义标签" @keyup.enter="addCustomTag" />
            <button @click="addCustomTag">添加</button>
          </div>
          <div class="current-tags">
            <span class="current-label">当前标签：</span>
            <span v-for="tag in tagEditor.tags" :key="tag" class="tag-badge" :class="getTagClass(tag)">
              {{ tag }}
              <button class="tag-remove" @click="removeTag(tag)">×</button>
            </span>
            <span v-if="tagEditor.tags.length === 0" class="no-tags">暂无标签</span>
          </div>
          <div class="tag-editor-actions">
            <button class="save-btn" @click="saveTags">保存</button>
            <button class="cancel-btn" @click="tagEditor.visible = false">取消</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/index.js'
import OldVersionWarning from '../components/OldVersionWarning.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import FilePreview from '../components/FilePreview.vue'

const route = useRoute()
const router = useRouter()
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
const deleteTarget = ref({ visible: false, item: null })
const showExportMenu = ref(false)

// 文件预览
const previewVisible = ref(false)
const previewVersion = ref(null)

// 标签编辑
const presetTags = ['审核通过', '施工图', '方案图', '已废弃', '待审核', '已归档']
const tagEditor = ref({ visible: false, version: null, tags: [], newTag: '' })

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

function confirmDeleteVersion(v) {
  deleteTarget.value = { visible: true, item: v }
}

async function doDeleteVersion() {
  const v = deleteTarget.value.item
  deleteTarget.value.visible = false
  if (!v) return
  try {
    const result = await api.deleteVersion(v.id)
    if (result.series_deleted) {
      router.push(`/project/${projectId}`)
    } else {
      versions.value = await api.listVersions(seriesId)
      series.value = await api.getSeries(seriesId)
    }
  } catch (e) { /* ignore */ }
}

function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }

function exportUrl(format) {
  return api.getExportSeriesUrl(seriesId, format)
}

// 点击外部关闭导出菜单
document.addEventListener('click', () => { showExportMenu.value = false })

// 标签相关函数
function getTagClass(tag) {
  const classes = {
    '审核通过': 'tag-success',
    '施工图': 'tag-primary',
    '方案图': 'tag-info',
    '已废弃': 'tag-danger',
    '待审核': 'tag-warning',
    '已归档': 'tag-secondary',
  }
  return classes[tag] || 'tag-default'
}

function openTagEditor(v) {
  tagEditor.value = {
    visible: true,
    version: v,
    tags: [...(v.tags || [])],
    newTag: '',
  }
}

function togglePresetTag(tag) {
  const idx = tagEditor.value.tags.indexOf(tag)
  if (idx >= 0) {
    tagEditor.value.tags.splice(idx, 1)
  } else {
    tagEditor.value.tags.push(tag)
  }
}

function addCustomTag() {
  const tag = tagEditor.value.newTag.trim()
  if (tag && !tagEditor.value.tags.includes(tag)) {
    tagEditor.value.tags.push(tag)
    tagEditor.value.newTag = ''
  }
}

function removeTag(tag) {
  const idx = tagEditor.value.tags.indexOf(tag)
  if (idx >= 0) {
    tagEditor.value.tags.splice(idx, 1)
  }
}

async function saveTags() {
  const v = tagEditor.value.version
  if (!v) return
  try {
    await api.updateTags(v.id, tagEditor.value.tags)
    v.tags = [...tagEditor.value.tags]
    tagEditor.value.visible = false
  } catch (e) {
    // ignore
  }
}

function openPreview(v) {
  previewVersion.value = v
  previewVisible.value = true
}

function closePreview() {
  previewVisible.value = false
  previewVersion.value = null
}
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
.header-actions { display: flex; gap: 12px; align-items: center; }
.upload-btn { background: #1a1a2e; color: #fff; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.upload-btn:hover { background: #2a2a4e; }

.export-dropdown { position: relative; }
.export-btn { background: #f5f5f5; border: 1px solid #ddd; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.export-btn:hover { background: #eee; }
.export-menu { position: absolute; top: 100%; right: 0; background: #fff; border: 1px solid #ddd; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 10; min-width: 140px; }
.export-item { display: block; padding: 10px 16px; color: #333; text-decoration: none; font-size: 14px; }
.export-item:hover { background: #f5f5f5; }

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
.delete-link { color: #e74c3c; background: none; border: none; cursor: pointer; font-size: 12px; padding: 0; }
.delete-link:hover { text-decoration: underline; }

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

/* ── tags ── */
.v-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.tag-badge { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 10px; font-weight: 500; }
.tag-badge.tag-success { background: #e8f5e9; color: #2e7d32; }
.tag-badge.tag-primary { background: #e3f2fd; color: #1565c0; }
.tag-badge.tag-info { background: #e0f7fa; color: #00838f; }
.tag-badge.tag-danger { background: #ffebee; color: #c62828; }
.tag-badge.tag-warning { background: #fff8e1; color: #f57f17; }
.tag-badge.tag-secondary { background: #f5f5f5; color: #616161; }
.tag-badge.tag-default { background: #eee; color: #666; }

/* ── tag editor ── */
.tag-editor-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.tag-editor { background: #fff; border-radius: 12px; padding: 24px; width: 420px; max-width: 90vw; }
.tag-editor h3 { font-size: 18px; margin-bottom: 20px; }
.preset-tags { margin-bottom: 16px; }
.preset-label { font-size: 13px; color: #666; margin-bottom: 8px; display: block; }
.preset-btn { background: #f5f5f5; border: 1px solid #ddd; padding: 6px 14px; border-radius: 16px; margin: 4px; cursor: pointer; font-size: 13px; }
.preset-btn:hover { background: #eee; }
.preset-btn.active { background: #1a1a2e; color: #fff; border-color: #1a1a2e; }
.custom-tag-input { display: flex; gap: 8px; margin-bottom: 16px; }
.custom-tag-input input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
.custom-tag-input button { background: #1a1a2e; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
.current-tags { margin-bottom: 20px; min-height: 32px; }
.current-label { font-size: 13px; color: #666; margin-bottom: 8px; display: block; }
.tag-remove { background: none; border: none; color: inherit; cursor: pointer; margin-left: 4px; font-size: 12px; opacity: 0.7; }
.tag-remove:hover { opacity: 1; }
.no-tags { color: #999; font-size: 13px; }
.tag-editor-actions { display: flex; gap: 12px; justify-content: flex-end; }
.save-btn { background: #27ae60; color: #fff; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; }
.cancel-btn { background: #f5f5f5; border: 1px solid #ddd; padding: 10px 24px; border-radius: 6px; cursor: pointer; }

/* 移动端适配 */
@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 12px; align-items: stretch; }
  .page-header h1 { font-size: 18px; word-break: break-all; }
  .header-actions { flex-wrap: wrap; }
  .upload-btn, .export-btn { flex: 1; text-align: center; }
  .v-body { flex-direction: column; }
  .v-thumb, .v-thumb-placeholder { width: 100% !important; height: 120px !important; }
  .v-actions { flex-wrap: wrap; gap: 8px; }
  .action-link { font-size: 13px; padding: 4px 0; }
  .tag-editor { padding: 16px; }
  .preset-btn { padding: 8px 12px; font-size: 14px; }
  .custom-tag-input { flex-direction: column; }
}
</style>
