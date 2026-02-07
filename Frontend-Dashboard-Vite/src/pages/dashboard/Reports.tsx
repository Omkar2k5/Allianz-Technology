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
        if (printWindow) {
            const suggestionsHtml = report.suggestions && report.suggestions.length > 0
                ? report.suggestions.map((s: any) => `
                    <div class="suggestion-item">
                        <div class="suggestion-title"><strong>${s.title}</strong></div>
                        <div class="suggestion-details">
                            Potential Savings: ${s.estimated_savings_co2_g?.toFixed(2)}g CO₂
                        </div>
                    </div>
                `).join('')
                : '<p>No specific sustainability recommendations for this period.</p>'

            // Generate Usage Trend Chart HTML (CSS Bar Chart)
            let usageChartHtml = '<p>No usage data available.</p>';
            if (report.usage_trend && report.usage_trend.length > 0) {
                const maxTokens = Math.max(...report.usage_trend.map((d: any) => d.tokens)) || 1;
                const barsHtml = report.usage_trend.slice(-15).map((d: any) => { // Last 15 days
                    const heightPct = Math.max(5, (d.tokens / maxTokens) * 100);
                    return `
                        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 5px;">
                            <div style="width: 100%; height: ${heightPct}%; background: #3b82f6; border-radius: 4px 4px 0 0; min-height: 2px;"></div>
                            <div style="font-size: 0.7em; color: #666; transform: rotate(-45deg); height: 20px; text-align: right; width: 100%; overflow: visible; white-space: nowrap;">${new Date(d.date).getDate()}</div>
                        </div>
                    `;
                }).join('');

                usageChartHtml = `
                    <div style="height: 150px; display: flex; align-items: flex-end; gap: 4px; padding-bottom: 30px; border-bottom: 1px solid #ddd;">
                        ${barsHtml}
                    </div>
                    <div style="text-align: center; font-size: 0.8em; color: #666; margin-top: 5px;">Token Usage (Last 15 Days)</div>
                `;
            }

            // Generate Model Distribution Table
            let modelTableHtml = '<p>No model data available.</p>';
            if (report.model_dist && report.model_dist.length > 0) {
                const rowsHtml = report.model_dist.map((m: any) => `
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">${m.model}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">${formatNumber(m.calls)}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">${formatNumber(m.tokens)}</td>
                         <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">${m.avg_latency.toFixed(0)} ms</td>
                    </tr>
                `).join('');

                modelTableHtml = `
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Model</th>
                                <th style="padding: 8px; text-align: right; border-bottom: 2px solid #ddd;">Calls</th>
                                <th style="padding: 8px; text-align: right; border-bottom: 2px solid #ddd;">Tokens</th>
                                <th style="padding: 8px; text-align: right; border-bottom: 2px solid #ddd;">Avg Latency</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>
                `;
            }

            printWindow.document.write(`
                <html>
                    <head>
                        <title>${report.title}</title>
                        <style>
                            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #333; line-height: 1.6; }
                            h1 { color: #1a1a1a; border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; }
                            h2 { color: #2c2c2c; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
                            .meta { color: #666; margin-bottom: 40px; background: #f8f9fa; padding: 15px; border-radius: 8px; }
                            .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }
                            .card { border: 1px solid #e5e7eb; padding: 25px; border-radius: 10px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
                            .full-width { grid-column: span 2; }
                            .label { font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; color: #6b7280; margin-bottom: 5px; }
                            .value { font-size: 1.8em; font-weight: 600; color: #111827; }
                            .suggestions { margin-top: 20px; }
                            .suggestion-item { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
                            .suggestion-title { color: #166534; margin-bottom: 5px; }
                            .suggestion-details { font-size: 0.9em; color: #15803d; }
                            .footer { margin-top: 60px; font-size: 0.85em; color: #9ca3af; text-align: center; border-top: 1px solid #f3f4f6; padding-top: 20px; }
                            
                            /* Visual Charts */
                            .chart-container { margin-top: 20px; }
                            .bar-chart { display: flex; align-items: center; margin-bottom: 10px; }
                            .bar-label { width: 150px; font-size: 0.9em; color: #444; }
                            .bar-track { flex-grow: 1; background: #eee; height: 20px; border-radius: 10px; overflow: hidden; }
                            .bar-fill { height: 100%; background: #3b82f6; width: 0%; transition: width 0.5s; }
                            .bar-value { margin-left: 10px; font-size: 0.9em; width: 50px; font-weight: bold; }
                            
                            .pie-chart-simple { 
                                width: 100px; height: 100px; border-radius: 50%; 
                                background: conic-gradient(#3b82f6 0% 70%, #eee 70% 100%); 
                                margin: 0 auto 10px; 
                            }

                            @media print {
                                body { padding: 20px; }
                                .card { break-inside: avoid; }
                                .bar-fill { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                            }
                        </style>
                    </head>
                    <body>
                        <h1>${report.title}</h1>
                        <div class="meta">
                            <p><strong>Generated on:</strong> ${report.date}</p>
                            <p><strong>Report Type:</strong> ${report.type}</p>
                            <p><strong>Format:</strong> PDF / Print</p>
                        </div>
                        
                        <h2>Operational Metrics</h2>
                        <div class="grid">
                            <div class="card">
                                <div class="label">Total AI Calls</div>
                                <div class="value">${report.highlights.calls}</div>
                                <div class="chart-container">
                                    <div class="bar-chart">
                                        <div class="bar-track"><div class="bar-fill" style="width: 85%; background: #2563eb;"></div></div>
                                    </div>
                                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">Vs. Previous Period</div>
                                </div>
                            </div>
                            <div class="card">
                                <div class="label">Total Energy Consumption</div>
                                <div class="value">${report.highlights.energy}</div>
                                 <div class="chart-container">
                                    <div class="bar-chart">
                                        <div class="bar-track"><div class="bar-fill" style="width: 65%; background: #f59e0b;"></div></div>
                                    </div>
                                     <div style="font-size: 0.8em; color: #666; margin-top: 5px;">Efficiency Rating: Good</div>
                                </div>
                            </div>
                            <div class="card">
                                <div class="label">Avg. Latency</div>
                                <div class="value">${report.highlights.latency}</div>
                            </div>
                            <div class="card">
                                <div class="label">Carbon Intensity</div>
                                <div class="value">${report.highlights.intensity}</div>
                            </div>
                        </div>
                        
                        <!-- NEW SECTION: Usage Trends -->
                        <h2>Usage & Distribution</h2>
                        <div class="grid">
                            <div class="card full-width">
                                <div class="label">Token Usage Over Time (Last 15 Days)</div>
                                ${usageChartHtml}
                            </div>
                            <div class="card full-width">
                                <div class="label">Model Distribution</div>
                                <div style="margin-top: 15px;">
                                    ${modelTableHtml}
                                </div>
                            </div>
                        </div>

                        <h2>Environmental Impact</h2>
                        <div class="grid">
                             <div class="card" style="border-left: 5px solid #ef4444;">
                                <div class="label">Total CO₂ Emissions</div>
                                <div class="value">${report.highlights.emissions}</div>
                                <div class="chart-container">
                                     <div class="bar-label" style="width: 100%; margin-bottom: 5px;">Emissions Breakdown</div>
                                     <div class="bar-chart">
                                        <div class="bar-label" style="width: 80px;">Scope 1</div>
                                        <div class="bar-track"><div class="bar-fill" style="width: 20%; background: #ef4444;"></div></div>
                                        <div class="bar-value">20%</div>
                                    </div>
                                    <div class="bar-chart">
                                        <div class="bar-label" style="width: 80px;">Scope 2</div>
                                        <div class="bar-track"><div class="bar-fill" style="width: 45%; background: #ef4444;"></div></div>
                                        <div class="bar-value">45%</div>
                                    </div>
                                    <div class="bar-chart">
                                        <div class="bar-label" style="width: 80px;">Scope 3</div>
                                        <div class="bar-track"><div class="bar-fill" style="width: 35%; background: #ef4444;"></div></div>
                                        <div class="bar-value">35%</div>
                                    </div>
                                </div>
                            </div>
                            <div class="card">
                                <div class="label">Sustainability Score</div>
                                <div class="value">88/100</div>
                                <div style="display: flex; align-items: center; margin-top: 15px;">
                                    <div class="pie-chart-simple" style="width: 60px; height: 60px; margin: 0 15px 0 0;"></div>
                                    <div style="font-size: 0.9em; color: #666;">Top 15% of industry peers</div>
                                </div>
                            </div>
                        </div>

                        <h2>ESG Recommendations</h2>
                        <div class="suggestions">
                            ${suggestionsHtml}
                        </div>

                        <div class="footer">
                            Generated by EcoCompute Analytics Dashboard • Confidenital
                        </div>
                        <script>
                            window.onload = function() { setTimeout(function() { window.print(); }, 500); }
                        </script>
                    </body>
                </html>
            `)
            printWindow.document.close()
        }
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
