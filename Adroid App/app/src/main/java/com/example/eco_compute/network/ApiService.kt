package com.example.eco_compute.network

import com.example.eco_compute.data.models.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Retrofit API service interface for authentication endpoints
 */
interface ApiService {
    
    /**
     * Register a new user
     */
    @POST("/api/v1/auth/register")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<AuthResponse>
    
    /**
     * Login with email and password
     */
    @POST("/api/v1/auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<AuthResponse>
    
    /**
     * Refresh access token
     */
    @POST("/api/v1/auth/refresh")
    suspend fun refreshToken(
        @Body request: TokenRefreshRequest
    ): Response<AuthResponse>
    
    /**
     * Get current user information
     */
    @GET("/api/v1/auth/me")
    suspend fun getCurrentUser(
        @Header("Authorization") token: String
    ): Response<UserResponse>
    
    /**
     * Logout user
     */
    @POST("/api/v1/auth/logout")
    suspend fun logout(
        @Header("Authorization") token: String,
        @Body request: TokenRefreshRequest
    ): Response<MessageResponse>
}
