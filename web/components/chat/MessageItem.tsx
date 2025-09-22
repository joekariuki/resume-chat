"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { ChatMessage } from "@/lib/schemas";

type Props = {
  message: ChatMessage;
};

export default function MessageItem({ message }: Props) {
  const isAssistant = message.role === "assistant";
  return (
    <li className="flex gap-3">
      <Avatar className="h-7 w-7 mt-1">
        <AvatarFallback className="text-[10px]">
          {isAssistant ? "AI" : "You"}
        </AvatarFallback>
      </Avatar>
      <div className="max-w-[80%] rounded-lg border bg-white p-3 text-sm dark:bg-zinc-900">
        <pre className="whitespace-pre-wrap break-words font-sans">{message.content}</pre>
      </div>
    </li>
  );
}
