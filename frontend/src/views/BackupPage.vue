<template>
  <div>
    <router-link to="/" class="back-link">← 返回首页</router-link>
    <BackupPanel />
  </div>
</template>

<script setup>
import BackupPanel from '../components/BackupPanel.vue'
</script>

<style scoped>
.back-link {
  color: #1a1a2e;
  text-decoration: none;
  font-size: 14px;
  display: inline-block;
  margin-bottom: 16px;
}
</style>
