package com.example.eco_compute.service

import android.app.*
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.example.eco_compute.R
import com.example.eco_compute.proxy.ProxyVpnService

/**
 * Foreground service to manage VPN lifecycle
 * Keeps the VPN running in the background with a persistent notification
 */
class ProxyService : Service() {
    
    companion object {
        private const val TAG = "ProxyService"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "proxy_service_channel"
        private const val CHANNEL_NAME = "Proxy Service"
        
        const val ACTION_START_PROXY = "com.example.eco_compute.START_PROXY"
        const val ACTION_STOP_PROXY = "com.example.eco_compute.STOP_PROXY"
        
        fun start(context: Context) {
            val intent = Intent(context, ProxyService::class.java).apply {
                action = ACTION_START_PROXY
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }
        
        fun stop(context: Context) {
            val intent = Intent(context, ProxyService::class.java).apply {
                action = ACTION_STOP_PROXY
            }
            context.startService(intent)
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return when (intent?.action) {
            ACTION_START_PROXY -> {
                startForegroundService()
                startVpnService()
                START_STICKY
            }
            ACTION_STOP_PROXY -> {
                stopVpnService()
                stopSelf()
                START_NOT_STICKY
            }
            else -> START_NOT_STICKY
        }
    }
    
    private fun startForegroundService() {
        val notification = createNotification(
            title = "EcoCompute Proxy Active",
            text = "Monitoring AI API requests"
        )
        
        startForeground(NOTIFICATION_ID, notification)
    }
    
    private fun startVpnService() {
        val intent = Intent(this, ProxyVpnService::class.java).apply {
            action = ProxyVpnService.ACTION_START
        }
        startService(intent)
    }
    
    private fun stopVpnService() {
        val intent = Intent(this, ProxyVpnService::class.java).apply {
            action = ProxyVpnService.ACTION_STOP
        }
        startService(intent)
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Notification for proxy service"
                setShowBadge(false)
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(title: String, text: String): Notification {
        // TODO: Add proper intent for opening the app
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(),
            PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_dialog_info) // TODO: Replace with app icon
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        stopVpnService()
    }
}
