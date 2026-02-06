import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
    Cell,
} from 'recharts'
import {
    BookOpen,
    Cpu,
    Zap,
    Cloud,
    ExternalLink,
    Info,
    CheckCircle2,
    AlertCircle,
    Leaf,
    Globe,
    Database,
} from 'lucide-react'

// Research-grade model data from TokenPowerBench 2025, Patterson et al., MLPerf
const researchModels = [
    {
        name: 'GPT-4o',
        provider: 'OpenAI',
        params: 'Unknown',
        energyJ: 0.3,
        energyKwh: 0.0003,
        co2G: 0.12,
        quality: 88,
        gpu: 'H100',
        measured: false,
        source: 'Query-based estimates',
        color: '#10b981',
    },
    {
        name: 'Llama 3 1B',
        provider: 'Meta',
        params: '1B',
        energyJ: 0.5,
        energyKwh: 0.0005,
        co2G: 0.2,
        quality: 65,
        gpu: 'H100',
        measured: true,
        source: 'TokenPowerBench 2025',
        color: '#22c55e',
    },
    {
        name: 'Claude 3 Haiku',
        provider: 'Anthropic',
        params: '~20-200B',
        energyJ: 1.0,
        energyKwh: 0.001,
        co2G: 0.4,
        quality: 75,
        gpu: 'TPU/A100',
        measured: false,
        source: 'Latency-based estimates',
        color: '#84cc16',
    },
    {
        name: 'Mistral 7B',
        provider: 'Mistral',
        params: '7B',
        energyJ: 1.5,
        energyKwh: 0.0015,
        co2G: 0.6,
        quality: 76,
        gpu: 'A100/H100',
        measured: false,
        source: 'TokenPowerBench + MLPerf',
        color: '#a3e635',
    },
    {
        name: 'Llama 3 8B',
        provider: 'Meta',
        params: '8B',
        energyJ: 2.0,
        energyKwh: 0.002,
        co2G: 0.8,
        quality: 75,
        gpu: 'H100',
        measured: false,
        source: 'Derived from TokenPowerBench',
        color: '#fbbf24',
    },
    {
        name: 'GPT-3.5 Turbo',
        provider: 'OpenAI',
        params: '175B',
        energyJ: 4.0,
        energyKwh: 0.004,
        co2G: 1.6,
        quality: 75,
        gpu: 'A100',
        measured: false,
        source: 'Scaled from GPT-3',
        color: '#fb923c',
    },
    {
        name: 'Mixtral 8x7B',
        provider: 'Mistral',
        params: 'MoE ~8B active',
        energyJ: 5.0,
        energyKwh: 0.005,
        co2G: 2.0,
        quality: 80,
        gpu: 'H100',
        measured: true,
        source: 'TokenPowerBench 2025',
        color: '#f97316',
    },
    {
        name: 'Llama 3 70B',
        provider: 'Meta',
        params: '70B',
        energyJ: 7.0,
        energyKwh: 0.007,
        co2G: 2.8,
        quality: 85,
        gpu: 'H100 (4x)',
        measured: true,
        source: 'TokenPowerBench 2025',
        color: '#ef4444',
    },
    {
        name: 'GPT-4',
        provider: 'OpenAI',
        params: '~1.7T',
        energyJ: 20.0,
        energyKwh: 0.02,
        co2G: 8.0,
        quality: 86,
        gpu: 'A100/H100',
        measured: false,
        source: 'FLOPs-scaled estimates',
        color: '#dc2626',
    },
    {
        name: 'Llama 2 70B',
        provider: 'Meta',
        params: '70B',
        energyJ: 111.4,
        energyKwh: 0.11,
        co2G: 44.0,
        quality: 82,
        gpu: 'A100',
        measured: true,
        source: 'MLPerf Inference v5.1',
        color: '#991b1b',
    },
    {
        name: 'Llama 3 405B',
        provider: 'Meta',
        params: '405B',
        energyJ: 175.0,
        energyKwh: 0.175,
        co2G: 70.0,
        quality: 92,
        gpu: '16x H100',
        measured: true,
        source: 'TokenPowerBench 2025',
        color: '#7f1d1d',
    },
]

