export type SatelliteStatus = "available" | "stale" | "unavailable" | "simulated";
export type PresentationApiStatus = "connected" | "mocked" | "error" | "connecting";

export interface WatchFactor {
  name: string;
  feature_key?: string | null;
  value: number;
  unit: string;
  impact: "increase" | "decrease" | "none";
  shap_value?: number | null;
  plain_language?: string | null;
}

export interface WatchEvidence {
  satelliteStatus: SatelliteStatus;
  fieldVerificationCount: number;
  apiStatus: PresentationApiStatus;
}

export interface WatchPresentationState {
  score: number | null;
  factors: WatchFactor[];
  evidence: WatchEvidence;
  freshness?: FreshnessState;
}

export interface ScoreBand {
  key: "normal" | "watch" | "urgent";
  range: string;
  label: string;
}

export interface PresentedFactor {
  factor: WatchFactor;
  rank: number;
  displayName: string;
  shapValue: number;
  description: string;
}

export interface WatchPresentation {
  band: ScoreBand | null;
  farmerStatus: "normal" | "watch" | "urgent" | "insufficient";
  farmerHeadline: string;
  farmerDescription: string;
  immediateActions: string[];
  plainLanguageFactors: string[];
  freshnessMessage: string;
  topFactors: PresentedFactor[];
  evidenceWarnings: string[];
  plainLanguageExplanation: string;
  farmerResponseProtocol: string[];
}

export interface FreshnessState {
  updatedAt: string | null;
  dataAgeHours: number | null;
  apiStatus: PresentationApiStatus;
  satelliteStatus: SatelliteStatus;
  loading?: boolean;
}

const SCORE_BANDS: ScoreBand[] = [
  { key: "normal", range: "0–49", label: "ติดตามปกติ" },
  { key: "watch", range: "50–69", label: "เฝ้าระวัง" },
  { key: "urgent", range: "70–100", label: "รีบตรวจเพิ่ม" },
];

const FEATURE_NAMES: Record<string, string> = {
  wind_speed: "ความเร็วลม",
  wind_speed_mean_d0_3: "ความเร็วลม",
  sst_anomaly: "อุณหภูมิผิวน้ำทะเล",
  sst_at_issue: "อุณหภูมิผิวน้ำทะเล",
  water_temp: "อุณหภูมิน้ำ",
  ndci: "สัญญาณสีของน้ำจากดาวเทียม",
  ndci_latest: "สัญญาณสีของน้ำจากดาวเทียม",
  ndwi: "สัญญาณพื้นที่น้ำจากดาวเทียม",
  salinity: "ความเค็ม",
  rainfall: "ปริมาณฝน",
  precipitation_sum_d0_3: "ปริมาณฝน",
};

function normalizedFeatureKey(factor: WatchFactor) {
  return (factor.feature_key ?? factor.name)
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
}

function directionText(shapValue: number) {
  return shapValue >= 0 ? "มีส่วนดันดัชนีขึ้น" : "มีส่วนกดดัชนีลง";
}

export function getFarmerStatus(score: number | null) {
  if (score === null || !Number.isFinite(score)) return "insufficient" as const;
  if (score >= 70) return "urgent" as const;
  if (score >= 50) return "watch" as const;
  return "normal" as const;
}

export function getFarmerHeadline(score: number | null) {
  switch (getFarmerStatus(score)) {
    case "normal":
      return "เฝ้าดูตามปกติ";
    case "watch":
      return "ควรตรวจน้ำเพิ่มวันนี้";
    case "urgent":
      return "ควรตรวจน้ำทันที";
    default:
      return "ข้อมูลยังไม่พอ—ให้ตรวจน้ำหน้างาน";
  }
}

