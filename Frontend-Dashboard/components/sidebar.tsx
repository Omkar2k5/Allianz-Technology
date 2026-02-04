'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  BarChart3,
  Zap,
  Wind,
  Cpu,
  Lightbulb,
  FileText,
  Settings,
  Leaf,
  ChevronLeft,
  BookOpen,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface SidebarProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/usage', label: 'Usage Tracking', icon: BarChart3 },
  { href: '/energy', label: 'Energy Consumption', icon: Zap },
  { href: '/emissions', label: 'Carbon Emissions', icon: Wind },
  { href: '/models', label: 'Model Efficiency', icon: Cpu },
  { href: '/recommendations', label: 'Recommendations', icon: Lightbulb },
  { href: '/rfe', label: 'Research for Estimation', icon: BookOpen },
  { href: '/reports', label: 'Reports & ESG', icon: FileText },
  { href: '/settings', label: 'Settings & Integrations', icon: Settings },
]

export function Sidebar({ open, onOpenChange }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 h-full w-64 bg-sidebar border-r border-sidebar-border transition-transform duration-300 z-40',
          open ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-6 border-b border-sidebar-border">
            <div className="w-8 h-8 bg-sidebar-primary rounded-lg flex items-center justify-center shrink-0">
              <Leaf className="w-5 h-5 text-sidebar-primary-foreground" />
            </div>
            <span className="text-lg font-bold text-sidebar-foreground hidden sm:inline">
              Eco-Compute
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-6 overflow-y-auto">
            <ul className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                          : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
                      )}
                    >
                      <Icon className="w-5 h-5 shrink-0" />
                      <span>{item.label}</span>
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          {/* Footer */}
          <div className="border-t border-sidebar-border p-6">
            <div className="text-xs text-sidebar-foreground/60 text-center">
              <p>© 2025 Eco-Compute</p>
              <p className="mt-2">Environmental AI Dashboard</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => onOpenChange(false)}
        />
      )}
    </>
  )
}
