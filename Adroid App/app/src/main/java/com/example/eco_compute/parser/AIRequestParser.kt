package com.example.eco_compute.parser

import org.json.JSONObject
import org.json.JSONArray

/**
 * Data class for parsed AI request information
 */
data class AIRequestData(
    val model: String,
    val prompt: String
)

/**
 * Parser for AI API requests
 * Supports OpenAI, Anthropic, Google Gemini, and other providers
 */
object AIRequestParser {
    
    /**
     * Parse AI request body to extract model and prompt
     * @param body The request body as string (JSON or URL-encoded)
     * @return AIRequestData if successfully parsed, null otherwise
     */
    fun parseAIRequest(body: String): AIRequestData? {
        if (body.isBlank()) return null
        
        // Check if this is a Gemini request (URL-encoded with f.req parameter)
        if (body.startsWith("f.req=")) {
            return parseGeminiRequest(body)
        }
        
        return try {
            val json = JSONObject(body)
            
            // Extract model
            val model = json.optString("model", "unknown")
            
            // Extract prompt from various possible fields
            val prompt = when {
                json.has("messages") -> extractFromMessages(json.getJSONArray("messages"))
                json.has("prompt") -> json.getString("prompt")
                json.has("content") -> json.getString("content")
                else -> ""
            }
            
            AIRequestData(model, prompt)
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Extract prompt text from messages array (ChatGPT format)
     */
    private fun extractFromMessages(messages: JSONArray): String {
        val prompts = mutableListOf<String>()
        
        for (i in 0 until messages.length()) {
            val message = messages.getJSONObject(i)
            val content = message.opt("content")
            
            when (content) {
                is String -> prompts.add(content)
                is JSONObject -> {
                    // Try nested parts array first (ChatGPT web format)
                    if (content.has("parts")) {
                        val parts = content.getJSONArray("parts")
                        for (j in 0 until parts.length()) {
                            val part = parts.optString(j, "")
                            if (part.isNotEmpty()) prompts.add(part)
                        }
                    } else {
                        // Fallback to direct string content
                        prompts.add(content.toString())
                    }
                }
            }
        }
        
        return prompts.joinToString(" ")
    }
    
    /**
     * Parse Gemini URL-encoded request
     */
    private fun parseGeminiRequest(body: String): AIRequestData? {
        return try {
            // URL decode the body
            val decoded = java.net.URLDecoder.decode(body, "UTF-8")
            
            // Extract the prompt - Gemini sends it in the f.req parameter as a nested JSON array
            // Simple heuristic: find text between quotes that looks like a user prompt
            val prompt = decoded
                .split("\\\"")
                .filter { it.length > 10 && !it.startsWith("c_") && !it.startsWith("r_") && !it.startsWith("rc_") }
                .find { !it.contains("google") && !it.contains("en-IN") && !it.contains("Aw") }
                ?: ""
            
            AIRequestData("gemini-pro", prompt)
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Check if a path is an AI completion endpoint
     */
    fun isAICompletionEndpoint(path: String): Boolean {
        // Exclude known auxiliary/list endpoints
        val excludedPaths = listOf(
            "/conversations", "/init", "/stream_status", "/textdocs",
            "/generate_autocompletions", "/prepare", "/finalize",
            "/ces/v1/", "/rgstr", "/lat/r", "/links/list", "/sentinel/",
            "/jserror", "/cspreport", "/batchexecute", "/sentry",
            "/title", "/artifacts", "/wiggle", "/feature_settings",
            "/projects", "/notification", "/sync/"
        )
        
        if (excludedPaths.any { path.contains(it, ignoreCase = true) }) {
            return false
        }
        
        // Only match specific conversation endpoints with actual prompts
        val includedPaths = listOf(
            "/chat/completions", "/completions", "/v1/messages",
            "/backend-api/f/conversation", "/backend-api/conversation/",
            "/api/chat", "/StreamGenerate", "/completion"
        )
        
        return includedPaths.any { path.contains(it, ignoreCase = true) }
    }
}
