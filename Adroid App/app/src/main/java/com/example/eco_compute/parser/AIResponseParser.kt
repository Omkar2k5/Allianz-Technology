package com.example.eco_compute.parser

import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.util.zip.GZIPInputStream

/**
 * Data class for parsed AI response information
 */
data class AIResponseData(
    val model: String,
    val promptTokens: Int,
    val completionTokens: Int,
    val totalTokens: Int
)

/**
 * Parser for AI API responses
 * Extracts token usage information from various AI provider formats
 */
object AIResponseParser {
    
    /**
     * Parse AI response body to extract token usage
     * @param body The response body as string (JSON or SSE format)
     * @return AIResponseData if successfully parsed, null otherwise
     */
    fun parseAIResponse(body: String): AIResponseData? {
        if (body.isBlank()) return null
        
        // Try standard JSON format first
        val jsonResult = parseStandardJSON(body)
        if (jsonResult != null) return jsonResult
        
        // Try ChatGPT SSE format (Server-Sent Events)
        // The response might be gzip-compressed, try to decompress first
        val decompressed = tryDecompressGzip(body.toByteArray())
        val textToParse = decompressed ?: body
        
        return parseSSEFormat(textToParse)
    }
    
    /**
     * Parse standard JSON response with usage field
     */
    private fun parseStandardJSON(body: String): AIResponseData? {
        return try {
            val json = JSONObject(body)
            
            if (json.has("usage")) {
                val usage = json.getJSONObject("usage")
                val model = json.optString("model", "unknown")
                
                val promptTokens = usage.optInt("prompt_tokens", 0)
                val completionTokens = usage.optInt("completion_tokens", 0)
                val totalTokens = usage.optInt("total_tokens", promptTokens + completionTokens)
                
                AIResponseData(model, promptTokens, completionTokens, totalTokens)
            } else {
                null
            }
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Parse Server-Sent Events (SSE) format
     */
    private fun parseSSEFormat(text: String): AIResponseData? {
        // Split into SSE frames (separated by \r\n\r\n or \n\n)
        val frames = text.split(Regex("\\r?\\n\\r?\\n"))
        
        for (frame in frames) {
            // Extract all data: lines
            val dataLines = frame.lines()
                .filter { it.startsWith("data: ") }
                .map { it.removePrefix("data: ") }
            
            if (dataLines.isEmpty()) continue
            
            val dataJoined = dataLines.joinToString("\n")
            if (dataJoined.trim() == "[DONE]") continue
            
            // Try to parse as JSON
            try {
                val json = JSONObject(dataJoined)
                
                // Look for usage in response.usage or message.usage
                val usage = json.optJSONObject("response")?.optJSONObject("usage")
                    ?: json.optJSONObject("message")?.optJSONObject("usage")
                    ?: json.optJSONObject("usage")
                
                if (usage != null) {
                    val model = json.optJSONObject("response")
                        ?.optJSONObject("message")
                        ?.optJSONObject("metadata")
                        ?.optString("model_slug")
                        ?: json.optString("model", "unknown")
                    
                    val promptTokens = usage.optInt("prompt_tokens", 
                        usage.optInt("input_tokens", 0))
                    val completionTokens = usage.optInt("completion_tokens",
                        usage.optInt("output_tokens", 0))
                    val totalTokens = usage.optInt("total_tokens", 
                        promptTokens + completionTokens)
                    
                    return AIResponseData(model, promptTokens, completionTokens, totalTokens)
                }
            } catch (e: Exception) {
                // Continue to next frame
                continue
            }
        }
        
        return null
    }
    
    /**
     * Try to decompress gzip data
     */
    private fun tryDecompressGzip(data: ByteArray): String? {
        return try {
            val inputStream = GZIPInputStream(ByteArrayInputStream(data))
            val outputStream = ByteArrayOutputStream()
            
            inputStream.copyTo(outputStream)
            outputStream.toString("UTF-8")
        } catch (e: Exception) {
            null
        }
    }
}
