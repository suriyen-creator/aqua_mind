import {
  ASSISTANT_DISCLAIMER,
  ASSISTANT_SUGGESTIONS,
  buildMockReply,
  buildGeminiContents,
  buildGeminiSystemInstruction,
  buildOllamaMessages,
  type AssistantContext,
  type AssistantMessage,
  type AssistantRequest,
  type AssistantResponse,
} from "../../../../lib/assistant";

const PROVIDER_TIMEOUT_MS = 20_000;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function parseRequest(value: unknown): AssistantRequest | string {
  if (!isRecord(value)) return "รูปแบบคำขอไม่ถูกต้อง";
  if (typeof value.message !== "string") return "ต้องส่ง message เป็นข้อความ";

  const message = value.message.trim();
  if (message.length < 1 || message.length > 500) {
    return "message ต้องมีความยาว 1–500 ตัวอักษร";
  }

  if (!Array.isArray(value.history) || value.history.some((item) => {
    if (!isRecord(item)) return true;
    return !((item.role === "user" || item.role === "assistant") && typeof item.content === "string");
  })) {
    return "history ต้องเป็นรายการข้อความที่มี role และ content ถูกต้อง";
  }

  const history = value.history as Array<{ role: "user" | "assistant"; content: string }>;
  if (!isRecord(value.context)) return "ต้องส่ง context ของสถานี";
  const rawContext = value.context;
  if (
    typeof rawContext.stationId !== "string" ||
    typeof rawContext.location !== "string" ||
    typeof rawContext.watchLevel !== "string" ||
    typeof rawContext.updatedAt !== "string" ||
    rawContext.scoreIsProbability !== false ||
    (!((rawContext.score === null) || (typeof rawContext.score === "number" && Number.isFinite(rawContext.score)))) ||
    !isStringArray(rawContext.actions) ||
    !isStringArray(rawContext.evidenceWarnings)
  ) {
    return "context ไม่ครบหรือมีชนิดข้อมูลไม่ถูกต้อง";
  }

  const context: AssistantContext = {
    stationId: rawContext.stationId,
    location: rawContext.location,
    watchLevel: rawContext.watchLevel,
    score: rawContext.score,
    scoreIsProbability: false,
    updatedAt: rawContext.updatedAt,
    actions: rawContext.actions,
    evidenceWarnings: rawContext.evidenceWarnings,
  };

  return {
    message,
    history: history.slice(-8) as AssistantMessage[],
    context,
  };
}

function jsonError(detail: string, status: number) {
  return Response.json({ detail }, { status });
}

async function requestOllama(request: AssistantRequest): Promise<string> {
  const baseUrl = process.env.AQUAMIND_OLLAMA_BASE_URL?.replace(/\/$/, "");
  const model = process.env.AQUAMIND_OLLAMA_MODEL?.trim();
  if (!baseUrl || !model) throw new Error("Ollama is not configured");

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), PROVIDER_TIMEOUT_MS);
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    const apiKey = process.env.AQUAMIND_OLLAMA_API_KEY?.trim();
    if (apiKey) headers.Authorization = `Bearer ${apiKey}`;

    const response = await fetch(`${baseUrl}/api/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        model,
        messages: buildOllamaMessages(request),
        stream: false,
      }),
      signal: controller.signal,
      cache: "no-store",
    });
    if (!response.ok) throw new Error("Ollama provider error");

    const payload = (await response.json()) as unknown;
    if (!isRecord(payload) || !isRecord(payload.message) || typeof payload.message.content !== "string") {
      throw new Error("Ollama response was incomplete");
    }
    const reply = payload.message.content.trim();
    if (!reply) throw new Error("Ollama response was empty");
    return reply;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function requestGemini(request: AssistantRequest): Promise<string> {
  const apiKey = process.env.AQUAMIND_GEMINI_API_KEY?.trim();
  const model = (process.env.AQUAMIND_GEMINI_MODEL?.trim() || "gemini-3.6-flash").replace(/^models\//, "");
  if (!apiKey || !model) throw new Error("Gemini is not configured");

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), PROVIDER_TIMEOUT_MS);
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": apiKey,
        },
        body: JSON.stringify({
          systemInstruction: {
            parts: [{ text: buildGeminiSystemInstruction(request.context) }],
          },
          contents: buildGeminiContents(request),
        }),
        signal: controller.signal,
        cache: "no-store",
      },
    );
    if (!response.ok) throw new Error("Gemini provider error");

    const payload = (await response.json()) as unknown;
    if (!isRecord(payload) || !Array.isArray(payload.candidates)) {
      throw new Error("Gemini response was incomplete");
    }
    const reply = payload.candidates
      .flatMap((candidate) => {
        if (!isRecord(candidate) || !isRecord(candidate.content) || !Array.isArray(candidate.content.parts)) return [];
        return candidate.content.parts
          .filter((part): part is Record<string, unknown> => isRecord(part) && typeof part.text === "string")
          .map((part) => part.text as string);
      })
      .join("\n")
      .trim();
    if (!reply) throw new Error("Gemini response was empty");
    return reply;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function POST(request: Request) {
  let rawBody: unknown;
  try {
    rawBody = await request.json();
  } catch {
    return jsonError("ส่ง JSON ไม่ถูกต้อง", 400);
  }

  const parsed = parseRequest(rawBody);
  if (typeof parsed === "string") return jsonError(parsed, 400);

  const configuredMode = process.env.AQUAMIND_ASSISTANT_MODE?.trim().toLowerCase();
  const mode = configuredMode === "ollama" || configuredMode === "gemini"
    ? configuredMode
    : "mock";

  if (mode === "mock") {
    const response: AssistantResponse = {
      reply: buildMockReply(parsed.message, parsed.context),
      mode: "mock",
      suggestions: ASSISTANT_SUGGESTIONS,
      disclaimer: ASSISTANT_DISCLAIMER,
    };
    return Response.json(response);
  }

  if (mode === "gemini") {
    try {
      const response: AssistantResponse = {
        reply: await requestGemini(parsed),
        mode: "gemini",
        suggestions: ASSISTANT_SUGGESTIONS,
        disclaimer: ASSISTANT_DISCLAIMER,
      };
      return Response.json(response);
    } catch {
      return jsonError("ผู้ช่วยเชื่อมต่อไม่ได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง", 502);
    }
  }

  try {
    const response: AssistantResponse = {
      reply: await requestOllama(parsed),
      mode: "ollama",
      suggestions: ASSISTANT_SUGGESTIONS,
      disclaimer: ASSISTANT_DISCLAIMER,
    };
    return Response.json(response);
  } catch {
    return jsonError("ผู้ช่วยเชื่อมต่อไม่ได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง", 502);
  }
}