function getFarmerDescription(score: number | null) {
  switch (getFarmerStatus(score)) {
    case "normal":
      return "สัญญาณที่มีอยู่ยังไม่ชี้ว่าต้องเพิ่มมาตรการพิเศษ ให้ติดตามตามรอบปกติ";
    case "watch":
      return "วันนี้ควรเพิ่มการสังเกตและตรวจค่าพื้นฐาน เพื่อประกอบการตัดสินใจของผู้ดูแลพื้นที่";
    case "urgent":
      return "ควรตรวจหน้างานโดยเร็ว โดยใช้ผลตรวจน้ำและอาการของปลาเป็นหลักก่อนตัดสินใจ";
    default:
      return "ระบบยังสรุปสถานการณ์ไม่ได้ ให้ตรวจสี กลิ่น พฤติกรรมปลา และค่าพื้นฐานในพื้นที่จริง";
  }
}

export function getScoreBand(score: number): ScoreBand {
  if (score >= 70) return SCORE_BANDS[2];
  if (score >= 50) return SCORE_BANDS[1];
  return SCORE_BANDS[0];
}

export function getFeatureDisplayName(factor: WatchFactor) {
  const key = normalizedFeatureKey(factor);
  const mapped = Object.entries(FEATURE_NAMES).find(([candidate]) => key.includes(candidate));
  return mapped?.[1] ?? factor.name;
}

export function getFactorDescription(factor: WatchFactor, shapValue = factor.shap_value ?? 0) {
  const key = normalizedFeatureKey(factor);
  const positive = shapValue >= 0;

  if (key.includes("wind")) {
    const windCondition = factor.value <= 8 ? "ลมค่อนข้างอ่อน" : "ลมค่อนข้างแรง";
    return `${windCondition} และในโมเดล${positive ? "มีส่วนดันดัชนีขึ้น" : "มีส่วนกดดัชนีลง"}`;
  }
  if (key.includes("sst") || key.includes("water_temp") || key.includes("temperature")) {
    const temperatureCondition = factor.value >= 1 ? "อุณหภูมิค่อนข้างสูงกว่าค่าฐาน" : "อุณหภูมิใกล้ค่าฐาน";
    return `${temperatureCondition} และในโมเดล${positive ? "มีส่วนดันดัชนีขึ้น" : "มีส่วนกดดัชนีลง"}`;
  }
  if (key.includes("ndci")) {
    const waterColorCondition = factor.value >= 0.15 ? "สัญญาณสีของน้ำค่อนข้างเด่น" : "สัญญาณสีของน้ำยังไม่เด่น";
    return `${waterColorCondition} และในโมเดล${positive ? "มีส่วนดันดัชนีขึ้น" : "มีส่วนกดดัชนีลง"}`;
  }
  if (key.includes("ndwi")) {
    return positive
      ? "สัญญาณพื้นที่น้ำมีส่วนสัมพันธ์กับคะแนนที่สูงขึ้นในโมเดล"
      : "สัญญาณพื้นที่น้ำมีส่วนกดคะแนนในโมเดลรอบนี้";
  }
  if (key.includes("salinity")) {
    return positive
      ? "ความเค็มมีส่วนสัมพันธ์กับคะแนนดัชนีที่สูงขึ้นในโมเดล"
      : "ความเค็มมีส่วนกดคะแนนดัชนีในโมเดลรอบนี้";
  }
  if (key.includes("rain") || key.includes("precipitation")) {
    return positive
      ? "ปริมาณฝนมีส่วนหนุนคะแนนดัชนีในแบบจำลอง"
      : "ปริมาณฝนมีส่วนกดคะแนนดัชนีในแบบจำลอง";
  }

  return `${getFeatureDisplayName(factor)} ${directionText(shapValue)} ในโมเดลรอบนี้`;
}

export function getTopFactors(factors: WatchFactor[]): PresentedFactor[] {
  return factors
    .filter((factor) => factor.shap_value !== null && factor.shap_value !== undefined)
    .slice()
    .sort((left, right) => Math.abs(right.shap_value ?? 0) - Math.abs(left.shap_value ?? 0))
    .slice(0, 3)
    .map((factor, index) => {
      const shapValue = factor.shap_value ?? 0;
      return {
        factor,
        rank: index + 1,
        displayName: getFeatureDisplayName(factor),
        shapValue,
        description: getFactorDescription(factor, shapValue),
      };
    });
}

