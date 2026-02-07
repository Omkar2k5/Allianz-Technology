package com.example.eco_compute.utils

/**
 * Metrics calculator for AI requests
 * Calculates energy consumption and CO2 emissions
 */
object MetricsCalculator {
    
    // Datacenter parameters (realistic)
    private const val NODE_POWER_W = 1200.0  // GPU + CPU + memory
    private const val BATCH_SIZE = 8.0        // Concurrent requests
    private const val PUE = 1.3               // Datacenter overhead (cooling, etc.)
    
    // India grid carbon intensity: 750 g CO2/kWh (conservative estimate)
    private const val CARBON_INTENSITY_G_PER_KWH = 750.0
    
    /**
     * Calculate energy consumption in Wh using physics-based formula
     * Formula: Energy (Wh) = (Node_Power_W / Batch_size) × Latency_ms × PUE / 3,600,000
     * 
     * @param model The AI model name (for future model-specific calculations)
     * @param totalTokens Total tokens processed
     * @param latencyMs Request latency in milliseconds
     * @return Energy consumption in Watt-hours (Wh)
     */
    fun calculateEnergyWh(model: String, totalTokens: Int, latencyMs: Long): Double {
        // Physics-based formula: Energy = Power × Time
        val effectivePowerW = NODE_POWER_W / BATCH_SIZE
        val latencyHours = latencyMs / 3_600_000.0
        
        return effectivePowerW * latencyHours * PUE
    }
    
    /**
     * Calculate CO2 emissions in grams based on energy consumption
     * 
     * @param energyWh Energy consumption in Watt-hours
     * @param carbonIntensity Optional carbon intensity (g CO2/kWh), defaults to India grid
     * @return CO2 emissions in grams
     */
    fun calculateCO2G(energyWh: Double, carbonIntensity: Double? = null): Double {
        val intensity = carbonIntensity ?: CARBON_INTENSITY_G_PER_KWH
        // Convert Wh to kWh and multiply by carbon intensity
        return (energyWh / 1000.0) * intensity
    }
    
    /**
     * Detect region/datacenter from provider and model
     * This helps track carbon intensity by geographic location
     * 
     * @param provider The AI provider (e.g., "OpenAI", "Anthropic", "Google")
     * @param model The model name
     * @return Detected region string
     */
    fun detectRegion(provider: String, model: String): String {
        val providerLower = provider.lowercase()
        val modelLower = model.lowercase()
        
        return when {
            providerLower.contains("openai") || providerLower.contains("chatgpt") -> {
                // OpenAI primarily uses US datacenters
                "US-East (Virginia)"
            }
            providerLower.contains("anthropic") || providerLower.contains("claude") -> {
                // Anthropic uses AWS, primarily US regions
                "US-West (Oregon)"
            }
            providerLower.contains("google") || providerLower.contains("gemini") -> {
                // Google Cloud - detect from model or default to US
                when {
                    modelLower.contains("asia") -> "Asia-Pacific (Singapore)"
                    modelLower.contains("europe") -> "Europe (Frankfurt)"
                    else -> "US-Central (Iowa)"
                }
            }
            else -> {
                // Fallback based on model name if provider is generic
                when {
                    modelLower.contains("gpt") -> "US-East (Virginia)"
                    modelLower.contains("claude") -> "US-West (Oregon)"
                    modelLower.contains("gemini") -> "US-Central (Iowa)"
                    else -> "Unknown"
                }
            }
        }
    }
}
