<template>
  <div id="app-container">
    <ServerConfig />
    <header class="app-header">
      <div class="header-content">
        <router-link to="/" class="logo">CAD 版本管理器</router-link>
        <button class="menu-toggle" @click="showMenu = !showMenu">☰</button>
        <nav class="header-nav" :class="{ show: showMenu }">
          <router-link to="/deletions" class="nav-link" @click="showMenu = false">删除历史</router-link>
          <router-link to="/backup" class="nav-link" @click="showMenu = false">备份管理</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ServerConfig from './components/ServerConfig.vue'
const showMenu = ref(false)
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #f5f5f5; color: #333; }
.app-header { background: #1a1a2e; padding: 12px 16px; }
.header-content { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; flex-wrap: wrap; }
.app-header .logo { color: #fff; font-size: 18px; font-weight: 700; text-decoration: none; }
.menu-toggle { display: none; background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; }
.header-nav { display: flex; gap: 20px; }
.nav-link { color: rgba(255,255,255,0.8); text-decoration: none; font-size: 14px; }
.nav-link:hover { color: #fff; }
.app-main { max-width: 1200px; margin: 16px auto; padding: 0 12px; }

/* 移动端适配 */
@media (max-width: 768px) {
  .menu-toggle { display: block; }
  .header-nav {
    display: none;
    width: 100%;
    flex-direction: column;
    padding: 12px 0;
    gap: 12px;
  }
  .header-nav.show { display: flex; }
  .app-main { padding: 0 8px; margin: 12px auto; }
}
</style>
