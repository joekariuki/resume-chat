"use client";

import { useState } from "react";
import type { ChatMessage } from "@/lib/schemas";
import {
	Card,
	CardContent,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

export default function ChatPanel() {
	const [messages, setMessages] = useState<ChatMessage[]>([
		{ role: "system", content: "You are a helpful assistant." },
	]);
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	async function sendMessage() {
		const trimmed = input.trim();
		if (!trimmed || loading) return;
		setError(null);
		setLoading(true);

		const userMsg: ChatMessage = { role: "user", content: trimmed };
		const history = messages.filter((m) => m.role !== "system");
		setMessages((prev) => [...prev, userMsg]);
		setInput("");

		try {
			const res = await fetch("/api/chat", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ message: trimmed, history }),
			});

			if (!res.ok) {
				const payload = await res.json().catch(() => null);
				const message =
					(payload && (payload as any).error) ||
					(payload && (payload as any).message) ||
					`Request failed with status ${res.status}`;
				setError(String(message));
				return;
			}

			const data = await res.json();
			const reply = String(data.reply ?? "");
			setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
		} catch (err: any) {
			setError(err?.message ?? "Unexpected error");
		} finally {
			setLoading(false);
		}
	}

	function resetChat() {
		setMessages([{ role: "system", content: "You are a helpful assistant." }]);
		setError(null);
		setInput("");
	}

	return (
		<Card className="rounded-xl">
			<CardHeader className="p-4 border-b">
				<CardTitle className="sr-only">Conversation</CardTitle>
				<ChatHeader onReset={resetChat} />
			</CardHeader>
			<CardContent className="p-0">
				<MessageList messages={messages} />
			</CardContent>

			{error && (
				<div className="border-t bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">
					{error}
				</div>
			)}

			<CardFooter className="flex flex-col gap-2 border-t p-4">
				<ChatInput
					value={input}
					onChange={setInput}
					onSubmit={() => void sendMessage()}
					loading={loading}
				/>
			</CardFooter>
		</Card>
	);
}
