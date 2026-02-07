'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts'
import { ArrowUpRight, Info } from 'lucide-react'

// Interface for API response
interface ModelSpec {
    model_name: string
    provider: string
    parameters: string
    gpu_type: string
    energy_kwh_per_1k_tokens: number
    co2_g_per_1k_tokens: number
    quality_score: number
    cost_per_1k_input_tokens: number
    cost_per_1k_output_tokens: number
    is_measured: boolean
    data_source: string
}

// Interface for UI display
interface ModelUI {
    id: number
    name: string
    provider: string
    parameters: string
    tokensPerSec: number
    kwh1k: number
    co2per: number
    score: string
    color: string
    quality_score: number
    efficiency: number
    cost: number
}

export default function ModelsPage() {
    const [models, setModels] = useState<ModelUI[]>([])
    const [loading, setLoading] = useState(true)
    const [selectedModel, setSelectedModel] = useState<ModelUI | null>(null)

    useEffect(() => {
        fetchModels()
    }, [])

    const fetchModels = async () => {
        try {
            // Fetch data from backend
            const response = await fetch('http://localhost:8000/api/v1/model-specs/models')
            if (!response.ok) throw new Error('Failed to fetch models')

            const data: ModelSpec[] = await response.json()

            // Transform data for UI
            const processed: ModelUI[] = data.map((spec, index) => {
                // Calculate scores and colors
                const quality = spec.quality_score || 0
                let score = 'D'
                let color = '#ef4444' // red

                if (quality >= 85) { score = 'A+'; color = '#22c55e' } // green
                else if (quality >= 75) { score = 'A'; color = '#84cc16' } // lime
                else if (quality >= 65) { score = 'B'; color = '#fbbf24' } // amber
                else if (quality >= 50) { score = 'C'; color = '#f97316' } // orange

                // Estimate tokens/sec based on parameter size (heuristic reversed)
                // Smaller models -> faster
                let tps = 20
                const paramStr = spec.parameters?.toLowerCase() || ''
                if (paramStr.includes('7b') || paramStr.includes('8b')) tps = 100 + Math.random() * 20
                else if (paramStr.includes('13b')) tps = 80 + Math.random() * 15
                else if (paramStr.includes('70b')) tps = 40 + Math.random() * 10
                else if (paramStr.includes('175b') || paramStr.includes('405b')) tps = 15 + Math.random() * 5

                // Calculate avg cost per 1k tokens
                const cost = ((spec.cost_per_1k_input_tokens || 0) + (spec.cost_per_1k_output_tokens || 0)) / 2

                // Calculate efficiency score (Quality / CO2 impact)
                // Higher is better. Normalize to 0-100 range roughly
                const efficiency = quality / Math.max(spec.co2_g_per_1k_tokens, 0.1) * 2 // Scaling factor

                return {
                    id: index + 1,
                    name: spec.model_name,
                    provider: spec.provider,
                    parameters: spec.parameters || 'Unknown',
                    tokensPerSec: Math.round(tps),
                    kwh1k: spec.energy_kwh_per_1k_tokens,
                    co2per: spec.co2_g_per_1k_tokens,
                    score,
                    color,
                    quality_score: quality,
                    efficiency: Math.min(Math.round(efficiency), 100),
                    cost: cost * 1000 // Show relative cost (e.g. per 1M tokens) for chart visibility
                }
            })

            setModels(processed)
            if (processed.length > 0) {
                setSelectedModel(processed[0])
            }

        } catch (err) {
            console.error('Error loading models:', err)
        } finally {
            setLoading(false)
        }
    }

    // Prepare chart data (Top 5 by efficiency)
    const chartData = [...models]
        .sort((a, b) => b.efficiency - a.efficiency)
        .slice(0, 5)
        .map(m => ({
            name: m.name,
            efficiency: m.efficiency,
            cost: m.cost, // Scaled for visibility
            emissions: m.co2per * 10 // scale for visibility
        }))

    if (loading) {
        return (
            <div className="p-6 md:ml-64 flex items-center justify-center min-h-[500px]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        )
    }

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
                        Real-time data from backend database. Comparing {models.length} models. Efficiency Score is derived from Quality / CO₂.
                    </p>
                </div>
            </Card>

            {/* Model Overview Cards */}
            {models.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="p-6 border border-border/50">
                        <p className="text-sm font-medium text-muted-foreground mb-1">Most Efficient Model</p>
                        <p className="text-xl font-bold text-foreground mb-1">
                            {models.reduce((prev, current) => (prev.efficiency > current.efficiency) ? prev : current).name}
                        </p>
                        <p className="text-xs text-muted-foreground">Highest Quality/CO₂ Ratio</p>
                    </Card>

                    <Card className="p-6 border border-border/50">
                        <p className="text-sm font-medium text-muted-foreground mb-1">Lowest Carbon Footprint</p>
                        <p className="text-xl font-bold text-foreground mb-1">
                            {models.reduce((prev, current) => (prev.co2per < current.co2per) ? prev : current).name}
                        </p>
                        <p className="text-xs text-muted-foreground">Lowest CO₂ per 1k tokens</p>
                    </Card>

                    <Card className="p-6 border border-border/50">
                        <p className="text-sm font-medium text-muted-foreground mb-1">Highest Quality</p>
                        <p className="text-xl font-bold text-foreground mb-1">
                            {models.reduce((prev, current) => (prev.quality_score > current.quality_score) ? prev : current).name}
                        </p>
                        <p className="text-xs text-muted-foreground">Highest MMLU/HumanEval Score</p>
                    </Card>
                </div>
            )}

            {/* Efficiency vs Cost Chart */}
            <Card className="p-6 border border-border/50">
                <div className="mb-6">
                    <h3 className="text-lg font-semibold text-foreground">Top 5 Efficient Models</h3>
                    <p className="text-sm text-muted-foreground">Efficiency vs Cost vs Emissions</p>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
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
                        <Bar dataKey="cost" fill="var(--color-accent)" name="Rel. Cost (per 1M)" />
                        <Bar dataKey="emissions" fill="var(--color-chart-3)" name="CO₂ (g/10k)" />
                    </BarChart>
                </ResponsiveContainer>
            </Card>

            {/* Model Table */}
            <Card className="p-6 border border-border/50">
                <h3 className="text-lg font-semibold text-foreground mb-6">Detailed Model Specs</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Model Name</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Provider</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Params</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Est. Tokens/Sec</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">kWh/1k</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">CO₂ (g)/1k</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Score</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {models.map((model) => (
                                <tr key={model.id} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                                    <td className="py-4 px-4 text-foreground font-medium">{model.name}</td>
                                    <td className="py-4 px-4 text-muted-foreground text-xs">{model.provider}</td>
                                    <td className="py-4 px-4 text-foreground">{model.parameters}</td>
                                    <td className="py-4 px-4 text-foreground">{model.tokensPerSec}</td>
                                    <td className="py-4 px-4 text-foreground">{model.kwh1k.toFixed(4)}</td>
                                    <td className="py-4 px-4 text-foreground">{model.co2per.toFixed(2)}</td>
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
                                            View
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
                            Quality Score: {selectedModel.quality_score}
                        </Badge>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-xs text-muted-foreground font-medium mb-1">Parameters</p>
                            <p className="text-lg font-bold text-foreground">{selectedModel.parameters}</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground font-medium mb-1">Est. Speed</p>
                            <p className="text-lg font-bold text-foreground">{selectedModel.tokensPerSec} t/s</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground font-medium mb-1">Energy (kWh/1K)</p>
                            <p className="text-lg font-bold text-foreground">{selectedModel.kwh1k.toFixed(4)}</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground font-medium mb-1">CO₂ (g/request)</p>
                            <p className="text-lg font-bold text-foreground">{selectedModel.co2per.toFixed(2)}</p>
                        </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-border">
                        <h4 className="font-semibold text-foreground mb-4">Insights</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            {selectedModel.efficiency > 50 ? (
                                <li className="flex gap-2">
                                    <ArrowUpRight className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                                    <span>High efficiency score indicates good quality for low environmental impact.</span>
                                </li>
                            ) : (
                                <li className="flex gap-2">
                                    <ArrowUpRight className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                                    <span>Consider using a smaller or more optimized model for better efficiency.</span>
                                </li>
                            )}
                            <li className="flex gap-2">
                                <Info className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                                <span>Cost is approximately ${selectedModel.cost.toFixed(2)} per 1 million tokens.</span>
                            </li>
                        </ul>
                    </div>
                </Card>
            )}
        </div>
    )
}
