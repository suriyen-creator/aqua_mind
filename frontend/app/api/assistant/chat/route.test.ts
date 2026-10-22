import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";

const context = {
  stationId: "chonburi_01",
  location: "Chonburi Coast",
  watchLevel: "ควรตรวจน้ำเพิ่มวันนี้",
  score: 56,
  scoreIsProbability: false as const,
  updatedAt: "2026-07-27T01:00:00Z",
  actions: ["เพิ่มความถี่ในการดูพื้นที่", "ตรวจ DO และ pH", "สังเกตสีและกลิ่นน้ำ"],
  evidenceWarnings: ["ยังไม่มีการยืนยันภาคสนาม"],
};

function request(message: string, history: unknown[] = []) {
  return new Request("http://localhost/api/assistant/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history, context }),
  });
}

describe("POST /api/assistant/chat", () => {
  beforeEach(() => {
    delete process.env.AQUAMIND_ASSISTANT_MODE;
    delete process.env.AQUAMIND_OLLAMA_BASE_URL;
    delete process.env.AQUAMIND_OLLAMA_MODEL;
    delete process.env.AQUAMIND_OLLAMA_API_KEY;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it.each([
    ["วันนี้ต้องทำอะไร?", "เพิ่มความถี่ในการดูพื้นที่"],
    ["ควรวัดค่าอะไร?", "DO"],
    ["ถ้าปลาลอยหัวทำอย่างไร?", "ปลาลอยหัว"],
    ["ข้อมูลล่าสุดเมื่อไร?", "2026-07-27T01:00:00Z"],
  ])("answers the mock shortcut %s", async (message, expectedText) => {
    const response = await POST(request(message));
    const payload = await response.json();

    expect(response.status).toBe(200);
    expect(payload.mode).toBe("mock");
    expect(payload.reply).toContain(expectedText);
    expect(payload.suggestions).toHaveLength(4);
    expect(payload.disclaimer).toContain("ไม่แทนผลตรวจ");
  });

  it("rejects blank and overlong messages", async () => {
    expect((await POST(request("   "))).status).toBe(400);
    expect((await POST(request("x".repeat(501)))).status).toBe(400);
  });

  it("returns a deterministic scope response for unsupported questions", async () => {
    const response = await POST(request("ช่วยบอกผลตรวจทางการแพทย์ของปลาให้หน่อย"));
    const payload = await response.json();

    expect(response.status).toBe(200);
    expect(payload.reply).toContain("ช่วยได้จากข้อมูล");
    expect(payload.reply).not.toContain("Probability");
  });

  it("uses only the latest eight history messages and an optional bearer token for Ollama", async () => {
    process.env.AQUAMIND_ASSISTANT_MODE = "ollama";
    process.env.AQUAMIND_OLLAMA_BASE_URL = "http://ollama.internal/";
    process.env.AQUAMIND_OLLAMA_MODEL = "aqua-model";
    process.env.AQUAMIND_OLLAMA_API_KEY = "test-secret";
    const mockedFetch = vi.fn().mockResolvedValue(Response.json({ message: { content: "คำตอบจาก Ollama" } }));
    vi.stubGlobal("fetch", mockedFetch);
    const history = Array.from({ length: 10 }, (_, index) => ({ role: index % 2 ? "assistant" : "user", content: `history-${index}` }));

    const response = await POST(request("ควรวัดค่าอะไร?", history));
    const payload = await response.json();
    const [, init] = mockedFetch.mock.calls[0] as [string, RequestInit];
    const body = JSON.parse(String(init.body)) as { model: string; stream: boolean; messages: Array<{ role: string; content: string }> };

    expect(response.status).toBe(200);
    expect(payload.mode).toBe("ollama");
    expect(body.model).toBe("aqua-model");
    expect(body.stream).toBe(false);
    expect(body.messages).toHaveLength(10);
    expect(body.messages.slice(1, -1).map((item) => item.content)).toEqual([
      "history-2", "history-3", "history-4", "history-5", "history-6", "history-7", "history-8", "history-9",
    ]);
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer test-secret");
    expect(body.messages[0].content).toContain("scoreIsProbability: false");
  });

  it("omits authorization when the Ollama key is empty", async () => {
    process.env.AQUAMIND_ASSISTANT_MODE = "ollama";
    process.env.AQUAMIND_OLLAMA_BASE_URL = "http://127.0.0.1:11434";
    process.env.AQUAMIND_OLLAMA_MODEL = "aqua-model";
    process.env.AQUAMIND_OLLAMA_API_KEY = "";
    const mockedFetch = vi.fn().mockResolvedValue(Response.json({ message: { content: "ไม่มี key ก็ทำงานได้" } }));
    vi.stubGlobal("fetch", mockedFetch);

    await POST(request("ข้อมูลล่าสุดเมื่อไร?"));
    const [, init] = mockedFetch.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>).Authorization).toBeUndefined();
  });

  it("sends Gemini generateContent requests with server-side key and safe context", async () => {
    process.env.AQUAMIND_ASSISTANT_MODE = "gemini";
    process.env.AQUAMIND_GEMINI_MODEL = "gemini-3.6-flash";
    process.env.AQUAMIND_GEMINI_API_KEY = "gemini-test-secret";
    const mockedFetch = vi.fn().mockResolvedValue(Response.json({
      candidates: [{ content: { parts: [{ text: "คำตอบจาก Gemini" }] } }],
    }));
    vi.stubGlobal("fetch", mockedFetch);

    const response = await POST(request("วันนี้ต้องทำอะไร?", [
      { role: "assistant", content: "ข้อความต้อนรับ" },
      { role: "user", content: "ช่วยดูพื้นที่นี้" },
    ]));
    const payload = await response.json();
    const [url, init] = mockedFetch.mock.calls[0] as [string, RequestInit];
    const body = JSON.parse(String(init.body)) as {
      systemInstruction: { parts: Array<{ text: string }> };
      contents: Array<{ role: string; parts: Array<{ text: string }> }>;
    };

    expect(response.status).toBe(200);
    expect(payload.mode).toBe("gemini");
    expect(payload.reply).toBe("คำตอบจาก Gemini");
    expect(url).toBe("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent");
    expect((init.headers as Record<string, string>)["x-goog-api-key"]).toBe("gemini-test-secret");
    expect(body.systemInstruction.parts[0].text).toContain("scoreIsProbability: false");
    expect(body.systemInstruction.parts[0].text).toContain("Chonburi Coast");
    expect(body.contents).toEqual([
      { role: "user", parts: [{ text: "ช่วยดูพื้นที่นี้\nวันนี้ต้องทำอะไร?" }] },
    ]);
  });

  it("filters provider failures and secrets from the 502 response", async () => {
    process.env.AQUAMIND_ASSISTANT_MODE = "ollama";
    process.env.AQUAMIND_OLLAMA_BASE_URL = "https://secret-provider.example";
    process.env.AQUAMIND_OLLAMA_MODEL = "aqua-model";
    process.env.AQUAMIND_OLLAMA_API_KEY = "super-secret-key";
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("provider body with super-secret-key", { status: 500 })));

    const response = await POST(request("วันนี้ต้องทำอะไร?"));
    const body = await response.text();

    expect(response.status).toBe(502);
    expect(body).toContain("ผู้ช่วยเชื่อมต่อไม่ได้");
    expect(body).not.toContain("secret-provider.example");
    expect(body).not.toContain("super-secret-key");
  });
});
