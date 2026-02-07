package com.example.eco_compute.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity for storing AI request logs locally
 * Matches the backend's genai_requests table schema
 */
@Entity(tableName = "ai_requests")
data class AIRequestEntity(
    @PrimaryKey
    val id: String,
    
    val userId: String,
    val provider: String,
    val model: String,
    
    val promptTokens: Int,
    val completionTokens: Int,
    val totalTokens: Int,
    
    val latencyMs: Long,
    val serverIp: String? = null,
    val region: String? = null,
    val carbonIntensity: Double? = null,
    
    val energyWh: Double,
    val co2G: Double,
    
    val timestamp: Long = System.currentTimeMillis(),
    val deviceName: String,
    
    val synced: Boolean = false
)
