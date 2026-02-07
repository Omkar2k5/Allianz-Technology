package com.example.eco_compute.proxy

import android.util.Log
import com.example.eco_compute.detector.AIDetector
import com.example.eco_compute.parser.AIRequestParser
import com.example.eco_compute.parser.AIResponseParser
import com.example.eco_compute.repository.AIRequestRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

/**
 * HTTP request data
 */
data class HttpRequest(
    val method: String,
    val url: String,
    val headers: Map<String, String>,
    val body: String
)

/**
 * HTTP response data
 */
data class HttpResponse(
    val statusCode: Int,
    val headers: Map<String, String>,
    val body: String
)

/**
 * HTTP Proxy Handler
 * Forwards HTTP requests and captures responses for AI detection
 */
class HttpProxyHandler(
    private val aiDetector: AIDetector,
    private val repository: AIRequestRepository,
    private val userId: String
) {
    
    companion object {
        private const val TAG = "HttpProxyHandler"
    }
    
    /**
     * Handle an HTTP request
     * @param rawRequest Raw HTTP request bytes
     * @return Raw HTTP response bytes
     */
    suspend fun handleRequest(rawRequest: ByteArray): ByteArray? {
        return withContext(Dispatchers.IO) {
            try {
                // Parse HTTP request
                val request = parseHttpRequest(rawRequest) ?: return@withContext null
                
                // Extract host and path
                val host = request.headers["Host"] ?: return@withContext null
                val path = extractPath(request.url)
                
                // Check if this is an AI API request
                if (aiDetector.isAIRequest(host, path)) {
                    Log.d(TAG, "AI API request detected: $host$path")
                    return@withContext handleAIRequest(request, host, path)
                } else {
                    // Forward non-AI requests
                    return@withContext forwardRequest(request)
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error handling request", e)
                null
            }
        }
    }
    
    /**
     * Handle an AI API request with logging
     */
    private suspend fun handleAIRequest(
        request: HttpRequest,
        host: String,
        path: String
    ): ByteArray? {
        val startTime = System.currentTimeMillis()
        
        // Parse AI request
        val requestData = AIRequestParser.parseAIRequest(request.body)
        
        // Forward request and get response
        val response = forwardHttpRequest(request) ?: return null
        
        val latency = System.currentTimeMillis() - startTime
        
        // Parse AI response
        val responseData = AIResponseParser.parseAIResponse(response.body)
        
        // Log to database if we got token usage
        if (requestData != null && responseData != null) {
            val provider = aiDetector.detectProvider(host)
            
            repository.logAIRequest(
                userId = userId,
                provider = provider,
                model = responseData.model,
                promptTokens = responseData.promptTokens,
                completionTokens = responseData.completionTokens,
                totalTokens = responseData.totalTokens,
                latencyMs = latency,
                serverIp = extractIpFromHost(host)
            )
            
            Log.i(TAG, "Logged AI request: $provider ${responseData.model} (${responseData.totalTokens} tokens)")
        }
        
        // Convert response back to bytes
        return buildHttpResponse(response)
    }
    
    /**
     * Forward a regular (non-AI) request
     */
    private suspend fun forwardRequest(request: HttpRequest): ByteArray? {
        val response = forwardHttpRequest(request) ?: return null
        return buildHttpResponse(response)
    }
    
    /**
     * Forward HTTP request to upstream server
     */
    private suspend fun forwardHttpRequest(request: HttpRequest): HttpResponse? {
        return withContext(Dispatchers.IO) {
            try {
                val url = URL(request.url)
                val connection = url.openConnection() as HttpURLConnection
                
                // Set method
                connection.requestMethod = request.method
                
                // Set headers
                request.headers.forEach { (key, value) ->
                    if (key.lowercase() != "host") { // Skip Host header
                        connection.setRequestProperty(key, value)
                    }
                }
                
                // Send body if present
                if (request.body.isNotEmpty() && request.method in listOf("POST", "PUT", "PATCH")) {
                    connection.doOutput = true
                    OutputStreamWriter(connection.outputStream).use { writer ->
                        writer.write(request.body)
                        writer.flush()
                    }
                }
                
                // Get response
                val statusCode = connection.responseCode
                val responseHeaders = connection.headerFields
                    .filterKeys { it != null }
                    .mapKeys { it.key!! }
                    .mapValues { it.value.joinToString(", ") }
                
                val responseBody = try {
                    BufferedReader(InputStreamReader(connection.inputStream)).use { reader ->
                        reader.readText()
                    }
                } catch (e: Exception) {
                    BufferedReader(InputStreamReader(connection.errorStream)).use { reader ->
                        reader.readText()
                    }
                }
                
                HttpResponse(statusCode, responseHeaders, responseBody)
                
            } catch (e: Exception) {
                Log.e(TAG, "Error forwarding request", e)
                null
            }
        }
    }
    
    /**
     * Parse raw HTTP request bytes
     */
    private fun parseHttpRequest(rawRequest: ByteArray): HttpRequest? {
        try {
            val requestString = String(rawRequest, Charsets.UTF_8)
            val lines = requestString.split("\r\n")
            
            if (lines.isEmpty()) return null
            
            // Parse request line
            val requestLine = lines[0].split(" ")
            if (requestLine.size < 3) return null
            
            val method = requestLine[0]
            val path = requestLine[1]
            
            // Parse headers
            val headers = mutableMapOf<String, String>()
            var bodyStart = 0
            
            for (i in 1 until lines.size) {
                val line = lines[i]
                if (line.isEmpty()) {
                    bodyStart = i + 1
                    break
                }
                
                val colonIndex = line.indexOf(':')
                if (colonIndex > 0) {
                    val key = line.substring(0, colonIndex).trim()
                    val value = line.substring(colonIndex + 1).trim()
                    headers[key] = value
                }
            }
            
            // Extract body
            val body = if (bodyStart < lines.size) {
                lines.subList(bodyStart, lines.size).joinToString("\r\n")
            } else {
                ""
            }
            
            // Build full URL
            val host = headers["Host"] ?: return null
            val scheme = if (headers.containsKey("X-Forwarded-Proto")) {
                headers["X-Forwarded-Proto"]!!
            } else {
                "http" // Default to HTTP for now
            }
            val url = "$scheme://$host$path"
            
            return HttpRequest(method, url, headers, body)
            
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing HTTP request", e)
            return null
        }
    }
    
    /**
     * Build raw HTTP response bytes
     */
    private fun buildHttpResponse(response: HttpResponse): ByteArray {
        val builder = StringBuilder()
        
        // Status line
        builder.append("HTTP/1.1 ${response.statusCode} OK\r\n")
        
        // Headers
        response.headers.forEach { (key, value) ->
            builder.append("$key: $value\r\n")
        }
        
        builder.append("\r\n")
        
        // Body
        builder.append(response.body)
        
        return builder.toString().toByteArray(Charsets.UTF_8)
    }
    
    /**
     * Extract path from URL
     */
    private fun extractPath(url: String): String {
        return try {
            val urlObj = URL(url)
            urlObj.path + (urlObj.query?.let { "?$it" } ?: "")
        } catch (e: Exception) {
            "/"
        }
    }
    
    /**
     * Extract IP from hostname (simplified)
     */
    private fun extractIpFromHost(host: String): String {
        // In a real implementation, perform DNS lookup
        // For now, just return the hostname
        return host
    }
}
