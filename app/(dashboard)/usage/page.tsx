'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Download } from 'lucide-react'

const usageData = [
  { date: 'Jul 20', calls: 2400, tokens: 4200 },
  { date: 'Jul 21', calls: 2210, tokens: 3800 },
  { date: 'Jul 22', calls: 2290, tokens: 5100 },
  { date: 'Jul 23', calls: 2000, tokens: 7200 },
  { date: 'Jul 24', calls: 2181, tokens: 6900 },
  { date: 'Jul 25', calls: 2500, tokens: 8300 },
  { date: 'Jul 26', calls: 2100, tokens: 7800 },
]

const modelUsage = [
  { name: 'GPT-4', calls: 1500, percentage: 35 },
  { name: 'Claude 3 Opus', calls: 1200, percentage: 28 },
  { name: 'Llama 3', calls: 800, percentage: 19 },
  { name: 'Mistral 8x7B', calls: 600, percentage: 14 },
  { name: 'Others', calls: 200, percentage: 4 },
]

export default function UsagePage() {
  return (
    <div className="p-6 space-y-6 md:ml-64">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-foreground">Usage Tracking</h2>
        <p className="text-muted-foreground">
          Monitor API calls, token usage, and model distribution across your team
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Total API Calls</p>
          <p className="text-3xl font-bold text-foreground">16,081</p>
          <p className="text-xs text-muted-foreground mt-2">↑ 12% from last period</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Total Tokens Used</p>
          <p className="text-3xl font-bold text-foreground">43.3M</p>
          <p className="text-xs text-muted-foreground mt-2">↑ 8% from last period</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Avg. Response Time</p>
          <p className="text-3xl font-bold text-foreground">347ms</p>
          <p className="text-xs text-muted-foreground mt-2">↓ 5% improvement</p>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="p-6 border border-border/50">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-foreground">Usage Trend</h3>
                <p className="text-sm text-muted-foreground">API calls and tokens over time</p>
              </div>
              <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                <Download className="w-4 h-4" />
                Export
              </Button>
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="date" stroke="var(--color-muted-foreground)" />
                <YAxis yAxisId="left" stroke="var(--color-muted-foreground)" />
                <YAxis yAxisId="right" orientation="right" stroke="var(--color-muted-foreground)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                  }}
                />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="calls"
                  stroke="var(--color-primary)"
                  strokeWidth={2}
                  dot={{ fill: 'var(--color-primary)', r: 4 }}
                  name="API Calls"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="tokens"
                  stroke="var(--color-accent)"
                  strokeWidth={2}
                  dot={{ fill: 'var(--color-accent)', r: 4 }}
                  name="Tokens"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <Card className="p-6 border border-border/50">
          <h3 className="text-lg font-semibold text-foreground mb-6">Model Distribution</h3>
          <div className="space-y-4">
            {modelUsage.map((model) => (
              <div key={model.name}>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-foreground">{model.name}</p>
                  <p className="text-sm text-muted-foreground">{model.percentage}%</p>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${model.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Detailed Table */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-6">Model Usage Breakdown</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Model Name</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">API Calls</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tokens In</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tokens Out</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Avg. Latency</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Cost</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50 hover:bg-muted/50">
                <td className="py-4 px-4 text-foreground font-medium">GPT-4</td>
                <td className="py-4 px-4 text-foreground">1,500</td>
                <td className="py-4 px-4 text-foreground">15.2M</td>
                <td className="py-4 px-4 text-foreground">3.8M</td>
                <td className="py-4 px-4 text-foreground">385ms</td>
                <td className="py-4 px-4 text-foreground">$234.50</td>
              </tr>
              <tr className="border-b border-border/50 hover:bg-muted/50">
                <td className="py-4 px-4 text-foreground font-medium">Claude 3 Opus</td>
                <td className="py-4 px-4 text-foreground">1,200</td>
                <td className="py-4 px-4 text-foreground">12.5M</td>
                <td className="py-4 px-4 text-foreground">2.9M</td>
                <td className="py-4 px-4 text-foreground">412ms</td>
                <td className="py-4 px-4 text-foreground">$189.75</td>
              </tr>
              <tr className="border-b border-border/50 hover:bg-muted/50">
                <td className="py-4 px-4 text-foreground font-medium">Llama 3</td>
                <td className="py-4 px-4 text-foreground">800</td>
                <td className="py-4 px-4 text-foreground">8.2M</td>
                <td className="py-4 px-4 text-foreground">1.8M</td>
                <td className="py-4 px-4 text-foreground">298ms</td>
                <td className="py-4 px-4 text-foreground">$45.20</td>
              </tr>
              <tr className="border-b border-border/50 hover:bg-muted/50">
                <td className="py-4 px-4 text-foreground font-medium">Mistral 8x7B</td>
                <td className="py-4 px-4 text-foreground">600</td>
                <td className="py-4 px-4 text-foreground">6.1M</td>
                <td className="py-4 px-4 text-foreground">1.4M</td>
                <td className="py-4 px-4 text-foreground">325ms</td>
                <td className="py-4 px-4 text-foreground">$32.15</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
