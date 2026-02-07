package com.example.eco_compute.proxy

import java.nio.ByteBuffer
import java.util.concurrent.ConcurrentHashMap

/**
 * TCP connection identifier
 */
data class TcpConnection(
    val sourceIp: String,
    val sourcePort: Int,
    val destIp: String,
    val destPort: Int
) {
    override fun toString(): String = "$sourceIp:$sourcePort -> $destIp:$destPort"
}

/**
 * TCP stream state for reassembly
 */
data class TcpStream(
    val connection: TcpConnection,
    var sequenceNumber: Long = 0,
    val buffer: MutableList<ByteArray> = mutableListOf(),
    var isHttps: Boolean = false,
    var isComplete: Boolean = false
)

/**
 * TCP Stream Reassembler
 * Reconstructs complete HTTP requests/responses from TCP packets
 */
class TcpStreamReassembler {
    
    private val streams = ConcurrentHashMap<TcpConnection, TcpStream>()
    
    companion object {
        private const val MAX_BUFFER_SIZE = 1024 * 1024 // 1MB max per stream
        private const val STREAM_TIMEOUT_MS = 30000L // 30 seconds
    }
    
    /**
     * Add a TCP packet to the stream
     * @return Complete HTTP message if available, null otherwise
     */
    fun addPacket(
        sourceIp: String,
        sourcePort: Int,
        destIp: String,
        destPort: Int,
        sequenceNumber: Long,
        payload: ByteArray,
        flags: Int
    ): ByteArray? {
        val connection = TcpConnection(sourceIp, sourcePort, destIp, destPort)
        
        // Get or create stream
        val stream = streams.getOrPut(connection) {
            TcpStream(connection, sequenceNumber)
        }
        
        // Check if this is HTTPS (port 443 or TLS handshake)
        if (destPort == 443 || isTlsHandshake(payload)) {
            stream.isHttps = true
        }
        
        // Add payload to buffer
        if (payload.isNotEmpty()) {
            stream.buffer.add(payload)
            
            // Check if we have a complete HTTP message
            val completeMessage = tryExtractHttpMessage(stream)
            if (completeMessage != null) {
                // Clear buffer and return message
                stream.buffer.clear()
                return completeMessage
            }
        }
        
        // Check for FIN flag (connection closing)
        if ((flags and 0x01) != 0) {
            stream.isComplete = true
            val message = stream.buffer.flatMap { it.toList() }.toByteArray()
            streams.remove(connection)
            return if (message.isNotEmpty()) message else null
        }
        
        // Clean up old streams
        cleanupOldStreams()
        
        return null
    }
    
    /**
     * Try to extract a complete HTTP message from the stream buffer
     */
    private fun tryExtractHttpMessage(stream: TcpStream): ByteArray? {
        val combined = stream.buffer.flatMap { it.toList() }.toByteArray()
        
        if (combined.isEmpty()) return null
        
        // Check if this looks like HTTP
        val header = String(combined.take(100).toByteArray(), Charsets.UTF_8)
        if (!header.startsWith("GET") && 
            !header.startsWith("POST") && 
            !header.startsWith("PUT") &&
            !header.startsWith("DELETE") &&
            !header.startsWith("HTTP/")) {
            return null
        }
        
        // Look for end of headers (\r\n\r\n)
        val headerEnd = findHeaderEnd(combined)
        if (headerEnd == -1) return null // Headers not complete yet
        
        // Parse Content-Length if present
        val headers = String(combined.take(headerEnd).toByteArray(), Charsets.UTF_8)
        val contentLength = extractContentLength(headers)
        
        if (contentLength != null) {
            // Check if we have the complete body
            val totalLength = headerEnd + 4 + contentLength
            if (combined.size >= totalLength) {
                return combined.take(totalLength).toByteArray()
            }
        } else {
            // No Content-Length, assume headers only (GET request, etc.)
            return combined.take(headerEnd + 4).toByteArray()
        }
        
        return null
    }
    
    /**
     * Find the end of HTTP headers (\r\n\r\n)
     */
    private fun findHeaderEnd(data: ByteArray): Int {
        for (i in 0 until data.size - 3) {
            if (data[i] == '\r'.code.toByte() &&
                data[i + 1] == '\n'.code.toByte() &&
                data[i + 2] == '\r'.code.toByte() &&
                data[i + 3] == '\n'.code.toByte()) {
                return i
            }
        }
        return -1
    }
    
    /**
     * Extract Content-Length from HTTP headers
     */
    private fun extractContentLength(headers: String): Int? {
        val regex = Regex("Content-Length:\\s*(\\d+)", RegexOption.IGNORE_CASE)
        val match = regex.find(headers)
        return match?.groupValues?.get(1)?.toIntOrNull()
    }
    
    /**
     * Check if payload contains TLS handshake
     */
    private fun isTlsHandshake(payload: ByteArray): Boolean {
        if (payload.size < 3) return false
        
        // TLS handshake starts with 0x16 (handshake), followed by version
        return payload[0] == 0x16.toByte() &&
               (payload[1] == 0x03.toByte()) && // TLS version 1.x
               (payload[2] in 0x00..0x03) // Minor version
    }
    
    /**
     * Clean up streams that haven't been updated recently
     */
    private fun cleanupOldStreams() {
        val now = System.currentTimeMillis()
        // Note: This is simplified - in production, track last update time per stream
        if (streams.size > 1000) {
            streams.clear() // Simple cleanup for now
        }
    }
    
    /**
     * Get stream for a connection
     */
    fun getStream(connection: TcpConnection): TcpStream? {
        return streams[connection]
    }
    
    /**
     * Remove a stream
     */
    fun removeStream(connection: TcpConnection) {
        streams.remove(connection)
    }
}
