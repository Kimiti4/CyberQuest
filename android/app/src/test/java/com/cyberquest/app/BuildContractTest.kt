package com.cyberquest.app

import java.io.File
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Contract tests for the G4 build configuration and transport-security rules.
 *
 * These pin the transport requirements from the approved G4 plan: HTTPS only,
 * no cleartext fallback, no trust-all trust manager and no hostname-verification
 * bypass in the shipped client.
 */
class BuildContractTest {
    private fun locate(vararg candidates: String): File {
        for (candidate in candidates) {
            val file = File(candidate)
            if (file.isFile) return file
        }
        throw AssertionError("Could not locate any of ${candidates.toList()}")
    }

    @Test
    fun applicationIdIsStableForTheFoundationScaffold() {
        assertEquals("com.cyberquest.app", BuildConfig.APPLICATION_ID)
    }

    @Test
    fun demoApiBaseUrlUsesHttps() {
        assertTrue(
            "Demo API base URL must use https://",
            BuildConfig.DEMO_API_BASE_URL.startsWith("https://"),
        )
    }

    @Test
    fun cleartextTrafficIsDisabledInTheManifest() {
        val manifest = locate(
            "src/main/AndroidManifest.xml",
            "app/src/main/AndroidManifest.xml",
            "../app/src/main/AndroidManifest.xml",
        ).readText()
        assertTrue(
            "Manifest must disable cleartext traffic",
            manifest.contains("android:usesCleartextTraffic=\"false\""),
        )
    }

    @Test
    fun clientDoesNotBypassCertificateOrHostnameValidation() {
        val source = locate(
            "src/main/java/com/cyberquest/app/MainActivity.kt",
            "app/src/main/java/com/cyberquest/app/MainActivity.kt",
            "../app/src/main/java/com/cyberquest/app/MainActivity.kt",
        ).readText()
        val forbidden = listOf(
            "X509TrustManager",
            "HostnameVerifier",
            "checkServerTrusted",
            "setHostnameVerifier",
            "TrustAll",
            "certificatePinner",
            "CertificatePinner",
        )
        for (token in forbidden) {
            assertFalse("Client must not contain $token", source.contains(token))
        }
    }

    @Test
    fun clientUsesExplicitNetworkTimeouts() {
        val source = locate(
            "src/main/java/com/cyberquest/app/MainActivity.kt",
            "app/src/main/java/com/cyberquest/app/MainActivity.kt",
            "../app/src/main/java/com/cyberquest/app/MainActivity.kt",
        ).readText()
        assertTrue("Connect timeout must be explicit", source.contains("connectTimeout"))
        assertTrue("Read timeout must be explicit", source.contains("readTimeout"))
    }
}
