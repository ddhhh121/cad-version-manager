<template>
  <div class="series-list">
    <div
      v-for="s in series"
      :key="s.id"
      class="series-item"
      :class="{ active: s.id === selectedId }"
      @click="$emit('select', s)"
    >
      <div class="thumb-wrapper">
        <img v-if="s.latest_version?.thumbnail_path"
          :src="thumbnailUrl(s.latest_version.id)"
          class="thumb" />
        <div v-else class="thumb-placeholder">无预览</div>
      </div>
      <div class="info">
        <span class="drawing-number">{{ s.drawing_number }}</span>
        <span class="version-badge">v{{ s.latest_version?.version_number || '?' }} · 共{{ s.version_count }}版</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { api } from '../api/index.js'
defineProps({ series: Array, selectedId: Number })
defineEmits(['select'])
function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }
</script>

<style scoped>
.series-list { display: flex; flex-direction: column; gap: 8px; }
.series-item { display: flex; gap: 12px; padding: 12px; border-radius: 8px; cursor: pointer; border: 2px solid transparent; background: #fff; }
.series-item.active { border-color: #1a1a2e; }
.series-item:hover { background: #fafafa; }
.thumb-wrapper { width: 100px; height: 75px; overflow: hidden; border-radius: 4px; background: #eee; flex-shrink: 0; }
.thumb { width: 100%; height: 100%; object-fit: cover; }
.thumb-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px; }
.info { display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.drawing-number { font-weight: 600; font-size: 16px; }
.version-badge { font-size: 13px; color: #666; }
</style>
