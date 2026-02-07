package com.example.eco_compute.network

import com.example.eco_compute.utils.Constants
import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Singleton Retrofit client for API calls
 */
object RetrofitClient {
    
    private var retrofit: Retrofit? = null
    
    /**
     * Get configured Retrofit instance
     */
    fun getInstance(): Retrofit {
        if (retrofit == null) {
            retrofit = Retrofit.Builder()
                .baseUrl(Constants.BASE_URL)
                .client(getOkHttpClient())
                .addConverterFactory(GsonConverterFactory.create(getGson()))
                .build()
        }
        return retrofit!!
    }
    
    /**
     * Get API service instance
     */
    fun getApiService(): ApiService {
        return getInstance().create(ApiService::class.java)
    }
    
    /**
     * Configure OkHttp client with interceptors and timeouts
     */
    private fun getOkHttpClient(): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        return OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(Constants.CONNECT_TIMEOUT, TimeUnit.SECONDS)
            .readTimeout(Constants.READ_TIMEOUT, TimeUnit.SECONDS)
            .writeTimeout(Constants.WRITE_TIMEOUT, TimeUnit.SECONDS)
            .build()
    }
    
    /**
     * Configure Gson for JSON serialization
     */
    private fun getGson() = GsonBuilder()
        .setLenient()
        .create()
}
