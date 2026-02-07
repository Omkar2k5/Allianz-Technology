package com.example.eco_compute.detector

/**
 * AI API request detector
 * Identifies AI service requests by hostname and path patterns
 */
class AIDetector {
    
    private val aiDomains = listOf(
        "api.openai.com",
        "openai.com",
        "chatgpt.com",
        "api.anthropic.com",
        "claude.ai",
        "openrouter.ai",
        "api.cohere.ai",
        "generativelanguage.googleapis.com",
        "gemini.google.com",
        "api.together.xyz",
        "api.perplexity.ai"
    )
    
    private val aiPaths = listOf(
        "/v1/chat/completions",
        "/v1/completions",
        "/v1/embeddings",
        "/v1/messages",
        "/messages",
        "/backend-api",
        "/api/chat",
        "/StreamGenerate",
        "/completion"
    )
    
    /**
     * Check if a request is to an AI API
     * @param host The hostname (e.g., "api.openai.com")
     * @param path The request path (e.g., "/v1/chat/completions")
     * @return true if this is an AI API request
     */
    fun isAIRequest(host: String, path: String = ""): Boolean {
        val isAIDomain = aiDomains.any { domain -> 
            host.contains(domain, ignoreCase = true) 
        }
        
        // If path is empty (CONNECT request), only check domain
        if (path.isEmpty()) {
            return isAIDomain
        }
        
        val isAIPath = aiPaths.any { apiPath -> 
            path.contains(apiPath, ignoreCase = true) 
        }
        
        return isAIDomain && isAIPath
    }
    
    /**
     * Detect the AI provider from hostname
     * @param host The hostname
     * @return Provider name (e.g., "OpenAI", "Anthropic", "Google")
     */
    fun detectProvider(host: String): String {
        return when {
            host.contains("openai.com", ignoreCase = true) || 
            host.contains("chatgpt.com", ignoreCase = true) -> "OpenAI"
            
            host.contains("anthropic.com", ignoreCase = true) || 
            host.contains("claude.ai", ignoreCase = true) -> "Anthropic"
            
            host.contains("google.com", ignoreCase = true) || 
            host.contains("gemini", ignoreCase = true) -> "Google"
            
            host.contains("cohere.ai", ignoreCase = true) -> "Cohere"
            
            host.contains("openrouter.ai", ignoreCase = true) -> "OpenRouter"
            
            host.contains("together.xyz", ignoreCase = true) -> "Together AI"
            
            host.contains("perplexity.ai", ignoreCase = true) -> "Perplexity"
            
            else -> "Unknown"
        }
    }
}
