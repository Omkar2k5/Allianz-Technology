import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import CountUp from 'react-countup'
import {
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts'
import { Download } from 'lucide-react'

import { API_URL } from '@/config'

export default function Energy() {
    const [loading, setLoading] = useState(true)
    const [dailyEnergy, setDailyEnergy] = useState<any[]>([])
    const [modelEnergy, setModelEnergy] = useState<any[]>([])
    const [overview, setOverview] = useState<any>(null)
    const [energyMetrics, setEnergyMetrics] = useState<any>(null)

    useEffect(() => {
        async function fetchData() {
            try {
                const token = localStorage.getItem('token')
                const headers: any = {}
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`
                }

                const [overviewRes, energyRes] = await Promise.all([
                    fetch(`${API_URL}/api/v1/dashboard/overview?days=30`, { headers }),
                    fetch(`${API_URL}/api/v1/dashboard/energy?days=30`, { headers })
                ])

                const overviewData = await overviewRes.json()
                const energyData = await energyRes.json()

                setOverview(overviewData)
                setEnergyMetrics(energyData)

                // Process Daily Energy for Area Chart
                if (energyData && energyData.daily_energy) {
                    const processed = energyData.daily_energy.map((d: any) => ({
                        month: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                        inference: d.energy_wh, // Already in Wh
                        training: 0 // Mock training data for now
                    }))
                    setDailyEnergy(processed)
                }

                // Process Model Energy for Bar Chart
                if (energyData && energyData.by_model) {
                    const processedModels = energyData.by_model.map((m: any) => ({
                        name: m.model,
                        inference: m.energy_wh, // Already in Wh
                        training: 0
                    }))
                    setModelEnergy(processedModels)
                }

            } catch (err) {
                console.error('Failed to fetch energy data', err)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
        const interval = setInterval(fetchData, 5000) // Poll every 5 seconds

        return () => clearInterval(interval)
    }, [])

    if (loading) {
        return (
            <div className="p-6 md:ml-64 flex items-center justify-center min-h-[500px]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        )
    }

    // Calculations
    const totalWh = (energyMetrics?.total_energy_wh || 0)
    const avgWhPerRequest = overview?.total_calls > 0 ? totalWh / overview.total_calls : 0
    const avgWhPerModel = modelEnergy.length > 0 ? totalWh / modelEnergy.length : 0

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
                    <p className="text-sm font-medium text-muted-foreground mb-1">Total Wh Consumed</p>
                    <p className="text-3xl font-bold text-foreground">
                        <CountUp end={totalWh} decimals={4} duration={1.5} /> Wh
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Last 30 days</p>
                </Card>

                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Avg. Wh/Request</p>
                    <p className="text-3xl font-bold text-foreground">
                        <CountUp end={avgWhPerRequest} decimals={6} duration={1.5} />
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Global Average</p>
                </Card>

                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Avg. Wh/Model</p>
                    <p className="text-3xl font-bold text-foreground">
                        <CountUp end={avgWhPerModel} decimals={6} duration={1.5} />
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Across active models</p>
                </Card>

                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">PUE Factor</p>
                    <p className="text-3xl font-bold text-foreground">1.10</p>
                    <p className="text-xs text-muted-foreground mt-2">Cloud Provider Default</p>
                </Card>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* PUE-Adjusted Energy */}
                <Card className="p-6 border border-border/50">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-lg font-semibold text-foreground">Energy Consumption Trend</h3>
                            <p className="text-sm text-muted-foreground">Last 30 days (Wh)</p>
                        </div>
                        <Button variant="outline" size="sm">
                            <Download className="w-4 h-4 mr-2" />
                            Export
                        </Button>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        {dailyEnergy.length > 0 ? (
                            <AreaChart data={dailyEnergy}>
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
                                    name="Inference (Wh)"
                                />
                            </AreaChart>
                        ) : (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                No energy data available
                            </div>
                        )}
                    </ResponsiveContainer>
                </Card>

                {/* Energy by Model */}
                <Card className="p-6 border border-border/50">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-lg font-semibold text-foreground">Energy Consumption by Model (Wh)</h3>
                            <p className="text-sm text-muted-foreground">Current period</p>
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        {modelEnergy.length > 0 ? (
                            <BarChart data={modelEnergy}>
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
                                <Bar dataKey="inference" fill="var(--color-primary)" name="Inference (Wh)" />
                            </BarChart>
                        ) : (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                No model data available
                            </div>
                        )}
                    </ResponsiveContainer>
                </Card>
            </div>

            {/* Breakdown Sections */}
            <div className="grid grid-cols-1 gap-6">
                <Card className="p-6 border border-border/50">
                    <h3 className="text-lg font-semibold text-foreground mb-4">Inference Energy Breakdown</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                        Inference energy is calculated based on token count and model-specific energy factors.
                    </p>
                    <ul className="space-y-2 text-sm">
                        <li className="text-foreground">• <span className="font-medium">Total Inference Wh:</span> {totalWh.toFixed(4)} Wh</li>
                        <li className="text-foreground">• <span className="font-medium">Avg. Latency/ms:</span> {overview?.avg_latency_ms || 0} ms</li>
                        <li className="text-foreground">• <span className="font-medium">Total Requests:</span> {overview?.total_calls?.toLocaleString() || 0}</li>
                    </ul>
                    <Button className="w-full mt-4 bg-primary text-primary-foreground hover:bg-primary/90">
                        View detailed logs
                    </Button>
                </Card>
            </div>

            {/* Activity Logs */}
            <Card className="p-6 border border-border/50">
                <h3 className="text-lg font-semibold text-foreground mb-6">Recent Activity Logs (Real-time)</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Timestamp</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Computer / Device</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Model</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tokens</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Latency (ms)</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Energy (Wh)</th>
                                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">CO₂ (g)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {energyMetrics?.recent_activity?.length > 0 ? (
                                energyMetrics.recent_activity.map((row: any, idx: number) => (
                                    <tr key={idx} className="border-b border-border/50 hover:bg-muted/50">
                                        <td className="py-4 px-4 text-foreground">
                                            {new Date(row.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                        </td>
                                        <td className="py-4 px-4 text-foreground font-mono text-xs">
                                            {row.computer_name}
                                        </td>
                                        <td className="py-4 px-4">
                                            <span className="px-2 py-1 rounded text-xs font-medium bg-primary/10 text-primary">
                                                {row.model}
                                            </span>
                                        </td>
                                        <td className="py-4 px-4 text-foreground">{row.tokens}</td>
                                        <td className="py-4 px-4 text-foreground">{row.latency_ms} ms</td>
                                        <td className="py-4 px-4 text-foreground font-medium">{row.energy_wh.toFixed(6)} Wh</td>
                                        <td className="py-4 px-4 text-foreground font-medium">{row.co2_g.toFixed(6)} g</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={7} className="py-8 text-center text-muted-foreground">
                                        No recent activity logs found.
                                    </td>
                                </tr>
                            )}
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
                            <p className="font-mono bg-muted/50 p-3 rounded">Energy (Wh) = Σ (Tokens × Energy_per_Token_Wh)</p>
                            <p className="mt-2 text-xs">For example, GPT-4 is estimated at 0.048 Wh/1k tokens.</p>
                        </div>
                        <div>
                            <p className="font-medium text-foreground mb-2">Real-Time Calculation:</p>
                            <p className="font-mono bg-muted/50 p-3 rounded">
                                {`Total Wh = ${totalWh.toFixed(2)} Wh`}
                            </p>
                        </div>
                        <div>
                            <p className="font-medium text-foreground mb-2">PUE (Power Usage Effectiveness):</p>
                            <p className="font-mono bg-muted/50 p-3 rounded">PUE = Total Facility Power / IT Equipment Power</p>
                            <p className="mt-2">A PUE of 1.10 is used (typical cloud provider efficiency).</p>
                        </div>
                    </div>
                </details>
            </Card>
        </div>
    )
}
