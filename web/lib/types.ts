/**
 * Shared chat-related TypeScript types used across the web application.
 *
 * These type definitions describe the structure of chat messages exchanged between
 * the user, assistant, and system, as well as the request/response payloads
 * used when communicating with the chat API.
 */

/**
 * A single message within a chat conversation.
 *
 * @property role - The role of the message sender ("user", "assistant", or "system").
 * @property content - The textual content of the message.
 */
export type ChatMessage = {
	role: "user" | "assistant" | "system";
	content: string;
};

/**
 * Payload sent to the chat API when requesting a response.
 *
 * @property message - The latest user input to be processed.
 * @property history - Optional prior messages providing conversational context.
 */
export type ChatRequest = {
	message: string;
	history?: ChatMessage[];
};

/**
 * Response returned by the chat API.
 *
 * @property reply - The assistant's response text.
 * @property handled - Whether the request was successfully handled by the API.
 */
export type ChatResponse = {
	reply: string;
	handled: boolean;
};

export type ContactRequest = {
	name: string;
	email: string;
	message: string;
	phone?: string;
};

export type ContactResponse = {
	success: boolean;
	// Other fields for API returns go here
};