// Cloud region data
const cloudRegions = [
    { region: 'Quebec, CA', provider: 'Azure', carbon: 10, renewable: 99, pue: 1.18, color: '#22c55e' },
    { region: 'Stockholm, SE', provider: 'AWS', carbon: 15, renewable: 85, pue: 1.15, color: '#22c55e' },
    { region: 'Norway', provider: 'Azure', carbon: 20, renewable: 98, pue: 1.18, color: '#22c55e' },
    { region: 'Zurich, CH', provider: 'GCP', carbon: 30, renewable: 99, pue: 1.10, color: '#84cc16' },
    { region: 'France', provider: 'Azure', carbon: 60, renewable: 96, pue: 1.18, color: '#84cc16' },
    { region: 'Finland', provider: 'GCP', carbon: 80, renewable: 98, pue: 1.08, color: '#84cc16' },
    { region: 'São Paulo, BR', provider: 'AWS', carbon: 90, renewable: 92, pue: 1.15, color: '#a3e635' },
    { region: 'Oregon, US', provider: 'AWS', carbon: 120, renewable: 97, pue: 1.10, color: '#fbbf24' },
    { region: 'California, US', provider: 'Azure', carbon: 200, renewable: 60, pue: 1.15, color: '#fb923c' },
    { region: 'Ireland', provider: 'AWS', carbon: 290, renewable: 45, pue: 1.15, color: '#f97316' },
    { region: 'Frankfurt, DE', provider: 'GCP', carbon: 360, renewable: 85, pue: 1.10, color: '#ef4444' },
    { region: 'Virginia, US', provider: 'AWS', carbon: 390, renewable: 30, pue: 1.20, color: '#dc2626' },
    { region: 'Singapore', provider: 'GCP', carbon: 430, renewable: 68, pue: 1.10, color: '#991b1b' },
    { region: 'Mumbai, IN', provider: 'GCP', carbon: 670, renewable: 60, pue: 1.10, color: '#7f1d1d' },
    { region: 'Cape Town, ZA', provider: 'Azure', carbon: 850, renewable: 15, pue: 1.18, color: '#450a0a' },
]

// Training energy data
const trainingData = [
    { model: 'GPT-3', energy: 1287, co2: 552, params: '175B', source: 'Patterson et al. 2021' },
    { model: 'Meena', energy: 232, co2: 98, params: '2.6B', source: 'Patterson et al. 2021' },
    { model: 'T5-XXL', energy: 86, co2: 36, params: '11B', source: 'Patterson et al. 2021' },
]

// Efficiency score calculation
const efficiencyData = researchModels.map((m) => ({
    name: m.name,
    efficiency: (m.quality / Math.max(m.co2G, 0.1)).toFixed(1),
    quality: m.quality,
    co2: m.co2G,
}))

