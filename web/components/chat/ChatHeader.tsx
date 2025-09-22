"use client";

import { Button } from "@/components/ui/button";

type Props = {
  onReset: () => void;
};

export default function ChatHeader({ onReset }: Props) {
  return (
    <header className="flex items-center justify-between">
      <h1 className="text-xl font-semibold tracking-tight">Resume Chat</h1>
      <Button variant="outline" size="sm" onClick={onReset}>
        Reset
      </Button>
    </header>
  );
}
