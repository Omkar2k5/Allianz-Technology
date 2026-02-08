package com.example.eco_compute.data.models

import com.google.gson.annotations.SerializedName

/**
 * Request model for user login
 */
data class LoginRequest(
    @SerializedName("email")
    val email: String,
    
    @SerializedName("password")
    val password: String
)

/**
 * Request model for user registration
 */
data class RegisterRequest(
    @SerializedName("email")
    val email: String,
    
    @SerializedName("password")
    val password: String,
    
    @SerializedName("first_name")
    val firstName: String,
    
    @SerializedName("last_name")
    val lastName: String,
    
    @SerializedName("team_name")
    val teamName: String? = null
)

/**
 * Request model for token refresh
 */
data class TokenRefreshRequest(
    @SerializedName("refresh_token")
    val refreshToken: String
)

/**
 * Response model for authentication (login/register)
 */
data class AuthResponse(
    @SerializedName("access_token")
    val accessToken: String,
    
    @SerializedName("refresh_token")
    val refreshToken: String,
    
    @SerializedName("token_type")
    val tokenType: String,
    
    @SerializedName("user")
    val user: UserResponse
)

/**
 * User information model
 */
data class UserResponse(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("email")
    val email: String,
    
    @SerializedName("first_name")
    val firstName: String,
    
    @SerializedName("last_name")
    val lastName: String,
    
    @SerializedName("role")
    val role: String,
    
    @SerializedName("team_id")
    val teamId: String? = null,
    
    @SerializedName("team_name")
    val teamName: String? = null,
    
    @SerializedName("is_active")
    val isActive: Boolean,
    
    @SerializedName("last_login")
    val lastLogin: String? = null,
    
    @SerializedName("created_at")
    val createdAt: String
)

/**
 * Generic message response
 */
data class MessageResponse(
    @SerializedName("message")
    val message: String
)

/**
 * Error response model
 */
data class ErrorResponse(
    @SerializedName("detail")
    val detail: String? = null,
    
    @SerializedName("message")
    val message: String? = null
) {
    fun getErrorMessage(): String {
        return detail ?: message ?: "An unknown error occurred"
    }
}
