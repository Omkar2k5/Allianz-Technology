package com.example.eco_compute.data.local.dao

import androidx.room.*
import com.example.eco_compute.data.local.entities.AIRequestEntity
import kotlinx.coroutines.flow.Flow

/**
 * DAO for AI request logging operations
 */
@Dao
interface AIRequestDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(request: AIRequestEntity)
    
    @Query("SELECT * FROM ai_requests ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentRequests(limit: Int = 100): Flow<List<AIRequestEntity>>
    
    @Query("SELECT * FROM ai_requests WHERE synced = 0 ORDER BY timestamp ASC LIMIT 100")
    suspend fun getUnsyncedRequests(): List<AIRequestEntity>
    
    @Query("UPDATE ai_requests SET synced = 1 WHERE id IN (:ids)")
    suspend fun markAsSynced(ids: List<String>)
    
    @Query("SELECT COUNT(*) FROM ai_requests")
    fun getTotalCount(): Flow<Int>
    
    @Query("SELECT SUM(totalTokens) FROM ai_requests")
    fun getTotalTokens(): Flow<Int?>
    
    @Query("SELECT SUM(co2G) FROM ai_requests")
    fun getTotalCO2(): Flow<Double?>
    
    @Query("DELETE FROM ai_requests WHERE synced = 1 AND timestamp < :before")
    suspend fun deleteSyncedBefore(before: Long)
    
    @Query("SELECT * FROM ai_requests WHERE timestamp >= :startTime AND timestamp <= :endTime")
    fun getRequestsInRange(startTime: Long, endTime: Long): Flow<List<AIRequestEntity>>
}
