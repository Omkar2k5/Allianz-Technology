package com.example.eco_compute.utils

import com.example.eco_compute.BuildConfig

/**
 * Application-wide constants
 */
object Constants {
    // API Configuration
    // TODO: Replace with your actual backend server IP address and port
    // Examples:
    // - Local network: "http://192.168.1.100:8000"
    // - Production: "https://api.ecocompute.com"
    // Fetched from local.properties -> buildConfigField
    const val BASE_URL = BuildConfig.BASE_URL
    
    // API Endpoints
    const val AUTH_REGISTER = "/api/v1/auth/register"
    const val AUTH_LOGIN = "/api/v1/auth/login"
    const val AUTH_REFRESH = "/api/v1/auth/refresh"
    const val AUTH_ME = "/api/v1/auth/me"
    const val AUTH_LOGOUT = "/api/v1/auth/logout"
    
    // Network Timeouts (in seconds)
    const val CONNECT_TIMEOUT = 30L
    const val READ_TIMEOUT = 30L
    const val WRITE_TIMEOUT = 30L
    
    // DataStore Keys
    const val DATASTORE_NAME = "eco_compute_prefs"
    const val KEY_ACCESS_TOKEN = "access_token"
    const val KEY_REFRESH_TOKEN = "refresh_token"
    const val KEY_USER_EMAIL = "user_email"
    const val KEY_USER_ID = "user_id"
    
    // Validation
    const val MIN_PASSWORD_LENGTH = 8
    const val MIN_NAME_LENGTH = 1
}
