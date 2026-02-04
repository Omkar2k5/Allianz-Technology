"""
Metrics calculator
"""

pub struct MetricsCalculator;

impl MetricsCalculator {
    pub fn new() -> Self {
        Self
    }

    pub fn calculate_cost(&self, model: &str, tokens: i32) -> f64 {
        // Cost per 1K tokens
        let cost_per_1k = match model {
            "gpt-4" => 0.03,
            "gpt-3.5-turbo" => 0.002,
            "claude-3-opus" => 0.015,
            "claude-3-sonnet" => 0.003,
            _ => 0.01, // default
        };
        
        (tokens as f64 / 1000.0) * cost_per_1k
    }

    pub fn calculate_energy(&self, model: &str, tokens: i32) -> f64 {
        // Energy in Wh per 1K tokens
        let energy_per_1k = match model {
            "gpt-4" => 0.8,
            "gpt-3.5-turbo" => 0.3,
            "claude-3-opus" => 0.7,
            _ => 0.5,
        };
        
        (tokens as f64 / 1000.0) * energy_per_1k
    }

    pub fn calculate_co2(&self, energy_wh: f64, carbon_intensity: f64) -> f64 {
        // carbon_intensity in kg CO2/kWh
        // energy_wh in Wh
        // Result in grams
        (energy_wh / 1000.0) * carbon_intensity * 1000.0
    }
}

impl Default for MetricsCalculator {
    fn default() -> Self {
        Self::new()
    }
}
