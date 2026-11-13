package com.cyberquest.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CyberQuestApp()
        }
    }
}

@Composable
private fun CyberQuestApp() {
    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(text = "CYBERQUEST", style = MaterialTheme.typography.headlineLarge)
                Text(
                    text = "Learn. Hack. Defend. Master.",
                    modifier = Modifier.padding(top = 12.dp),
                    style = MaterialTheme.typography.bodyLarge,
                )
                Text(
                    text = "Engineering foundation build",
                    modifier = Modifier.padding(top = 24.dp),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
}
