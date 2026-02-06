import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
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

export default function Usage() {
    const [loading, setLoading] = useState(true)
    const [dailyUsage, setDailyUsage] = useState<any[]>([])
    const [modelStats, setModelStats] = useState<any[]>([])
    const [totalTokens, setTotalTokens] = useState<number>(0)
    const [overview, setOverview] = useState<any>(null)

    useEffect(() => {
        async function fetchData() {
            try {
                const token = localStorage.getItem('token')
                const headers: any = {}
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`
                }

                const [overviewRes, usageRes] = await Promise.all([
                    fetch('http://127.0.0.1:8000/api/v1/dashboard/overview?days=30', { headers }),
                    fetch('http://127.0.0.1:8000/api/v1/dashboard/usage?days=30', { headers })
                ])

                const overviewData = await overviewRes.json()
                const usageData = await usageRes.json()

                setOverview(overviewData)

                // Process Daily Usage
                if (usageData && usageData.daily_usage) {
                    const processed = usageData.daily_usage.map((d: any) => ({
                        date: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                        calls: d.calls,
                        tokens: d.tokens
                    }))
                    setDailyUsage(processed)
                }

                // Process Model Stats
                if (usageData && usageData.model_distribution) {
                    const totalCalls = usageData.model_distribution.reduce((acc: number, curr: any) => acc + curr.calls, 0)
                    const totalToks = usageData.model_distribution.reduce((acc: number, curr: any) => acc + curr.tokens, 0)
                    setTotalTokens(totalToks)

                    const processedModels = usageData.model_distribution.map((m: any) => ({
                        name: m.model,
                        calls: m.calls,
                        tokens: m.tokens,
                        percentage: totalCalls > 0 ? Math.round((m.calls / totalCalls) * 100) : 0,
                        tokens_input: m.tokens_input,
                        tokens_output: m.tokens_output,
                        avg_latency: m.avg_latency,
                        cost_usd: m.cost_usd
                    }))
                    setModelStats(processedModels)
                }

            } catch (err) {
                console.error('Failed to fetch usage data', err)
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
                <h2 className="text-3xl font-bold text-foreground">Usage Tracking</h2>
                <p className="text-muted-foreground">
                    Monitor API calls, token usage, and model distribution across your team
                </p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Total API Calls</p>
                    <p className="text-3xl font-bold text-foreground">
                        {overview?.total_calls?.toLocaleString() || 0}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">
                        {overview?.calls_growth_percent > 0 ? '↑' : '↓'} {Math.abs(overview?.calls_growth_percent || 0)}% from last period
                    </p>
                </Card>

                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Total Tokens Used</p>
                    <p className="text-3xl font-bold text-foreground">
                        {totalTokens > 1000000 ? `${(totalTokens / 1000000).toFixed(1)}M` : totalTokens.toLocaleString()}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Last 30 days</p>
                </Card>

                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Avg. Response Time</p>
                    <p className="text-3xl font-bold text-foreground">
                        {overview?.avg_latency_ms || 0}ms
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Global Average</p>
                </Card>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <Card className="p-6 border border-border/50">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-lg font-semibold text-foreground">Usage Trend</h3>
                                <p className="text-sm text-muted-foreground">API calls and tokens over time (30 days)</p>
                            </div>
                            <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                                <Download className="w-4 h-4" />
                                Export
                            </Button>
                        </div>
                        <ResponsiveContainer width="100%" height={350}>
                            {dailyUsage.length > 0 ? (
                                <LineChart data={dailyUsage}>
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
                            ) : (
                                <div className="flex items-center justify-center h-full text-muted-foreground">
                                    No usage data available
                                </div>
                            )}
                        </ResponsiveContainer>
                    </Card>
                </div>

                <Card className="p-6 border border-border/50">
                    <h3 className="text-lg font-semibold text-foreground mb-6">Model Distribution</h3>
                    <div className="space-y-4">
                        {modelStats.length > 0 ? (
                            modelStats.map((model) => (
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
                            ))
                        ) : (
                            <div className="text-sm text-muted-foreground text-center">No data available</div>
                        )}
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
                            {modelStats.length > 0 ? (
                                modelStats.map((model) => (
                                    <tr key={model.name} className="border-b border-border/50 hover:bg-muted/50">
                                        <td className="py-4 px-4 text-foreground font-medium">{model.name}</td>
                                        <td className="py-4 px-4 text-foreground">{model.calls.toLocaleString()}</td>
                                        <td className="py-4 px-4 text-foreground">{(model.tokens_input || 0).toLocaleString()}</td>
                                        <td className="py-4 px-4 text-foreground">{(model.tokens_output || 0).toLocaleString()}</td>
                                        <td className="py-4 px-4 text-foreground">{Math.round(model.avg_latency || 0)}ms</td>
                                        <td className="py-4 px-4 text-foreground">${(model.cost_usd || 0).toFixed(4)}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={6} className="py-8 text-center text-muted-foreground">
                                        No model usage data recorded yet.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
