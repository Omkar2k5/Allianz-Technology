'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  AreaChart,
  Area,
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
import { Download, Zap, TrendingDown } from 'lucide-react'

const energyData = [
  { month: 'Feb', inference: 150, training: 450 },
  { month: 'Mar', inference: 165, training: 420 },
  { month: 'Apr', inference: 180, training: 400 },
  { month: 'May', inference: 200, training: 380 },
  { month: 'Jun', inference: 190, training: 350 },
  { month: 'Jul', inference: 210, training: 320 },
  { month: 'Aug', inference: 230, training: 280 },
]

const gpuData = [
  { timestamp: '2024-03-10', time: '14:30:00', device: 'GPU', type: 'NVIDIA-V100-1', usage: 92, temp: 78, power: 280 },
  { timestamp: '2024-03-10', time: '14:31:15', device: 'CPU', type: 'Intel-Xeon-E5-2', usage: 65, temp: 55, power: 110 },
  { timestamp: '2024-03-10', time: '14:32:30', device: 'GPU', type: 'NVIDIA-A100-3', usage: 88, temp: 75, power: 250 },
  { timestamp: '2024-03-10', time: '14:33:45', device: 'GPU', type: 'NVIDIA-V100-1', usage: 95, temp: 80, power: 290 },
  { timestamp: '2024-03-10', time: '14:35:00', device: 'CPU', type: 'AMD-EPYC-7272-4', usage: 70, temp: 60, power: 120 },
]

export default function EnergyPage() {
  return (
    <div className="p-6 space-y-6 md:ml-64">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-foreground">Energy Consumption Overview</h2>
        <p className="text-muted-foreground">
          Monitor and analyze the energy consumption of your AI model deployments
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Total kWh Consumed</p>
          <p className="text-3xl font-bold text-foreground">1.2 MWh</p>
          <p className="text-xs text-muted-foreground mt-2">↑ 5.2% vs last month</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Avg. kWh/Request</p>
          <p className="text-3xl font-bold text-foreground">0.003</p>
          <p className="text-xs text-muted-foreground mt-2">↓ 1.8% vs last month</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Avg. kWh/Model</p>
          <p className="text-3xl font-bold text-foreground">54.8</p>
          <p className="text-xs text-muted-foreground mt-2">↑ 2.1% vs last month</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">PUE Factor</p>
          <p className="text-3xl font-bold text-foreground">1.25</p>
          <p className="text-xs text-muted-foreground mt-2">↑ 2% overall</p>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PUE-Adjusted Energy */}
        <Card className="p-6 border border-border/50">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground">PUE-Adjusted Energy Consumption</h3>
              <p className="text-sm text-muted-foreground">Last 7 months</p>
            </div>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={energyData}>
              <defs>
                <linearGradient id="colorEnergy" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0} />
                </linearGradient>
              </defs>
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
              <Area
                type="monotone"
                dataKey="inference"
                stackId="1"
                stroke="var(--color-primary)"
                fill="url(#colorEnergy)"
                name="Inference (kWh)"
              />
              <Area
                type="monotone"
                dataKey="training"
                stackId="1"
                stroke="var(--color-accent)"
                fill="var(--color-accent)"
                fillOpacity={0.3}
                name="Training (kWh)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Energy by Model */}
        <Card className="p-6 border border-border/50">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground">Energy Consumption by Model (kWh)</h3>
              <p className="text-sm text-muted-foreground">Current period</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { name: 'GPT-4', inference: 75, training: 0 },
              { name: 'Llama-2', inference: 60, training: 30 },
              { name: 'Mistral', inference: 50, training: 20 },
              { name: 'Claude 3', inference: 68, training: 0 },
              { name: 'Codeara', inference: 35, training: 15 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="name" stroke="var(--color-muted-foreground)" />
              <YAxis stroke="var(--color-muted-foreground)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Bar dataKey="inference" fill="var(--color-primary)" name="Inference (kWh)" />
              <Bar dataKey="training" fill="var(--color-accent)" name="Training (kWh)" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Breakdown Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 border border-border/50">
          <h3 className="text-lg font-semibold text-foreground mb-4">Inference Energy Breakdown</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Inference energy typically refers to the energy consumed when an AI model processes predictions for generate outputs.
          </p>
          <ul className="space-y-2 text-sm">
            <li className="text-foreground">• <span className="font-medium">Total Inference kWh:</span> 750 kWh</li>
            <li className="text-foreground">• <span className="font-medium">Avg. Latency/ms:</span> 150 ms</li>
            <li className="text-foreground">• <span className="font-medium">Avg. Power:</span> 320 W</li>
          </ul>
          <Button className="w-full mt-4 bg-primary text-primary-foreground hover:bg-primary/90">
            View detailed logs
          </Button>
        </Card>

        <Card className="p-6 border border-border/50">
          <h3 className="text-lg font-semibold text-foreground mb-4">Training Energy Breakdown</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Training energy is the energy required to teach an AI model using large datasets. This phase is often resource-intensive and accounts for a significant portion of a model's lifecycle energy footprint.
          </p>
          <ul className="space-y-2 text-sm">
            <li className="text-foreground">• <span className="font-medium">Total Training kWh:</span> 450 kWh</li>
            <li className="text-foreground">• <span className="font-medium">Training Duration:</span> 120 hours</li>
            <li className="text-foreground">• <span className="font-medium">Avg. GPU Utilization:</span> 98%</li>
          </ul>
          <Button className="w-full mt-4 bg-primary text-primary-foreground hover:bg-primary/90">
            View training jobs
          </Button>
        </Card>
      </div>

      {/* GPU/CPU Activity */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-6">GPU/CPU Activity Logs</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Timestamp</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Device Type</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Device ID</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Usage (%)</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Temp (°C)</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Power (W)</th>
              </tr>
            </thead>
            <tbody>
              {gpuData.map((row, idx) => (
                <tr key={idx} className="border-b border-border/50 hover:bg-muted/50">
                  <td className="py-4 px-4 text-foreground">{row.time}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      row.device === 'GPU' 
                        ? 'bg-primary/10 text-primary' 
                        : 'bg-accent/10 text-accent'
                    }`}>
                      {row.device}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-foreground text-xs font-mono">{row.type}</td>
                  <td className="py-4 px-4 text-foreground">{row.usage}%</td>
                  <td className="py-4 px-4 text-foreground">{row.temp}°C</td>
                  <td className="py-4 px-4 text-foreground font-medium">{row.power}W</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Energy Calculation Formula */}
      <Card className="p-6 border border-border/50">
        <details>
          <summary className="cursor-pointer flex items-center gap-2 text-lg font-semibold text-foreground hover:text-primary">
            Understanding Energy Calculation Formulas
            <span>+</span>
          </summary>
          <div className="mt-4 space-y-4 text-sm text-muted-foreground">
            <div>
              <p className="font-medium text-foreground mb-2">Basic Energy Formula:</p>
              <p className="font-mono bg-muted/50 p-3 rounded">Energy (kWh) = Power (W) × Time (hours) / 1000</p>
            </div>
            <div>
              <p className="font-medium text-foreground mb-2">PUE (Power Usage Effectiveness):</p>
              <p className="font-mono bg-muted/50 p-3 rounded">PUE = Total Facility Power / IT Equipment Power</p>
              <p className="mt-2">A PUE of 1.0 means all energy is used by IT equipment. Higher values indicate overhead.</p>
            </div>
          </div>
        </details>
      </Card>
    </div>
  )
}
