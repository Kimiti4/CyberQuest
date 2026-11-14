package com.cyberquest.app

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

private data class DemoIndicator(val id: String, val label: String)
private data class DemoOption(val id: String, val label: String)
private data class DemoMission(
    val title: String,
    val organisation: String,
    val notice: String,
    val briefing: String,
    val sender: String,
    val replyTo: String,
    val subject: String,
    val body: List<String>,
    val displayedLink: String,
    val indicators: List<DemoIndicator>,
    val options: List<DemoOption>,
)

private data class DemoFeedback(val label: String, val identified: Boolean)
private data class DemoResult(
    val score: Int,
    val maxScore: Int,
    val responseExplanation: String,
    val xpAwarded: Int,
    val competencyAwarded: Boolean,
    val persistence: String,
    val missedIndicators: List<String>,
    val incorrectSelections: List<String>,
    val feedback: List<DemoFeedback>,
)

private object DemoApi {
    private val mainHandler = Handler(Looper.getMainLooper())
    private val baseUrl = BuildConfig.DEMO_API_BASE_URL.trimEnd('/')

    fun getMission(onResult: (Result<DemoMission>) -> Unit) {
        request("GET", "/v1/demo/missions/phishing-detective", null) { result ->
            onResult(result.mapCatching(::parseMission))
        }
    }

    fun submit(selected: List<String>, responseId: String, onResult: (Result<DemoResult>) -> Unit) {
        val body = JSONObject()
            .put("selected_indicator_ids", JSONArray(selected))
            .put("response_id", responseId)
        request("POST", "/v1/demo/missions/phishing-detective/assessment", body.toString()) { result ->
            onResult(result.mapCatching(::parseResult))
        }
    }

    private fun request(method: String, path: String, body: String?, done: (Result<JSONObject>) -> Unit) {
        Thread {
            val result = runCatching {
                val connection = URL(baseUrl + path).openConnection() as HttpURLConnection
                try {
                    connection.requestMethod = method
                    connection.connectTimeout = 5000
                    connection.readTimeout = 5000
                    connection.setRequestProperty("Accept", "application/json")
                    if (body != null) {
                        connection.doOutput = true
                        connection.setRequestProperty("Content-Type", "application/json")
                        connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
                    }
                    val status = connection.responseCode
                    val stream = if (status in 200..299) connection.inputStream else connection.errorStream
                    val response = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
                    if (status !in 200..299) error("Demo API returned HTTP $status")
                    JSONObject(response)
                } finally {
                    connection.disconnect()
                }
            }
            mainHandler.post { done(result) }
        }.start()
    }

    private fun parseMission(json: JSONObject): DemoMission {
        val email = json.getJSONObject("email")
        return DemoMission(
            title = json.getString("title"),
            organisation = json.getString("organisation"),
            notice = json.getString("simulation_notice"),
            briefing = json.getString("briefing"),
            sender = email.getString("from_address"),
            replyTo = email.getString("reply_to"),
            subject = email.getString("subject"),
            body = email.getJSONArray("body").toStringList(),
            displayedLink = email.getString("displayed_link"),
            indicators = json.getJSONArray("indicators").toObjectList {
                DemoIndicator(it.getString("id"), it.getString("label"))
            },
            options = json.getJSONArray("response_options").toObjectList {
                DemoOption(it.getString("id"), it.getString("label"))
            },
        )
    }

    private fun parseResult(json: JSONObject) = DemoResult(
        score = json.getInt("score"),
        maxScore = json.getInt("max_score"),
        responseExplanation = json.getString("response_explanation"),
        xpAwarded = json.getInt("xp_awarded"),
        competencyAwarded = json.getBoolean("competency_awarded"),
        persistence = json.getString("persistence"),
        missedIndicators = json.getJSONArray("missed_indicators").toStringList(),
        incorrectSelections = json.getJSONArray("incorrect_selections").toStringList(),
        feedback = json.getJSONArray("feedback").toObjectList {
            DemoFeedback(it.getString("explanation"), it.getBoolean("identified"))
        },
    )

    private fun JSONArray.toStringList(): List<String> = (0 until length()).map { getString(it) }

    private fun <T> JSONArray.toObjectList(mapper: (JSONObject) -> T): List<T> =
        (0 until length()).map { mapper(getJSONObject(it)) }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { CyberQuestApp() }
    }
}

