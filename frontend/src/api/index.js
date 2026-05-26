const BASE = '/api'

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
  listProjects: () => request('GET', '/projects'),
  createProject: (data) => request('POST', '/projects', data),
  getProject: (id) => request('GET', `/projects/${id}`),
  uploadDrawing: (projectId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return request('POST', `/projects/${projectId}/upload`, fd)
  },

  getSeries: (id) => request('GET', `/series/${id}`),
  listVersions: (seriesId) => request('GET', `/series/${seriesId}/versions`),

  getVersion: (id) => request('GET', `/versions/${id}`),
  updateChangeNote: (seriesId, versionId, changeNote) =>
    request('POST', `/series/${seriesId}/versions/${versionId}/note`, { change_note: changeNote }),
  compareVersions: (vid1, vid2) => request('GET', `/compare/${vid1}/${vid2}`),
  getThumbnailUrl: (versionId) => `${BASE}/versions/${versionId}/thumbnail`,
  getDownloadUrl: (versionId) => `${BASE}/versions/${versionId}/download`,
}
