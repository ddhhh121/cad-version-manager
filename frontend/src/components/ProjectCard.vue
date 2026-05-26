<template>
  <div class="project-card" @click="$router.push(`/project/${project.id}`)">
    <h3>{{ project.name }}</h3>
    <p class="desc">{{ project.description || '暂无描述' }}</p>
    <div class="meta">
      <span>{{ project.series_count }} 个图纸系列</span>
      <span>{{ formatDate(project.created_at) }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ project: Object })
function formatDate(d) {
  return new Date(d).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.project-card {
  background: #fff; border-radius: 8px; padding: 20px;
  cursor: pointer; transition: box-shadow .2s;
  border: 1px solid #e8e8e8;
}
.project-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.1); }
.project-card h3 { font-size: 18px; margin-bottom: 8px; }
.project-card .desc { color: #666; font-size: 14px; margin-bottom: 12px; }
.project-card .meta { display: flex; justify-content: space-between; color: #999; font-size: 13px; }
</style>
