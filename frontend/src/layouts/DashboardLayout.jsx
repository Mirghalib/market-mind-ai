import { Outlet } from 'react-router-dom'
import Sidebar from '@/components/dashboard/Sidebar'

export default function DashboardLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 text-zinc-100 lg:flex-row">
      <Sidebar />
      <main className="min-w-0 flex-1">
        <Outlet />
      </main>
    </div>
  )
}
