// 开发环境使用 proxy，生产环境使用配置的地址
const isDev = import.meta.env.DEV

function getBaseUrl() {
  if (isDev) return '/api'
  // 优先使用用户配置的服务器地址
  const saved = window.API_BASE_URL || localStorage.getItem('server_url')
  if (saved) return saved + '/api'
  // 默认使用 localhost
  return 'http://localhost:8000/api'
}

const BASE = getBaseUrl()

async function request(method, path, body) {
  const opts = { method, headers: {} }
  if (body && body instanceof FormData) {
    opts.body = body
  } else if (body) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  }
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || '请求失败')
  }
  return res.json()
}

export const api = {
  listProjects: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.search) qs.set('search', params.search)
    if (params.sort_by) qs.set('sort_by', params.sort_by)
    if (params.order) qs.set('order', params.order)
    const q = qs.toString()
    return request('GET', `/projects${q ? '?' + q : ''}`)
  },
  createProject: (data) => request('POST', '/projects', data),
  getProject: (id) => request('GET', `/projects/${id}`),
  updateProject: (id, data) => request('PUT', `/projects/${id}`, data),
  deleteProject: (id) => request('DELETE', `/projects/${id}`),
  uploadDrawing: (projectId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return request('POST', `/projects/${projectId}/upload`, fd)
  },

  getSeries: (id) => request('GET', `/series/${id}`),
  deleteSeries: (id) => request('DELETE', `/series/${id}`),
  listVersions: (seriesId) => request('GET', `/series/${seriesId}/versions`),

  getVersion: (id) => request('GET', `/versions/${id}`),
  deleteVersion: (id) => request('DELETE', `/versions/${id}`),
  updateChangeNote: (seriesId, versionId, changeNote) =>
    request('POST', `/series/${seriesId}/versions/${versionId}/note`, { change_note: changeNote }),
  updateTags: (versionId, tags) =>
    request('PUT', `/versions/${versionId}/tags`, { tags }),
  compareVersions: (vid1, vid2) => request('GET', `/compare/${vid1}/${vid2}`),
  getThumbnailUrl: (versionId) => `${BASE}/versions/${versionId}/thumbnail`,
  getDownloadUrl: (versionId) => `${BASE}/versions/${versionId}/download`,

  getExportProjectUrl: (projectId, format = 'excel') => `${BASE}/export/project/${projectId}?format=${format}`,
  getExportSeriesUrl: (seriesId, format = 'excel') => `${BASE}/export/series/${seriesId}?format=${format}`,

  createBackup: () => request('POST', '/backup/create'),
  listBackups: () => request('GET', '/backup/list'),
  getBackupDownloadUrl: (backupId) => `${BASE}/backup/download/${backupId}`,
  restoreBackup: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return request('POST', '/backup/restore', fd)
  },
  deleteBackup: (backupId) => request('DELETE', `/backup/${backupId}`),

  listDeletions: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.entity_type) qs.set('entity_type', params.entity_type)
    if (params.limit) qs.set('limit', params.limit)
    if (params.offset) qs.set('offset', params.offset)
    const q = qs.toString()
    return request('GET', `/deletions${q ? '?' + q : ''}`)
  },
  restoreDeletion: (logId) => request('POST', `/deletions/${logId}/restore`),

  // 智能上传
  smartUpload: (file, projectId) => {
    const fd = new FormData()
    fd.append('file', file)
    if (projectId) fd.append('project_id', projectId)
    return request('POST', '/smart-upload', fd)
  },
  smartUploadBatch: (files, projectId) => {
    const fd = new FormData()
    files.forEach(f => fd.append('files', f))
    if (projectId) fd.append('project_id', projectId)
    return request('POST', '/smart-upload-batch', fd)
  },
}
