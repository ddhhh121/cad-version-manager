<template>
  <div>
    <router-link to="/" class="back-link">← 返回项目列表</router-link>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="project">
      <div class="project-header">
        <div v-if="editingTitle" class="edit-title-row">
          <input
            ref="titleInput"
            v-model="editName"
            class="edit-title-input"
            @keydown.enter="doRename"
            @keydown.escape="editingTitle = false"
            @blur="doRename"
          />
          <button class="btn-sm" @click="doRename">✓</button>
          <button class="btn-sm-ghost" @click="editingTitle = false">✕</button>
        </div>
        <h1 v-else>
          {{ project.name }}
          <button class="btn-edit-icon" @click="startRename" title="重命名">✎</button>
        </h1>
        <label class="upload-btn">
          上传图纸
          <input type="file" accept=".dwg,.dxf" hidden @change="onUpload" />
        </label>
      </div>

      <div v-if="uploadError" class="error">{{ uploadError }}</div>

      <div v-if="seriesList.length === 0" class="empty">还没有图纸，上传第一个开始管理</div>

      <div v-for="s in seriesList" :key="s.id" class="series-row">
        <router-link
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
        <button class="btn-del-series" @click="confirmDeleteSeries(s)" title="删除系列">✕</button>
      </div>
    </template>

    <ConfirmDialog
      :visible="deleteTarget.visible"
      title="删除图纸系列"
      :message="`确定要删除「${deleteTarget.item?.drawing_number || ''}」吗？所有版本都会被永久删除。`"
      @confirm="doDeleteSeries"
      @cancel="deleteTarget.visible = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const route = useRoute()
const project = ref(null)
const seriesList = ref([])
const loading = ref(true)
const error = ref('')
const uploadError = ref('')
const editingTitle = ref(false)
const editName = ref('')
const titleInput = ref(null)
const deleteTarget = reactive({ visible: false, item: null })

async function loadProject() {
  loading.value = true
  error.value = ''
  try {
    project.value = await api.getProject(route.params.id)
    seriesList.value = project.value.series_list || []
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function startRename() {
  editName.value = project.value.name
  editingTitle.value = true
  await nextTick()
  titleInput.value?.focus()
}

async function doRename() {
  const name = editName.value.trim()
  editingTitle.value = false
  if (!name || name === project.value.name) return
  try {
    await api.updateProject(project.value.id, { name })
    project.value.name = name
  } catch (e) { /* ignore */ }
}

function confirmDeleteSeries(s) {
  deleteTarget.item = s
  deleteTarget.visible = true
}

async function doDeleteSeries() {
  const s = deleteTarget.item
  deleteTarget.visible = false
  if (!s) return
  try {
    await api.deleteSeries(s.id)
    await loadProject()
  } catch (e) { /* ignore */ }
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

.edit-title-row { display: flex; gap: 4px; align-items: center; }
.edit-title-input { font-size: 24px; font-weight: 700; border: 1px solid #1a1a2e; border-radius: 4px; padding: 2px 8px; width: 300px; }
.btn-sm { background: #1a1a2e; color: #fff; border: none; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 14px; }
.btn-sm-ghost { background: none; border: 1px solid #ccc; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 14px; }
.btn-edit-icon { background: none; border: none; color: #bbb; cursor: pointer; font-size: 16px; padding: 0 4px; }
.btn-edit-icon:hover { color: #1a1a2e; }

.empty { color: #999; text-align: center; padding: 60px; }
.error { color: #e74c3c; padding: 8px 0; margin-bottom: 8px; font-size: 14px; }

.series-row { display: flex; align-items: stretch; gap: 0; margin-bottom: 6px; }
.series-card {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border-radius: 6px 0 0 6px; padding: 10px 14px;
  border: 1px solid #e8e8e8; text-decoration: none; color: inherit;
  transition: box-shadow .15s; flex: 1;
}
.series-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.btn-del-series {
  background: #fff; border: 1px solid #e8e8e8; border-left: none;
  border-radius: 0 6px 6px 0; color: #ccc; cursor: pointer;
  font-size: 14px; padding: 0 12px; flex-shrink: 0;
}
.btn-del-series:hover { color: #e74c3c; background: #fef0f0; }

.card-thumb { width: 60px; height: 45px; border-radius: 4px; overflow: hidden; background: #eee; flex-shrink: 0; }
.card-thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #999; font-size: 10px; }

.card-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.drawing-number { font-weight: 600; font-size: 14px; }
.series-meta { font-size: 12px; color: #888; }

.latest-tag { background: #27ae60; color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 8px; flex-shrink: 0; }
.arrow { color: #ccc; font-size: 14px; flex-shrink: 0; }
</style>
