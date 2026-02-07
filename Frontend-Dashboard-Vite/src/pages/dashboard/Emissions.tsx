import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import CountUp from 'react-countup'
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts'
import { Download } from 'lucide-react'

export default function Emissions() {
    const [loading, setLoading] = useState(true)
    const [emissionsData, setEmissionsData] = useState<any>(null)

    useEffect(() => {
        fetchEmissionsData()
        const interval = setInterval(fetchEmissionsData, 5000) // Poll every 5 seconds
        return () => clearInterval(interval)
    }, [])

    const fetchEmissionsData = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/dashboard/emissions?days=30')
            const data = await response.json()
            setEmissionsData(data)
            setLoading(false)
        } catch (error) {
            console.error('Failed to fetch emissions data:', error)
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="p-6 space-y-6 md:ml-64">
                <div className="flex items-center justify-center h-64">
                    <p className="text-muted-foreground">Loading emissions data...</p>
                </div>
            </div>
        )
    }

    // Calculate metrics
    const totalCO2 = emissionsData?.total_co2_g || 0
    const totalCO2Kg = totalCO2 / 1000
    const avgCO2PerRequest = emissionsData?.by_region?.length > 0
        ? totalCO2 / emissionsData.by_region.reduce((sum: number, r: any) => sum + r.requests, 0)
        : 0

    // Process monthly trend data
    const monthlyTrend = emissionsData?.monthly_trend?.map((m: any) => ({
        month: new Date(m.month).toLocaleDateString('en-US', { month: 'short' }),
        emissions: m.co2_g / 1000 // Convert to kg
    })) || []

    // Process regional data
    const regionalData = emissionsData?.by_region?.map((r: any) => ({
        region: r.region || 'Unknown',
        emissions: r.co2_g / 1000, // Convert to kg
        requests: r.requests,
        percentage: (r.co2_g / totalCO2) * 100
    })) || []

    return (
        <div className="p-6 space-y-6 md:ml-64">
            {/* Header */}
            <div className="flex flex-col gap-2">
                <h2 className="text-3xl font-bold text-foreground">Carbon Emissions Overview</h2>
                <p className="text-muted-foreground">
                    Monitor and analyze the CO₂ emissions of your AI models across different regions
                </p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Total CO₂ Emissions</p>
                    <p className="text-3xl font-bold text-foreground">
                        <CountUp end={totalCO2Kg} decimals={2} duration={1.5} /> kg
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Last 30 days</p>
                </Card>

                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Avg. CO₂ per Request</p>
                    <p className="text-3xl font-bold text-foreground">
                        <CountUp end={avgCO2PerRequest} decimals={3} duration={1.5} /> g
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Carbon per AI call</p>
                </Card>

                <Card className="p-6 border border-border/50">
                    <p className="text-sm font-medium text-muted-foreground mb-1">Active Regions</p>
                    <p className="text-3xl font-bold text-foreground">
                        {regionalData.length}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Deployment locations</p>
                </Card>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* CO₂ Reduction Trends */}
                <Card className="p-6 border border-border/50">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-lg font-semibold text-foreground">CO₂ Emissions Trend</h3>
                            <p className="text-sm text-muted-foreground">Monthly emissions (kg)</p>
                        </div>
                        <Button variant="outline" size="sm">
                            <Download className="w-4 h-4 mr-2" />
                            Export
                        </Button>
                    </div>
                    {monthlyTrend.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={monthlyTrend}>
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
                                    name="CO₂ (kg)"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                            No trend data available
                        </div>
                    )}
                </Card>

                {/* Regional Breakdown */}
                <Card className="p-6 border border-border/50">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-lg font-semibold text-foreground">Emissions by Region</h3>
                            <p className="text-sm text-muted-foreground">Regional distribution</p>
                        </div>
                    </div>
                    {regionalData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={regionalData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                <XAxis dataKey="region" stroke="var(--color-muted-foreground)" />
                                <YAxis stroke="var(--color-muted-foreground)" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--color-card)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                                <Bar dataKey="emissions" fill="var(--color-primary)" name="CO₂ (kg)" />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                            No regional data available
                        </div>
                    )}
                </Card>
            </div>

            {/* Regional Breakdown Table */}
            <Card className="p-6 border border-border/50">
                <h3 className="text-lg font-semibold text-foreground mb-6">Regional Carbon Intensity Analysis</h3>
                <div className="space-y-4">
                    {regionalData.length > 0 ? (
                        regionalData.map((region: any) => (
                            <div key={region.region}>
                                <div className="flex items-center justify-between mb-2">
                                    <div>
                                        <p className="text-sm font-medium text-foreground">{region.region}</p>
                                        <p className="text-xs text-muted-foreground">
                                            {region.emissions.toFixed(2)} kg CO₂ • {region.requests} requests
                                        </p>
                                    </div>
                                    <p className="text-sm font-semibold text-foreground">{region.percentage.toFixed(1)}%</p>
                                </div>
                                <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all"
                                        style={{ width: `${Math.min(region.percentage, 100)}%` }}
                                    />
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="text-center py-8 text-muted-foreground">
                            No regional data available
                        </div>
                    )}
                </div>
            </Card>

            {/* Emissions Calculation Formula */}
            <Card className="p-6 border border-border/50">
                <h3 className="text-lg font-semibold text-foreground mb-4">Emissions Calculation Formula</h3>
                <div className="space-y-4 text-sm text-muted-foreground">
                    <div className="p-4 bg-muted/50 rounded-lg border border-border">
                        <p className="font-mono font-medium text-foreground mb-2">
                            CO₂ (g) = Energy (Wh) × Grid_Intensity (g CO₂/kWh) / 1000
                        </p>
                        <ul className="space-y-1 text-xs mt-3">
                            <li><span className="font-medium">Energy:</span> Calculated using datacenter power × latency</li>
                            <li><span className="font-medium">Grid Intensity:</span> India: 750 g CO₂/kWh</li>
                            <li><span className="font-medium">Formula:</span> Energy (Wh) = (1200W / 8) × Latency_ms × 1.3 / 3,600,000</li>
                        </ul>
                    </div>
                    <div className="p-4 bg-muted/50 rounded-lg border border-border">
                        <p className="font-medium text-foreground mb-2">Example Calculation:</p>
                        <ul className="space-y-1 text-xs">
                            <li>Request: 2452 tokens, 807ms latency</li>
                            <li>Energy: (1200W / 8) × 807ms × 1.3 / 3,600,000 = 0.044 Wh</li>
                            <li>CO₂: 0.044 Wh × 750 / 1000 = <span className="font-semibold text-foreground">0.033 g</span></li>
                        </ul>
                    </div>
                </div>
            </Card>
        </div>
    )
}