export default function RFE() {
    const [activeTab, setActiveTab] = useState('models')

    return (
        <div className="p-6 space-y-6 md:ml-64">
            {/* Header */}
            <div className="flex flex-col gap-2">
                <div className="flex items-center gap-3">
                    <BookOpen className="w-8 h-8 text-primary" />
                    <h2 className="text-3xl font-bold text-foreground">Research for Estimation (RFE)</h2>
                </div>
                <p className="text-muted-foreground">
                    Production-grade carbon tracking data from TokenPowerBench 2025, Patterson et al., MLPerf Power, and IEA grid carbon factors
                </p>
            </div>

            {/* Key Insights */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="p-6 border border-border/50 bg-gradient-to-br from-green-500/10 to-green-600/5">
                    <div className="flex items-center gap-3 mb-2">
                        <Leaf className="w-5 h-5 text-green-600" />
                        <p className="text-sm font-medium text-muted-foreground">Most Efficient</p>
                    </div>
                    <p className="text-2xl font-bold text-foreground">GPT-4o</p>
                    <p className="text-xs text-muted-foreground mt-1">0.12g CO₂/1k tokens</p>
                </Card>

                <Card className="p-6 border border-border/50 bg-gradient-to-br from-blue-500/10 to-blue-600/5">
                    <div className="flex items-center gap-3 mb-2">
                        <Database className="w-5 h-5 text-blue-600" />
                        <p className="text-sm font-medium text-muted-foreground">Models Tracked</p>
                    </div>
                    <p className="text-2xl font-bold text-foreground">{researchModels.length}</p>
                    <p className="text-xs text-muted-foreground mt-1">6 measured, 5 estimated</p>
                </Card>

                <Card className="p-6 border border-border/50 bg-gradient-to-br from-purple-500/10 to-purple-600/5">
                    <div className="flex items-center gap-3 mb-2">
                        <Globe className="w-5 h-5 text-purple-600" />
                        <p className="text-sm font-medium text-muted-foreground">Cloud Regions</p>
                    </div>
                    <p className="text-2xl font-bold text-foreground">{cloudRegions.length}</p>
                    <p className="text-xs text-muted-foreground mt-1">AWS, GCP, Azure</p>
                </Card>

                <Card className="p-6 border border-border/50 bg-gradient-to-br from-amber-500/10 to-amber-600/5">
                    <div className="flex items-center gap-3 mb-2">
                        <Cloud className="w-5 h-5 text-amber-600" />
                        <p className="text-sm font-medium text-muted-foreground">Cleanest Region</p>
                    </div>
                    <p className="text-2xl font-bold text-foreground">Quebec</p>
                    <p className="text-xs text-muted-foreground mt-1">10g CO₂/kWh (99% renewable)</p>
                </Card>
            </div>

            {/* Data Sources */}
            <Card className="p-6 border border-primary/20 bg-primary/5">
                <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <div className="space-y-2">
                        <p className="text-sm font-semibold text-foreground">Research-Grade Data Sources</p>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-muted-foreground">
                            <div className="flex items-start gap-2">
                                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-medium text-foreground">TokenPowerBench 2025</p>
                                    <p>H100/A100 inference measurements</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-2">
                                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-medium text-foreground">Patterson et al. 2021</p>
                                    <p>GPT-3 training: 1,287 MWh, 552 tons CO₂</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-2">
                                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-medium text-foreground">IEA/Ember 2023</p>
                                    <p>Grid carbon intensity by country</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Main Content Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-4 lg:w-auto">
                    <TabsTrigger value="models">
                        <Cpu className="w-4 h-4 mr-2" />
                        Models
                    </TabsTrigger>
                    <TabsTrigger value="regions">
                        <Cloud className="w-4 h-4 mr-2" />
                        Cloud Regions
                    </TabsTrigger>
                    <TabsTrigger value="training">
                        <Zap className="w-4 h-4 mr-2" />
                        Training Data
                    </TabsTrigger>
                    <TabsTrigger value="references">
                        <BookOpen className="w-4 h-4 mr-2" />
                        References
                    </TabsTrigger>
                </TabsList>

                {/* Models Tab */}
                <TabsContent value="models" className="space-y-6">
                    {/* Energy vs Quality Scatter */}
                    <Card className="p-6 border border-border/50">
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-foreground">Energy Efficiency vs Quality</h3>
                            <p className="text-sm text-muted-foreground">Lower CO₂ + higher quality = more efficient</p>
                        </div>
                        <ResponsiveContainer width="100%" height={400}>
                            <ScatterChart>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                <XAxis
                                    type="number"
                                    dataKey="co2G"
                                    name="CO₂ (g/1k tokens)"
                                    stroke="var(--color-muted-foreground)"
                                    label={{ value: 'CO₂ Emissions (g/1k tokens)', position: 'insideBottom', offset: -5 }}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="quality"
                                    name="Quality Score"
                                    stroke="var(--color-muted-foreground)"
                                    label={{ value: 'Quality Score', angle: -90, position: 'insideLeft' }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--color-card)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '0.5rem',
                                    }}
                                    content={({ active, payload }) => {
                                        if (active && payload && payload.length) {
                                            const data = payload[0].payload
                                            return (
                                                <div className="bg-card p-3 border border-border rounded-lg shadow-lg">
                                                    <p className="font-semibold text-foreground">{data.name}</p>
                                                    <p className="text-xs text-muted-foreground">{data.provider}</p>
                                                    <div className="mt-2 space-y-1 text-xs">
                                                        <p>Quality: {data.quality}</p>
                                                        <p>CO₂: {data.co2G}g/1k tokens</p>
                                                        <p>Energy: {data.energyKwh} kWh/1k</p>
                                                        <p className="text-muted-foreground">{data.source}</p>
                                                    </div>
                                                </div>
                                            )
                                        }
                                        return null
                                    }}
                                />
                                <Scatter data={researchModels} fill="var(--color-primary)">
                                    {researchModels.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Scatter>
                            </ScatterChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Efficiency Ranking */}
                    <Card className="p-6 border border-border/50">
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-foreground">Efficiency Ranking</h3>
                            <p className="text-sm text-muted-foreground">Quality Score / CO₂ Emissions (higher is better)</p>
                        </div>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={efficiencyData.sort((a, b) => parseFloat(b.efficiency) - parseFloat(a.efficiency))}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                <XAxis dataKey="name" stroke="var(--color-muted-foreground)" angle={-45} textAnchor="end" height={120} />
                                <YAxis stroke="var(--color-muted-foreground)" label={{ value: 'Efficiency Score', angle: -90, position: 'insideLeft' }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--color-card)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                                <Bar dataKey="efficiency" fill="var(--color-primary)" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Model Comparison Table */}
                    <Card className="p-6 border border-border/50">
                        <h3 className="text-lg font-semibold text-foreground mb-6">Detailed Model Specifications</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-border">
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Model</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Provider</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Params</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">GPU</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Energy (J/token)</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">CO₂ (g/1k)</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Quality</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Source</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Measured</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {researchModels.sort((a, b) => a.co2G - b.co2G).map((model) => (
                                        <tr key={model.name} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                                            <td className="py-4 px-4 font-medium text-foreground">{model.name}</td>
                                            <td className="py-4 px-4 text-muted-foreground text-xs">{model.provider}</td>
                                            <td className="py-4 px-4 text-foreground">{model.params}</td>
                                            <td className="py-4 px-4 text-xs text-muted-foreground">{model.gpu}</td>
                                            <td className="py-4 px-4 text-foreground">{model.energyJ}</td>
                                            <td className="py-4 px-4">
                                                <span
                                                    className="px-2 py-1 rounded text-xs font-semibold"
                                                    style={{
                                                        backgroundColor: model.color + '20',
                                                        color: model.color,
                                                    }}
                                                >
                                                    {model.co2G}
                                                </span>
                                            </td>
                                            <td className="py-4 px-4 text-foreground">{model.quality}</td>
                                            <td className="py-4 px-4 text-xs text-muted-foreground max-w-[150px] truncate">{model.source}</td>
                                            <td className="py-4 px-4">
                                                {model.measured ? (
                                                    <Badge className="bg-green-500/20 text-green-700 border-green-500/50">
                                                        <CheckCircle2 className="w-3 h-3 mr-1" />
                                                        Yes
                                                    </Badge>
                                                ) : (
                                                    <Badge className="bg-amber-500/20 text-amber-700 border-amber-500/50">
                                                        <AlertCircle className="w-3 h-3 mr-1" />
                                                        Estimated
                                                    </Badge>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </Card>
                </TabsContent>

                {/* Cloud Regions Tab */}
                <TabsContent value="regions" className="space-y-6">
                    {/* Carbon Intensity Map */}
                    <Card className="p-6 border border-border/50">
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-foreground">Cloud Region Carbon Intensity</h3>
                            <p className="text-sm text-muted-foreground">gCO₂/kWh by region (lower is better)</p>
                        </div>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={cloudRegions.sort((a, b) => a.carbon - b.carbon)}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                <XAxis dataKey="region" stroke="var(--color-muted-foreground)" angle={-45} textAnchor="end" height={120} />
                                <YAxis stroke="var(--color-muted-foreground)" label={{ value: 'Carbon Intensity (gCO₂/kWh)', angle: -90, position: 'insideLeft' }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--color-card)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                                <Bar dataKey="carbon">
                                    {cloudRegions.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Renewable Energy % */}
                    <Card className="p-6 border border-border/50">
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-foreground">Renewable Energy Percentage</h3>
                            <p className="text-sm text-muted-foreground">% renewable energy by cloud region</p>
                        </div>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={cloudRegions.sort((a, b) => b.renewable - a.renewable)}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                <XAxis dataKey="region" stroke="var(--color-muted-foreground)" angle={-45} textAnchor="end" height={120} />
                                <YAxis stroke="var(--color-muted-foreground)" label={{ value: 'Renewable %', angle: -90, position: 'insideLeft' }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--color-card)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                                <Bar dataKey="renewable" fill="var(--color-primary)" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Region Comparison Table */}
                    <Card className="p-6 border border-border/50">
                        <h3 className="text-lg font-semibold text-foreground mb-6">Cloud Region Details</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-border">
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Region</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Provider</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Carbon (gCO₂/kWh)</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Renewable %</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">PUE</th>
                                        <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Rating</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {cloudRegions.sort((a, b) => a.carbon - b.carbon).map((region) => (
                                        <tr key={region.region} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                                            <td className="py-4 px-4 font-medium text-foreground">{region.region}</td>
                                            <td className="py-4 px-4 text-muted-foreground">{region.provider}</td>
                                            <td className="py-4 px-4">
                                                <span
                                                    className="px-2 py-1 rounded text-xs font-semibold"
                                                    style={{
                                                        backgroundColor: region.color + '20',
                                                        color: region.color,
                                                    }}
                                                >
                                                    {region.carbon}
                                                </span>
                                            </td>
                                            <td className="py-4 px-4 text-foreground">{region.renewable}%</td>
                                            <td className="py-4 px-4 text-foreground">{region.pue}</td>
                                            <td className="py-4 px-4">
                                                {region.carbon < 100 ? (
                                                    <Badge className="bg-green-500/20 text-green-700 border-green-500/50">Excellent</Badge>
                                                ) : region.carbon < 300 ? (
                                                    <Badge className="bg-blue-500/20 text-blue-700 border-blue-500/50">Good</Badge>
                                                ) : region.carbon < 500 ? (
                                                    <Badge className="bg-amber-500/20 text-amber-700 border-amber-500/50">Moderate</Badge>
                                                ) : (
                                                    <Badge className="bg-red-500/20 text-red-700 border-red-500/50">High Impact</Badge>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </Card>
                </TabsContent>

                {/* Training Data Tab */}
                <TabsContent value="training" className="space-y-6">
                    <Card className="p-6 border border-border/50">
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-foreground">Model Training Energy Consumption</h3>
                            <p className="text-sm text-muted-foreground">One-time training costs from Patterson et al. 2021</p>
                        </div>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={trainingData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                <XAxis dataKey="model" stroke="var(--color-muted-foreground)" />
                                <YAxis stroke="var(--color-muted-foreground)" label={{ value: 'Energy (MWh)', angle: -90, position: 'insideLeft' }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--color-card)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '0.5rem',
                                    }}
                                />
                                <Legend />
                                <Bar dataKey="energy" fill="var(--color-primary)" name="Training Energy (MWh)" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {trainingData.map((model) => (
                            <Card key={model.model} className="p-6 border border-border/50">
                                <h4 className="font-semibold text-foreground mb-4">{model.model}</h4>
                                <div className="space-y-3">
                                    <div>
                                        <p className="text-xs text-muted-foreground">Parameters</p>
                                        <p className="text-lg font-bold text-foreground">{model.params}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-muted-foreground">Training Energy</p>
                                        <p className="text-lg font-bold text-foreground">{model.energy} MWh</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-muted-foreground">Training CO₂</p>
                                        <p className="text-lg font-bold text-foreground">{model.co2} tons</p>
                                    </div>
                                    <div className="pt-2 border-t border-border">
                                        <p className="text-xs text-muted-foreground">{model.source}</p>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>

                    <Card className="p-6 border border-amber-500/20 bg-amber-500/5">
                        <div className="flex items-start gap-3">
                            <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="text-sm font-semibold text-foreground mb-2">Training vs Inference</p>
                                <p className="text-sm text-muted-foreground">
                                    Training is a one-time cost, but inference happens millions of times. For GPT-3, training consumed 1,287 MWh, but if used for 1 billion requests, inference would consume significantly more energy over time.
                                </p>
                            </div>
                        </div>
                    </Card>
                </TabsContent>

                {/* References Tab */}
                <TabsContent value="references" className="space-y-6">
                    <Card className="p-6 border border-border/50">
                        <h3 className="text-lg font-semibold text-foreground mb-6">Research Papers & Data Sources</h3>
                        <div className="space-y-6">
                            <div className="border-l-4 border-primary pl-4">
                                <h4 className="font-semibold text-foreground mb-2">TokenPowerBench 2025</h4>
                                <p className="text-sm text-muted-foreground mb-3">
                                    Measured energy consumption for LLM inference on H100/A100 GPUs. Provides the most accurate data for modern models including Llama 3, Mixtral, and others.
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    <Badge className="bg-green-500/20 text-green-700 border-green-500/50">Measured Data</Badge>
                                    <Badge className="bg-blue-500/20 text-blue-700 border-blue-500/50">High Confidence</Badge>
                                </div>
                            </div>

                            <div className="border-l-4 border-blue-600 pl-4">
                                <h4 className="font-semibold text-foreground mb-2">Patterson et al. 2021</h4>
                                <p className="text-sm text-muted-foreground mb-3">
                                    "Carbon Emissions and Large Neural Network Training" - Comprehensive study of GPT-3 training energy (1,287 MWh, 552 tons CO₂) and other models.
                                </p>
                                <Button variant="outline" size="sm" className="text-xs" asChild>
                                    <a href="https://arxiv.org/abs/2104.10350" target="_blank" rel="noopener noreferrer">
                                        <ExternalLink className="w-3 h-3 mr-2" />
                                        View Paper
                                    </a>
                                </Button>
                            </div>

                            <div className="border-l-4 border-purple-600 pl-4">
                                <h4 className="font-semibold text-foreground mb-2">MLPerf Inference v5.1 Power</h4>
                                <p className="text-sm text-muted-foreground mb-3">
                                    Standardized, audited benchmarks for LLM inference power consumption. Provides measured data for Llama 2 70B and other models.
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    <Badge className="bg-green-500/20 text-green-700 border-green-500/50">Audited</Badge>
                                    <Badge className="bg-purple-500/20 text-purple-700 border-purple-500/50">Industry Standard</Badge>
                                </div>
                            </div>

                            <div className="border-l-4 border-amber-600 pl-4">
                                <h4 className="font-semibold text-foreground mb-2">IEA & Ember Climate (2023)</h4>
                                <p className="text-sm text-muted-foreground mb-3">
                                    Grid carbon intensity factors by country. Provides the basis for calculating regional CO₂ emissions from energy consumption.
                                </p>
                                <div className="flex gap-2">
                                    <Button variant="outline" size="sm" className="text-xs" asChild>
                                        <a href="https://www.iea.org/" target="_blank" rel="noopener noreferrer">
                                            <ExternalLink className="w-3 h-3 mr-2" />
                                            IEA
                                        </a>
                                    </Button>
                                    <Button variant="outline" size="sm" className="text-xs" asChild>
                                        <a href="https://ember-climate.org/" target="_blank" rel="noopener noreferrer">
                                            <ExternalLink className="w-3 h-3 mr-2" />
                                            Ember
                                        </a>
                                    </Button>
                                </div>
                            </div>

                            <div className="border-l-4 border-green-600 pl-4">
                                <h4 className="font-semibold text-foreground mb-2">Cloud Provider Sustainability Reports</h4>
                                <p className="text-sm text-muted-foreground mb-3">
                                    AWS, Google Cloud, and Azure publish annual sustainability reports with PUE (Power Usage Effectiveness) and renewable energy procurement data.
                                </p>
                                <div className="flex gap-2">
                                    <Button variant="outline" size="sm" className="text-xs" asChild>
                                        <a href="https://sustainability.aboutamazon.com/" target="_blank" rel="noopener noreferrer">
                                            <ExternalLink className="w-3 h-3 mr-2" />
                                            AWS
                                        </a>
                                    </Button>
                                    <Button variant="outline" size="sm" className="text-xs" asChild>
                                        <a href="https://cloud.google.com/sustainability" target="_blank" rel="noopener noreferrer">
                                            <ExternalLink className="w-3 h-3 mr-2" />
                                            GCP
                                        </a>
                                    </Button>
                                    <Button variant="outline" size="sm" className="text-xs" asChild>
                                        <a href="https://azure.microsoft.com/en-us/explore/global-infrastructure/sustainability" target="_blank" rel="noopener noreferrer">
                                            <ExternalLink className="w-3 h-3 mr-2" />
                                            Azure
                                        </a>
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Calculation Methodology */}
                    <Card className="p-6 border border-border/50">
                        <h3 className="text-lg font-semibold text-foreground mb-6">Calculation Methodology</h3>
                        <div className="space-y-4 text-sm">
                            <div className="bg-muted/50 p-4 rounded-lg">
                                <p className="font-semibold text-foreground mb-2">Energy Conversion (Canonical)</p>
                                <code className="text-xs bg-background px-2 py-1 rounded">1 J/token = 0.001 kWh / 1k tokens</code>
                            </div>

                            <div className="bg-muted/50 p-4 rounded-lg">
                                <p className="font-semibold text-foreground mb-2">CO₂ Calculation</p>
                                <code className="text-xs bg-background px-2 py-1 rounded">
                                    CO₂ (g/1k tokens) = kWh/1k × grid_intensity (gCO₂/kWh) × PUE
                                </code>
                                <p className="text-xs text-muted-foreground mt-2">Default grid intensity: 400 gCO₂/kWh (US average)</p>
                            </div>

                            <div className="bg-muted/50 p-4 rounded-lg">
                                <p className="font-semibold text-foreground mb-2">Efficiency Score</p>
                                <code className="text-xs bg-background px-2 py-1 rounded">Efficiency = Quality Score / CO₂ Emissions</code>
                                <p className="text-xs text-muted-foreground mt-2">Higher values indicate better quality per unit of carbon emissions</p>
                            </div>
                        </div>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
