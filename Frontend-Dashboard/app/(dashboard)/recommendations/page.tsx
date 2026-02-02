'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Lightbulb, CheckCircle, AlertCircle, Zap, Wind, Cpu } from 'lucide-react'

const recommendations = [
  {
    id: 1,
    title: 'Switch to Smaller Model',
    description:
      'Your "Large Language Model X" consumes 25% more energy than "EcoGenius-7B" for similar tasks.',
    impact: 'Reduce CO₂ by 20%, save 15% on costs',
    difficulty: 'High',
    status: 'pending',
    icon: Cpu,
    estimated_savings: '250 tons CO₂/year',
  },
  {
    id: 2,
    title: 'Optimize Prompt for Efficiency',
    description:
      'Refine prompts to reduce token usage by an estimated 15% without losing creative quality used 2x more tokens.',
    impact: 'Reduce token usage by 15%, lower emissions',
    difficulty: 'Medium',
    status: 'pending',
    icon: Lightbulb,
    estimated_savings: '180 tons CO₂/year',
  },
  {
    id: 3,
    title: 'Utilize Low-Carbon Region',
    description:
      'Current AI workload in US-East-1 with high carbon intensity. Move to EU-West-3 (powered by renewables) for a potential 40% reduction.',
    impact: 'Reduce CO₂ by 40%',
    difficulty: 'Medium',
    status: 'pending',
    icon: Wind,
    estimated_savings: '320 tons CO₂/year',
  },
  {
    id: 4,
    title: 'Reduce Inference Batch Size',
    description:
      'Optimize batch processing during inference jobs to increase energy consumption and peak demand. Reducing by 10% can flatten energy curves.',
    impact: 'Improve efficiency by 8%, lower peak demand',
    difficulty: 'Low',
    status: 'applied',
    icon: Zap,
    estimated_savings: '100 tons CO₂/year',
  },
]

const optimizationHistory = [
  {
    date: '2023-11-15 10:30 AM',
    action: 'Switched to "Eco-Model-A" for Recommendation Engine',
    impact: '-10% CO₂',
    status: 'Applied',
  },
  {
    date: '2023-11-14 02:15 PM',
    action: 'Optimized "Marketing Campaign" prompt in Image Generation',
    impact: '-5% Energy',
    status: 'Applied',
  },
  {
    date: '2023-11-12 09:00 AM',
    action: 'Moved "Data Analysis" job to EU-Central (low carbon intensity)',
    impact: '-12% CO₂',
    status: 'Applied',
  },
  {
    date: '2023-11-10 04:45 PM',
    action: 'Reduced batch size for "Image Generation" pipeline',
    impact: '+8% CO₂ (pending reversal)',
    status: 'Rolled Back',
  },
]

