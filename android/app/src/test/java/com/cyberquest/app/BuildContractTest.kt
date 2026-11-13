package com.cyberquest.app

import org.junit.Assert.assertEquals
import org.junit.Test

class BuildContractTest {
    @Test
    fun applicationIdIsStableForTheFoundationScaffold() {
        assertEquals("com.cyberquest.app", BuildConfig.APPLICATION_ID)
    }
}
