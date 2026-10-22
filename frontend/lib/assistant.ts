export type AssistantRole = "user" | "assistant";

export interface AssistantMessage {
  role: AssistantRole;
  content: string;
}

export interface AssistantContext {
  stationId: string;
  location: string;
  watchLevel: string;
  score: number | null;
  scoreIsProbability: false;
  updatedAt: string;
  actions: string[];
  evidenceWarnings: string[];
}

export interface AssistantRequest {
  message: string;
  history: AssistantMessage[];
  context: AssistantContext;
}

export interface AssistantResponse {
  reply: string;
  mode: "mock" | "ollama" | "gemini";
  suggestions: string[];
  disclaimer: string;
}

export const ASSISTANT_SUGGESTIONS = [
  "วันนี้ต้องทำอะไร?",
  "ควรวัดค่าอะไร?",
  "ถ้าปลาลอยหัวทำอย่างไร?",
  "ข้อมูลล่าสุดเมื่อไร?",
];

export const ASSISTANT_DISCLAIMER =
  "คำตอบนี้ใช้ช่วยจัดลำดับการตรวจเท่านั้น ไม่แทนผลตรวจน้ำหรือคำแนะนำจากผู้เชี่ยวชาญหน้างาน";

export const OLLAMA_SYSTEM_PROMPT = `
คุณคือ AquaMind Assistant ผู้ช่วยผู้เลี้ยงปลาในบ่อและกระชัง ตอบภาษาไทยแบบง่าย กระชับ และสุภาพ
ใช้เฉพาะข้อมูลสถานะที่ระบบส่งให้และประวัติการสนทนา ห้ามแต่งค่าที่ไม่มีในบริบท
เรียก score ว่า “คะแนนดัชนีเฝ้าระวังสภาพแวดล้อม” หรือ “ดัชนี” เท่านั้น ห้ามเรียกว่า Probability หรือโอกาสเกิดเหตุการณ์
ห้ามยืนยันว่าเกิด Bloom หรือโรคจากคะแนน อาการ หรือข้อมูลดาวเทียมเพียงอย่างเดียว
ให้แนะนำการตรวจสี กลิ่น พฤติกรรมปลา และ DO, pH, อุณหภูมิ, ความเค็มเมื่อมีอุปกรณ์
ห้ามสั่งเปลี่ยนน้ำ ย้ายกระชัง ลดอาหาร ใช้ยา หรือมาตรการที่มีต้นทุนสูงจากข้อมูลชุดนี้เพียงอย่างเดียว
ถ้าพบปลาลอยหัวหรืออาการผิดปกติ ให้แนะนำตรวจหน้างานและติดต่อผู้เชี่ยวชาญตามความเหมาะสม
ถ้าข้อมูลไม่พอหรือเก่า ให้บอกตรง ๆ ว่ายังสรุปไม่ได้และควรตรวจพื้นที่จริง
ตอบเป็นคำแนะนำที่ทำได้ทันทีไม่เกิน 5 ข้อ และย้ำข้อจำกัดเมื่อจำเป็น
`.trim();

export const GEMINI_SYSTEM_PROMPT = OLLAMA_SYSTEM_PROMPT;

function normalizeMessage(message: string) {
  return message.trim().replace(/\s+/g, " ").toLowerCase();
}

function actionList(context: AssistantContext) {
  return context.actions.length
    ? context.actions.slice(0, 3)
    : [
        "ตรวจสี กลิ่น และความผิดปกติของน้ำ",
        "สังเกตพฤติกรรมปลา",
        "วัด DO, pH และอุณหภูมิ หากมีอุปกรณ์",
      ];
}

