<template>
  <div>
    <div class="page-header">
      <h1>项目</h1>
      <button class="btn-primary" @click="showCreate = true">+ 新建项目</button>
    </div>

    <div v-if="showCreate" class="create-form">
      <input v-model="newName" placeholder="项目名称" @keyup.enter="create" />
      <input v-model="newDesc" placeholder="描述（可选）" />
      <button class="btn-primary" @click="create">创建</button>
      <button class="btn-ghost" @click="showCreate = false">取消</button>
    </div>

    <div class="toolbar">
      <input v-model="searchQuery" placeholder="搜索项目名称..." class="search-input" @input="onSearchInput" />
      <select v-model="sortBy" class="sort-select" @change="load">
        <option value="created_at">创建时间</option>
        <option value="name">名称</option>
        <option value="series_count">图纸数</option>
      </select>
      <button class="btn-icon" @click="orderAsc = !orderAsc; load()">
        {{ orderAsc ? '↑' : '↓' }}
      </button>
    </div>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="card-grid">
      <ProjectCard
        v-for="p in projects" :key="p.id" :project="p"
        @deleted="load" @renamed="load"
      />
      <div v-if="projects.length === 0" class="empty">
        {{ searchQuery ? '没有匹配的项目' : '还没有项目，新建一个吧' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api/index.js'
import ProjectCard from '../components/ProjectCard.vue'

const projects = ref([])
const loading = ref(true)
const error = ref('')
const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')
const searchQuery = ref('')
const sortBy = ref('created_at')
const orderAsc = ref(false)

let searchTimer = null

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(load, 300)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    projects.value = await api.listProjects({
      search: searchQuery.value || undefined,
      sort_by: sortBy.value,
      order: orderAsc.value ? 'asc' : 'desc',
    })
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function create() {
  if (!newName.value.trim()) return
  await api.createProject({ name: newName.value.trim(), description: newDesc.value.trim() })
  showCreate.value = false
  newName.value = ''
  newDesc.value = ''
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { font-size: 24px; }
.btn-primary { background: #1a1a2e; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-ghost { background: none; border: 1px solid #ccc; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-left: 8px; }

.toolbar { display: flex; gap: 8px; margin-bottom: 16px; align-items: center; }
.search-input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; min-width: 0; }
.search-input:focus { outline: none; border-color: #1a1a2e; }
.sort-select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; background: #fff; cursor: pointer; }
.btn-icon { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 8px 12px; cursor: pointer; font-size: 16px; }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.create-form { background: #fff; padding: 16px; border-radius: 8px; margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.create-form input { flex: 1; min-width: 140px; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
.empty { color: #999; text-align: center; padding: 60px; }
.error { color: #e74c3c; padding: 16px; }
</style>
