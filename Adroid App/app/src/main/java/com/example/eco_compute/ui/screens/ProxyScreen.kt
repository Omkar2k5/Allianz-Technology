package com.example.eco_compute.ui.screens

import android.app.Activity
import android.content.Intent
import android.net.VpnService
import android.util.Log
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.eco_compute.data.local.entities.AIRequestEntity
import com.example.eco_compute.repository.AIRequestRepository
import com.example.eco_compute.service.ProxyService
import kotlinx.coroutines.launch

/**
 * Proxy control and monitoring screen
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProxyScreen() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val repository = remember { AIRequestRepository(context) }
    
    var isProxyEnabled by remember { mutableStateOf(false) }
    val recentRequests by repository.getRecentRequests(20).collectAsState(initial = emptyList())
    val totalCount by repository.getTotalCount().collectAsState(initial = 0)
    val totalTokens by repository.getTotalTokens().collectAsState(initial = 0)
    val totalCO2 by repository.getTotalCO2().collectAsState(initial = 0.0)
    
    // VPN permission launcher
    val vpnPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        Log.i("ProxyScreen", "VPN permission result: ${result.resultCode}")
        if (result.resultCode == Activity.RESULT_OK) {
            // Permission granted, start the proxy
            ProxyService.start(context)
            isProxyEnabled = true
        } else {
            Log.w("ProxyScreen", "VPN permission denied/cancelled")
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("AI Request Monitor") }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Proxy Control Card
            item {
                ProxyControlCard(
                    isEnabled = isProxyEnabled,
                    onToggle = { enabled ->
                        if (enabled) {
                            // Request VPN permission
                            val intent = VpnService.prepare(context)
                            if (intent != null) {
                                Log.i("ProxyScreen", "VPN permission required, launching intent")
                                Toast.makeText(context, "Requesting VPN permission", Toast.LENGTH_SHORT).show()
                                vpnPermissionLauncher.launch(intent)
                            } else {
                                Log.i("ProxyScreen", "VPN permission already granted, starting service")
                                Toast.makeText(context, "Starting Proxy Service", Toast.LENGTH_SHORT).show()
                                ProxyService.start(context)
                                isProxyEnabled = true
                            }
                        } else {
                            Log.i("ProxyScreen", "Stopping proxy service")
                            ProxyService.stop(context)
                            isProxyEnabled = false
                        }
                    }
                )
            }
            
            // Stats Card
            item {
                StatsCard(
                    totalRequests = totalCount,
                    totalTokens = totalTokens ?: 0,
                    totalCO2 = totalCO2 ?: 0.0
                )
            }
            
            // Recent Requests Header
            item {
                Text(
                    text = "Recent AI Requests",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // Recent Requests List
            items(recentRequests) { request ->
                AIRequestCard(request)
            }
            
            if (recentRequests.isEmpty()) {
                item {
                    Text(
                        text = "No AI requests logged yet",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
fun ProxyControlCard(
    isEnabled: Boolean,
    onToggle: (Boolean) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Proxy Status",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = if (isEnabled) "Active" else "Inactive",
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (isEnabled) 
                            MaterialTheme.colorScheme.primary 
                        else 
                            MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Switch(
                    checked = isEnabled,
                    onCheckedChange = onToggle
                )
            }
            
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = if (isEnabled) Icons.Default.CheckCircle else Icons.Default.Warning,
                    contentDescription = null,
                    tint = if (isEnabled) 
                        MaterialTheme.colorScheme.primary 
                    else 
                        MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = if (isEnabled) 
                        "Monitoring all AI API requests" 
                    else 
                        "Enable to start monitoring",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
fun StatsCard(
    totalRequests: Int,
    totalTokens: Int,
    totalCO2: Double
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Statistics",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(
                    label = "Requests",
                    value = totalRequests.toString()
                )
                StatItem(
                    label = "Tokens",
                    value = String.format("%,d", totalTokens)
                )
                StatItem(
                    label = "CO₂",
                    value = String.format("%.2fg", totalCO2)
                )
            }
        }
    }
}

@Composable
fun StatItem(label: String, value: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun AIRequestCard(request: AIRequestEntity) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = request.provider,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${request.totalTokens} tokens",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Text(
                text = request.model,
                style = MaterialTheme.typography.bodyMedium
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "${request.latencyMs}ms",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = String.format("%.2fg CO₂", request.co2G),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
