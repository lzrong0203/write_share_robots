package com.example.sentimentmontior

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.sentimentmontior.ui.theme.SentimentMontiorTheme
import com.google.firebase.messaging.FirebaseMessaging


class MainActivity : ComponentActivity() {
    private var subscriptionStatus = mutableStateOf("正在檢查通知權限...")

    // 註冊權限請求啟動器
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            // 權限已授予
            subscriptionStatus.value = "已獲得通知權限，正在訂閱..."
            // 訂閱主題
            subscribeToTopic()
        } else {
            // 權限被拒絕
            subscriptionStatus.value = "通知權限被拒絕，將無法接收股票情緒通知"
        }
    }

    // 訂閱主題的方法
    private fun subscribeToTopic() {
        FirebaseMessaging.getInstance().subscribeToTopic("sentiment_alerts")
            .addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    subscriptionStatus.value = "已成功訂閱股票情緒通知"
                } else {
                    subscriptionStatus.value = "通知訂閱失敗，請檢查網路連接"
                }
                Log.d("MainActivity", subscriptionStatus.value)
            }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // 檢查並請求通知權限
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            when {
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) == PackageManager.PERMISSION_GRANTED -> {
                    // 已有權限，直接訂閱主題
                    subscriptionStatus.value = "已有通知權限，正在訂閱..."
                    subscribeToTopic()
                }
                shouldShowRequestPermissionRationale(Manifest.permission.POST_NOTIFICATIONS) -> {
                    // 顯示權限說明
                    subscriptionStatus.value = "需要通知權限才能接收股票情緒更新"
                    // 請求權限
                    requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
                else -> {
                    // 直接請求權限
                    requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
            }
        } else {
            // Android 12 及以下版本不需要明確請求通知權限
            subscriptionStatus.value = "正在訂閱通知..."
            subscribeToTopic()
        }

        setContent {
            SentimentMontiorTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(innerPadding)
                            .padding(16.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "股票情緒監控",
                            style = MaterialTheme.typography.headlineMedium,
                            modifier = Modifier.padding(bottom = 16.dp)
                        )

                        Text(
                            text = subscriptionStatus.value,
                            style = MaterialTheme.typography.bodyLarge,
                            textAlign = TextAlign.Center
                        )

                        Spacer(modifier = Modifier.height(32.dp))

                        Text(
                            text = "此應用程式將接收股票情緒分析的通知",
                            style = MaterialTheme.typography.bodyMedium,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    SentimentMontiorTheme {
        Greeting("Android")
    }
}