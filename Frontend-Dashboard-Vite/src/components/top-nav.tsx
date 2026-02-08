import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { Menu, Bell, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { API_URL } from '@/config'

interface TopNavProps {
  onMenuClick: () => void
}

export function TopNav({ onMenuClick }: TopNavProps) {
  const navigate = useNavigate()
  const [user, setUser] = useState<any>(() => {
    // Try to load initial state from local storage to avoid flash of "User"
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        return JSON.parse(storedUser)
      } catch (e) {
        console.error("Failed to parse stored user", e)
      }
    }
    return null
  })

  useEffect(() => {
    // Load user from local storage or fetch profile
    const token = localStorage.getItem('token')
    if (!token) return

    // Simply decode token or use stored user info if available
    // For now, let's try to fetch user info
    fetch(`${API_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch user')
        return res.json()
      })
      .then(data => setUser(data))
      .catch(err => {
        // Silently fail if auth endpoint is unreachable or token invalid
        console.warn('Auth check failed:', err.message)
      })
  }, [])

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('token')
      const refreshToken = localStorage.getItem('refresh_token')

      if (token && refreshToken) {
        await fetch(`${API_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ refresh_token: refreshToken })
        })
      }
    } catch (error) {
      console.error("Logout failed", error)
    } finally {
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      toast.success('Logged out successfully')
      navigate('/login')
    }
  }

  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-6 gap-4">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="md:hidden"
        >
          <Menu className="w-5 h-5" />
        </Button>

        <div>
          <h1 className="text-lg font-semibold text-foreground">Dashboard</h1>
        </div>
      </div>

      <div className="flex items-center gap-4 ml-auto">
        {/* Notifications */}
        <Button variant="ghost" size="icon">
          <Bell className="w-5 h-5" />
        </Button>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="flex items-center gap-2">
              <Avatar className="w-8 h-8">
                <AvatarImage src="https://github.com/shadcn.png" />
                <AvatarFallback>
                  {user?.first_name?.[0]}{user?.last_name?.[0] || 'U'}
                </AvatarFallback>
              </Avatar>
              <span className="hidden sm:inline text-sm font-medium">
                {user ? `${user.first_name} ${user.last_name}` : 'Loading...'}
              </span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <div className="px-4 py-3 border-b border-border">
              <p className="text-sm font-medium text-foreground">
                {user ? `${user.first_name} ${user.last_name}` : '...'}
              </p>
              <p className="text-xs text-muted-foreground">
                {user?.email || ''}
              </p>
            </div>
            <DropdownMenuItem className="border-t border-border" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              <span>Sign out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
