'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { API_URL } from '@/config'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Download, BarChart3, FileText, Calendar, Filter } from 'lucide-react'

// Helper function to format numbers
const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
}

const customReportOptions = [
    {
        title: 'Energy Trends',
        type: 'energy',
        description: 'Line Charts',
    },
    {
        title: 'CO₂ by Region',
        type: 'emissions',
        description: 'Bar Charts',
    },
    {
        title: 'Model Efficiency',
        type: 'efficiency',
        description: 'Pie Charts',
    },
    {
        title: 'Usage Breakdown',
        type: 'usage',
        description: 'Area Chart',
    },
]

export default function ReportsPage() {
    const [chartType, setChartType] = useState('energy')
    const [dateRange, setDateRange] = useState('last-30')
    const [generatedReports, setGeneratedReports] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchInitialReports()
    }, [])

    const fetchInitialReports = async () => {
        try {
            const [monthlyRes, quarterlyRes, annualRes] = await Promise.all([
                fetch(`${API_URL}/api/v1/dashboard/overview?days=30`),
                fetch(`${API_URL}/api/v1/dashboard/overview?days=90`),
                fetch(`${API_URL}/api/v1/dashboard/overview?days=365`)
            ])

            const monthlyData = await monthlyRes.json()
            const quarterlyData = await quarterlyRes.json()
            const annualData = await annualRes.json()

            const now = new Date()
            const formatDate = (date: Date) => date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

            const createReportObj = (id: number, title: string, data: any) => ({
                id,
                title,
                date: `Generated ${formatDate(now)}`,
                type: 'Summary Report',
                format: 'PDF',
                size: '2.4 MB',
                highlights: {
                    calls: formatNumber(data.total_calls),
                    energy: `${formatNumber(data.total_energy_wh)} Wh`,
                    emissions: `${(data.total_co2_g / 1000).toFixed(2)} kg`,
                    latency: `${data.avg_latency_ms} ms`,
                    intensity: `${(data.total_co2_g / (data.total_calls || 1)).toFixed(3)} g/call`
                },
                suggestions: data.recommendations || []
            })

            const newReports = [
                createReportObj(1, `Monthly AI Usage Report - ${now.toLocaleString('default', { month: 'long' })}`, monthlyData),
                createReportObj(2, 'Quarterly ESG Report - Last 90 Days', quarterlyData),
                createReportObj(3, 'Annual Sustainability Report - Last 365 Days', annualData),
            ]

            setGeneratedReports(newReports)
        } catch (error) {
            console.error('Failed to fetch report data', error)
            setGeneratedReports([])
        } finally {
            setLoading(false)
        }
    }

    const handleGenerateReport = async () => {
        setLoading(true)
        try {
            // Determine days based on selection
            let days = 30
            if (dateRange === 'last-7') days = 7
            if (dateRange === 'last-30') days = 30
            if (dateRange === 'monthly') days = 30
            if (dateRange === 'quarterly') days = 90
            if (dateRange === 'yearly') days = 365

            // Fetch Overview Data
            const overviewRes = await fetch(`${API_URL}/api/v1/dashboard/overview?days=${days}`)
            const overviewData = await overviewRes.json()

            // Fetch Usage Data (for charts)
            const usageRes = await fetch(`${API_URL}/api/v1/dashboard/usage?days=${days}`)
            const usageData = await usageRes.json()

            console.log('Usage Data Debug:', usageData) // Debug Log mechanism
            // alert(JSON.stringify(usageData)) // Aggressive Debugging

            const now = new Date()
            const newReport = {
                id: Date.now(),
                title: `Custom ${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Report (${days} Days)`,
                date: `Generated ${now.toLocaleDateString()}`,
                type: 'Custom Report',
                format: 'PDF',
                size: '1.2 MB',
                highlights: {
                    calls: formatNumber(overviewData.total_calls),
                    energy: `${formatNumber(overviewData.total_energy_wh)} Wh`,
                    emissions: `${(overviewData.total_co2_g / 1000).toFixed(2)} kg`,
                    latency: `${overviewData.avg_latency_ms} ms`,
                    intensity: `${(overviewData.total_co2_g / (overviewData.total_calls || 1)).toFixed(3)} g/call`
                },
                suggestions: overviewData.recommendations || [],
                usage_trend: usageData.daily_usage || [],
                model_dist: usageData.model_distribution || []
            }

            setGeneratedReports(prev => [newReport, ...prev])
        } catch (err) {
            console.error(err)
            alert("Error fetching data: " + err)
        } finally {
            setLoading(false)
        }
    }

    const handleDownload = (report: any) => {
        const printWindow = window.open('', '_blank')
        if (!printWindow) {
            alert('Please allow popups to generate the report.')
            return
        }

        // --- Helper for formatting Date ---
        const reportDate = new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })

        // --- Recommendation HTML Generator ---
        const suggestionsHtml = report.suggestions && report.suggestions.length > 0
            ? report.suggestions.map((s: any) => `
                <div class="suggestion-item">
                    <div class="suggestion-icon">💡</div>
                    <div class="suggestion-content">
                        <div class="suggestion-title">${s.title}</div>
                        <div class="suggestion-details">
                            Implementation Difficulty: <span class="badge ${s.difficulty?.toLowerCase() || 'medium'}">${s.difficulty || 'Medium'}</span>
                            <span style="margin: 0 10px; color: #ccc;">|</span>
                            Potential Savings: <strong>${s.estimated_savings_co2_g?.toFixed(1)}g CO₂</strong>
                        </div>
                    </div>
                </div>
            `).join('')
            : '<div class="empty-state">No specific sustainability recommendations for this period. Operations are running efficiently.</div>'

        // --- Usage Chart HTML Generator ---
        let usageChartHtml = '<div class="empty-state">No usage data available for this period.</div>';
        if (report.usage_trend && report.usage_trend.length > 0) {
            const maxTokens = Math.max(...report.usage_trend.map((d: any) => d.tokens)) || 1;
            const barsHtml = report.usage_trend.slice(-30).map((d: any) => { // Last 30 days max
                const heightPct = Math.max(5, (d.tokens / maxTokens) * 100);
                const dateObj = new Date(d.date);
                const day = dateObj.getDate();
                const isWeekend = dateObj.getDay() === 0 || dateObj.getDay() === 6;
                const barColor = isWeekend ? '#93c5fd' : '#3b82f6';

                return `
                    <div class="chart-bar-container">
                        <div class="chart-bar" style="height: ${heightPct}%; background: ${barColor};">
                            <span class="tooltip">${formatNumber(d.tokens)}</span>
                        </div>
                        <div class="chart-label">${day}</div>
                    </div>
                `;
            }).join('');

            usageChartHtml = `
                <div class="chart-wrapper">
                    <div class="chart-y-axis">
                        <span>${formatNumber(maxTokens)}</span>
                        <span>${formatNumber(maxTokens / 2)}</span>
                        <span>0</span>
                    </div>
                    <div class="chart-area">
                        ${barsHtml}
                    </div>
                </div>
                <div class="chart-legend">Daily Token Usage (Last 30 Days) • <span style="color:#93c5fd">■</span> Weekend • <span style="color:#3b82f6">■</span> Weekday</div>
            `;
        }

        // --- Model Distribution Generator ---
        let modelTableHtml = '<div class="empty-state">No model data available.</div>';
        if (report.model_dist && report.model_dist.length > 0) {
            // Sort by tokens desc
            const sortedModels = [...report.model_dist].sort((a, b) => b.tokens - a.tokens);

            const rowsHtml = sortedModels.map((m: any) => `
                <tr>
                    <td>
                        <div style="font-weight: 600;">${m.model}</div>
                    </td>
                    <td class="text-right">${formatNumber(m.calls)}</td>
                    <td class="text-right">${formatNumber(m.tokens)}</td>
                    <td class="text-right">${m.avg_latency.toFixed(0)} ms</td>
                    <td class="text-right">${m.energy_wh?.toFixed(2) || '0.00'} Wh</td>
                    <td class="text-right">${m.co2_g?.toFixed(2) || '0.00'} g</td>
                </tr>
            `).join('');

            modelTableHtml = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Model Name</th>
                            <th class="text-right">Calls</th>
                            <th class="text-right">Total Tokens</th>
                            <th class="text-right">Avg Latency</th>
                            <th class="text-right">Energy</th>
                            <th class="text-right">CO₂ Emission</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            `;
        }

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>${report.title}</title>
                    <style>
                        @page { size: A4; margin: 20mm; }
                        body { font-family: 'Inter', system-ui, -apple-system, sans-serif; color: #1e293b; line-height: 1.5; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                        
                        /* Header */
                        .header { border-bottom: 2px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }
                        .logo { font-size: 24px; font-weight: 800; color: #2563eb; letter-spacing: -1px; }
                        .report-title { font-size: 32px; font-weight: 700; margin: 10px 0 0 0; color: #0f172a; }
                        .report-meta { text-align: right; color: #64748b; font-size: 0.9em; }

                        /* Typography */
                        h1 { font-size: 24px; color: #0f172a; margin-bottom: 15px; }
                        h2 { font-size: 18px; color: #334155; margin: 30px 0 15px 0; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
                        
                        /* Metrics Grid */
                        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
                        .metric-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; }
                        .metric-label { font-size: 0.75em; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 5px; }
                        .metric-value { font-size: 1.5em; font-weight: 700; color: #0f172a; }
                        .metric-sub { font-size: 0.8em; color: #16a34a; margin-top: 2px; }

                        /* Charts */
                        .section-card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
                        .chart-wrapper { display: flex; height: 180px; align-items: flex-end; gap: 10px; margin-top: 10px; }
                        .chart-y-axis { display: flex; flex-direction: column; justify-content: space-between; height: 100%; font-size: 0.7em; color: #94a3b8; padding-right: 10px; border-right: 1px solid #e2e8f0; }
                        .chart-area { display: flex; flex: 1; align-items: flex-end; justify-content: space-between; height: 100%; }
                        .chart-bar-container { display: flex; flex-direction: column; align-items: center; width: 100%; }
                        .chart-bar { width: 60%; border-radius: 4px 4px 0 0; min-height: 2px; position: relative; }
                        .chart-label { font-size: 0.7em; color: #64748b; margin-top: 4px; }
                        .chart-legend { text-align: center; font-size: 0.8em; color: #64748b; margin-top: 10px; }

                        /* Tables */
                        .data-table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
                        .data-table th { text-align: left; padding: 12px 8px; border-bottom: 2px solid #e2e8f0; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 0.75em; }
                        .data-table td { padding: 12px 8px; border-bottom: 1px solid #f1f5f9; color: #334155; }
                        .data-table tr:last-child td { border-bottom: none; }
                        .text-right { text-align: right; }

                        /* Recommendations */
                        .suggestion-item { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 15px; margin-bottom: 10px; display: flex; gap: 15px; }
                        .suggestion-icon { font-size: 24px; }
                        .suggestion-title { font-weight: 600; color: #166534; margin-bottom: 4px; }
                        .suggestion-details { font-size: 0.85em; color: #15803d; }
                        .badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 0.8em; font-weight: 600; text-transform: uppercase; }
                        .badge.easy { background: #dcfce7; color: #166534; }
                        .badge.medium { background: #fef9c3; color: #854d0e; }
                        .badge.hard { background: #fee2e2; color: #991b1b; }

                        .empty-state { padding: 30px; text-align: center; color: #94a3b8; font-style: italic; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1; }

                        /* Footer */
                        .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; font-size: 0.8em; color: #94a3b8; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <div>
                            <div class="logo">EcoCompute</div>
                            <h1 class="report-title">${report.title}</h1>
                        </div>
                        <div class="report-meta">
                            Generated on: ${reportDate}<br>
                            Period: ${report.type === 'Custom Report' ? 'Custom Range' : 'Standard Period'}<br>
                            Report ID: #${report.id.toString().slice(-6)}
                        </div>
                    </div>

                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">Total AI Calls</div>
                            <div class="metric-value">${report.highlights.calls}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Total Energy</div>
                            <div class="metric-value">${report.highlights.energy}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">CO₂ Emissions</div>
                            <div class="metric-value" style="color: #ef4444;">${report.highlights.emissions}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Avg Latency</div>
                            <div class="metric-value">${report.highlights.latency}</div>
                        </div>
                    </div>

                    <h2>📈 Operational Analysis</h2>
                    <div class="section-card">
                        <h3 style="margin: 0 0 15px 0; font-size: 16px;">Daily Token Usage Trend</h3>
                        ${usageChartHtml}
                    </div>

                    <h2>📊 Model Distribution</h2>
                    <div class="section-card">
                        ${modelTableHtml}
                    </div>

                    <h2>🌱 Sustainability & Optimization</h2>
                    <div style="margin-bottom: 10px;">Recommended Actions:</div>
                    ${suggestionsHtml}

                    <div class="footer">
                        <div>Confidential & Proprietary • Internal Use Only</div>
                        <div>Powered by EcoCompute Analytics Engine</div>
                    </div>

                    <script>
                        window.onload = function() { 
                            // Auto-print after slight delay to ensure rendering
                            setTimeout(function() { window.print(); }, 800); 
                        }
                    </script>
                </body>
            </html>
        `)
        printWindow.document.close()
    }

    return (
        <div className="p-6 space-y-6 md:ml-64">
            {/* Header */}
            <div className="flex flex-col gap-2">
                <h2 className="text-3xl font-bold text-foreground">Reports & ESG</h2>
                <p className="text-muted-foreground">
                    Generate and manage custom environmental reports and ESG metrics for your AI operations
                </p>
            </div>

            {/* Report Builder */}
            <Card className="p-6 border border-border/50">
                <h3 className="text-lg font-semibold text-foreground mb-6 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Report Builder
                </h3>
                <p className="text-sm text-muted-foreground mb-6">Configure and generate custom environmental reports.</p>

                <div className="space-y-6">
                    {/* Report Type Selection */}
                    <div>
                        <label className="text-sm font-medium text-foreground block mb-3">Select Category</label>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                            {customReportOptions.map((option) => (
                                <button
                                    key={option.type}
                                    onClick={() => setChartType(option.type)}
                                    className={`p-3 rounded-lg border-2 transition-colors text-left ${chartType === option.type
                                        ? 'border-primary bg-primary/5'
                                        : 'border-border hover:border-primary/50'
                                        }`}
                                >
                                    <p className="text-sm font-medium text-foreground">{option.title}</p>
                                    <p className="text-xs text-muted-foreground">Detailed Analysis</p>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Date Range */}
                    <div>
                        <label className="text-sm font-medium text-foreground block mb-3">Date Range</label>
                        <div className="flex gap-3">
                            <Select value={dateRange} onValueChange={setDateRange}>
                                <SelectTrigger className="w-full">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="last-7">Last 7 Days</SelectItem>
                                    <SelectItem value="last-30">Last 30 Days</SelectItem>
                                    <SelectItem value="monthly">This Month</SelectItem>
                                    <SelectItem value="quarterly">This Quarter</SelectItem>
                                    <SelectItem value="yearly">This Year</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Generate Button */}
                    <Button
                        className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10"
                        onClick={handleGenerateReport}
                        disabled={loading}
                    >
                        {loading ? 'Generating...' : (
                            <>
                                <Download className="w-4 h-4 mr-2" />
                                Generate Report
                            </>
                        )}
                    </Button>
                </div>
            </Card>

            {/* Generated Reports */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-foreground">Generated Reports</h3>
                    <Button variant="outline" size="sm">
                        <Filter className="w-4 h-4 mr-2" />
                        Filter
                    </Button>
                </div>

                <div className="space-y-3">
                    {generatedReports.map((report) => (
                        <Card key={report.id} className="p-6 border border-border/50 hover:border-primary/50 transition-colors">
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <FileText className="w-5 h-5 text-primary" />
                                        <h4 className="text-base font-semibold text-foreground">{report.title}</h4>
                                        <Badge className="text-xs" variant="secondary">
                                            {report.type}
                                        </Badge>
                                    </div>

                                    <p className="text-sm text-muted-foreground mb-4">{report.date}</p>

                                    {/* Report Highlights */}
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                                        <div>
                                            <p className="text-xs text-muted-foreground font-medium mb-1">Total Calls</p>
                                            <p className="text-sm font-bold text-foreground">{report.highlights.calls}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-muted-foreground font-medium mb-1">Energy</p>
                                            <p className="text-sm font-bold text-foreground">{report.highlights.energy}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-muted-foreground font-medium mb-1">CO₂ Emissions</p>
                                            <p className="text-sm font-bold text-foreground">{report.highlights.emissions}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-muted-foreground font-medium mb-1">Avg. Latency</p>
                                            <p className="text-sm font-bold text-foreground">{report.highlights.latency}</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="text-right flex-shrink-0">
                                    <Badge variant="outline" className="text-xs mb-3 block">
                                        {report.format} • {report.size}
                                    </Badge>
                                    <Button
                                        className="bg-primary text-primary-foreground hover:bg-primary/90 text-xs"
                                        onClick={() => handleDownload(report)}
                                    >
                                        <Download className="w-3 h-3 mr-1" />
                                        Download
                                    </Button>
                                </div>
                            </div>
                        </Card>
                    ))}
                    {generatedReports.length === 0 && !loading && (
                        <div className="text-center py-8 text-muted-foreground border dashed rounded-lg">
                            No reports generated yet.
                        </div>
                    )}
                </div>
            </div>

            {/* ESG Framework */}
            <Card className="p-6 border border-border/50">
                <h3 className="text-lg font-semibold text-foreground mb-4">ESG Framework</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <p className="text-sm font-semibold text-foreground mb-2">Environmental</p>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li>• CO₂ Emissions Tracking</li>
                            <li>• Energy Consumption Monitoring</li>
                            <li>• Carbon Neutrality Goals</li>
                            <li>• Renewable Energy Usage %</li>
                        </ul>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-foreground mb-2">Social</p>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li>• Team Training Programs</li>
                            <li>• Sustainability Awareness</li>
                            <li>• Community Engagement</li>
                            <li>• Data Privacy & Security</li>
                        </ul>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-foreground mb-2">Governance</p>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li>• Compliance Reporting</li>
                            <li>• Policy Framework</li>
                            <li>• Risk Management</li>
                            <li>• Audit & Transparency</li>
                        </ul>
                    </div>
                </div>
            </Card>
        </div>
    )
}
