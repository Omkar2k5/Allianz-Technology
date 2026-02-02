'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Eye,
  EyeOff,
  Plus,
  Trash2,
  Save,
  Moon,
  Sun,
  Shield,
  Zap,
} from 'lucide-react'

const integrations = [
  {
    name: 'OpenAI API Key',
    provider: 'OpenAI',
    status: 'Connected',
    key: 'sk-opn••••••••••••••••••••',
    connected: true,
  },
  {
    name: 'Google AI API Key',
    provider: 'Google',
    status: 'Connected',
    key: 'gk-goo••••••••••••••••••••',
    connected: true,
  },
  {
    name: 'Anthropic API Key',
    provider: 'Anthropic',
    status: 'Not Connected',
    key: '',
    connected: false,
  },
  {
    name: 'Azure AI Services Key',
    provider: 'Microsoft',
    status: 'Not Connected',
    key: '',
    connected: false,
  },
]

const teamMembers = [
  {
    name: 'Alice Smith',
    email: 'alice.smith@example.com',
    role: 'Admin',
    avatar: 'AS',
  },
  {
    name: 'Bob Johnson',
    email: 'bob.johnson@example.com',
    role: 'Analyst',
    avatar: 'BJ',
  },
  {
    name: 'Charlie Brown',
    email: 'charlie.brown@example.com',
    role: 'Developer',
    avatar: 'CB',
  },
]

