<template>
  <div v-if="visible" class="confirm-overlay" @click.self="$emit('cancel')">
    <div class="confirm-dialog">
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
      <div class="confirm-actions">
        <button class="btn-ghost" @click="$emit('cancel')">取消</button>
        <button class="btn-danger" @click="$emit('confirm')">确认删除</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '确定要执行此操作吗？此操作不可撤销。' },
})
defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.confirm-dialog {
  background: #fff; border-radius: 12px; padding: 32px;
  max-width: 400px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,.2);
}
.confirm-dialog h3 { font-size: 18px; margin-bottom: 8px; }
.confirm-dialog p { color: #666; font-size: 14px; }
.confirm-actions { display: flex; gap: 12px; justify-content: center; margin-top: 20px; }
.btn-ghost { background: none; border: 1px solid #ccc; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-danger { background: #e74c3c; color: #fff; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-danger:hover { background: #c0392b; }
</style>
