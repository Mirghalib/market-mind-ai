import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '@/components/dashboard/Sidebar'
import TopBar from '@/components/dashboard/TopBar'

export default function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleSearch = (query) => {
    // Local UI search — results are filtered client-side where relevant.
    if (query) return
  }

  return (
    <div className="flex min-h-screen flex-col bg-muted text-foreground transition-colors lg:flex-row dark:bg-zinc-950 dark:text-zinc-100">
      <Sidebar mobileOpen={mobileOpen} onOpenChange={setMobileOpen} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar onMenuClick={() => setMobileOpen(true)} onSearch={handleSearch} />
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