export function getEvidenceWarnings(evidence: WatchEvidence) {
  const warnings: string[] = [];

  if (evidence.satelliteStatus === "unavailable") {
    warnings.push("รอบนี้ไม่มีภาพดาวเทียม จึงควรตรวจสภาพน้ำในพื้นที่จริงประกอบ");
  } else if (evidence.satelliteStatus === "stale") {
    warnings.push("ภาพดาวเทียมที่มีอยู่เก่า จึงควรยืนยันสภาพน้ำหน้างานก่อนตัดสินใจ");
  }

  if (evidence.fieldVerificationCount === 0) {
    warnings.push("ยังไม่มีการยืนยันภาคสนาม จึงไม่ควรสรุปว่าเกิดบลูมแล้ว");
  }
  if (evidence.apiStatus === "error") {
    warnings.push("การเชื่อมต่อข้อมูลมีปัญหา ควรตรวจข้อมูลต้นทางอีกครั้ง");
  }
  if (evidence.apiStatus === "connecting") {
    warnings.push("กำลังรอข้อมูลล่าสุด จึงยังไม่ควรสรุปว่าสถานการณ์ปกติ");
  }
  if (evidence.apiStatus === "mocked") {
    warnings.push("โหมดทดสอบใช้ข้อมูลจำลองเพื่อดูการแสดงผลเท่านั้น");
  }

  return warnings;
}

export function getPlainLanguageFactors(factors: WatchFactor[]) {
  const relevantFactors = getTopFactors(factors).map((item) => item.factor);
  const fallbackFactors = relevantFactors.length ? relevantFactors : factors.slice(0, 3);

  return fallbackFactors.map((factor) => {
    if (factor.plain_language?.trim()) return factor.plain_language.trim();

    const key = normalizedFeatureKey(factor);
    if (key.includes("wind")) {
      return factor.value <= 8 ? "ลมอ่อน น้ำอาจนิ่งกว่าปกติ" : "ลมแรง ควรสังเกตการเปลี่ยนแปลงของน้ำ";
    }
    if (key.includes("sst") || key.includes("water_temp") || key.includes("temperature")) {
      return factor.value >= 1 ? "น้ำอุ่นกว่าค่าฐาน" : "อุณหภูมิน้ำใกล้ค่าฐาน";
    }
    if (key.includes("ndci")) {
      return factor.value >= 0.15 ? "สีน้ำหรือความขุ่นเปลี่ยนไปจากปกติ" : "สีน้ำยังไม่เด่นจากข้อมูลดาวเทียม";
    }
    if (key.includes("rain") || key.includes("precipitation")) {
      return factor.value > 0 ? "มีฝนในช่วงข้อมูล ควรสังเกตน้ำหลังฝน" : "ยังไม่พบสัญญาณฝนเด่นในช่วงข้อมูล";
    }
    if (key.includes("salinity")) return "ความเค็มเป็นปัจจัยที่ควรวัดประกอบ";
    return `ควรสังเกต${getFeatureDisplayName(factor)} ในพื้นที่จริง`;
  });
}

