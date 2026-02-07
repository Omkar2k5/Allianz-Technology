package com.example.eco_compute.data.repository

import com.example.eco_compute.data.models.*
import com.example.eco_compute.data.storage.TokenManager
import com.example.eco_compute.network.ApiService
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Repository for authentication operations
 */
class AuthRepository(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) {
    
    /**
     * Result wrapper for API calls
     */
    sealed class Result<out T> {
        data class Success<T>(val data: T) : Result<T>()
        data class Error(val message: String) : Result<Nothing>()
        object Loading : Result<Nothing>()
    }
    
    /**
     * Register a new user
     */
    suspend fun register(
        email: String,
        password: String,
        firstName: String,
        lastName: String
    ): Result<AuthResponse> = withContext(Dispatchers.IO) {
        try {
            val request = RegisterRequest(
                email = email,
                password = password,
                firstName = firstName,
                lastName = lastName
            )
            
            val response = apiService.register(request)
            
            if (response.isSuccessful && response.body() != null) {
                val authResponse = response.body()!!
                
                // Save tokens and user info
                tokenManager.saveTokens(
                    authResponse.accessToken,
                    authResponse.refreshToken
                )
                tokenManager.saveUserInfo(
                    authResponse.user.id,
                    authResponse.user.email
                )
                
                Result.Success(authResponse)
            } else {
                val errorBody = response.errorBody()?.string()
                val errorMessage = try {
                    val errorResponse = Gson().fromJson(errorBody, ErrorResponse::class.java)
                    errorResponse.getErrorMessage()
                } catch (e: Exception) {
                    "Registration failed: ${response.message()}"
                }
                Result.Error(errorMessage)
            }
        } catch (e: Exception) {
            Result.Error("Network error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }
    
    /**
     * Login with email and password
     */
    suspend fun login(
        email: String,
        password: String
    ): Result<AuthResponse> = withContext(Dispatchers.IO) {
        try {
            val request = LoginRequest(email, password)
            val response = apiService.login(request)
            
            if (response.isSuccessful && response.body() != null) {
                val authResponse = response.body()!!
                
                // Save tokens and user info
                tokenManager.saveTokens(
                    authResponse.accessToken,
                    authResponse.refreshToken
                )
                tokenManager.saveUserInfo(
                    authResponse.user.id,
                    authResponse.user.email
                )
                
                Result.Success(authResponse)
            } else {
                val errorBody = response.errorBody()?.string()
                val errorMessage = try {
                    val errorResponse = Gson().fromJson(errorBody, ErrorResponse::class.java)
                    errorResponse.getErrorMessage()
                } catch (e: Exception) {
                    "Login failed: ${response.message()}"
                }
                Result.Error(errorMessage)
            }
        } catch (e: Exception) {
            Result.Error("Network error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }
    
    /**
     * Get current user information
     */
    suspend fun getCurrentUser(): Result<UserResponse> = withContext(Dispatchers.IO) {
        try {
            val accessToken = tokenManager.getAccessToken()
            if (accessToken.isNullOrEmpty()) {
                return@withContext Result.Error("Not authenticated")
            }
            
            val response = apiService.getCurrentUser("Bearer $accessToken")
            
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!)
            } else {
                Result.Error("Failed to get user info: ${response.message()}")
            }
        } catch (e: Exception) {
            Result.Error("Network error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }
    
    /**
     * Logout user
     */
    suspend fun logout(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val accessToken = tokenManager.getAccessToken()
            val refreshToken = tokenManager.getRefreshToken()
            
            if (!accessToken.isNullOrEmpty() && !refreshToken.isNullOrEmpty()) {
                val request = TokenRefreshRequest(refreshToken)
                apiService.logout("Bearer $accessToken", request)
            }
            
            // Clear tokens regardless of API call success
            tokenManager.clearAll()
            Result.Success(true)
        } catch (e: Exception) {
            // Still clear tokens even if API call fails
            tokenManager.clearAll()
            Result.Success(true)
        }
    }
    
    /**
     * Check if user is authenticated
     */
    suspend fun isAuthenticated(): Boolean {
        return tokenManager.isAuthenticated()
    }
}
