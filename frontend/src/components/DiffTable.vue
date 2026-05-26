<template>
  <div class="diff-table-wrapper">
    <h4>变更明细</h4>
    <table class="diff-table">
      <thead>
        <tr>
          <th>字段</th>
          <th>v{{ oldVersionNumber }}（旧）</th>
          <th class="arrow-col"></th>
          <th>v{{ newVersionNumber }}（新）</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in diffs" :key="d.field" :class="{ changed: d.changed, unchanged: !d.changed }">
          <td class="field-label">{{ d.label }}</td>
          <td class="old-val">{{ d.old_value || '-' }}</td>
          <td class="arrow-col">
            <span v-if="d.changed" class="arrow">──▶</span>
            <span v-else class="no-change">─</span>
          </td>
          <td class="new-val">{{ d.new_value || '-' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({ diffs: Array, oldVersionNumber: Number, newVersionNumber: Number })
</script>

<style scoped>
.diff-table-wrapper { margin-top: 24px; }
.diff-table-wrapper h4 { margin-bottom: 12px; font-size: 16px; }
.diff-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.diff-table th { background: #f8f8f8; padding: 10px 12px; text-align: left; font-weight: 600; }
.diff-table td { padding: 10px 12px; border-bottom: 1px solid #eee; }
tr.changed { background: #fff5f5; border-left: 4px solid #e74c3c; }
tr.unchanged { border-left: 4px solid #27ae60; }
.field-label { font-weight: 500; }
.arrow { color: #e67e22; font-weight: bold; }
.no-change { color: #ccc; }
.old-val { color: #888; }
.new-val { color: #333; font-weight: 500; }
</style>
