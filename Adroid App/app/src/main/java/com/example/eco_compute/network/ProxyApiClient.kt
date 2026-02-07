package com.example.eco_compute.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * API Service for sending intercepted AI requests to backend
 */
interface ProxyApiService {
    
    @retrofit2.http.POST("api/ai-requests/log")
    suspend fun logAIRequest(
        @retrofit2.http.Body request: AIRequestLog
    ): retrofit2.Response<Unit>
}

/**
 * Data class for AI request log
 */
data class AIRequestLog(
    val userId: String,
    val provider: String,
    val model: String,
    val prompt: String?,
    val promptTokens: Int,
    val completionTokens: Int,
    val totalTokens: Int,
    val latencyMs: Long,
    val serverIp: String?,
    val region: String?,
    val energyWh: Double,
    val co2G: Double,
    val timestamp: Long,
    val deviceName: String
)

/**
 * Retrofit client for proxy API
 */
object ProxyApiClient {
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(com.example.eco_compute.utils.Constants.BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val apiService: ProxyApiService = retrofit.create(ProxyApiService::class.java)
}
