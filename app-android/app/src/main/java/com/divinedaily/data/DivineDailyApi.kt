package com.divinedaily.data

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface DivineDailyApi {
    @POST("api/v1/divinations/start")
    suspend fun startDivination(@Body req: CreateDivinationRequest): DivinationSession

    @GET("api/v1/divinations/{id}/result")
    suspend fun getResult(@Path("id") id: String): DivinationResult

    @POST("api/v1/divinations/follow-up")
    suspend fun submitFollowUp(@Body ans: FollowUpAnswer): Map<String, String>
}

