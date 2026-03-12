import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'
import './styles/shared.css'
import { WorkspaceProvider } from './context/WorkspaceContext.tsx'

const originalFetch = window.fetch.bind(window)

window.fetch = ((input: RequestInfo | URL, init?: RequestInit) => {
  const requestUrl = typeof input === 'string'
    ? input
    : input instanceof URL
      ? input.toString()
      : input.url

  const isApiRequest = requestUrl.includes('/api/') || requestUrl.includes('/api/v1/')
  if (!isApiRequest) {
    return originalFetch(input, init)
  }

  const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || ''
  const orgId = localStorage.getItem('voxcore_org_id') || localStorage.getItem('voxcore_company_id') || '1'
  const workspaceId = localStorage.getItem('voxcore_workspace_id') || localStorage.getItem('vox_workspace') || '1'
  const datasourceId = localStorage.getItem('voxcore_datasource_id') || localStorage.getItem('vox_datasource') || ''

  const headers = new Headers(init?.headers || (typeof input !== 'string' && !(input instanceof URL) ? input.headers : undefined))
  if (token && !headers.has('Authorization')) headers.set('Authorization', `Bearer ${token}`)
  if (!headers.has('X-Org-ID')) headers.set('X-Org-ID', orgId)
  if (!headers.has('X-Workspace-ID')) headers.set('X-Workspace-ID', workspaceId)
  if (datasourceId && !headers.has('X-Datasource-ID')) headers.set('X-Datasource-ID', datasourceId)

  return originalFetch(input, { ...init, headers })
}) as typeof window.fetch

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <WorkspaceProvider>
        <App />
      </WorkspaceProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
