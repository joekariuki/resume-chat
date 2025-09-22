"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatMessage } from "@/lib/schemas";
import { useEffect, useRef } from "react";
import MessageItem from "./MessageItem";

type Props = {
  messages: ChatMessage[];
};

export default function MessageList({ messages }: Props) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <ScrollArea className="h-[55vh] p-4">
      <ul className="space-y-4">
        {messages
          .filter((m) => m.role !== "system")
          .map((m, idx) => (
            <MessageItem key={idx} message={m} />
          ))}
        <div ref={endRef} />
      </ul>
    </ScrollArea>
  );
}
