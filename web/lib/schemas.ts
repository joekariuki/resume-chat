import { z } from "zod";

export const chatMessageSchema = z.object({
	role: z.enum(["user", "assistant", "system"]),
	content: z.string().min(1, "Message cannot be empty"),
});

export const chatRequestSchema = z.object({
	message: z.string(),
	history: z.array(chatMessageSchema).optional(),
});

export const chatResponseSchema = z.object({
	reply: z.string(),
	handled: z.boolean(),
});

export const contactRequestSchema = z.object({
	name: z.string().min(1, "Name is required"),
	email: z.email("Invalid email"),
	message: z.string().min(1, "Message is required"),
	phone: z.string().optional(),
});

export const contactResponseSchema = z.object({
	success: z.boolean(),
});

// Types
export type ChatMessage = z.infer<typeof chatMessageSchema>;
export type ChatRequest = z.infer<typeof chatRequestSchema>;
export type ChatResponse = z.infer<typeof chatResponseSchema>;
export type ContactRequest = z.infer<typeof contactRequestSchema>;
export type ContactResponse = z.infer<typeof contactResponseSchema>;
