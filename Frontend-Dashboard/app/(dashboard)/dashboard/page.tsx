'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { TrendingUp, AlertCircle, Zap, Wind, Activity, ArrowUpRight } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

const tokenUsageData = [
  { date: 'Jul 20', tokens: 4200 },
  { date: 'Jul 21', tokens: 3800 },
  { date: 'Jul 22', tokens: 5100 },
  { date: 'Jul 23', tokens: 7200 },
  { date: 'Jul 24', tokens: 6900 },
  { date: 'Jul 25', tokens: 8300 },
  { date: 'Jul 26', tokens: 7800 },
]

const recentCalls = [
  {
    id: 1,
    timestamp: '2024-07-26 10:00:00',
    model: 'GPT-4',
    tokensIn: 1500,
    tokensOut: 500,
    latency: 350,
    region: 'US East (N. Virginia)',
    team: 'Data Science',
  },
  {
    id: 2,
    timestamp: '2024-07-26 10:01:30',
    model: 'Claude 3 Opus',
    tokensIn: 2000,
    tokensOut: 700,
    latency: 420,
    region: 'Europe (Frankfurt)',
    team: 'Product Dev',
  },
  {
    id: 3,
    timestamp: '2024-07-26 10:03:00',
    model: 'Llama 3',
    tokensIn: 800,
    tokensOut: 300,
    latency: 280,
    region: 'US East (N. Virginia)',
    team: 'Marketing',
  },
  {
    id: 4,
    timestamp: '2024-07-26 10:05:15',
    model: 'Mistral 8x7B',
    tokensIn: 1200,
    tokensOut: 400,
    latency: 310,
    region: 'Asia Pacific (Singapore)',
    team: 'Research',
  },
]

export default function DashboardPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('7days')

  return (
    <div className="p-6 space-y-6 md:ml-64">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-foreground">Dashboard Overview</h2>
        <p className="text-muted-foreground">
          Monitor your AI model usage and environmental impact
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6 border border-border/50">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Total AI Calls</p>
              <p className="text-3xl font-bold text-foreground">2.5M</p>
              <p className="text-xs text-muted-foreground mt-2">↑ 23% last week</p>
            </div>
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-primary" />
            </div>
          </div>
        </Card>

        <Card className="p-6 border border-border/50">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Total Energy</p>
              <p className="text-3xl font-bold text-foreground">15,300</p>
              <p className="text-xs text-muted-foreground mt-2">↓ 2% last month</p>
            </div>
            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-accent" />
            </div>
          </div>
        </Card>

        <Card className="p-6 border border-border/50">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">CO₂ Emissions</p>
              <p className="text-3xl font-bold text-foreground">7.8</p>
              <p className="text-xs text-muted-foreground mt-2">tons (↑ 2.3% last quarter)</p>
            </div>
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <Wind className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </Card>

        <Card className="p-6 border border-border/50">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Avg. Model Efficiency</p>
              <p className="text-3xl font-bold text-foreground">88%</p>
              <p className="text-xs text-muted-foreground mt-2">↑ 1.3% overall</p>
            </div>
            <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </Card>
      </div>

      {/* Critical Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Card className="p-6 border border-border/50">
            <h3 className="text-lg font-semibold text-foreground mb-4">Critical Alerts</h3>
            <div className="space-y-3">
              <Alert className="border-l-4 border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20">
                <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-500" />
                <AlertTitle className="text-yellow-900 dark:text-yellow-400">
                  Inefficient prompt detected
                </AlertTitle>
                <AlertDescription className="text-yellow-800 dark:text-yellow-500 text-sm mt-1">
                  Prompt for "generate creative copy" used 2x more tokens than average. Consider refining.
                </AlertDescription>
              </Alert>

              <Alert className="border-l-4 border-orange-500 bg-orange-50 dark:bg-orange-950/20">
                <AlertCircle className="h-4 w-4 text-orange-600 dark:text-orange-500" />
                <AlertTitle className="text-orange-900 dark:text-orange-400">
                  High carbon region in use
                </AlertTitle>
                <AlertDescription className="text-orange-800 dark:text-orange-500 text-sm mt-1">
                  Model "GPT-4" deployed in US-East-1 with high carbon intensity. Migrate to US-West-2?
                </AlertDescription>
              </Alert>

              <Alert className="border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/20">
                <AlertCircle className="h-4 w-4 text-blue-600 dark:text-blue-500" />
                <AlertTitle className="text-blue-900 dark:text-blue-400">
                  Outdated model version
                </AlertTitle>
                <AlertDescription className="text-blue-800 dark:text-blue-500 text-sm mt-1">
                  Model "Llama-2-7B" is an older version. Upgrade to Llama-3 for better efficiency.
                </AlertDescription>
              </Alert>
            </div>
          </Card>

          {/* Token Usage Chart */}
          <Card className="p-6 border border-border/50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground">Token Usage Over Time</h3>
              <div className="text-sm text-muted-foreground">Last 7 days</div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={tokenUsageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="date" stroke="var(--color-muted-foreground)" />
                <YAxis stroke="var(--color-muted-foreground)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="tokens"
                  stroke="var(--color-primary)"
                  strokeWidth={2}
                  dot={{ fill: 'var(--color-primary)', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Recommendations */}
        <Card className="p-6 border border-border/50">
          <h3 className="text-lg font-semibold text-foreground mb-4">Recommendations</h3>
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-sm font-medium text-foreground">Optimize Prompt Engineering</p>
              <p className="text-xs text-muted-foreground mt-1">
                Refine prompts to reduce token usage by an estimated 15%
              </p>
            </div>

            <div className="p-3 rounded-lg bg-accent/5 border border-accent/10">
              <p className="text-sm font-medium text-foreground">Utilize Green-mode Routing</p>
              <p className="text-xs text-muted-foreground mt-1">
                Enable automated routing to low-carbon cloud regions
              </p>
            </div>

            <div className="p-3 rounded-lg bg-green-100/10 dark:bg-green-900/10 border border-green-500/20">
              <p className="text-sm font-medium text-foreground">Update Model Versions</p>
              <p className="text-xs text-muted-foreground mt-1">
                Switch to newer model versions for better efficiency
              </p>
            </div>

            <Button className="w-full mt-4 bg-primary text-primary-foreground hover:bg-primary/90">
              View All Recommendations
            </Button>
          </div>
        </Card>
      </div>

      {/* Recent API Calls */}
      <Card className="p-6 border border-border/50">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-foreground">Recent AI Calls</h3>
          <Button variant="outline" className="text-sm bg-transparent">
            Export to CSV
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Timestamp</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Model</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tokens In</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tokens Out</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Latency</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Region</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Team</th>
              </tr>
            </thead>
            <tbody>
              {recentCalls.map((call) => (
                <tr key={call.id} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                  <td className="py-4 px-4 text-foreground">{call.timestamp}</td>
                  <td className="py-4 px-4 text-foreground font-medium">{call.model}</td>
                  <td className="py-4 px-4 text-foreground">{call.tokensIn.toLocaleString()}</td>
                  <td className="py-4 px-4 text-foreground">{call.tokensOut.toLocaleString()}</td>
                  <td className="py-4 px-4 text-foreground">{call.latency}ms</td>
                  <td className="py-4 px-4 text-muted-foreground text-xs">{call.region}</td>
                  <td className="py-4 px-4 text-muted-foreground text-xs">{call.team}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
          <p className="text-sm text-muted-foreground">Page 1 of 2</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              Previous
            </Button>
            <Button variant="outline" size="sm">
              Next
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
