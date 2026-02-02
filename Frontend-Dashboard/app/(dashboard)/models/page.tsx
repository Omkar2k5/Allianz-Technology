'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { ArrowUpRight, Info } from 'lucide-react'

const modelEfficiencyData = [
  {
    id: 1,
    name: 'EcoGenius-7B',
    provider: 'GreenAI Labs',
    parameters: '7 Billion',
    tokensPerSec: 120,
    kwh1k: 0.0003,
    co2per: 0.05,
    score: 'A+',
    color: '#22c55e',
  },
  {
    id: 2,
    name: 'CarbonLite-34B',
    provider: 'Sustainable AI Co.',
    parameters: '34 Billion',
    tokensPerSec: 85,
    kwh1k: 0.0008,
    co2per: 0.12,
    score: 'A',
    color: '#84cc16',
  },
  {
    id: 3,
    name: 'PromptPro-13B',
    provider: 'GreenGen Innovations',
    parameters: '13 Billion',
    tokensPerSec: 95,
    kwh1k: 0.0005,
    co2per: 0.08,
    score: 'B',
    color: '#fbbf24',
  },
  {
    id: 4,
    name: 'InsightForge-70B',
    provider: 'EcoScale AI',
    parameters: '70 Billion',
    tokensPerSec: 60,
    kwh1k: 0.0015,
    co2per: 0.25,
    score: 'C',
    color: '#f97316',
  },
  {
    id: 5,
    name: 'DataChoir-175B',
    provider: 'Global AI Corp',
    parameters: '175 Billion',
    tokensPerSec: 40,
    kwh1k: 0.0030,
    co2per: 0.45,
    score: 'D',
    color: '#ef4444',
  },
]

const comparisonData = [
  { name: 'EcoGenius-7B', efficiency: 95, cost: 20, emissions: 5 },
  { name: 'CarbonLite-34B', efficiency: 88, cost: 45, emissions: 12 },
  { name: 'PromptPro-13B', efficiency: 92, cost: 35, emissions: 8 },
  { name: 'InsightForge-70B', efficiency: 72, cost: 80, emissions: 25 },
  { name: 'DataChoir-175B', efficiency: 45, cost: 150, emissions: 45 },
]

export default function ModelsPage() {
  const [selectedModel, setSelectedModel] = useState(modelEfficiencyData[0])

  return (
    <div className="p-6 space-y-6 md:ml-64">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-foreground">Model Efficiency Comparison</h2>
        <p className="text-muted-foreground">
          Compare key performance and environmental metrics across different AI models
        </p>
      </div>

      {/* Info Section */}
      <Card className="p-4 bg-primary/5 border border-primary/10 flex gap-3">
        <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-foreground">Model Efficiency Overview</p>
          <p className="text-sm text-muted-foreground mt-1">
            Compare key performance and environmental metrics across different AI models. Efficiency Score (A+ to D) is calculated based on tokens per second, energy consumption, and CO₂ emissions.
          </p>
        </div>
      </Card>

      {/* Model Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Most Efficient Model</p>
          <p className="text-xl font-bold text-foreground mb-1">{modelEfficiencyData[0].name}</p>
          <p className="text-xs text-muted-foreground">Efficiency Score: {modelEfficiencyData[0].score}</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Highest Throughput</p>
          <p className="text-xl font-bold text-foreground mb-1">{modelEfficiencyData[0].name}</p>
          <p className="text-xs text-muted-foreground">{modelEfficiencyData[0].tokensPerSec} tokens/sec</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Lowest Carbon Footprint</p>
          <p className="text-xl font-bold text-foreground mb-1">{modelEfficiencyData[0].name}</p>
          <p className="text-xs text-muted-foreground">{modelEfficiencyData[0].co2per}g CO₂ per request</p>
        </Card>
      </div>

      {/* Efficiency vs Cost */}
      <Card className="p-6 border border-border/50">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-foreground">Efficiency vs Cost Analysis</h3>
          <p className="text-sm text-muted-foreground">Performance vs operational cost across models</p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={comparisonData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis dataKey="name" stroke="var(--color-muted-foreground)" angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="var(--color-muted-foreground)" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--color-card)',
                border: '1px solid var(--color-border)',
                borderRadius: '0.5rem',
              }}
            />
            <Legend />
            <Bar dataKey="efficiency" fill="var(--color-primary)" name="Efficiency Score" />
            <Bar dataKey="cost" fill="var(--color-accent)" name="Relative Cost" />
            <Bar dataKey="emissions" fill="var(--color-chart-3)" name="CO₂ Emissions" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Model Table */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-6">Model Efficiency Overview</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Compare key performance and environmental metrics across different AI models.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Model Name</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Provider</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Parameters</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tokens/Sec</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">kWh/1K</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">CO₂/g</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Score</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody>
              {modelEfficiencyData.map((model) => (
                <tr key={model.id} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                  <td className="py-4 px-4 text-foreground font-medium">{model.name}</td>
                  <td className="py-4 px-4 text-muted-foreground text-xs">{model.provider}</td>
                  <td className="py-4 px-4 text-foreground">{model.parameters}</td>
                  <td className="py-4 px-4 text-foreground">{model.tokensPerSec}</td>
                  <td className="py-4 px-4 text-foreground">{model.kwh1k}</td>
                  <td className="py-4 px-4 text-foreground">{model.co2per}</td>
                  <td className="py-4 px-4">
                    <Badge
                      className="text-xs font-semibold"
                      style={{
                        backgroundColor: model.color + '20',
                        color: model.color,
                        border: `1px solid ${model.color}`,
                      }}
                    >
                      {model.score}
                    </Badge>
                  </td>
                  <td className="py-4 px-4">
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs bg-transparent"
                      onClick={() => setSelectedModel(model)}
                    >
                      View Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Selected Model Details */}
      {selectedModel && (
        <Card className="p-6 border border-border/50">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground">{selectedModel.name}</h3>
              <p className="text-sm text-muted-foreground">{selectedModel.provider}</p>
            </div>
            <Badge
              className="text-sm font-bold"
              style={{
                backgroundColor: selectedModel.color + '20',
                color: selectedModel.color,
                border: `1px solid ${selectedModel.color}`,
              }}
            >
              Score: {selectedModel.score}
            </Badge>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-muted-foreground font-medium mb-1">Parameters</p>
              <p className="text-lg font-bold text-foreground">{selectedModel.parameters}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium mb-1">Tokens/Sec</p>
              <p className="text-lg font-bold text-foreground">{selectedModel.tokensPerSec}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium mb-1">Energy (kWh/1K)</p>
              <p className="text-lg font-bold text-foreground">{selectedModel.kwh1k}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium mb-1">CO₂ (g/request)</p>
              <p className="text-lg font-bold text-foreground">{selectedModel.co2per}</p>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-border">
            <h4 className="font-semibold text-foreground mb-4">Recommendations</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex gap-2">
                <ArrowUpRight className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                <span>This model is ideal for high-throughput, low-latency applications</span>
              </li>
              <li className="flex gap-2">
                <ArrowUpRight className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                <span>Consider deploying in multiple regions to reduce latency</span>
              </li>
              <li className="flex gap-2">
                <ArrowUpRight className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                <span>Enable caching to reduce redundant API calls and emissions</span>
              </li>
            </ul>
          </div>
        </Card>
      )}
    </div>
  )
}
