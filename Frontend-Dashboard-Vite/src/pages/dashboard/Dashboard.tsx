import { useState, useEffect } from 'react'
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
import { AnimatedNumber } from '@/components/AnimatedNumber'

import { API_URL } from '@/config'

export default function Dashboard() {
    const [loading, setLoading] = useState(true)
    const [overview, setOverview] = useState<any>(null)
    const [usage, setUsage] = useState<any>(null)
    const [tokenData, setTokenData] = useState<any[]>([])

    useEffect(() => {
        async function fetchData() {
            try {
                const token = localStorage.getItem('token')
                const headers: any = {}
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`
                }

                const [overviewRes, usageRes] = await Promise.all([
                    fetch(`${API_URL}/api/v1/dashboard/overview?days=7`, { headers }),
                    fetch(`${API_URL}/api/v1/dashboard/usage?days=7`, { headers })
                ])

                const overviewData = await overviewRes.json()
                const usageData = await usageRes.json()

                console.log('Dashboard data updated:', {
                    total_calls: overviewData?.total_calls,
                    total_energy_wh: overviewData?.total_energy_wh,
                    total_co2_g: overviewData?.total_co2_g,
                    avg_latency_ms: overviewData?.avg_latency_ms
                })

                setOverview(overviewData)
                setUsage(usageData)

                // Process usage data for chart
                if (usageData && usageData.daily_usage) {
                    const processed = usageData.daily_usage.map((d: any) => ({
                        date: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                        tokens: d.tokens
                    }))
                    setTokenData(processed)
                }

            } catch (err) {
                console.error('Failed to fetch dashboard data', err)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
        const interval = setInterval(fetchData, 2000)

        return () => clearInterval(interval)
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
                            <p className="text-3xl font-bold text-foreground">
                                <AnimatedNumber value={overview?.total_calls || 0} />
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">
                                {overview?.calls_growth_percent > 0 ? '↑' : '↓'} <AnimatedNumber value={Math.abs(overview?.calls_growth_percent || 0)} decimals={1} />% last period
                            </p>
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
                            <p className="text-3xl font-bold text-foreground">
                                <AnimatedNumber value={overview?.total_energy_wh || 0} decimals={0} suffix="Wh" />
                            </p>
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
                            <p className="text-3xl font-bold text-foreground">
                                <AnimatedNumber value={overview?.total_co2_g || 0} decimals={0} suffix="g" />
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">from backend model</p>
                        </div>
                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                            <Wind className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                    </div>
                </Card>

                <Card className="p-6 border border-border/50">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground mb-1">Avg. Latency</p>
                            <p className="text-3xl font-bold text-foreground">
                                <AnimatedNumber value={overview?.avg_latency_ms || 0} suffix="ms" />
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">Global average</p>
                        </div>
                        <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                            <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                    </div>
                </Card>
            </div>

            {/* Token Usage Chart */}
            <Card className="p-6 border border-border/50">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-foreground">Token Usage Over Time</h3>
                    <div className="text-sm text-muted-foreground">Last 7 days</div>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    {tokenData.length > 0 ? (
                        <LineChart data={tokenData}>
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
                    ) : (
                        <div className="flex items-center justify-center h-full text-muted-foreground">
                            No usage data available
                        </div>
                    )}
                </ResponsiveContainer>
            </Card>
        </div>
    )
}
