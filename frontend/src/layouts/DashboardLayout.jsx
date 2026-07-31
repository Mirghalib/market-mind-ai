import { Outlet } from 'react-router-dom'
import Sidebar from '@/components/dashboard/Sidebar'

export default function DashboardLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 text-zinc-900 transition-colors lg:flex-row dark:bg-zinc-950 dark:text-zinc-100">
      <Sidebar />
      <main className="min-w-0 flex-1">
        <Outlet />
      </main>
    </div>
  )
}
