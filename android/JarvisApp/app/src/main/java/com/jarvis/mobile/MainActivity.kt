package com.jarvis.mobile

import android.content.Context
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.jarvis.mobile.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "JARVIS"
        private const val PREFS_NAME = "jarvis_prefs"
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_DEVICE_ID = "device_id"

        // Public HTTPS Cloudflare Tunnel Endpoint
        private const val DEFAULT_SERVER_URL = "https://elements-specify-discussions-comply.trycloudflare.com"
    }

    private lateinit var binding: ActivityMainBinding
    private val client = OkHttpClient()

    private lateinit var deviceId: String
    private lateinit var deviceName: String
    private lateinit var serverUrl: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Initialize device identity and server endpoint automatically
        deviceId = getOrCreateDeviceId()
        deviceName = getDeviceName()
        serverUrl = DEFAULT_SERVER_URL // Ensure active public HTTPS tunnel URL is used
        saveServerUrl(serverUrl)

        // Populate device information in UI
        binding.deviceNameText.text = deviceName
        binding.deviceIdText.text = "ID: $deviceId"
        binding.deviceOsText.text = "Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT}) • App v1.0"
        binding.serverUrlInput.setText(serverUrl)

        // Set up action listeners
        binding.heartbeatButton.setOnClickListener {
            performHeartbeat()
        }

        binding.syncButton.setOnClickListener {
            connectAndRegister()
        }

        binding.settingsToggle.setOnClickListener {
            val isVisible = binding.settingsContainer.visibility == View.VISIBLE
            binding.settingsContainer.visibility = if (isVisible) View.GONE else View.VISIBLE
        }

        binding.saveServerButton.setOnClickListener {
            val newUrl = binding.serverUrlInput.text.toString().trim().trimEnd('/')
            if (newUrl.isNotEmpty()) {
                saveServerUrl(newUrl)
                serverUrl = newUrl
                binding.settingsContainer.visibility = View.GONE
                connectAndRegister()
            }
        }

        // Auto-connect and register seamlessly on launch
        connectAndRegister()
    }

    private fun getOrCreateDeviceId(): String {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val savedId = prefs.getString(KEY_DEVICE_ID, null)
        if (!savedId.isNullOrEmpty()) {
            return savedId
        }

        val androidId = Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID)
        val newId = if (!androidId.isNullOrEmpty() && androidId != "9774d56d682e549c") {
            "android-$androidId"
        } else {
            "android-${UUID.randomUUID().toString().take(8)}"
        }

        prefs.edit().putString(KEY_DEVICE_ID, newId).apply()
        return newId
    }

    private fun getDeviceName(): String {
        val manufacturer = Build.MANUFACTURER.replaceFirstChar {
            if (it.isLowerCase()) it.titlecase(Locale.getDefault()) else it.toString()
        }
        val model = Build.MODEL
        return if (model.startsWith(manufacturer, ignoreCase = true)) {
            model
        } else {
            "$manufacturer $model"
        }
    }

    private fun getServerUrl(): String {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
    }

    private fun saveServerUrl(url: String) {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_SERVER_URL, url).apply()
    }

    private fun updateStatusPill(status: String, isOnline: Boolean) {
        binding.statusPill.text = status
        if (isOnline) {
            binding.statusPill.setTextColor(Color.parseColor("#0EC997"))
        } else if (status.contains("CONNECTING")) {
            binding.statusPill.setTextColor(Color.parseColor("#FFB703"))
        } else {
            binding.statusPill.setTextColor(Color.parseColor("#FF4D4D"))
        }
    }

    private fun appendLog(logMessage: String) {
        val timeStamp = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
        val currentText = binding.statusText.text.toString()
        val newEntry = "[$timeStamp] $logMessage"
        binding.statusText.text = if (currentText.isEmpty() || currentText.contains("Initializing")) {
            newEntry
        } else {
            "$newEntry\n$currentText"
        }
    }

    private fun connectAndRegister() {
        updateStatusPill("CONNECTING...", false)
        appendLog("Connecting to JARVIS server at $serverUrl...")

        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                registerDeviceNetworkCall()
            }

            if (result.first) {
                updateStatusPill("ONLINE", true)
                appendLog("Connected & Registered successfully! ${result.second}")
            } else {
                updateStatusPill("OFFLINE", false)
                appendLog("Connection failed: ${result.second}")
            }
        }
    }

    private fun registerDeviceNetworkCall(): Pair<Boolean, String> {
        return try {
            val healthUrl = "$serverUrl/api/health"
            val healthRequest = Request.Builder().url(healthUrl).get().build()
            val healthResponse = client.newCall(healthRequest).execute()

            if (!healthResponse.isSuccessful) {
                return Pair(false, "Server health check returned HTTP ${healthResponse.code}")
            }

            val payload = JSONObject().apply {
                put("device_id", deviceId)
                put("device_name", deviceName)
                put("device_type", "android")
                put("os_name", "Android ${Build.VERSION.RELEASE}")
                put("app_version", "1.0")
            }

            val mediaType = "application/json; charset=utf-8".toMediaType()
            val body = payload.toString().toRequestBody(mediaType)
            val request = Request.Builder()
                .url("$serverUrl/api/auth/register-device")
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: ""

            if (response.code == 409) {
                // Device already registered in DB, send heartbeat instead
                return Pair(true, "Device registered. Sync active.")
            }

            if (!response.isSuccessful) {
                return Pair(false, "Registration error ${response.code}: $responseBody")
            }

            Pair(true, "Device registered.")
        } catch (e: IOException) {
            Log.e(TAG, "Network call failed", e)
            Pair(false, "Cannot reach server at $serverUrl. (${e.localizedMessage})")
        } catch (e: Exception) {
            Log.e(TAG, "Unexpected error", e)
            Pair(false, "Error: ${e.localizedMessage}")
        }
    }

    private fun performHeartbeat() {
        appendLog("Sending heartbeat to server...")
        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                sendHeartbeatNetworkCall()
            }

            if (result.first) {
                updateStatusPill("ONLINE", true)
                appendLog("Heartbeat acknowledged: ${result.second}")
            } else {
                updateStatusPill("OFFLINE", false)
                appendLog("Heartbeat failed: ${result.second}")
            }
        }
    }

    private fun sendHeartbeatNetworkCall(): Pair<Boolean, String> {
        return try {
            val payload = JSONObject().apply {
                put("device_id", deviceId)
                put("battery_level", 100)
                put("connection_type", "wifi")
                put("status_message", "active")
            }

            val mediaType = "application/json; charset=utf-8".toMediaType()
            val body = payload.toString().toRequestBody(mediaType)
            val request = Request.Builder()
                .url("$serverUrl/api/devices/heartbeat")
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            if (!response.isSuccessful) {
                return Pair(false, "HTTP ${response.code}")
            }

            Pair(true, "Device active & synchronized")
        } catch (e: Exception) {
            Log.e(TAG, "Heartbeat failed", e)
            Pair(false, e.localizedMessage ?: "Network error")
        }
    }
}
