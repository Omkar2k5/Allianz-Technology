# GreenAI SDK

TypeScript/JavaScript SDK for environmental impact tracking of GenAI applications.

## Installation

```bash
npm install @greenai/sdk
```

## Quick Start

### Basic Usage

```typescript
import { GreenAI } from '@greenai/sdk';

const client = new GreenAI({
  apiKey: process.env.OPENAI_API_KEY,
  proxyUrl: 'http://localhost:8001',
  appId: 'my-app',
  useCase: 'customer-support'
});

const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello, how can I help?' }]
});

// Access sustainability metrics
const metrics = GreenAI.getSustainabilityMetrics(response);
console.log(`Energy: ${metrics.energyWh} Wh`);
console.log(`CO2: ${metrics.co2G} g`);
console.log(`Tokens: ${metrics.tokensTotal}`);
```

### Drop-in Replacement

Replace your existing OpenAI import:

```typescript
// Before
import OpenAI from 'openai';
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// After
import { GreenAI } from '@greenai/sdk';
const client = new GreenAI({
  apiKey: process.env.OPENAI_API_KEY,
  proxyUrl: 'http://localhost:8001',
  appId: 'my-app'
});
```

## Configuration

### GreenAIConfig

```typescript
interface GreenAIConfig {
  apiKey: string;              // OpenAI API key (required)
  proxyUrl?: string;           // Proxy URL (default: http://localhost:8001)
  appId?: string;              // Your application ID
  useCase?: string;            // Use case (e.g., 'customer-support', 'content-generation')
  riskLevel?: 'low' | 'medium' | 'high';  // Risk level for policy enforcement
  region?: string;             // Cloud region (e.g., 'us-east-1')
}
```

### Update Configuration

```typescript
client.updateConfig({
  useCase: 'code-generation',
  riskLevel: 'high'
});
```

## Sustainability Metrics

Every response includes sustainability metrics:

```typescript
interface SustainabilityMetrics {
  energyWh: number;      // Energy consumption in Watt-hours
  co2G: number;          // CO2 emissions in grams
  tokensTotal: number;   // Total tokens used
  region: string;        // Cloud region
}
```

Access metrics:

```typescript
const metrics = GreenAI.getSustainabilityMetrics(response);
```

## Policy Enforcement

The proxy can enforce policies based on your configuration:

- **Model Restrictions**: Block expensive models for low-priority use cases
- **Auto-Downgrade**: Automatically downgrade to more efficient models
- **Carbon Limits**: Enforce CO2 emission thresholds

Example policy violation response:

```json
{
  "error": "Policy violation",
  "message": "GPT-4 usage restricted for low-priority requests",
  "policy": "Low Priority GPT-4 Restriction"
}
```

## Examples

### Customer Support Chatbot

```typescript
const client = new GreenAI({
  apiKey: process.env.OPENAI_API_KEY,
  proxyUrl: 'http://localhost:8001',
  appId: 'customer-support-bot',
  useCase: 'customer-support',
  riskLevel: 'medium'
});

const response = await client.chat.completions.create({
  model: 'gpt-3.5-turbo',
  messages: [
    { role: 'system', content: 'You are a helpful customer support agent.' },
    { role: 'user', content: 'How do I reset my password?' }
  ]
});
```

### Content Generation

```typescript
const client = new GreenAI({
  apiKey: process.env.OPENAI_API_KEY,
  proxyUrl: 'http://localhost:8001',
  appId: 'content-generator',
  useCase: 'content-generation',
  riskLevel: 'low',
  region: 'eu-west-3'  // Low-carbon region
});

const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [
    { role: 'user', content: 'Write a blog post about sustainability' }
  ]
});
```

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Test
npm test
```

## License

MIT
