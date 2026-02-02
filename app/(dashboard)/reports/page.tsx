'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Download, BarChart3, FileText, Calendar, Filter } from 'lucide-react'

const reports = [
  {
    id: 1,
    title: 'Monthly AI Usage & Impact Report - November 2024',
    date: 'Generated Nov 30, 2024',
    type: 'Monthly Summary',
    format: 'PDF',
    size: '2.4 MB',
    highlights: {
      calls: '2.5M',
      energy: '15,300 Wh',
      emissions: '7.8 tons',
      efficiency: '88%',
    },
  },
  {
    id: 2,
    title: 'Quarterly ESG Report - Q3 2024',
    date: 'Generated Oct 15, 2024',
    type: 'Quarterly ESG',
    format: 'PDF',
    size: '5.2 MB',
    highlights: {
      calls: '7.2M',
      energy: '45,900 Wh',
      emissions: '22.4 tons',
      efficiency: '86%',
    },
  },
  {
    id: 3,
    title: 'Annual Sustainability Report - 2023',
    date: 'Generated Jan 5, 2024',
    type: 'Annual Report',
    format: 'PDF',
    size: '8.7 MB',
    highlights: {
      calls: '28.5M',
      energy: '189,000 Wh',
      emissions: '94.5 tons',
      efficiency: '84%',
    },
  },
]

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

const graphThumbnails = [
  {
    title: 'Energy Trends',
    type: 'Line Charts',
    icon: '📈',
  },
  {
    title: 'CO₂ by Region',
    type: 'Bar Charts',
    icon: '📊',
  },
  {
    title: 'Model Efficiency',
    type: 'Pie Charts',
    icon: '🥧',
  },
  {
    title: 'Usage Breakdown',
    type: 'Area Chart',
    icon: '📐',
  },
  {
    title: 'Emissions Timeline',
    type: 'Timeline',
    icon: '⏱️',
  },
  {
    title: 'Cost Savings',
    type: 'Gauge Chart',
    icon: '📉',
  },
]

export default function ReportsPage() {
  const [chartType, setChartType] = useState('energy')
  const [dateRange, setDateRange] = useState('monthly')

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
            <label className="text-sm font-medium text-foreground block mb-3">Select Chart Type</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {customReportOptions.map((option) => (
                <button
                  key={option.type}
                  onClick={() => setChartType(option.type)}
                  className={`p-3 rounded-lg border-2 transition-colors text-left ${
                    chartType === option.type
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <p className="text-sm font-medium text-foreground">{option.title}</p>
                  <p className="text-xs text-muted-foreground">{option.description}</p>
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
                  <SelectItem value="custom">Custom Range</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Custom Date if Selected */}
          {dateRange === 'custom' && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-foreground block mb-2">From</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-border rounded-lg bg-card text-foreground text-sm"
                  defaultValue="2024-11-01"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground block mb-2">To</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-border rounded-lg bg-card text-foreground text-sm"
                  defaultValue="2024-11-30"
                />
              </div>
            </div>
          )}

          {/* Generate Button */}
          <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10">
            <Download className="w-4 h-4 mr-2" />
            Generate Report
          </Button>
        </div>
      </Card>

      {/* Graph Thumbnails */}
      <div>
        <h3 className="text-lg font-semibold text-foreground mb-4">Graph Thumbnails for Reports</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Select and include these visuals in your custom reports.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {graphThumbnails.map((graph, idx) => (
            <Card key={idx} className="p-6 border border-border/50 hover:border-primary/50 transition-colors cursor-pointer">
              <div className="text-center">
                <div className="text-4xl mb-3">{graph.icon}</div>
                <p className="text-sm font-medium text-foreground">{graph.title}</p>
                <p className="text-xs text-muted-foreground mt-1">{graph.type}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>

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
          {reports.map((report) => (
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
                      <p className="text-xs text-muted-foreground font-medium mb-1">Avg. Efficiency</p>
                      <p className="text-sm font-bold text-foreground">{report.highlights.efficiency}</p>
                    </div>
                  </div>
                </div>

                <div className="text-right flex-shrink-0">
                  <Badge variant="outline" className="text-xs mb-3 block">
                    {report.format} • {report.size}
                  </Badge>
                  <Button className="bg-primary text-primary-foreground hover:bg-primary/90 text-xs">
                    <Download className="w-3 h-3 mr-1" />
                    Download
                  </Button>
                </div>
              </div>
            </Card>
          ))}
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
