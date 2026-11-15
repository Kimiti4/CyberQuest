import { NextRequest, NextResponse } from "next/server";

const apiBase = process.env.CYBERQUEST_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const response = await fetch(
      new URL("/v1/demo/missions/phishing-detective/assessment", apiBase),
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
        cache: "no-store",
        signal: AbortSignal.timeout(5000),
      },
    );
    return new NextResponse(await response.text(), {
      status: response.status,
      headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      { code: "demo_api_unavailable", message: "The local demo API is unavailable." },
      { status: 502, headers: { "cache-control": "no-store" } },
    );
  }
}
