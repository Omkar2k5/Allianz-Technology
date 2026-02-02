/**
 * GreenAI SDK
 * 
 * Drop-in replacement for OpenAI SDK with automatic environmental impact tracking
 * 
 * Usage:
 * ```typescript
 * import { GreenAI } from '@greenai/sdk';
 * 
 * const client = new GreenAI({
 *   apiKey: process.env.OPENAI_API_KEY,
 *   proxyUrl: 'http://localhost:8001',
 *   appId: 'my-app',
 *   useCase: 'customer-support'
 * });
 * 
 * const response = await client.chat.completions.create({
 *   model: 'gpt-4',
 *   messages: [{ role: 'user', content: 'Hello!' }]
 * });
 * ```
 */

import OpenAI from 'openai';
import axios from 'axios';

export interface GreenAIConfig {
  apiKey: string;
  proxyUrl?: string;
  appId?: string;
  useCase?: string;
  riskLevel?: 'low' | 'medium' | 'high';
  region?: string;
}

export interface SustainabilityMetrics {
  energyWh: number;
  co2G: number;
  tokensTotal: number;
  region: string;
}

export class GreenAI {
  private config: GreenAIConfig;
  private client: OpenAI;
  private proxyUrl: string;

  constructor(config: GreenAIConfig) {
    this.config = config;
    this.proxyUrl = config.proxyUrl || 'http://localhost:8001';

    // Create OpenAI client pointing to our proxy
    this.client = new OpenAI({
      apiKey: config.apiKey,
      baseURL: `${this.proxyUrl}/v1`,
    });
  }

  /**
   * Chat completions with automatic sustainability tracking
   */
  get chat() {
    return {
      completions: {
        create: async (params: any) => {
          // Add custom headers for metadata
          const headers: Record<string, string> = {};
          
          if (this.config.appId) {
            headers['x-app-id'] = this.config.appId;
          }
          if (this.config.useCase) {
            headers['x-use-case'] = this.config.useCase;
          }
          if (this.config.riskLevel) {
            headers['x-risk-level'] = this.config.riskLevel;
          }
          if (this.config.region) {
            headers['x-region'] = this.config.region;
          }

          // Make request through proxy
          const response = await axios.post(
            `${this.proxyUrl}/v1/chat/completions`,
            params,
            {
              headers: {
                'Authorization': `Bearer ${this.config.apiKey}`,
                'Content-Type': 'application/json',
                ...headers
              }
            }
          );

          // Extract sustainability metrics from response headers
          const metrics: SustainabilityMetrics = {
            energyWh: parseFloat(response.headers['x-energy-wh'] || '0'),
            co2G: parseFloat(response.headers['x-co2-g'] || '0'),
            tokensTotal: parseInt(response.headers['x-tokens-total'] || '0'),
            region: response.headers['x-region'] || 'unknown'
          };

          // Attach metrics to response
          const result = response.data;
          (result as any)._sustainability = metrics;

          return result;
        }
      }
    };
  }

  /**
   * Get sustainability metrics from last response
   */
  static getSustainabilityMetrics(response: any): SustainabilityMetrics | null {
    return response._sustainability || null;
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<GreenAIConfig>) {
    this.config = { ...this.config, ...config };
  }
}

// Export types
export type { GreenAIConfig, SustainabilityMetrics };

// Default export
export default GreenAI;
