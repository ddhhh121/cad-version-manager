<template>
  <div v-if="visible" class="overlay" @click.self="dismiss">
    <div class="warning-dialog">
      <div class="warn-icon">⚠️</div>
      <h3>你正在查看 v{{ currentVersion }}（旧版本）</h3>
      <p>最新版本是 <strong>v{{ latestVersion }}</strong> · {{ latestDate }}</p>
      <p v-if="latestNote" class="latest-note">变更说明: "{{ latestNote }}"</p>
      <div class="warn-actions">
        <router-link v-if="targetPath" :to="targetPath" class="btn-primary" @click="dismiss">
          查看最新 v{{ latestVersion }}
        </router-link>
        <button class="btn-ghost" @click="dismiss">继续看当前 v{{ currentVersion }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  currentVersion: Number,
  latestVersion: Number,
  latestVersionId: Number,
  latestNote: String,
  latestDate: String,
  targetPath: String,
})
const emit = defineEmits(['dismiss'])
function dismiss() { emit('dismiss') }
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.warning-dialog { background: #fff; border-radius: 12px; padding: 32px; max-width: 440px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,.2); }
.warn-icon { font-size: 40px; margin-bottom: 12px; }
.warning-dialog h3 { font-size: 18px; margin-bottom: 8px; }
.warning-dialog p { color: #666; margin-bottom: 6px; font-size: 14px; }
.latest-note { font-style: italic; color: #555; }
.warn-actions { display: flex; gap: 12px; justify-content: center; margin-top: 20px; }
.btn-primary { background: #1a1a2e; color: #fff; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; }
.btn-ghost { background: none; border: 1px solid #ccc; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
</style>