export function getImmediateActions(score: number | null, evidence?: WatchEvidence) {
  const status = getFarmerStatus(score);
  const actions = status === "urgent"
    ? [
        "ตรวจสี กลิ่น และความผิดปกติของน้ำทันที",
        "วัด DO, pH, อุณหภูมิ และความเค็ม หากมีอุปกรณ์",
        "สังเกตปลาลอยหัวหรือพฤติกรรมผิดปกติ แล้วติดต่อผู้เชี่ยวชาญเมื่อพบความผิดปกติ",
      ]
    : status === "watch"
      ? [
          "เพิ่มความถี่ในการดูบ่อหรือพื้นที่วันนี้",
          "ตรวจสี กลิ่น พฤติกรรมปลา และค่าพื้นฐานของน้ำ",
          "หลังฝนตกหรือช่วงน้ำนิ่ง ให้ตรวจซ้ำและบันทึกผล",
        ]
      : status === "normal"
        ? [
            "เฝ้าดูสี กลิ่น และการเปลี่ยนแปลงของน้ำตามปกติ",
            "สังเกตพฤติกรรมปลาและตรวจน้ำตามรอบที่ใช้อยู่",
            "บันทึกสิ่งผิดปกติไว้เปรียบเทียบกับรอบถัดไป",
          ]
        : [
            "ตรวจสี กลิ่น และการเปลี่ยนแปลงของน้ำหน้างาน",
            "สังเกตพฤติกรรมปลา โดยเฉพาะการลอยหัวหรือรวมกลุ่มผิดปกติ",
            "วัด DO, pH และอุณหภูมิ หากมีอุปกรณ์",
          ];

  if (evidence?.satelliteStatus === "unavailable" || evidence?.satelliteStatus === "stale") {
    actions[2] = "เพิ่มการตรวจภาคสนาม เพราะภาพดาวเทียมยังไม่พร้อมหรือไม่สดใหม่";
  }
  return actions;
}

export function getFreshnessMessage(state: FreshnessState) {
  if (state.loading || state.apiStatus === "connecting") {
    return "กำลังรอข้อมูลล่าสุด—ยังไม่ควรสรุปสถานการณ์";
  }
  if (state.apiStatus === "error") {
    return "เชื่อมต่อข้อมูลล่าสุดไม่สำเร็จ—ให้ตรวจข้อมูลหน้างานก่อน";
  }
  if (!state.updatedAt || state.updatedAt === "waiting for API") {
    return "ยังไม่มีเวลาข้อมูลที่ยืนยันได้—ให้ตรวจน้ำหน้างาน";
  }

  let message = "มีเวลาข้อมูลล่าสุดแล้ว";
  if (state.dataAgeHours === null || !Number.isFinite(state.dataAgeHours)) {
    message = `ข้อมูลล่าสุด: ${state.updatedAt} แต่ยังระบุอายุข้อมูลไม่ได้`;
  } else if (state.dataAgeHours < 1) {
    message = `ข้อมูลล่าสุดเมื่อประมาณ ${Math.max(1, Math.round(state.dataAgeHours * 60))} นาทีที่แล้ว`;
  } else if (state.dataAgeHours < 48) {
    message = `ข้อมูลล่าสุดเมื่อประมาณ ${state.dataAgeHours.toFixed(state.dataAgeHours < 10 ? 1 : 0)} ชั่วโมงที่แล้ว`;
  } else {
    message = `ข้อมูลล่าสุดเมื่อประมาณ ${Math.round(state.dataAgeHours / 24)} วันที่แล้ว`;
  }

  if (state.satelliteStatus === "stale") return `${message} ภาพดาวเทียมเก่า ควรตรวจหน้างานประกอบ`;
  if (state.satelliteStatus === "unavailable") return `${message} รอบนี้ไม่มีภาพดาวเทียมที่ใช้ยืนยันได้`;
  return message;
}

