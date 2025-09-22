import { NextRequest, NextResponse } from "next/server";
import { chatRequestSchema, chatResponseSchema } from "@/lib/schemas";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const API_URL = process.env.API_URL;

export async function POST(req: NextRequest) {
	if (!API_URL) {
		return NextResponse.json({ error: "API_URL not found" }, { status: 500 });
	}

	try {
		// Validate request
		const data = await req.json();
		const parsed = chatRequestSchema.safeParse(data);
		if (!parsed.success) {
			return NextResponse.json(
				{ error: "Invalid request data", issues: parsed.error.issues },
				{ status: 400 }
			);
		}

		// Timeout/abort (client disconnect + timeout)
		const signal = AbortSignal.any([req.signal, AbortSignal.timeout(20_000)]);

		const res = await fetch(`${API_URL}/chat`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(parsed.data),
			cache: "no-store",
			signal,
		});

		const contentType = res.headers.get("content-type") || "";
		const isJson = contentType.includes("application/json");
		const payload = isJson
			? await res.json().catch(() => null)
			: await res.text();

		if (!res.ok) {
			const message =
				(payload && (payload as any).error) ||
				(payload && (payload as any).message) ||
				`Upstream error ${res.status}`;
			// Upstream status passthrough
			return NextResponse.json({ error: message }, { status: res.status });
		}

		// Optional: response validation
		if (isJson) {
			const validated = chatResponseSchema.parse(payload);
			return NextResponse.json(validated, { status: 200 });
		}

		return new NextResponse(String(payload), {
			status: 200,
			headers: { "Content-Type": contentType || "text/plain" },
		});
	} catch (err: any) {
		if (err?.name === "AbortError" || err?.name === "TimeoutError") {
			return NextResponse.json(
				{ error: "Upstream request timed out" },
				{ status: 504 }
			);
		}
		return NextResponse.json(
			{
				error: "[API_CHAT] Unexpected error",
				detail: err?.message ?? String(err),
			},
			{ status: 500 }
		);
	}
}
