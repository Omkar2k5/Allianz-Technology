package com.example.eco_compute.proxy

import android.content.Intent
import android.net.VpnService
import android.os.ParcelFileDescriptor
import android.util.Log
import com.example.eco_compute.detector.AIDetector
import com.example.eco_compute.repository.AIRequestRepository
import kotlinx.coroutines.*
import java.io.FileInputStream
import java.io.FileOutputStream
import java.nio.ByteBuffer

/**
 * VPN Service for intercepting network traffic
 * Creates a local VPN tunnel to monitor AI API requests
 */
class ProxyVpnService : VpnService() {
    
    private var vpnInterface: ParcelFileDescriptor? = null
    private var isRunning = false
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private lateinit var aiDetector: AIDetector
    private lateinit var repository: AIRequestRepository
    private lateinit var httpProxyHandler: HttpProxyHandler
    private lateinit var tcpReassembler: TcpStreamReassembler
    
    companion object {
        private const val TAG = "ProxyVpnService"
        const val ACTION_START = "com.example.eco_compute.START_VPN"
        const val ACTION_STOP = "com.example.eco_compute.STOP_VPN"
        
        // VPN configuration
        private const val VPN_ADDRESS = "10.0.0.2"
        private const val VPN_ROUTE = "0.0.0.0"
        private const val VPN_DNS = "8.8.8.8"
        private const val VPN_MTU = 1500
        
        // TCP flags
        private const val TCP_FIN = 0x01
        private const val TCP_SYN = 0x02
        private const val TCP_RST = 0x04
        private const val TCP_PSH = 0x08
        private const val TCP_ACK = 0x10
        
        // Local proxy server port
        private const val PROXY_PORT = 8899
    }
    
    private lateinit var localProxyServer: LocalProxyServer
    
    override fun onCreate() {
        super.onCreate()
        aiDetector = AIDetector()
        repository = AIRequestRepository(applicationContext)
        httpProxyHandler = HttpProxyHandler(aiDetector, repository, "android-user") // TODO: Get actual user ID
        tcpReassembler = TcpStreamReassembler()
        
        // Initialize local proxy server
        localProxyServer = LocalProxyServer(
            port = PROXY_PORT,
            aiDetector = aiDetector,
            userId = "android-user",
            deviceName = "${android.os.Build.MANUFACTURER} ${android.os.Build.MODEL}"
        )
        
        Log.d(TAG, "ProxyVpnService created")
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return when (intent?.action) {
            ACTION_START -> {
                startVpn()
                START_STICKY
            }
            ACTION_STOP -> {
                stopVpn()
                START_NOT_STICKY
            }
            else -> START_NOT_STICKY
        }
    }
    