export function getPlainLanguageExplanation(state: WatchPresentationState) {
  if (state.score === null) {
    return `${getFarmerHeadline(null)} ${getFarmerDescription(null)}`;
  }
  const band = getScoreBand(state.score);
  const factors = getTopFactors(state.factors);
  const warnings = getEvidenceWarnings(state.evidence);
  const factorSummary = factors.slice(0, 2).map((factor) => factor.description).join(" ");
  const bandSummary = band.key === "normal"
    ? "ตอนนี้ค่าดัชนีอยู่ระดับติดตามปกติ"
    : band.key === "watch"
      ? "ตอนนี้ค่าดัชนีอยู่ระดับเฝ้าระวัง"
      : "ตอนนี้ค่าดัชนีอยู่ระดับรีบตรวจเพิ่ม";
  const evidenceSummary = warnings.find((warning) => !warning.includes("โหมดทดสอบ"));

  return [
    `${bandSummary} (${Math.round(state.score)}/100) สำหรับดัชนีเฝ้าระวังสภาพแวดล้อม`,
    factorSummary || "ปัจจัยที่ใช้คำนวณยังไม่เพียงพอให้สรุปเหตุผลเด่น",
    evidenceSummary,
    "ดัชนีนี้ไม่ใช่การยืนยันว่าเกิดบลูมแล้ว และควรใช้ร่วมกับการตรวจพื้นที่จริง",
  ].filter(Boolean).join(" ");
}

export function getFarmerResponseProtocol(state: WatchPresentationState) {
  if (state.score === null) {
    return [
      ...getImmediateActions(null, state.evidence),
      "หากพบความผิดปกติชัดเจน ให้ติดต่อผู้เชี่ยวชาญพร้อมผลตรวจ",
    ];
  }
  const band = getScoreBand(state.score);
  const protocol = band.key === "normal"
    ? [
        "เฝ้าดูสภาพน้ำตามปกติ",
        "ตรวจน้ำตามรอบที่ใช้อยู่",
        "ยังไม่ต้องเพิ่มมาตรการพิเศษ",
      ]
    : band.key === "watch"
      ? [
          "เพิ่มความถี่ในการดูบ่อหรือพื้นที่",
          "ตรวจสี กลิ่น และความผิดปกติของน้ำ",
          "หลังฝนตกหนักหรือช่วงน้ำนิ่งให้ตรวจซ้ำ",
          "เตรียมช่องทางติดต่อผู้เชี่ยวชาญหากค่าดัชนีสูงขึ้น",
        ]
      : [
          "เพิ่มความถี่การตรวจทันที",
          "ตรวจ DO, pH, อุณหภูมิ และความเค็ม หากมีอุปกรณ์",
          "ตรวจบริเวณน้ำนิ่งหรือมุมอับก่อน",
          "หากพบปลาลอยหัว กลิ่นผิดปกติ หรือสีน้ำผิดปกติ ให้ติดต่อผู้เชี่ยวชาญ",
          "ห้ามสรุปว่าเป็นพิษจากข้อมูลโมเดลอย่างเดียว",
        ];

  if (state.evidence.satelliteStatus === "unavailable" || state.evidence.satelliteStatus === "stale") {
    protocol.push("เพิ่มการตรวจภาคสนาม เพราะหลักฐานดาวเทียมยังไม่พร้อมหรือไม่สดใหม่");
  }
  if (state.evidence.fieldVerificationCount === 0) {
    protocol.push("ยืนยันด้วยการตรวจพื้นที่จริง เพราะยังไม่มีผลตรวจภาคสนามยืนยัน");
  }

  return protocol;
}

export function buildWatchPresentation(state: WatchPresentationState): WatchPresentation {
  const band = state.score === null ? null : getScoreBand(state.score);
  const evidenceWarnings = getEvidenceWarnings(state.evidence);
  return {
    band,
    farmerStatus: getFarmerStatus(state.score),
    farmerHeadline: getFarmerHeadline(state.score),
    farmerDescription: getFarmerDescription(state.score),
    immediateActions: getImmediateActions(state.score, state.evidence),
    plainLanguageFactors: getPlainLanguageFactors(state.factors),
    freshnessMessage: getFreshnessMessage(state.freshness ?? {
      updatedAt: null,
      dataAgeHours: null,
      apiStatus: state.evidence.apiStatus,
      satelliteStatus: state.evidence.satelliteStatus,
    }),
    topFactors: getTopFactors(state.factors),
    evidenceWarnings,
    plainLanguageExplanation: getPlainLanguageExplanation(state),
    farmerResponseProtocol: getFarmerResponseProtocol(state),
  };
}
