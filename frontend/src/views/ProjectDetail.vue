<template>
  <div>
    <router-link to="/" class="back-link">← 返回项目列表</router-link>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="project">
      <div class="project-header">
        <h1>{{ project.name }}</h1>
      </div>

      <div class="detail-layout">
        <aside class="sidebar">
          <DrawingSeriesList
            :series="seriesList"
            :selectedId="selectedSeries?.id"
            @select="selectedSeries = $event"
          />
        </aside>
        <section class="main-area">
          <VersionTimeline
            :series="selectedSeries"
            :projectId="project.id"
            @refresh="loadProject"
          />
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import DrawingSeriesList from '../components/DrawingSeriesList.vue'
import VersionTimeline from '../components/VersionTimeline.vue'

const route = useRoute()
const project = ref(null)
const seriesList = ref([])
const selectedSeries = ref(null)
const loading = ref(true)
const error = ref('')

async function loadProject() {
  loading.value = true
  error.value = ''
  try {
    project.value = await api.getProject(route.params.id)
    seriesList.value = project.value.series_list || []
    if (selectedSeries.value) {
      const updated = seriesList.value.find(s => s.id === selectedSeries.value.id)
      selectedSeries.value = updated || seriesList.value[0] || null
    } else if (seriesList.value.length > 0) {
      selectedSeries.value = seriesList.value[0]
    }
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

onMounted(loadProject)
</script>

<style scoped>
.back-link { color: #1a1a2e; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }
.project-header { margin-bottom: 20px; }
.project-header h1 { font-size: 24px; }
.detail-layout { display: grid; grid-template-columns: 320px 1fr; gap: 20px; align-items: start; }
@media (max-width: 768px) { .detail-layout { grid-template-columns: 1fr; } }
.error { color: #e74c3c; padding: 16px; }
</style>