export function buildMockReply(message: string, context: AssistantContext) {
  const normalized = normalizeMessage(message);
  const actions = actionList(context);
  const location = context.location || context.stationId;

  if (normalized.includes("วันนี้ต้องทำอะไร") || normalized.includes("ต้องทำอะไรวันนี้")) {
    return `สำหรับ ${location} วันนี้:\n1. ${actions[0]}\n2. ${actions[1]}\n3. ${actions[2]}`;
  }

  if (normalized.includes("ควรวัดค่าอะไร") || normalized.includes("วัดค่าอะไร")) {
    return "เริ่มจาก DO ก่อน ถ้ามีอุปกรณ์ให้วัด pH อุณหภูมิ และความเค็มร่วมด้วย พร้อมดูสี กลิ่น และพฤติกรรมปลา การวัดซ้ำเวลาใกล้เคียงกันจะช่วยเปรียบเทียบได้";
  }

  if (normalized.includes("ปลาลอยหัว") || normalized.includes("ลอยหัว")) {
    return "ถ้าปลาลอยหัว ให้สังเกตว่าพบมากน้อยแค่ไหนและตรวจ DO ทันทีถ้ามีอุปกรณ์ จากนั้นตรวจ pH อุณหภูมิ สี และกลิ่นของน้ำ หากยังผิดปกติหรือปลามีอาการมากขึ้น ให้ติดต่อผู้เชี่ยวชาญ อย่าเพิ่งเปลี่ยนน้ำ ย้ายกระชัง หรือลดอาหารจากอาการเดียวโดยยังไม่มีผลตรวจ";
  }

  if (normalized.includes("ข้อมูลล่าสุด") || normalized.includes("อัปเดต") || normalized.includes("update")) {
    return `ข้อมูลของ ${location} ล่าสุดตามหน้าจอ: ${context.updatedAt || "ยังไม่มีเวลาที่ระบุได้"} ระดับการเฝ้าระวังตอนนี้คือ ${context.watchLevel}`;
  }

  return `ผมช่วยได้จากข้อมูลของ ${location} ในหน้าจอนี้เท่านั้น ตอนนี้ระดับคือ ${context.watchLevel} และ${context.score === null ? "ยังไม่มีคะแนนที่ใช้สรุปได้" : "มีคะแนนดัชนีเฝ้าระวัง"} กรุณาถามเรื่องงานตรวจวันนี้ ค่าที่ควรวัด อาการปลาลอยหัว หรือเวลาข้อมูลล่าสุด`;
}

export function buildOllamaContext(context: AssistantContext) {
  return [
    `stationId: ${context.stationId}`,
    `location: ${context.location}`,
    `watchLevel: ${context.watchLevel}`,
    `score: ${context.score === null ? "ไม่มีคะแนน" : context.score}`,
    `scoreIsProbability: false`,
    `updatedAt: ${context.updatedAt}`,
    `actions: ${context.actions.join(" | ") || "ไม่มีคำแนะนำ"}`,
    `evidenceWarnings: ${context.evidenceWarnings.join(" | ") || "ไม่มีข้อความเตือน"}`,
  ].join("\n");
}

export function buildOllamaMessages(request: AssistantRequest) {
  return [
    {
      role: "system" as const,
      content: `${OLLAMA_SYSTEM_PROMPT}\n\nข้อมูลหน้าจอที่อนุญาตให้ใช้:\n${buildOllamaContext(request.context)}`,
    },
    ...request.history.slice(-8),
    { role: "user" as const, content: request.message },
  ];
}

export function buildGeminiSystemInstruction(context: AssistantContext) {
  return `${GEMINI_SYSTEM_PROMPT}\n\nข้อมูลหน้าจอที่อนุญาตให้ใช้:\n${buildOllamaContext(context)}`;
}

export function buildGeminiContents(request: AssistantRequest) {
  const turns = request.history.slice(-8).map((message) => ({
    role: message.role === "assistant" ? "model" as const : "user" as const,
    text: message.content,
  }));

  turns.push({ role: "user", text: request.message });

  const contents: Array<{ role: "user" | "model"; parts: Array<{ text: string }> }> = [];
  for (const turn of turns) {
    const previous = contents[contents.length - 1];
    if (!previous && turn.role === "model") continue;
    if (previous?.role === turn.role) {
      previous.parts[0].text += `\n${turn.text}`;
      continue;
    }
    contents.push({ role: turn.role, parts: [{ text: turn.text }] });
  }
  return contents;
}
