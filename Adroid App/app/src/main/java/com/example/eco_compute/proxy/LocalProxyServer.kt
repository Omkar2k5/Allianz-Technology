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
            
            // Now intercept the TLS traffic
            interceptTlsTraffic(host, portStr, clientSocket, clientInput, clientOutput)
        } else {
            // For non-AI traffic, just tunnel through
            tunnelConnection(host, portStr, clientInput, clientOutput)
        }
    }
    
    /**
     * Intercept TLS traffic for AI APIs
     */
    private suspend fun interceptTlsTraffic(
        host: String,
        port: Int,
        clientSocket: Socket,
        clientInput: InputStream,
        clientOutput: OutputStream
    ) {
        try {
            // Create a trust-all SSL context (for interception)
            val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
                override fun checkClientTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {}
                override fun checkServerTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {}
                override fun getAcceptedIssuers(): Array<java.security.cert.X509Certificate> = arrayOf()
            })
            
            val sslContext = SSLContext.getInstance("TLS")
            sslContext.init(null, trustAllCerts, java.security.SecureRandom())
            
            // Connect to the real server
            val serverSocket = sslContext.socketFactory.createSocket(host, port) as SSLSocket
            val serverInput = serverSocket.getInputStream()
            val serverOutput = serverSocket.getOutputStream()
            
            Log.d(TAG, "TLS connection established to $host:$port")
            
            // Create coroutines to relay data and inspect it
            val job1 = scope.launch {
                relayAndInspect(clientInput, serverOutput, host, true) // Client → Server (requests)
            }
            
            val job2 = scope.launch {
                relayAndInspect(serverInput, clientOutput, host, false) // Server → Client (responses)
            }
            
            // Wait for both to complete
            job1.join()
            job2.join()
            
            serverSocket.close()
            
        } catch (e: Exception) {
            Log.e(TAG, "Error intercepting TLS traffic", e)
        }
    }
    
    /**
     * Relay data between streams and inspect for AI content
     */
    private suspend fun relayAndInspect(
        input: InputStream,
        output: OutputStream,
        host: String,
        isRequest: Boolean
    ) {
        val buffer = ByteArray(8192)
        val dataBuffer = mutableListOf<Byte>()
        
        try {
            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break
                
                // Forward the data
                output.write(buffer, 0, bytesRead)
                output.flush()
                
                // Collect data for inspection
                for (i in 0 until bytesRead) {
                    dataBuffer.add(buffer[i])
                }
                
                // Try to parse if we have enough data
                if (dataBuffer.size > 100) {
                    val data = dataBuffer.toByteArray()
                    val dataString = String(data, Charsets.UTF_8)
                    
                    if (isRequest) {
                        // Try to parse as AI request
                        val requestData = AIRequestParser.parseAIRequest(dataString)
                        if (requestData != null) {
                            Log.i(TAG, "📤 AI Request: ${requestData.model} - ${requestData.prompt.take(100)}")
                        }
                    } else {
                        // Try to parse as AI response
                        val responseData = AIResponseParser.parseAIResponse(dataString)
                        if (responseData != null) {
                            Log.i(TAG, "📥 AI Response: ${responseData.totalTokens} tokens")
                            
                            // Send to backend API
                            sendToBackend(host, responseData)
                        }
                    }
                }
            }
        } catch (e: Exception) {
            // Connection closed or error
        }
    }
    
    /**
     * Send intercepted data to backend API
     */
    private suspend fun sendToBackend(host: String, responseData: com.example.eco_compute.parser.AIResponseData) {
        try {
            val provider = aiDetector.detectProvider(host)
            val region = MetricsCalculator.detectRegion(provider, responseData.model)
            val energyWh = MetricsCalculator.calculateEnergyWh(responseData.model, responseData.totalTokens, 1000)
            val co2G = MetricsCalculator.calculateCO2G(energyWh)
            
            val requestLog = AIRequestLog(
                userId = userId,
                provider = provider,
                model = responseData.model,
                prompt = null,
                promptTokens = responseData.promptTokens,
                completionTokens = responseData.completionTokens,
                totalTokens = responseData.totalTokens,
                latencyMs = 1000,
                serverIp = host,
                region = region,
                energyWh = energyWh,
                co2G = co2G,
                timestamp = System.currentTimeMillis(),
                deviceName = deviceName
            )
            
            val response = ProxyApiClient.apiService.logAIRequest(requestLog)
            if (response.isSuccessful) {
                Log.i(TAG, "✅ Sent to backend: $provider ${responseData.model} (${responseData.totalTokens} tokens)")
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
