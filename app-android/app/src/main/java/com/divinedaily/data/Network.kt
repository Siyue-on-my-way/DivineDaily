package com.divinedaily.data

import com.divinedaily.BuildConfig
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit

object Network {
    private val moshi: Moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val httpClient: OkHttpClient by lazy { createOkHttpClient() }

    @Volatile
    private var cachedBaseUrl: String? = null

    @Volatile
    private var cachedApi: DivineDailyApi? = null

    private fun createOkHttpClient(): OkHttpClient {
        val builder = OkHttpClient.Builder()
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(20, TimeUnit.SECONDS)
            .writeTimeout(20, TimeUnit.SECONDS)

        if (BuildConfig.DEBUG) {
            val logging = HttpLoggingInterceptor()
            logging.level = HttpLoggingInterceptor.Level.BASIC
            builder.addInterceptor(logging)
        }
        return builder.build()
    }

    fun api(baseUrl: String = BuildConfig.API_BASE_URL): DivineDailyApi {
        val normalized = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"
        val current = cachedApi
        if (current != null && cachedBaseUrl == normalized) return current

        val created = Retrofit.Builder()
            .baseUrl(normalized)
            .client(httpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(DivineDailyApi::class.java)

        cachedBaseUrl = normalized
        cachedApi = created
        return created
    }
}
