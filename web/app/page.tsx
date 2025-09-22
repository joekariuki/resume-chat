import ChatPanel from "@/components/chat/ChatPanel";

export default function Home() {
  return (
    <div className="min-h-screen w-full bg-background text-foreground">
      <div className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-6 sm:px-6 lg:px-8">
        <ChatPanel />
      </div>
    </div>
  );
}
