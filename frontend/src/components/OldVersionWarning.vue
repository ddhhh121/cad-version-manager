<template>
  <div v-if="visible" class="overlay" @click.self="$emit('dismiss')">
    <div class="warning-dialog">
      <h3>你正在查看旧版本</h3>
      <p>最新版本是 v{{ latestVersion }}</p>
      <router-link v-if="targetPath" :to="targetPath" class="btn-primary" @click="$emit('dismiss')">
        查看最新 v{{ latestVersion }}
      </router-link>
      <button class="btn-ghost" @click="$emit('dismiss')">继续看当前</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean, currentVersion: Number, latestVersion: Number,
  latestVersionId: Number, latestNote: String, latestDate: String, targetPath: String,
})
defineEmits(['dismiss'])
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.warning-dialog { background: #fff; border-radius: 12px; padding: 32px; max-width: 440px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,.2); }
.btn-primary { background: #1a1a2e; color: #fff; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; margin-right: 8px; }
.btn-ghost { background: none; border: 1px solid #ccc; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
</style>
