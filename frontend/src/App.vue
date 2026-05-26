<template>
  <div id="app-container">
    <header class="app-header">
      <router-link to="/" class="logo">CAD 版本管理器</router-link>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #f5f5f5; color: #333; }
.app-header { background: #1a1a2e; padding: 16px 32px; }
.app-header .logo { color: #fff; font-size: 18px; font-weight: 700; text-decoration: none; }
.app-main { max-width: 1200px; margin: 24px auto; padding: 0 16px; }
</style>