    private fun startVpn() {
        if (isRunning) {
            Log.d(TAG, "VPN already running")
            return
        }
        
        try {
            // Start local proxy server first
            localProxyServer.start()
            Log.i(TAG, "Local proxy server started on port $PROXY_PORT")
            
            // Establish VPN connection with HTTP proxy
            vpnInterface = Builder()
                .setSession("EcoCompute Proxy")
                .addAddress(VPN_ADDRESS, 32)
                .addRoute(VPN_ROUTE, 0)
                .addDnsServer(VPN_DNS)
                .setMtu(VPN_MTU)
                .setBlocking(false)
                .setHttpProxy(android.net.ProxyInfo.buildDirectProxy("127.0.0.1", PROXY_PORT))
                .establish()
            
            if (vpnInterface == null) {
                Log.e(TAG, "Failed to establish VPN interface")
                localProxyServer.stop()
                return
            }
            
            isRunning = true
            Log.i(TAG, "VPN started successfully with HTTP proxy on 127.0.0.1:$PROXY_PORT")
            
            // Start packet processing
            scope.launch {
                processPackets()
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error starting VPN", e)
            stopVpn()
        }
    }
    
    private fun stopVpn() {
        isRunning = false
        
        try {
            // Stop local proxy server
            localProxyServer.stop()
            
            vpnInterface?.close()
            vpnInterface = null
            Log.i(TAG, "VPN stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping VPN", e)
        }
    }
    
    private suspend fun processPackets() {
        val vpnInput = FileInputStream(vpnInterface!!.fileDescriptor)
        val vpnOutput = FileOutputStream(vpnInterface!!.fileDescriptor)
        
        val buffer = ByteBuffer.allocate(VPN_MTU)
        
        try {
            while (isRunning) {
                // Read packet from VPN interface
                buffer.clear()
                val length = vpnInput.channel.read(buffer)
                
                if (length > 0) {
                    buffer.flip()
                    
                    // Process the packet
                    withContext(Dispatchers.Default) {
                        handlePacket(buffer, vpnOutput)
                    }
                } else {
                    // No data, yield to avoid busy waiting
                    delay(10)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error processing packets", e)
        } finally {
            vpnInput.close()
            vpnOutput.close()
        }
    }
    
    private suspend fun handlePacket(packet: ByteBuffer, vpnOutput: FileOutputStream) {
        try {
            // Parse IP header
            val ipVersion = (packet.get(0).toInt() shr 4) and 0x0F
            if (ipVersion != 4) {
                // Only support IPv4 for now
                return
            }
            
            val protocol = packet.get(9).toInt() and 0xFF
            
            when (protocol) {
                6 -> handleTcpPacket(packet, vpnOutput) // TCP
                17 -> handleUdpPacket(packet, vpnOutput) // UDP
                else -> {
                    // Forward other protocols as-is
                    forwardPacket(packet, vpnOutput)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling packet", e)
        }
    }
    
    private suspend fun handleTcpPacket(packet: ByteBuffer, vpnOutput: FileOutputStream) {
        try {
            // Extract IP header info
            val ihl = (packet.get(0).toInt() and 0x0F) * 4
            val sourceIp = extractSourceIp(packet)
            val destIp = extractDestinationIp(packet)
            
            // Extract TCP header info
            val sourcePort = extractSourcePort(packet, ihl)
            val destPort = extractDestinationPort(packet, ihl)
            val sequenceNumber = extractSequenceNumber(packet, ihl)
            val flags = extractTcpFlags(packet, ihl)
            
            // Extract payload
            val tcpHeaderLength = ((packet.get(ihl + 12).toInt() shr 4) and 0x0F) * 4
            val payloadStart = ihl + tcpHeaderLength
            val payloadLength = packet.limit() - payloadStart
            
            val payload = if (payloadLength > 0) {
                val payloadBytes = ByteArray(payloadLength)
                packet.position(payloadStart)
                packet.get(payloadBytes)
                payloadBytes
            } else {
                byteArrayOf()
            }
            
            // Check if this is HTTP/HTTPS traffic (ports 80, 443, 8080, etc.)
            if (destPort == 80 || destPort == 443 || destPort == 8080) {
                Log.d(TAG, "HTTP(S) packet to $destIp:$destPort (${payload.size} bytes)")
                
                // Add to TCP stream reassembler
                val completeMessage = tcpReassembler.addPacket(
                    sourceIp, sourcePort, destIp, destPort,
                    sequenceNumber, payload, flags
                )
                
                if (completeMessage != null && destPort != 443) { // Only handle HTTP for now
                    Log.d(TAG, "Complete HTTP message received (${completeMessage.size} bytes)")
                    
                    // Handle HTTP request
                    scope.launch {
                        val response = httpProxyHandler.handleRequest(completeMessage)
                        if (response != null) {
                            // TODO: Inject response back into VPN
                            Log.d(TAG, "Got HTTP response (${response.size} bytes)")
                        }
                    }
                }
            }
            
            // Forward packet as-is for now
            packet.position(0)
            forwardPacket(packet, vpnOutput)
            
        } catch (e: Exception) {
            Log.e(TAG, "Error handling TCP packet", e)
            packet.position(0)
            forwardPacket(packet, vpnOutput)
        }
    }
    
    private suspend fun handleUdpPacket(packet: ByteBuffer, vpnOutput: FileOutputStream) {
        // Forward UDP packets (DNS, etc.)
        forwardPacket(packet, vpnOutput)
    }
    
    private fun forwardPacket(packet: ByteBuffer, vpnOutput: FileOutputStream) {
        try {
            vpnOutput.channel.write(packet)
        } catch (e: Exception) {
            Log.e(TAG, "Error forwarding packet", e)
        }
    }
    
    private fun extractSourceIp(packet: ByteBuffer): String {
        val ip1 = packet.get(12).toInt() and 0xFF
        val ip2 = packet.get(13).toInt() and 0xFF
        val ip3 = packet.get(14).toInt() and 0xFF
        val ip4 = packet.get(15).toInt() and 0xFF
        return "$ip1.$ip2.$ip3.$ip4"
    }
    
    private fun extractDestinationIp(packet: ByteBuffer): String {
        val ip1 = packet.get(16).toInt() and 0xFF
        val ip2 = packet.get(17).toInt() and 0xFF
        val ip3 = packet.get(18).toInt() and 0xFF
        val ip4 = packet.get(19).toInt() and 0xFF
        return "$ip1.$ip2.$ip3.$ip4"
    }
    
    private fun extractSourcePort(packet: ByteBuffer, ihl: Int): Int {
        val port1 = packet.get(ihl).toInt() and 0xFF
        val port2 = packet.get(ihl + 1).toInt() and 0xFF
        return (port1 shl 8) or port2
    }
    
    private fun extractDestinationPort(packet: ByteBuffer, ihl: Int): Int {
        val port1 = packet.get(ihl + 2).toInt() and 0xFF
        val port2 = packet.get(ihl + 3).toInt() and 0xFF
        return (port1 shl 8) or port2
    }
    
    private fun extractSequenceNumber(packet: ByteBuffer, ihl: Int): Long {
        val seq1 = (packet.get(ihl + 4).toInt() and 0xFF).toLong()
        val seq2 = (packet.get(ihl + 5).toInt() and 0xFF).toLong()
        val seq3 = (packet.get(ihl + 6).toInt() and 0xFF).toLong()
        val seq4 = (packet.get(ihl + 7).toInt() and 0xFF).toLong()
        return (seq1 shl 24) or (seq2 shl 16) or (seq3 shl 8) or seq4
    }
    
    private fun extractTcpFlags(packet: ByteBuffer, ihl: Int): Int {
        return packet.get(ihl + 13).toInt() and 0xFF
    }
    
    override fun onDestroy() {
        super.onDestroy()
        stopVpn()
        scope.cancel()
        Log.d(TAG, "ProxyVpnService destroyed")
    }
}
