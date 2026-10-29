const { app, BrowserWindow, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const http = require('http')

let mainWindow = null
let backendProcess = null
const BACKEND_PORT = 8000

// 检查后端是否已启动
function checkBackend() {
  return new Promise((resolve) => {
    http.get(`http://localhost:${BACKEND_PORT}/api/health`, (res) => {
      if (res.statusCode === 200) {
        resolve(true)
      } else {
        resolve(false)
      }
    }).on('error', () => {
      resolve(false)
    })
  })
}

// 启动后端
async function startBackend() {
  // 先检查后端是否已经在运行
  const isRunning = await checkBackend()
  if (isRunning) {
    console.log('Backend already running')
    return
  }

  // 确定后端可执行文件路径
  let backendPath
  if (app.isPackaged) {
    // 打包后的路径
    backendPath = path.join(process.resourcesPath, 'backend', 'cad-backend.exe')
  } else {
    // 开发环境路径
    backendPath = path.join(__dirname, '..', 'backend', 'dist', 'cad-backend.exe')
  }

  console.log('Starting backend from:', backendPath)

  backendProcess = spawn(backendPath, [], {
    env: {
      ...process.env,
      PORT: String(BACKEND_PORT),
    },
    windowsHide: true,
  })

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`)
  })

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`)
  })

  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err)
  })

  backendProcess.on('exit', (code) => {
    console.log(`Backend exited with code ${code}`)
    backendProcess = null
  })

  // 等待后端启动
  let retries = 30
  while (retries > 0) {
    const isReady = await checkBackend()
    if (isReady) {
      console.log('Backend is ready')
      return
    }
    await new Promise(resolve => setTimeout(resolve, 500))
    retries--
  }

  throw new Error('Backend failed to start')
}

// 停止后端
function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend...')
    backendProcess.kill()
    backendProcess = null
  }
}

// 创建窗口
async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 600,
    title: 'CAD 版本管理器',
    icon: getIconPath(),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  // 加载前端
  const frontendPath = getFrontendPath()
  console.log('Loading frontend from:', frontendPath)
  mainWindow.loadFile(frontendPath)

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 获取图标路径
function getIconPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'build', 'icon.ico')
  }
  return path.join(__dirname, '..', 'build', 'icon.ico')
}

// 获取前端路径
function getFrontendPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'frontend', 'dist', 'index.html')
  }
  return path.join(__dirname, '..', 'frontend', 'dist', 'index.html')
}

// 应用启动
app.whenReady().then(async () => {
  try {
    await startBackend()
    await createWindow()
  } catch (err) {
    console.error('Startup error:', err)
    dialog.showErrorBox('启动失败', `无法启动应用：${err.message}`)
    app.quit()
  }
})

// 所有窗口关闭
app.on('window-all-closed', () => {
  stopBackend()
  app.quit()
})

// 应用退出前
app.on('before-quit', () => {
  stopBackend()
})

// macOS 激活
app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    await createWindow()
  }
})
