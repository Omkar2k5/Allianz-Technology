package com.example.eco_compute.repository

import android.content.Context
import android.os.Build
import com.example.eco_compute.data.local.AppDatabase
import com.example.eco_compute.data.local.entities.AIRequestEntity
import com.example.eco_compute.utils.MetricsCalculator
import kotlinx.coroutines.flow.Flow
import java.util.UUID

/**
 * Repository for AI request logging
 * Handles local database operations and metrics calculation
 */
class AIRequestRepository(context: Context) {
    
    private val database = AppDatabase.getDatabase(context)
    private val aiRequestDao = database.aiRequestDao()
    private val deviceName = "${Build.MANUFACTURER} ${Build.MODEL}"
    
    /**
     * Log an AI request to the local database
     * 
     * @param userId User ID
     * @param provider AI provider (e.g., "OpenAI", "Anthropic")
     * @param model Model name (e.g., "gpt-4", "claude-3")
     * @param promptTokens Number of prompt tokens
     * @param completionTokens Number of completion tokens
     * @param totalTokens Total tokens
     * @param latencyMs Request latency in milliseconds
     * @param serverIp Optional server IP address
     */
    suspend fun logAIRequest(
        userId: String,
        provider: String,
        model: String,
        promptTokens: Int,
        completionTokens: Int,
        totalTokens: Int,
        latencyMs: Long,
        serverIp: String? = null
    ) {
        // Calculate metrics
        val region = MetricsCalculator.detectRegion(provider, model)
        val energyWh = MetricsCalculator.calculateEnergyWh(model, totalTokens, latencyMs)
        val co2G = MetricsCalculator.calculateCO2G(energyWh)
        
        // Create entity
        val entity = AIRequestEntity(
            id = UUID.randomUUID().toString(),
            userId = userId,
            provider = provider,
            model = model,
            promptTokens = promptTokens,
            completionTokens = completionTokens,
            totalTokens = totalTokens,
            latencyMs = latencyMs,
            serverIp = serverIp,
            region = region,
            carbonIntensity = null, // Will be detected by backend
            energyWh = energyWh,
            co2G = co2G,
            timestamp = System.currentTimeMillis(),
            deviceName = deviceName,
            synced = false
        )
        
        aiRequestDao.insert(entity)
    }
    
    /**
     * Get recent AI requests
     */
    fun getRecentRequests(limit: Int = 100): Flow<List<AIRequestEntity>> {
        return aiRequestDao.getRecentRequests(limit)
    }
    
    /**
     * Get unsynced requests for backend sync
     */
    suspend fun getUnsyncedRequests(): List<AIRequestEntity> {
        return aiRequestDao.getUnsyncedRequests()
    }
    
    /**
     * Mark requests as synced
     */
    suspend fun markAsSynced(ids: List<String>) {
        aiRequestDao.markAsSynced(ids)
    }
    
    /**
     * Get total request count
     */
    fun getTotalCount(): Flow<Int> {
        return aiRequestDao.getTotalCount()
    }
    
    /**
     * Get total tokens processed
     */
    fun getTotalTokens(): Flow<Int?> {
        return aiRequestDao.getTotalTokens()
    }
    
    /**
     * Get total CO2 emissions
     */
    fun getTotalCO2(): Flow<Double?> {
        return aiRequestDao.getTotalCO2()
    }
    
    /**
     * Delete old synced requests
     */
    suspend fun deleteOldSyncedRequests(daysOld: Int = 30) {
        val cutoffTime = System.currentTimeMillis() - (daysOld * 24 * 60 * 60 * 1000L)
        aiRequestDao.deleteSyncedBefore(cutoffTime)
    }
}
