import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from '@/components/sidebar'
import { TopNav } from '@/components/top-nav'

export default function DashboardLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(true)

    return (
        <div className="flex h-screen bg-background text-foreground font-sans antialiased">
            <Sidebar open={sidebarOpen} onOpenChange={setSidebarOpen} />
            <div className="flex-1 flex flex-col overflow-hidden">
                <TopNav onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
                <main className="flex-1 overflow-y-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}
