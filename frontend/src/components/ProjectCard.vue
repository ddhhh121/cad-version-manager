<template>
  <div class="project-card" @click="$router.push(`/project/${project.id}`)">
    <div class="card-top">
      <div v-if="editing" class="edit-row" @click.stop>
        <input
          ref="nameInput"
          v-model="editName"
          class="edit-input"
          @keydown.enter="doRename"
          @keydown.escape="editing = false"
          @blur="doRename"
        />
        <button class="btn-icon-sm" @click="doRename">✓</button>
        <button class="btn-icon-sm" @click="editing = false">✕</button>
      </div>
      <h3 v-else>
        {{ project.name }}
        <button class="btn-icon-link" @click.stop="startRename" title="重命名">✎</button>
      </h3>
      <button class="btn-icon-link del-icon" @click.stop="showConfirm = true" title="删除项目">✕</button>
    </div>
    <p class="desc">{{ project.description || '暂无描述' }}</p>
    <div class="meta">
      <span>{{ project.series_count }} 个图纸系列</span>
      <span>{{ formatDate(project.created_at) }}</span>
    </div>

    <ConfirmDialog
      :visible="showConfirm"
      title="删除项目"
      :message="`确定要删除项目「${project.name}」吗？其中的所有图纸和版本都会被永久删除。`"
      @confirm="doDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { api } from '../api/index.js'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({ project: Object })
const emit = defineEmits(['deleted', 'renamed'])

const editing = ref(false)
const editName = ref('')
const nameInput = ref(null)
const showConfirm = ref(false)

function formatDate(d) {
  return new Date(d).toLocaleDateString('zh-CN')
}

async function startRename() {
  editName.value = props.project.name
  editing.value = true
  await nextTick()
  nameInput.value?.focus()
}

async function doRename() {
  const name = editName.value.trim()
  editing.value = false
  if (!name || name === props.project.name) return
  try {
    await api.updateProject(props.project.id, { name })
    emit('renamed')
  } catch (e) { /* ignore */ }
}

async function doDelete() {
  showConfirm.value = false
  try {
    await api.deleteProject(props.project.id)
    emit('deleted')
  } catch (e) { /* ignore */ }
}
</script>

<style scoped>
.project-card {
  background: #fff; border-radius: 8px; padding: 20px;
  cursor: pointer; transition: box-shadow .2s;
  border: 1px solid #e8e8e8; position: relative;
}
.project-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.1); }
.project-card h3 { font-size: 18px; margin-bottom: 8px; }
.project-card .desc { color: #666; font-size: 14px; margin-bottom: 12px; }
.project-card .meta { display: flex; justify-content: space-between; color: #999; font-size: 13px; }

.card-top { display: flex; justify-content: space-between; align-items: flex-start; }
.edit-row { display: flex; gap: 4px; flex: 1; }
.edit-input { font-size: 18px; font-weight: 700; border: 1px solid #1a1a2e; border-radius: 4px; padding: 2px 6px; flex: 1; min-width: 0; }

.btn-icon-link {
  background: none; border: none; color: #bbb; cursor: pointer;
  font-size: 14px; padding: 0 4px; line-height: 1;
}
.btn-icon-link:hover { color: #1a1a2e; }
.del-icon { color: #ccc; }
.del-icon:hover { color: #e74c3c; }

.btn-icon-sm {
  background: none; border: 1px solid #ccc; border-radius: 4px;
  cursor: pointer; font-size: 14px; padding: 2px 8px;
}
</style>
