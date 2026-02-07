package com.example.eco_compute.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.eco_compute.data.repository.AuthRepository
import com.example.eco_compute.utils.Constants
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for Signup screen
 */
class SignupViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    // UI State
    private val _uiState = MutableStateFlow(SignupUiState())
    val uiState: StateFlow<SignupUiState> = _uiState.asStateFlow()
    
    // Navigation events
    private val _navigationEvent = MutableStateFlow<NavigationEvent?>(null)
    val navigationEvent: StateFlow<NavigationEvent?> = _navigationEvent.asStateFlow()
    
    /**
     * Update first name field
     */
    fun onFirstNameChange(firstName: String) {
        _uiState.value = _uiState.value.copy(
            firstName = firstName,
            firstNameError = null
        )
    }
    
    /**
     * Update last name field
     */
    fun onLastNameChange(lastName: String) {
        _uiState.value = _uiState.value.copy(
            lastName = lastName,
            lastNameError = null
        )
    }
    
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
     * Update confirm password field
     */
    fun onConfirmPasswordChange(confirmPassword: String) {
        _uiState.value = _uiState.value.copy(
            confirmPassword = confirmPassword,
            confirmPasswordError = null
        )
    }
    
    /**
     * Perform registration
     */
    fun signup() {
        // Validate input
        if (!validateInput()) {
            return
        }
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            when (val result = authRepository.register(
                email = _uiState.value.email,
                password = _uiState.value.password,
                firstName = _uiState.value.firstName,
                lastName = _uiState.value.lastName
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
     * Navigate to login screen
     */
    fun navigateToLogin() {
        _navigationEvent.value = NavigationEvent.NavigateToLogin
    }
    
    /**
     * Clear navigation event after handling
     */
    fun onNavigationHandled() {
        _navigationEvent.value = null
    }
    
    /**
     * Validate signup input
     */
    private fun validateInput(): Boolean {
        var isValid = true
        
        if (_uiState.value.firstName.isBlank()) {
            _uiState.value = _uiState.value.copy(firstNameError = "First name is required")
            isValid = false
        } else if (_uiState.value.firstName.length < Constants.MIN_NAME_LENGTH) {
            _uiState.value = _uiState.value.copy(firstNameError = "First name is too short")
            isValid = false
        }
        
        if (_uiState.value.lastName.isBlank()) {
            _uiState.value = _uiState.value.copy(lastNameError = "Last name is required")
            isValid = false
        } else if (_uiState.value.lastName.length < Constants.MIN_NAME_LENGTH) {
            _uiState.value = _uiState.value.copy(lastNameError = "Last name is too short")
            isValid = false
        }
        
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
        } else if (_uiState.value.password.length < Constants.MIN_PASSWORD_LENGTH) {
            _uiState.value = _uiState.value.copy(
                passwordError = "Password must be at least ${Constants.MIN_PASSWORD_LENGTH} characters"
            )
            isValid = false
        }
        
        if (_uiState.value.confirmPassword.isBlank()) {
            _uiState.value = _uiState.value.copy(confirmPasswordError = "Please confirm password")
            isValid = false
        } else if (_uiState.value.password != _uiState.value.confirmPassword) {
            _uiState.value = _uiState.value.copy(confirmPasswordError = "Passwords do not match")
            isValid = false
        }
        
        return isValid
    }
    
    /**
     * UI State data class
     */
    data class SignupUiState(
        val firstName: String = "",
        val lastName: String = "",
        val email: String = "",
        val password: String = "",
        val confirmPassword: String = "",
        val firstNameError: String? = null,
        val lastNameError: String? = null,
        val emailError: String? = null,
        val passwordError: String? = null,
        val confirmPasswordError: String? = null,
        val isLoading: Boolean = false,
        val error: String? = null
    )
    
    /**
     * Navigation events
     */
    sealed class NavigationEvent {
        object NavigateToDashboard : NavigationEvent()
        object NavigateToLogin : NavigationEvent()
    }
}
