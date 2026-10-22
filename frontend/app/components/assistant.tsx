"use client";

import { FormEvent, useState } from "react";
import { Bot, RotateCcw, Send, User } from "lucide-react";
import {
  ASSISTANT_DISCLAIMER,
  ASSISTANT_SUGGESTIONS,
  type AssistantContext,
  type AssistantResponse,
} from "@/lib/assistant";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  mode?: AssistantResponse["mode"];
}

interface AssistantProps {
  context: AssistantContext;
}

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content: "สวัสดีครับ ผมช่วยเรียงลำดับงานตรวจจากสถานะพื้นที่นี้ได้ ลองเลือกคำถามด้านล่างได้เลย",
};

export default function Assistant({ context }: AssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [suggestions, setSuggestions] = useState(ASSISTANT_SUGGESTIONS);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [failedMessage, setFailedMessage] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState<AssistantResponse["mode"] | null>(null);

  async function requestReply(message: string, history: ChatMessage[]) {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          history: history.slice(-8).map(({ role, content }) => ({ role, content })),
          context,
        }),
      });
      if (!response.ok) throw new Error("assistant request failed");
      const payload = (await response.json()) as AssistantResponse;
      setMessages((current) => [
        ...current,
        { id: `${Date.now()}-assistant`, role: "assistant", content: payload.reply, mode: payload.mode },
      ]);
      setSuggestions(payload.suggestions.length ? payload.suggestions : ASSISTANT_SUGGESTIONS);
      setActiveMode(payload.mode);
      setFailedMessage(null);
    } catch {
      setError("ส่งคำถามไม่สำเร็จ ลองใหม่ได้โดยข้อความเดิมจะยังอยู่");
      setFailedMessage(message);
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(message: string) {
    const cleanMessage = message.trim();
    if (!cleanMessage || loading) return;
    const history = messages;
    setMessages((current) => [
      ...current,
      { id: `${Date.now()}-user`, role: "user", content: cleanMessage },
    ]);
    setDraft("");
    await requestReply(cleanMessage, history);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await sendMessage(draft);
  }

  async function retry() {
    if (!failedMessage || loading) return;
    const history = messages.slice(0, -1);
    await requestReply(failedMessage, history);
  }

  return (
    <section aria-labelledby="assistant-heading" className="rounded-[18px] border border-slate-200 bg-white p-4 shadow-none sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[12px] bg-sky-50 text-sky-700" aria-hidden="true">
            <Bot className="h-5 w-5" />
          </span>
          <div>
            <h2 id="assistant-heading" className="text-[20px] font-bold text-slate-900">AquaMind Assistant</h2>
            <p className="mt-0.5 text-[15px] leading-6 text-slate-600">ถามเรื่องงานตรวจจากข้อมูลของพื้นที่นี้</p>
          </div>
        </div>
        {activeMode === "mock" && (
          <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[13px] font-semibold text-amber-800">
            คำตอบจำลอง
          </span>
        )}
        {activeMode === "ollama" && (
          <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[13px] font-semibold text-emerald-800">
            ผู้ช่วยในเครื่อง
          </span>
        )}
        {activeMode === "gemini" && (
          <span className="rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[13px] font-semibold text-blue-800">
            Gemini
          </span>
        )}
      </div>

      <div role="log" aria-live="polite" aria-label="บทสนทนากับ AquaMind Assistant" className="mt-3 max-h-64 space-y-2.5 overflow-y-auto rounded-[12px] bg-slate-50 p-2.5">
        {messages.map((message) => (
          <div key={message.id} className={`flex gap-2 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            {message.role === "assistant" && <Bot className="mt-2 h-4 w-4 shrink-0 text-sky-700" aria-hidden="true" />}
            <div className={`max-w-[88%] whitespace-pre-line rounded-[12px] px-3 py-2.5 text-[15px] leading-6 ${message.role === "user" ? "bg-sky-700 text-white" : "border border-slate-200 bg-white text-slate-800"}`}>
              {message.content}
              {message.mode === "mock" && <span className="mt-1.5 block text-[12px] font-semibold text-amber-700">คำตอบจำลอง</span>}
            </div>
            {message.role === "user" && <User className="mt-2 h-4 w-4 shrink-0 text-sky-700" aria-hidden="true" />}
          </div>
        ))}
        {loading && <p className="px-6 text-[15px] text-slate-500" aria-label="กำลังรอคำตอบ">กำลังเตรียมคำตอบ…</p>}
      </div>

      <div className="mt-3 flex flex-wrap gap-2" aria-label="คำถามลัด">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => void sendMessage(suggestion)}
            disabled={loading}
            className="min-h-11 rounded-full border border-sky-200 bg-sky-50 px-3 text-[14px] font-medium text-sky-800 transition hover:bg-sky-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {suggestion}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="mt-3 flex flex-col gap-2 sm:flex-row">
        <label htmlFor="assistant-message" className="sr-only">พิมพ์คำถาม</label>
        <input
          id="assistant-message"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          maxLength={500}
          placeholder="เช่น วันนี้ต้องทำอะไร?"
          className="min-h-12 min-w-0 flex-1 rounded-[14px] border border-slate-300 bg-white px-4 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-600 focus:ring-2 focus:ring-sky-200"
        />
        <button
          type="submit"
          disabled={loading || !draft.trim()}
          className="inline-flex min-h-12 items-center justify-center gap-2 rounded-[14px] bg-sky-700 px-5 text-[15px] font-bold text-white transition hover:bg-sky-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-600"
        >
          <Send className="h-5 w-5" aria-hidden="true" /> ส่งคำถาม
        </button>
      </form>
      <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[14px] leading-5 text-slate-500">
        <p>{ASSISTANT_DISCLAIMER}</p>
        {error && (
          <button type="button" onClick={() => void retry()} disabled={loading} className="inline-flex min-h-11 items-center gap-1 font-bold text-amber-800 underline underline-offset-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600 disabled:opacity-50">
            <RotateCcw className="h-4 w-4" aria-hidden="true" /> ลองใหม่
          </button>
        )}
      </div>
      {error && <p role="alert" className="mt-2 text-[15px] font-semibold leading-6 text-amber-800">{error}</p>}
    </section>
  );
}
