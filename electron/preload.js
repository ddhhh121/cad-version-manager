const { contextBridge } = require('electron')

// 暴露一些 API 给渲染进程（如果需要的话）
contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron,
  },
})
