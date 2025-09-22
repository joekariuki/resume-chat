"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { KeyboardEvent } from "react";

type Props = {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  loading?: boolean;
};

export default function ChatInput({ value, onChange, onSubmit, loading }: Props) {
  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  }

  return (
    <div className="flex flex-col gap-2 w-full">
      <div className="flex items-end gap-3 w-full">
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="min-h-[44px] max-h-40"
        />
        <Button onClick={onSubmit} disabled={loading || !value.trim()}>
          {loading ? "Sending..." : "Send"}
        </Button>
      </div>
      <Separator />
      <p className="text-xs text-muted-foreground">Press Enter to send, Shift+Enter for a new line.</p>
    </div>
  );
}
