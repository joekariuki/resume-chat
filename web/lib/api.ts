/**
 * API utilities for making JSON POST requests with timeout and robust error handling.
 *
 * Environment:
 * - NEXT_PUBLIC_API_URL: Base URL for the API. Trailing slash is trimmed automatically.
 *
 * Exports:
 * - postJSON<TResponse>(path, body, options): Promise<TResponse>
 */

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

type FetchOptions = {
	timeoutMs?: number;
	headers?: Record<string, string>;
};

/**
 * Sends a POST request with a JSON body and robust timeout/error handling.
 *
 * @template TResponse The expected response type after parsing.
 * @param {string} path - Path to append to the API base URL (e.g., "/chat").
 * @param {unknown} body - Serializable payload to send as JSON.
 * @param {{ timeoutMs?: number; headers?: Record<string, string> }} [options] -
 *   Optional settings for request timeout and additional headers.
 * @param {number} [options.timeoutMs=20000] - Timeout in milliseconds before aborting the request.
 * @param {Record<string, string>} [options.headers] - Additional headers to merge with defaults.
 * @returns {Promise<TResponse>} Resolves with the parsed JSON (or text) response.
 * @throws {Error} If the base API URL is not set, the request times out, or the response is non-OK.
 */
async function postJSON<TResponse>(
	path: string,
	body: unknown,
	{ timeoutMs = 20000, headers = {} }: FetchOptions = {}
): Promise<TResponse> {
	// Check if api url is set
	if (!API_BASE) {
		throw new Error("NEXT_PUBLIC_API_URL is not set");
	}

	const controller = new AbortController();
	const id = setTimeout(() => controller.abort(), timeoutMs);

	try {
		const res = await fetch(`${API_BASE}${path}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				...headers,
			},
			body: JSON.stringify(body),
			signal: controller.signal,
		});

		const contentType = res.headers.get("content-type") || "";
		const isJson = contentType.includes("application/json");

		if (!res.ok) {
			// Attempt to parse an error payload
			const isError = isJson ? await res.json().catch(() => null) : null;

			const message =
				(isError && (isError.error || isError.message)) ||
				`Request failed with status ${res.status}`;

			throw new Error(message);
		}

		return (isJson ? await res.json() : await res.text()) as TResponse;
	} catch (error) {
		if ((error as Error).name === "AbortError") {
			throw new Error("Request timed out");
		}
		throw error;
	} finally {
		clearTimeout(id);
	}
}
