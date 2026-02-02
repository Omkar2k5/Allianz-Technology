'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
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
import { Download, Leaf } from 'lucide-react'

const emissionsTrend = [
  { month: 'Jan', emissions: 1200 },
  { month: 'Feb', emissions: 1150 },
  { month: 'Mar', emissions: 1300 },
  { month: 'Apr', emissions: 1100 },
  { month: 'May', emissions: 1050 },
  { month: 'Jun', emissions: 1200 },
  { month: 'Dec', emissions: 950 },
]

const emissionsByRegion = [
  { region: 'US East (N. Virginia)', emissions: 2500, percentage: 35 },
  { region: 'Europe (Frankfurt)', emissions: 1800, percentage: 25 },
  { region: 'Asia Pacific (Singapore)', emissions: 1400, percentage: 20 },
  { region: 'US West (Oregon)', emissions: 1200, percentage: 17 },
  { region: 'Canada (Central)', emissions: 300, percentage: 3 },
]

const modelFamily = [
  { name: 'GPT-4 Series', value: 3000, color: 'var(--color-primary)' },
  { name: 'Llama-2 Variants', value: 1800, color: 'var(--color-accent)' },
  { name: 'Custom Fine-tuned', value: 1200, color: 'var(--color-chart-3)' },
  { name: 'Claude Opus', value: 900, color: 'var(--color-chart-4)' },
]

export default function EmissionsPage() {
  const [timeline, setTimeline] = useState(70)

  return (
    <div className="p-6 space-y-6 md:ml-64">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-foreground">Carbon Emissions Overview</h2>
        <p className="text-muted-foreground">
          Monitor and analyze the CO₂ emissions of your AI models across different regions and teams
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Avg. CO₂ per Model</p>
          <p className="text-3xl font-bold text-foreground">1.8</p>
          <p className="text-xs text-muted-foreground mt-2">tons/model - Average carbon footprint</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Avg. CO₂ per Request</p>
          <p className="text-3xl font-bold text-foreground">0.04</p>
          <p className="text-xs text-muted-foreground mt-2">g/request - Carbon per AI call</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Total CO₂ per Team</p>
          <p className="text-3xl font-bold text-foreground">2.5</p>
          <p className="text-xs text-muted-foreground mt-2">tons/team - Cumulative emissions</p>
        </Card>
      </div>

      {/* Global AI Carbon Intensity Map */}
      <Card className="p-6 border border-border/50">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-foreground">Global AI Carbon Intensity Map</h3>
            <p className="text-sm text-muted-foreground">
              Visualize real-time carbon intensity and emissions hotspots for your AI deployments worldwide.
            </p>
          </div>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>

        {/* Region Selection */}
        <div className="mb-6">
          <label className="text-sm font-medium text-foreground block mb-3">Region: Global</label>
          <div className="flex gap-2">
            <select className="px-3 py-2 border border-border rounded-lg text-sm bg-card text-foreground">
              <option>Global</option>
              <option>North America</option>
              <option>Europe</option>
              <option>Asia Pacific</option>
            </select>
          </div>
        </div>

        {/* Timeline Slider */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-foreground">Timeline: {timeline}%</label>
            <Button variant="outline" size="sm">
              Apply Filters
            </Button>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={timeline}
            onChange={(e) => setTimeline(Number(e.target.value))}
            className="w-full h-2 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        {/* Placeholder for Map */}
        <div className="w-full h-72 bg-muted rounded-lg flex items-center justify-center border border-border">
          <div className="text-center">
            <Leaf className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
            <p className="text-muted-foreground">Data visualization placeholder</p>
          </div>
        </div>
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CO₂ Reduction Trends */}
        <Card className="p-6 border border-border/50">
          <h3 className="text-lg font-semibold text-foreground mb-6">CO₂ Reduction Trends Post-Optimization</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Tracking the effectiveness of optimization strategies over the last year.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={emissionsTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="month" stroke="var(--color-muted-foreground)" />
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
                dataKey="emissions"
                stroke="var(--color-accent)"
                strokeWidth={2}
                dot={{ fill: 'var(--color-accent)', r: 4 }}
                name="CO₂ Emissions (tons)"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Emissions by Model Family */}
        <Card className="p-6 border border-border/50">
          <h3 className="text-lg font-semibold text-foreground mb-6">Emissions by Model Family</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Breakdown of total CO₂ emissions across different model families.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={modelFamily}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {modelFamily.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '0.5rem',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Regional Breakdown */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-6">Regional Carbon Intensity Analysis</h3>
        <div className="space-y-4">
          {emissionsByRegion.map((region) => (
            <div key={region.region}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="text-sm font-medium text-foreground">{region.region}</p>
                  <p className="text-xs text-muted-foreground">{region.emissions} tons CO₂</p>
                </div>
                <p className="text-sm font-semibold text-foreground">{region.percentage}%</p>
              </div>
              <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all"
                  style={{ width: `${region.percentage * 3.33}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Energy Calculation Breakdown */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-4">Emissions Calculation Formula</h3>
        <div className="space-y-4 text-sm text-muted-foreground">
          <div className="p-4 bg-muted/50 rounded-lg border border-border">
            <p className="font-mono font-medium text-foreground mb-2">CO₂ Emissions (tons) = Energy (kWh) × Carbon Intensity (kg CO₂/kWh) / 1000</p>
            <ul className="space-y-1 text-xs mt-3">
              <li><span className="font-medium">Energy:</span> kWh consumed by AI models</li>
              <li><span className="font-medium">Carbon Intensity:</span> Regional grid's CO₂ per kWh</li>
              <li><span className="font-medium">Region varies:</span> US-East: 0.4 kg/kWh, Germany: 0.1 kg/kWh</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  )
}