export default function SettingsPage() {
  const [theme, setTheme] = useState('light')
  const [showKeys, setShowKeys] = useState<{ [key: string]: boolean }>({})
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)
  const [emailAlerts, setEmailAlerts] = useState(true)

  const toggleKeyVisibility = (key: string) => {
    setShowKeys((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  return (
    <div className="p-6 space-y-6 md:ml-64">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-foreground">Settings & Integrations</h2>
        <p className="text-muted-foreground">
          Manage your platform settings, integrations, team, and preferences
        </p>
      </div>

      {/* Preferences Section */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-6">Preferences</h3>
        <div className="space-y-6">
          {/* Theme Selection */}
          <div>
            <label className="text-sm font-medium text-foreground block mb-3">
              Application Theme
            </label>
            <div className="flex gap-3">
              <button
                onClick={() => setTheme('light')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-colors ${
                  theme === 'light'
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <Sun className="w-4 h-4" />
                <span className="text-sm font-medium">Light</span>
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-colors ${
                  theme === 'dark'
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <Moon className="w-4 h-4" />
                <span className="text-sm font-medium">Dark</span>
              </button>
            </div>
          </div>

          <Separator />

          {/* Default Cloud Region */}
          <div>
            <label className="text-sm font-medium text-foreground block mb-3">
              Default Cloud Region
            </label>
            <Select defaultValue="us-east">
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="us-east">US East (N. Virginia)</SelectItem>
                <SelectItem value="us-west">US West (Oregon)</SelectItem>
                <SelectItem value="eu-west">EU West (Ireland)</SelectItem>
                <SelectItem value="eu-central">EU Central (Frankfurt)</SelectItem>
                <SelectItem value="ap-southeast">Asia Pacific (Singapore)</SelectItem>
                <SelectItem value="ca-central">Canada (Central)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground mt-2">
              This region will be used as the default for new deployments
            </p>
          </div>

          <Separator />

          {/* Notifications */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground block">
                  Email Notifications
                </label>
                <p className="text-xs text-muted-foreground mt-1">
                  Receive alerts and updates via email
                </p>
              </div>
              <Switch checked={notificationsEnabled} onCheckedChange={setNotificationsEnabled} />
            </div>

            {notificationsEnabled && (
              <div className="flex items-center justify-between pl-0 py-3 border-t border-border/50">
                <div>
                  <label className="text-sm font-medium text-foreground block">
                    Carbon Emission Alerts
                  </label>
                  <p className="text-xs text-muted-foreground mt-1">
                    Get notified when emissions exceed thresholds
                  </p>
                </div>
                <Switch checked={emailAlerts} onCheckedChange={setEmailAlerts} />
              </div>
            )}
          </div>
        </div>

        <Button className="mt-6 bg-primary text-primary-foreground hover:bg-primary/90 gap-2">
          <Save className="w-4 h-4" />
          Save Settings
        </Button>
      </Card>

      {/* API Integrations */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-2 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          API Integrations
        </h3>
        <p className="text-sm text-muted-foreground mb-6">
          Configure API access to third-party generative AI services
        </p>

        <div className="space-y-4">
          {integrations.map((integration, idx) => (
            <div
              key={idx}
              className="p-4 border border-border/50 rounded-lg hover:border-primary/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-sm font-semibold text-foreground">{integration.name}</p>
                  <p className="text-xs text-muted-foreground">{integration.provider}</p>
                </div>
                <Badge
                  variant={integration.connected ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {integration.status}
                </Badge>
              </div>

              {integration.connected && (
                <div className="flex items-center gap-2 mb-4">
                  <input
                    type={showKeys[integration.name] ? 'text' : 'password'}
                    value={integration.key}
                    readOnly
                    className="flex-1 px-3 py-2 border border-border rounded-lg bg-muted text-muted-foreground text-sm font-mono"
                  />
                  <button
                    onClick={() => toggleKeyVisibility(integration.name)}
                    className="p-2 hover:bg-muted rounded-lg transition-colors"
                  >
                    {showKeys[integration.name] ? (
                      <EyeOff className="w-4 h-4 text-muted-foreground" />
                    ) : (
                      <Eye className="w-4 h-4 text-muted-foreground" />
                    )}
                  </button>
                </div>
              )}

              <div className="flex gap-2">
                {integration.connected ? (
                  <>
                    <Button variant="outline" size="sm" className="text-xs bg-transparent">
                      Regenerate Key
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive text-xs"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      Disconnect
                    </Button>
                  </>
                ) : (
                  <Button size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90 text-xs">
                    <Plus className="w-3 h-3 mr-1" />
                    Generate New Key
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Team Management */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-2 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Team Management
        </h3>
        <p className="text-sm text-muted-foreground mb-6">
          Assign roles to team members to manage access levels
        </p>

        <div className="space-y-3">
          {teamMembers.map((member, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-4 border border-border/50 rounded-lg hover:border-primary/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-semibold text-primary">
                  {member.avatar}
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{member.name}</p>
                  <p className="text-xs text-muted-foreground">{member.email}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Select defaultValue={member.role.toLowerCase()}>
                  <SelectTrigger className="w-32 text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="analyst">Analyst</SelectItem>
                    <SelectItem value="developer">Developer</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>

                <Button
                  variant="ghost"
                  size="sm"
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <Button className="mt-6 bg-primary text-primary-foreground hover:bg-primary/90 gap-2">
          <Plus className="w-4 h-4" />
          Add Team Member
        </Button>
      </Card>

      {/* Energy Threshold Alerts */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-6">Energy Threshold Alerts</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Receive alerts when models exceed specified energy consumption limits
        </p>

        <div className="space-y-4">
          {[
            { label: 'Global kWh Alert Threshold', value: 150, unit: 'kWh' },
            { label: 'GPT-4 Max kWh', value: 75, unit: 'kWh' },
            { label: 'Claude 3 Opus Max kWh', value: 60, unit: 'kWh' },
          ].map((threshold, idx) => (
            <div key={idx}>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-foreground">{threshold.label}</label>
                <span className="text-sm font-semibold text-foreground">
                  {threshold.value} {threshold.unit}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="200"
                value={threshold.value}
                className="w-full h-2 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>
          ))}
        </div>

        <Button className="mt-6 bg-primary text-primary-foreground hover:bg-primary/90">
          <Plus className="w-4 h-4 mr-2" />
          Add Model-Specific Threshold
        </Button>
      </Card>

      {/* Danger Zone */}
      <Card className="p-6 border-2 border-destructive/50 bg-destructive/5">
        <h3 className="text-lg font-semibold text-destructive mb-2">Danger Zone</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Irreversible and destructive actions
        </p>

        <div className="space-y-3">
          <div className="p-4 border border-destructive/30 rounded-lg">
            <p className="text-sm font-medium text-foreground mb-3">Delete All Historical Data</p>
            <p className="text-sm text-muted-foreground mb-4">
              This will permanently delete all your historical usage data, metrics, and reports. This action cannot be undone.
            </p>
            <Button
              variant="destructive"
              className="text-xs"
            >
              Delete Data
            </Button>
          </div>

          <div className="p-4 border border-destructive/30 rounded-lg">
            <p className="text-sm font-medium text-foreground mb-3">Deactivate Account</p>
            <p className="text-sm text-muted-foreground mb-4">
              Deactivate your Eco-Compute account and remove all associated data. This action is irreversible.
            </p>
            <Button
              variant="destructive"
              className="text-xs"
            >
              Deactivate Account
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
