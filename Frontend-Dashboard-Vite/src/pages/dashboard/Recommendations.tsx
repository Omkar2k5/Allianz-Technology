import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { CheckCircle, Zap, Wind, Timer, TrendingUp } from 'lucide-react'
import { API_URL } from '@/config'
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ComposedChart,
    Line
} from 'recharts'

interface ModelData {
    model: string
    calls: number
    tokens: number
    avg_latency: number
    energy_wh: number
    co2_g: number
    efficiency_score?: number
}

export default function Recommendations() {
    const [models, setModels] = useState<ModelData[]>([])
    const [loading, setLoading] = useState(true)
    const [bestModel, setBestModel] = useState<ModelData | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token')
                const headers: any = {}
                if (token) headers['Authorization'] = `Bearer ${token}`

                const res = await fetch(`${API_URL}/api/v1/dashboard/usage?days=30`, { headers })
                const data = await res.json()

                if (data && data.model_distribution) {
                    const processed: ModelData[] = data.model_distribution.map((m: any) => {
                        // Avoid division by zero
                        const tokens = m.tokens || 1
                        const energyPerToken = m.energy_wh / tokens
                        const co2PerToken = m.co2_g / tokens

                        // Simple Efficiency Score (Lower is better)
                        // Weighted: 40% Energy, 40% CO2, 20% Latency (normalized roughly)
                        // Normalize metrics for scoring (heuristic)
                        const normEnergy = energyPerToken * 100000 // scale to ~0-10
                        const normCO2 = co2PerToken * 10000 // scale to ~0-10
                        const normLatency = m.avg_latency / 100 // scale 100ms to 1

                        const score = (normEnergy * 0.4) + (normCO2 * 0.4) + (normLatency * 0.2)

                        return {
                            ...m,
                            efficiency_score: score,
                            energy_per_1k: energyPerToken * 1000,
                            co2_per_1k: co2PerToken * 1000
                        }
                    })

                    // Sort by efficiency (lowest score is best)
                    processed.sort((a, b) => (a.efficiency_score || 0) - (b.efficiency_score || 0))

                    setModels(processed)
                    if (processed.length > 0) setBestModel(processed[0])
                }
            } catch (err) {
                console.error("Failed to fetch data", err)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

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
                <h2 className="text-3xl font-bold text-foreground">AI Model Recommendations</h2>
                <p className="text-muted-foreground">
                    Data-driven insights to optimize for performance and sustainability
                </p>
            </div>

            {/* Best Model Highlight */}
            {bestModel && (
                <Card className="p-6 border border-green-200 bg-green-50/30 dark:border-green-900/50 dark:bg-green-900/10">
                    <div className="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
                        <div className="flex gap-4">
                            <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center flex-shrink-0">
                                <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
                            </div>
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <h3 className="text-xl font-bold text-foreground">Top Recommendation: {bestModel.model}</h3>
                                    <Badge className="bg-green-500 hover:bg-green-600">Best Overall</Badge>
                                </div>
                                <p className="text-muted-foreground max-w-2xl">
                                    Based on your usage history, <strong>{bestModel.model}</strong> delivers the best balance of low latency ({bestModel.avg_latency.toFixed(0)}ms) and minimal environmental impact.
                                </p>
                            </div>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-center w-full md:w-auto">
                            <div>
                                <p className="text-xs text-muted-foreground">Energy/1k</p>
                                <p className="font-bold text-green-700 dark:text-green-400 text-lg">
                                    {((bestModel.energy_wh / (bestModel.tokens || 1)) * 1000).toFixed(4)} Wh
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">CO₂/1k</p>
                                <p className="font-bold text-green-700 dark:text-green-400 text-lg">
                                    {((bestModel.co2_g / (bestModel.tokens || 1)) * 1000).toFixed(4)} g
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Latency</p>
                                <p className="font-bold text-foreground text-lg">
                                    {bestModel.avg_latency.toFixed(0)} ms
                                </p>
                            </div>
                        </div>
                    </div>
                </Card>
            )}

            {/* Comparison Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Efficiency Landscape */}
                <Card className="p-6 border border-border/50">
                    <div className="mb-6">
                        <h3 className="text-lg font-semibold text-foreground">Efficiency Landscape</h3>
                        <p className="text-sm text-muted-foreground">
                            Energy consumption and latency by model
                        </p>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <ComposedChart
                            data={models.slice(0, 6)}
                            margin={{ top: 20, right: 30, bottom: 60, left: 20 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                            <XAxis
                                dataKey="model"
                                stroke="var(--color-muted-foreground)"
                                angle={-45}
                                textAnchor="end"
                                height={80}
                                interval={0}
                                tick={{ fontSize: 11 }}
                            />
                            <YAxis
                                yAxisId="left"
                                stroke="var(--color-muted-foreground)"
                                label={{ value: 'Energy (Wh)', angle: -90, position: 'insideLeft' }}
                            />
                            <YAxis
                                yAxisId="right"
                                orientation="right"
                                stroke="var(--color-muted-foreground)"
                                label={{ value: 'Latency (ms)', angle: 90, position: 'insideRight' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'var(--color-card)',
                                    border: '1px solid var(--color-border)',
                                    borderRadius: '0.5rem',
                                }}
                            />
                            <Legend />
                            <Bar yAxisId="left" dataKey="energy_wh" name="Energy (Wh)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                            <Line yAxisId="right" type="monotone" dataKey="avg_latency" name="Latency (ms)" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </Card>

                {/* Model Comparison Bar Chart */}
                <Card className="p-6 border border-border/50">
                    <div className="mb-6">
                        <h3 className="text-lg font-semibold text-foreground">Environmental Impact per 1k Tokens</h3>
                        <p className="text-sm text-muted-foreground">
                            Normalized comparison of energy and emissions
                        </p>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart
                            data={models.slice(0, 5)}
                            layout="vertical"
                            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={true} vertical={true} />
                            <XAxis type="number" stroke="var(--color-muted-foreground)" />
                            <YAxis type="category" dataKey="model" width={100} stroke="var(--color-foreground)" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'var(--color-card)',
                                    border: '1px solid var(--color-border)',
                                    borderRadius: '0.5rem',
                                }}
                            />
                            <Legend />
                            {/* @ts-ignore */}
                            <Bar dataKey="energy_per_1k" name="Energy (Wh/1k)" fill="#ef4444" radius={[0, 4, 4, 0]} />
                            {/* @ts-ignore */}
                            <Bar dataKey="co2_per_1k" name="CO₂ (g/1k)" fill="#22c55e" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            {/* Model Ranking Table */}
            <Card className="p-6 border border-border/50">
                <h3 className="text-lg font-semibold text-foreground mb-4">Model Ranking (Efficiency Score)</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Rank</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Model</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Latency</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Energy/1k Tokens</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">CO₂/1k Tokens</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Total Tokens</th>
                            </tr>
                        </thead>
                        <tbody>
                            {models.map((model, idx) => (
                                <tr key={model.model} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                                    <td className="py-4 px-4 text-foreground font-bold">#{idx + 1}</td>
                                    <td className="py-4 px-4 text-foreground font-medium flex items-center gap-2">
                                        {idx === 0 && <CheckCircle className="w-4 h-4 text-green-500" />}
                                        {model.model}
                                    </td>
                                    <td className="py-4 px-4 text-foreground">{model.avg_latency.toFixed(0)} ms</td>
                                    <td className="py-4 px-4 text-foreground">
                                        {((model.energy_wh / (model.tokens || 1)) * 1000).toFixed(4)} Wh
                                    </td>
                                    <td className="py-4 px-4 text-foreground">
                                        {((model.co2_g / (model.tokens || 1)) * 1000).toFixed(4)} g
                                    </td>
                                    <td className="py-4 px-4 text-foreground">{model.tokens.toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>

        </div>
    )
}
