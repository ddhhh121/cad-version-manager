import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'ProjectList', component: () => import('../views/ProjectList.vue') },
  { path: '/project/:id', name: 'ProjectDetail', component: () => import('../views/ProjectDetail.vue') },
  { path: '/project/:projectId/series/:seriesId', name: 'SeriesDetail', component: () => import('../views/SeriesDetail.vue') },
  { path: '/compare/:vid1/:vid2', name: 'VersionCompare', component: () => import('../views/VersionCompare.vue') },
  { path: '/deletions', name: 'DeletionHistory', component: () => import('../views/DeletionHistory.vue') },
  { path: '/backup', name: 'Backup', component: () => import('../views/BackupPage.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