@Composable
private fun CyberQuestApp() {
    val mission = remember { mutableStateOf<DemoMission?>(null) }
    val result = remember { mutableStateOf<DemoResult?>(null) }
    val error = remember { mutableStateOf<String?>(null) }
    val loading = remember { mutableStateOf(true) }
    val submitting = remember { mutableStateOf(false) }
    val selected = remember { mutableStateListOf<String>() }
    val response = remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        DemoApi.getMission { outcome ->
            outcome.onSuccess { mission.value = it }
                .onFailure { error.value = "Cannot reach the demo API. Configure CYBERQUEST_DEMO_API_BASE_URL and retry." }
            loading.value = false
        }
    }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                item {
                    Text("CYBERQUEST", style = MaterialTheme.typography.labelLarge)
                    Text("Learn. Hack. Defend. Master.", style = MaterialTheme.typography.titleMedium)
                    Text("ADULT LEARNING DEMO · 18+", style = MaterialTheme.typography.labelSmall)
                }
                if (loading.value) {
                    item { CircularProgressIndicator() }
                } else if (mission.value == null) {
                    item {
                        Text("Phishing Detective", style = MaterialTheme.typography.headlineMedium)
                        Text(error.value ?: "Demo unavailable")
                        Text("Start the FastAPI service and configure the API URL in the Android build.")
                    }
                } else {
                    val data = mission.value!!
                    item {
                        Text(data.title, style = MaterialTheme.typography.headlineMedium)
                        Text("Fictional incident · ${data.organisation}")
                        Text(data.notice, color = MaterialTheme.colorScheme.tertiary)
                        Text(data.briefing)
                    }
                    item {
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text("SIMULATED EMAIL", style = MaterialTheme.typography.labelMedium)
                                Text(data.subject, style = MaterialTheme.typography.titleMedium)
                                Text("From: ${data.sender}")
                                Text("Reply-to: ${data.replyTo}")
                                data.body.forEach { Text(it) }
                                Text("Displayed link (not clickable): ${data.displayedLink}")
                            }
                        }
                    }
                    if (result.value == null) {
                        item {
                            Text("Identify the warning signs", style = MaterialTheme.typography.titleLarge)
                            Text("Select all that apply. The server evaluates your choices.")
                        }
                        items(data.indicators, key = { it.id }) { indicator ->
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Start) {
                                Checkbox(
                                    checked = indicator.id in selected,
                                    onCheckedChange = { checked ->
                                        if (checked) selected.add(indicator.id) else selected.remove(indicator.id)
                                    },
                                )
                                Text(indicator.label, modifier = Modifier.padding(top = 12.dp))
                            }
                        }
                        item {
                            Text("Choose a safe response", style = MaterialTheme.typography.titleLarge)
                        }
                        items(data.options, key = { it.id }) { option ->
                            Row(modifier = Modifier.fillMaxWidth()) {
                                RadioButton(selected = response.value == option.id, onClick = { response.value = option.id })
                                Text(option.label, modifier = Modifier.padding(top = 12.dp))
                            }
                        }
                        item {
                            Button(
                                onClick = {
                                    submitting.value = true
                                    error.value = null
                                    DemoApi.submit(selected.toList(), response.value) { outcome ->
                                        outcome.onSuccess { result.value = it }
                                            .onFailure { error.value = "Assessment failed. Check the API connection and retry." }
                                        submitting.value = false
                                    }
                                },
                                enabled = response.value.isNotBlank() && !submitting.value,
                                modifier = Modifier.fillMaxWidth(),
                            ) { Text(if (submitting.value) "Evaluating…" else "Submit for assessment") }
                            error.value?.let { Text(it, color = MaterialTheme.colorScheme.error) }
                        }
                    } else {
                        item {
                            Text("Your practice result", style = MaterialTheme.typography.headlineMedium)
                            Text("${result.value!!.score} / ${result.value!!.maxScore}", style = MaterialTheme.typography.displaySmall)
                            Text(result.value!!.responseExplanation)
                            Text("Indicator feedback", style = MaterialTheme.typography.titleMedium)
                            result.value!!.feedback.forEach { item ->
                                Text("${if (item.identified) "Identified" else "Missed"} · ${item.label}")
                            }
                            if (result.value!!.incorrectSelections.isNotEmpty()) {
                                Text("Incorrect selections: ${result.value!!.incorrectSelections.joinToString()}")
                            }
                            Text("XP awarded: ${result.value!!.xpAwarded}")
                            Text("Competency awarded: ${result.value!!.competencyAwarded}")
                            Text("Saved: ${result.value!!.persistence != "not_saved"}")
                            Text("This is practice feedback, not verified competency evidence.")
                            TextButton(onClick = {
                                result.value = null
                                selected.clear()
                                response.value = ""
                            }) { Text("Try again") }
                        }
                    }
                }
            }
        }
    }
}
