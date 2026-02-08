package com.example.eco_compute.proxy

import android.util.Log
import com.example.eco_compute.detector.AIDetector
import com.example.eco_compute.network.AIRequestLog
import com.example.eco_compute.network.ProxyApiClient
import com.example.eco_compute.parser.AIRequestParser
import com.example.eco_compute.parser.AIResponseParser
import com.example.eco_compute.utils.MetricsCalculator
import kotlinx.coroutines.*
import java.io.InputStream
import java.io.OutputStream
import java.net.ServerSocket
import java.net.Socket
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLSocket
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

/**
 * Local SOCKS/HTTP Proxy Server
 * Runs on localhost and intercepts traffic routed through VPN
 */
class LocalProxyServer(
    private val port: Int = 8899,
    private val aiDetector: AIDetector,
    private val userId: String,
    private val deviceName: String
) {
    
    private var serverSocket: ServerSocket? = null
    private var isRunning = false
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    companion object {
        private const val TAG = "LocalProxyServer"
    }
    
    /**
     * Start the proxy server
     */
    fun start() {
        if (isRunning) {
            Log.d(TAG, "Proxy server already running")
            return
        }
        
        scope.launch {
            try {
                serverSocket = ServerSocket(port)
                isRunning = true
                Log.i(TAG, "Proxy server started on port $port")
                
                while (isRunning) {
                    try {
                        val clientSocket = serverSocket?.accept()
                        if (clientSocket != null) {
                            launch {
                                handleClient(clientSocket)
                            }
                        }
                    } catch (e: Exception) {
                        if (isRunning) {
                            Log.e(TAG, "Error accepting client", e)
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error starting proxy server", e)
            }
        }
    }
    
    /**
     * Stop the proxy server
     */
    fun stop() {
        isRunning = false
        try {
            serverSocket?.close()
            serverSocket = null
            scope.cancel()
            Log.i(TAG, "Proxy server stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping proxy server", e)
        }
    }
    
    /**
     * Handle a client connection
     */
    private suspend fun handleClient(clientSocket: Socket) {
        try {
            val clientInput = clientSocket.getInputStream()
            val clientOutput = clientSocket.getOutputStream()
            
            // Read the HTTP CONNECT request
            val requestLine = readLine(clientInput)
            Log.d(TAG, "Request: $requestLine")
            
            if (requestLine.startsWith("CONNECT")) {
                handleHttpsConnect(requestLine, clientInput, clientOutput, clientSocket)
            } else {
                handleHttpRequest(requestLine, clientInput, clientOutput)
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error handling client", e)
        } finally {
            clientSocket.close()
        }
    }
    
    /**
     * Handle HTTPS CONNECT request
     */
    private suspend fun handleHttpsConnect(
        requestLine: String,
        clientInput: InputStream,
        clientOutput: OutputStream,
        clientSocket: Socket
    ) {
        // Parse CONNECT request
        val parts = requestLine.split(" ")
        if (parts.size < 2) return
        
        val hostPort = parts[1]
        val host: String
        val portStr: Int
        
        if (hostPort.contains(":")) {
            val split = hostPort.split(":")
            host = split[0]
            portStr = split[1].toIntOrNull() ?: 443
        } else {
            host = hostPort
            portStr = 443
        }
        
        Log.d(TAG, "HTTPS CONNECT to $host:$portStr")
        
        // Check if this is an AI API
        val isAI = aiDetector.isAIRequest(host, "")
        
        if (isAI) {
            Log.i(TAG, "🤖 AI API detected: $host")
            
            // Read and discard remaining headers
            while (true) {
                val line = readLine(clientInput)
                if (line.isEmpty()) break
            }
            
            // Send 200 Connection Established
            clientOutput.write("HTTP/1.1 200 Connection Established\r\n\r\n".toByteArray())
            clientOutput.flush()
            
            // Perform SNI-based logging (tunneling without decryption)
            tunnelAndLog(host, portStr, clientSocket, clientInput, clientOutput)
        } else {
            // For non-AI traffic, just tunnel through
            tunnelConnection(host, portStr, clientInput, clientOutput)
        }
    }
    
    /**
     * Intercept TLS traffic for AI APIs
     */
    /**
     * Tunnel connection and log metrics (SNI approach)
     */
    private suspend fun tunnelAndLog(
        host: String,
        port: Int,
        clientSocket: Socket,
        clientInput: InputStream,
        clientOutput: OutputStream
    ) {
        val startTime = System.currentTimeMillis()
        var totalBytes = 0L
        
        try {
            // Connect to real server
            val serverSocket = Socket(host, port)
            val serverInput = serverSocket.getInputStream()
            val serverOutput = serverSocket.getOutputStream()
            
            Log.d(TAG, "Tunnel established to $host:$port")
            
            // Relay data bidirectionally and count bytes
            val job1 = scope.launch {
                val bytes = relayAndCount(clientInput, serverOutput)
                totalBytes += bytes
            }
            
            val job2 = scope.launch {
                val bytes = relayAndCount(serverInput, clientOutput)
                totalBytes += bytes
            }
            
            job1.join()
            job2.join()
            
            serverSocket.close()
            
        } catch (e: Exception) {
            Log.e(TAG, "Error tunneling to $host", e)
        } finally {
            val duration = System.currentTimeMillis() - startTime
            if (totalBytes > 0) {
                Log.i(TAG, "Connection closed. Duration: ${duration}ms, Bytes: $totalBytes")
                sendToBackend(host, duration, totalBytes)
            }
        }
    }
    
    /**
     * Relay data and count bytes
     */
    private fun relayAndCount(input: InputStream, output: OutputStream): Long {
        val buffer = ByteArray(8192)
        var total = 0L
        try {
            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break
                output.write(buffer, 0, bytesRead)
                output.flush()
                total += bytesRead
            }
        } catch (e: Exception) {
            // Connection closed
        }
        return total
    }
    
    /**
     * Send intercepted data to backend API
     */
    /**
     * Send SNI-based log to backend
     */
    private suspend fun sendToBackend(
        host: String, 
        durationMs: Long, 
        bytesTransferred: Long
    ) {
        try {
            val provider = aiDetector.detectProvider(host)
            // Estimate tokens based on bytes (very rough approximation: 1 token ~ 4 bytes)
            // This is just a proxy metric since we can't see the content
            val estimatedTokens = (bytesTransferred / 4).toInt()
            
            val modelName = "Encrypted (HTTPS)"
            val region = MetricsCalculator.detectRegion(provider, modelName)
            val energyWh = MetricsCalculator.calculateEnergyWh(modelName, estimatedTokens, durationMs)
            val co2G = MetricsCalculator.calculateCO2G(energyWh)
            
            val requestLog = AIRequestLog(
                userId = userId,
                provider = provider,
                model = modelName,
                prompt = null,
                promptTokens = 0,
                completionTokens = 0,
                totalTokens = estimatedTokens,
                latencyMs = durationMs,
                serverIp = host,
                region = region,
                energyWh = energyWh,
                co2G = co2G,
                timestamp = System.currentTimeMillis(),
                deviceName = deviceName
            )
            
            val response = ProxyApiClient.apiService.logAIRequest(requestLog)
            if (response.isSuccessful) {
                Log.i(TAG, "✅ Sent to backend: $provider ($estimatedTokens est. tokens, ${durationMs}ms)")
            } else {
                Log.e(TAG, "❌ Failed to send to backend: ${response.code()}")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error sending to backend", e)
        }
    }
    
    /**
     * Handle regular HTTP request
     */
    private suspend fun handleHttpRequest(
        requestLine: String,
        clientInput: InputStream,
        clientOutput: OutputStream
    ) {
        // Simple HTTP handling (not implemented for now)
        clientOutput.write("HTTP/1.1 501 Not Implemented\r\n\r\n".toByteArray())
    }
    
    /**
     * Tunnel connection for non-AI traffic
     */
    private suspend fun tunnelConnection(
        host: String,
        port: Int,
        clientInput: InputStream,
        clientOutput: OutputStream
    ) {
        try {
            val serverSocket = Socket(host, port)
            val serverInput = serverSocket.getInputStream()
            val serverOutput = serverSocket.getOutputStream()
            
            // Send 200 Connection Established
            clientOutput.write("HTTP/1.1 200 Connection Established\r\n\r\n".toByteArray())
            clientOutput.flush()
            
            // Relay data bidirectionally
            val job1 = scope.launch {
                relay(clientInput, serverOutput)
            }
            
            val job2 = scope.launch {
                relay(serverInput, clientOutput)
            }
            
            job1.join()
            job2.join()
            
            serverSocket.close()
            
        } catch (e: Exception) {
            Log.e(TAG, "Error tunneling connection", e)
        }
    }
    
    /**
     * Simple relay between streams
     */
    private fun relay(input: InputStream, output: OutputStream) {
        val buffer = ByteArray(8192)
        try {
            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break
                output.write(buffer, 0, bytesRead)
                output.flush()
            }
        } catch (e: Exception) {
            // Connection closed
        }
    }
    
    /**
     * Read a line from input stream
     */
    private fun readLine(input: InputStream): String {
        val line = StringBuilder()
        var prev = 0
        while (true) {
            val b = input.read()
            if (b == -1) break
            if (prev == '\r'.code && b == '\n'.code) {
                line.deleteCharAt(line.length - 1)
                break
            }
            line.append(b.toChar())
            prev = b
        }
        return line.toString()
    }
}
