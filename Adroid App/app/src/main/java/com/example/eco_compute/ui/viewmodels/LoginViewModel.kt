package com.example.eco_compute.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.eco_compute.data.models.AuthResponse
import com.example.eco_compute.data.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for Login screen
 */
class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    // UI State
    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()
    
    // Navigation events
    private val _navigationEvent = MutableStateFlow<NavigationEvent?>(null)
    val navigationEvent: StateFlow<NavigationEvent?> = _navigationEvent.asStateFlow()
    
    /**
     * Update email field
     */
    fun onEmailChange(email: String) {
        _uiState.value = _uiState.value.copy(
            email = email,
            emailError = null
        )
    }
    
    /**
     * Update password field
     */
    fun onPasswordChange(password: String) {
        _uiState.value = _uiState.value.copy(
            password = password,
            passwordError = null
        )
    }
    
    /**
     * Perform login
     */
    fun login() {
        // Validate input
        if (!validateInput()) {
            return
        }
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            when (val result = authRepository.login(
                email = _uiState.value.email,
                password = _uiState.value.password
            )) {
                is AuthRepository.Result.Success -> {
                    _uiState.value = _uiState.value.copy(isLoading = false)
                    _navigationEvent.value = NavigationEvent.NavigateToDashboard
                }
                is AuthRepository.Result.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                else -> {}
            }
        }
    }
    
    /**
     * Navigate to signup screen
     */
    fun navigateToSignup() {
        _navigationEvent.value = NavigationEvent.NavigateToSignup
    }
    
    /**
     * Clear navigation event after handling
     */
    fun onNavigationHandled() {
        _navigationEvent.value = null
    }
    
    /**
     * Validate login input
     */
    private fun validateInput(): Boolean {
        var isValid = true
        
        if (_uiState.value.email.isBlank()) {
            _uiState.value = _uiState.value.copy(emailError = "Email is required")
            isValid = false
        } else if (!android.util.Patterns.EMAIL_ADDRESS.matcher(_uiState.value.email).matches()) {
            _uiState.value = _uiState.value.copy(emailError = "Invalid email format")
            isValid = false
        }
        
        if (_uiState.value.password.isBlank()) {
            _uiState.value = _uiState.value.copy(passwordError = "Password is required")
            isValid = false
        }
        
        return isValid
    }
    
    /**
     * UI State data class
     */
    data class LoginUiState(
        val email: String = "",
        val password: String = "",
        val emailError: String? = null,
        val passwordError: String? = null,
        val isLoading: Boolean = false,
        val error: String? = null
    )
    
    /**
     * Navigation events
     */
    sealed class NavigationEvent {
        object NavigateToDashboard : NavigationEvent()
        object NavigateToSignup : NavigationEvent()
    }
}
