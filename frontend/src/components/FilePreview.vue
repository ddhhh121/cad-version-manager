<template>
  <div v-if="visible" class="preview-overlay" @click.self="close">
    <div class="preview-container">
      <div class="preview-header">
        <h3>{{ title }}</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>

      <div class="preview-content">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else-if="preview.type === 'svg'" class="svg-container" ref="svgContainer">
          <div v-html="preview.content" class="svg-wrapper"
            :style="{ transform: `scale(${scale}) translate(${panX}px, ${panY}px)` }"
            @mousedown="startPan"
            @mousemove="onPan"
            @mouseup="endPan"
            @mouseleave="endPan"
          ></div>
        </div>
        <div v-else-if="preview.type === 'unsupported'" class="unsupported">
          <div class="unsupported-icon">📄</div>
          <div class="unsupported-message">{{ preview.message }}</div>
          <a v-if="downloadUrl" :href="downloadUrl" class="download-link">下载文件</a>
        </div>
        <div v-else class="error">{{ preview.message || '预览失败' }}</div>
      </div>

      <div v-if="preview.type === 'svg'" class="preview-controls">
        <button @click="zoomIn" title="放大">+</button>
        <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
        <button @click="zoomOut" title="缩小">-</button>
        <button @click="resetView" title="重置">⟲</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { api } from '../api/index.js'

const props = defineProps({
  visible: Boolean,
  versionId: Number,
  title: { type: String, default: '文件预览' },
  downloadUrl: String,
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref('')
const preview = ref({ type: null })
const scale = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const lastMouseX = ref(0)
const lastMouseY = ref(0)

watch(() => props.visible, async (val) => {
  if (val && props.versionId) {
    await loadPreview()
  } else {
    resetView()
  }
})

async function loadPreview() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`/api/versions/${props.versionId}/preview`)
    preview.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function close() {
  emit('close')
}

function zoomIn() {
  scale.value = Math.min(5, scale.value * 1.2)
}

function zoomOut() {
  scale.value = Math.max(0.1, scale.value / 1.2)
}

function resetView() {
  scale.value = 1
  panX.value = 0
  panY.value = 0
}

function startPan(e) {
  if (e.button !== 0) return
  isPanning.value = true
  lastMouseX.value = e.clientX
  lastMouseY.value = e.clientY
}

function onPan(e) {
  if (!isPanning.value) return
  const dx = e.clientX - lastMouseX.value
  const dy = e.clientY - lastMouseY.value
  panX.value += dx / scale.value
  panY.value += dy / scale.value
  lastMouseX.value = e.clientX
  lastMouseY.value = e.clientY
}

function endPan() {
  isPanning.value = false
}
</script>

<style scoped>
.preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.preview-container {
  background: #fff;
  border-radius: 12px;
  width: 90vw;
  max-width: 1000px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.preview-header h3 {
  font-size: 18px;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.preview-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #e74c3c;
}

.svg-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  cursor: grab;
  background: #f8f8f8;
}

.svg-container:active {
  cursor: grabbing;
}

.svg-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform-origin: center center;
}

.svg-wrapper :deep(svg) {
  max-width: 90%;
  max-height: 90%;
}

.unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
}

.unsupported-icon {
  font-size: 48px;
}

.unsupported-message {
  color: #666;
  font-size: 16px;
}

.download-link {
  background: #1a1a2e;
  color: #fff;
  padding: 10px 24px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
}

.download-link:hover {
  background: #2a2a4e;
}

.preview-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px;
  border-top: 1px solid #eee;
  background: #fafafa;
}

.preview-controls button {
  background: #fff;
  border: 1px solid #ddd;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-controls button:hover {
  background: #f5f5f5;
}

.zoom-level {
  font-size: 14px;
  color: #666;
  min-width: 50px;
  text-align: center;
}
</style>
