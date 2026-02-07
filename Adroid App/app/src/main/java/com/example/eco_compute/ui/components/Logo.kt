package com.example.eco_compute.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.eco_compute.R

/**
 * Eco-Compute logo component matching the frontend design
 */
@Composable
fun EcoComputeLogo(
    modifier: Modifier = Modifier,
    showText: Boolean = true,
    iconSize: Int = 40,
    textSize: Int = 24,
    textColor: Color? = null
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Logo icon with green background
        Box(
            modifier = Modifier
                .size(iconSize.dp)
                .background(
                    color = Color(0xFF10B981), // Green-500
                    shape = androidx.compose.foundation.shape.RoundedCornerShape(8.dp)
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                painter = painterResource(id = R.drawable.ic_leaf),
                contentDescription = "Eco-Compute Logo",
                tint = Color.White,
                modifier = Modifier.size((iconSize * 0.6).dp)
            )
        }
        
        if (showText) {
            Spacer(modifier = Modifier.width(12.dp))
            
            Text(
                text = "Eco-Compute",
                fontSize = textSize.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
        }
    }
}
