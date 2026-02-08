'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { API_URL } from '@/config'
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ZAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
    Legend
} from 'recharts'
import { Info, Leaf, Zap, Trophy, Activity } from 'lucide-react'

// Interface for API response
interface ModelSpec {
    id: string
    model_name: string
    provider: string
    parameters: string
    energy_kwh_per_1k_tokens: number
    co2_g_per_1k_tokens: number
    quality_score: number
    cost_per_1k_input_tokens: number
    cost_per_1k_output_tokens: number
}

// Interface for UI display
interface ModelUI extends ModelSpec {
    efficiency_score: number
    color: string
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe', '#00C49F', '#FFBB28', '#FF8042']

export default function ModelsPage() {
    const [models, setModels] = useState<ModelUI[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchModels()
    }, [])

    const fetchModels = async () => {
        try {
            // Fetch from the new endpoint
            const response = await fetch(`${API_URL}/api/v1/model-specs/`)
            if (!response.ok) throw new Error('Failed to fetch models')

            const data: ModelSpec[] = await response.json()

            const processed: ModelUI[] = data.map((m, i) => ({
                ...m,
                // Calculate simple efficiency score: Quality / Energy
                efficiency_score: m.quality_score / (m.energy_kwh_per_1k_tokens || 0.0001),
                color: COLORS[i % COLORS.length]
            }))

            setModels(processed)
        } catch (err) {
            console.error('Error loading models:', err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="p-6 md:ml-64 flex items-center justify-center min-h-[500px]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        )
    }

    const bestModel = models.reduce((prev, current) =>
        (prev.efficiency_score > current.efficiency_score) ? prev : current
        , models[0])

    const lowestCarbon = models.reduce((prev, current) =>
        (current.co2_g_per_1k_tokens > 0 && current.co2_g_per_1k_tokens < prev.co2_g_per_1k_tokens) ? current : prev
        , models[0])

    return (
        <div className="p-6 space-y-6 md:ml-64 relative">
            <div className="flex flex-col gap-2">
                <h2 className="text-3xl font-bold text-foreground">Model Efficiency Landscape</h2>
                <p className="text-muted-foreground">
                    Visualize the trade-off between Model Quality, Energy Efficiency, and Environmental Impact.
                </p>
            </div>

            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20">
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2 text-green-600 dark:text-green-400">
                            <Trophy className="h-4 w-4" /> Best Quality/Energy Ratio
                        </CardDescription>
                        <CardTitle className="text-2xl">{bestModel?.model_name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-muted-foreground">Efficiency Score:</span>
                            <span className="font-bold">{bestModel?.efficiency_score.toFixed(0)}</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-emerald-500/10 to-transparent border-emerald-500/20">
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                            <Leaf className="h-4 w-4" /> Lowest Carbon Footprint
                        </CardDescription>
                        <CardTitle className="text-2xl">{lowestCarbon?.model_name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-muted-foreground">CO₂ per 1k tokens:</span>
                            <span className="font-bold">{lowestCarbon?.co2_g_per_1k_tokens.toFixed(3)}g</span>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2">
                            <Activity className="h-4 w-4" /> Models Tracked
                        </CardDescription>
                        <CardTitle className="text-2xl">{models.length}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-xs text-muted-foreground mt-1">
                            Live data from model registry
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Bubble Chart */}
            <Card className="p-6">
                <div className="mb-6 flex justify-between items-start">
                    <div>
                        <h3 className="text-lg font-semibold">Efficiency Landscape</h3>
                        <p className="text-sm text-muted-foreground">
                            X: Quality Score | Y: Energy Efficiency (Higher is better) | Bubble Size: CO₂ Impact
                        </p>
                    </div>
                </div>

                <div className="h-[400px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart
                            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
                            <XAxis
                                type="number"
                                dataKey="quality_score"
                                name="Quality"
                                domain={[0, 100]}
                                label={{ value: 'Quality Score (MMLU)', position: 'bottom', offset: 0 }}
                                stroke="currentColor"
                                className="text-xs"
                            />
                            <YAxis
                                type="number"
                                dataKey="efficiency_score"
                                name="Efficiency"
                                label={{ value: 'Energy Efficiency', angle: -90, position: 'insideLeft' }}
                                stroke="currentColor"
                                className="text-xs"
                            />
                            <ZAxis type="number" dataKey="co2_g_per_1k_tokens" range={[60, 400]} name="CO₂ Impact" />
                            <Tooltip
                                cursor={{ strokeDasharray: '3 3' }}
                                content={({ active, payload }) => {
                                    if (active && payload && payload.length) {
                                        const data = payload[0].payload;
                                        return (
                                            <div className="bg-card border border-border p-3 rounded shadow-lg text-sm">
                                                <p className="font-bold mb-1">{data.model_name}</p>
                                                <p className="text-muted-foreground">Provider: {data.provider}</p>
                                                <div className="my-1 h-px bg-border" />
                                                <p>Quality: <span className="font-mono">{data.quality_score}</span></p>
                                                <p>Energy/1k: <span className="font-mono">{data.energy_kwh_per_1k_tokens} kWh</span></p>
                                                <p>CO₂/1k: <span className="font-mono">{data.co2_g_per_1k_tokens} g</span></p>
                                            </div>
                                        );
                                    }
                                    return null;
                                }}
                            />
                            <Legend />
                            <Scatter name="AI Models" data={models} fill="#8884d8">
                                {models.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Scatter>
                        </ScatterChart>
                    </ResponsiveContainer>
                </div>
            </Card>

            {/* Detailed Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Detailed Specifications</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-muted/50 text-muted-foreground uppercase text-xs">
                                <tr>
                                    <th className="px-4 py-3 rounded-tl-lg">Model</th>
                                    <th className="px-4 py-3">Provider</th>
                                    <th className="px-4 py-3">Quality</th>
                                    <th className="px-4 py-3 text-right">Energy (kWh/1k)</th>
                                    <th className="px-4 py-3 text-right">CO₂ (g/1k)</th>
                                    <th className="px-4 py-3 rounded-tr-lg text-right">Est. Cost ($/1M)</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {models.map((model) => (
                                    <tr key={model.id} className="hover:bg-muted/50 transition-colors">
                                        <td className="px-4 py-3 font-medium">
                                            <div className="flex items-center gap-2">
                                                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: model.color }}></span>
                                                {model.model_name}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">{model.provider}</td>
                                        <td className="px-4 py-3">
                                            <Badge variant={model.quality_score > 80 ? "default" : "secondary"}>
                                                {model.quality_score}
                                            </Badge>
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono">{model.energy_kwh_per_1k_tokens.toFixed(5)}</td>
                                        <td className="px-4 py-3 text-right font-mono">{model.co2_g_per_1k_tokens.toFixed(3)}</td>
                                        <td className="px-4 py-3 text-right font-mono">
                                            ${((model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens) / 2 * 1000).toFixed(2)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
