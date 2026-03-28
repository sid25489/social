export default function MessagingPage() {
  return (
    <div className="flex h-screen flex-col">
      <div className="p-4 border-b border-border font-bold sticky top-0 bg-background/80 backdrop-blur z-10">Messages</div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="flex justify-end"><div className="bg-primary text-primary-foreground p-3 rounded-2xl rounded-tr-none max-w-[80%]">Hey, what's up?</div></div>
        <div className="flex justify-start"><div className="bg-accent p-3 rounded-2xl rounded-tl-none max-w-[80%]">Just testing the new UI, looks awesome!</div></div>
      </div>
      <div className="p-4 border-t border-border mt-auto mb-16 md:mb-0">
        <input placeholder="Type a message..." className="w-full bg-accent rounded-full px-4 py-2 outline-none focus:ring-2 focus:ring-primary" />
      </div>
    </div>
  );
}