export default function RecommendationsPage() {
  return (
    <div className="p-6 space-y-6 md:ml-64">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-foreground">Recommendations & Optimization</h2>
        <p className="text-muted-foreground">
          Actionable insights to reduce your AI models' environmental impact and operational costs
        </p>
      </div>

      {/* Savings Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Potential CO₂ Savings</p>
          <p className="text-3xl font-bold text-foreground">750</p>
          <p className="text-xs text-muted-foreground mt-2">tons/year if all recommendations applied</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Cost Savings</p>
          <p className="text-3xl font-bold text-foreground">$24.5K</p>
          <p className="text-xs text-muted-foreground mt-2">annual savings from optimizations</p>
        </Card>

        <Card className="p-6 border border-border/50">
          <p className="text-sm font-medium text-muted-foreground mb-1">Already Applied</p>
          <p className="text-3xl font-bold text-foreground">1</p>
          <p className="text-xs text-muted-foreground mt-2">recommendations (8% CO₂ reduction)</p>
        </Card>
      </div>

      {/* Actionable Recommendations */}
      <div className="space-y-4">
        {recommendations.map((rec) => {
          const Icon = rec.icon
          const isDone = rec.status === 'applied'
          return (
            <Card
              key={rec.id}
              className={`p-6 border ${isDone ? 'border-green-200 bg-green-50/50 dark:border-green-900/30 dark:bg-green-950/20' : 'border-border/50'}`}
            >
              <div className="flex gap-4">
                <div
                  className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isDone
                      ? 'bg-green-100 dark:bg-green-900/30'
                      : 'bg-primary/10'
                  }`}
                >
                  {isDone ? (
                    <CheckCircle className={`w-6 h-6 ${isDone ? 'text-green-600 dark:text-green-400' : 'text-primary'}`} />
                  ) : (
                    <Icon className={`w-6 h-6 ${isDone ? 'text-green-600 dark:text-green-400' : 'text-primary'}`} />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <h3 className="text-lg font-semibold text-foreground">{rec.title}</h3>
                    <Badge
                      className="text-xs"
                      variant={isDone ? 'default' : 'secondary'}
                    >
                      {isDone ? 'Applied' : rec.difficulty}
                    </Badge>
                  </div>

                  <p className="text-sm text-muted-foreground mb-3">{rec.description}</p>

                  <div className="flex flex-wrap gap-4 mb-4 text-sm">
                    <div>
                      <p className="text-xs text-muted-foreground font-medium">Impact</p>
                      <p className="text-foreground font-medium">{rec.impact}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground font-medium">Estimated Savings</p>
                      <p className="text-foreground font-medium">{rec.estimated_savings}</p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    {isDone ? (
                      <Button variant="outline" disabled className="text-xs bg-transparent">
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Applied
                      </Button>
                    ) : (
                      <>
                        <Button className="bg-primary text-primary-foreground hover:bg-primary/90 text-xs">
                          Apply Optimization
                        </Button>
                        <Button variant="outline" className="text-xs bg-transparent">
                          Learn More
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Prompt Optimization Preview */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-4">Prompt Optimization Preview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-3">Original Prompt</p>
            <div className="p-4 bg-muted/50 rounded-lg border border-border text-sm text-foreground font-mono">
              Generate a highly detailed historical essay about the impact of the Industrial Revolution on
              European society from 1750-1900, focusing on social, economic, and technological changes with an
              extensive bibliography.
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-3">Optimized Prompt</p>
            <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-300 dark:border-green-900 text-sm text-foreground font-mono">
              Summarize the Industrial Revolution's socio-economic impact (1750-1900) in 500 words with key sources.
            </div>
          </div>
        </div>
        <p className="text-sm text-muted-foreground mt-4">
          <span className="font-medium text-green-600 dark:text-green-400">Estimated Savings: -29% CO₂, -15% Energy</span>
        </p>
        <Button className="mt-4 bg-primary text-primary-foreground hover:bg-primary/90">
          Apply Optimization
        </Button>
      </Card>

      {/* Green-Mode Automation */}
      <Card className="p-6 border border-border/50">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-foreground">Enable Green-Mode</h3>
            <p className="text-sm text-muted-foreground">Automatically routes workloads to regions with lowest carbon intensity</p>
          </div>
          <Badge className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-900">
            Inactive
          </Badge>
        </div>

        <p className="text-sm text-muted-foreground mb-4">
          Status: <span className="font-medium">Inactive</span> - Automatically routes AI workloads to regions with the lowest carbon intensity, reducing your overall footprint.
        </p>

        <div className="p-4 bg-muted/50 rounded-lg border border-border mb-4 space-y-2 text-sm">
          <p>
            <span className="font-medium text-foreground">Configure Regions:</span>
            <select className="ml-2 px-2 py-1 border border-border rounded bg-card text-foreground">
              <option>Select an override...</option>
            </select>
          </p>
        </div>

        <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
          Configure Regions
        </Button>
      </Card>

      {/* Optimization Action History */}
      <Card className="p-6 border border-border/50">
        <h3 className="text-lg font-semibold text-foreground mb-6">Optimization Action History</h3>
        <div className="space-y-3">
          {optimizationHistory.map((item, idx) => (
            <div
              key={idx}
              className="flex items-start justify-between p-4 border border-border/50 rounded-lg hover:bg-muted/30 transition-colors"
            >
              <div>
                <p className="text-sm font-medium text-foreground">{item.action}</p>
                <p className="text-xs text-muted-foreground mt-1">{item.date}</p>
              </div>
              <div className="text-right">
                <Badge
                  variant={item.status === 'Applied' ? 'default' : 'secondary'}
                  className="text-xs mb-2"
                >
                  {item.status}
                </Badge>
                <p className={`text-sm font-medium ${
                  item.impact.includes('+') 
                    ? 'text-red-600 dark:text-red-400' 
                    : 'text-green-600 dark:text-green-400'
                }`}>
                  {item.impact}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
