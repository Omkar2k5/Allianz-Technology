package com.example.eco_compute.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.example.eco_compute.data.repository.AuthRepository
import com.example.eco_compute.data.storage.TokenManager
import com.example.eco_compute.network.RetrofitClient
import com.example.eco_compute.ui.screens.*
import com.example.eco_compute.ui.viewmodels.LoginViewModel
import com.example.eco_compute.ui.viewmodels.SignupViewModel

/**
 * Navigation routes
 */
object Routes {
    const val SPLASH = "splash"
    const val LOGIN = "login"
    const val SIGNUP = "signup"
    const val DASHBOARD = "dashboard"
}

/**
 * Main navigation graph
 */
@Composable
fun NavigationGraph(
    navController: NavHostController
) {
    val context = LocalContext.current
    val tokenManager = TokenManager(context)
    val apiService = RetrofitClient.getApiService()
    val authRepository = AuthRepository(apiService, tokenManager)
    
    NavHost(
        navController = navController,
        startDestination = Routes.SPLASH
    ) {
        // Splash Screen
        composable(Routes.SPLASH) {
            SplashScreen(
                tokenManager = tokenManager,
                onNavigateToLogin = {
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                },
                onNavigateToDashboard = {
                    navController.navigate(Routes.DASHBOARD) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                }
            )
        }
        
        // Login Screen
        composable(Routes.LOGIN) {
            val viewModel = LoginViewModel(authRepository)
            
            LoginScreen(
                viewModel = viewModel,
                onNavigateToSignup = {
                    navController.navigate(Routes.SIGNUP)
                },
                onNavigateToDashboard = {
                    navController.navigate(Routes.DASHBOARD) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }
        
        // Signup Screen
        composable(Routes.SIGNUP) {
            val viewModel = SignupViewModel(authRepository)
            
            SignupScreen(
                viewModel = viewModel,
                onNavigateToLogin = {
                    navController.popBackStack()
                },
                onNavigateToDashboard = {
                    navController.navigate(Routes.DASHBOARD) {
                        popUpTo(Routes.SIGNUP) { inclusive = true }
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }
        
        // Dashboard Screen
        composable(Routes.DASHBOARD) {
            DashboardScreen(
                tokenManager = tokenManager,
                authRepository = authRepository,
                onNavigateToLogin = {
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(Routes.DASHBOARD) { inclusive = true }
                    }
                }
            )
        }
    }
}
