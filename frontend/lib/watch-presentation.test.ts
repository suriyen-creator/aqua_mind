import { describe, expect, it } from "vitest";

import {
  buildWatchPresentation,
  getFarmerHeadline,
  getFreshnessMessage,
  getTopFactors,
  type WatchPresentationState,
} from "./watch-presentation";

function stateFor(score: number): WatchPresentationState {
  return {
    score,
    factors: [
      { name: "Wind speed", feature_key: "wind_speed", value: 5.5, unit: "km/h", impact: "increase", shap_value: 4.6 },
      { name: "SST anomaly", feature_key: "sst_anomaly", value: 1.2, unit: "°C", impact: "increase", shap_value: 3.1 },
      { name: "NDCI", feature_key: "ndci", value: 0.18, unit: "index", impact: "decrease", shap_value: -2.2 },
    ],
    evidence: {
      satelliteStatus: "unavailable",
      fieldVerificationCount: 0,
      apiStatus: "mocked",
    },
  };
}

describe("watch presentation", () => {
  it("builds a normal-band narrative for score 30", () => {
    const presentation = buildWatchPresentation(stateFor(30));

    expect(presentation.band.key).toBe("normal");
    expect(presentation.plainLanguageExplanation).toContain("ติดตามปกติ");
    expect(presentation.farmerResponseProtocol).toContain("เฝ้าดูสภาพน้ำตามปกติ");
    expect(presentation.evidenceWarnings).toContain("ยังไม่มีการยืนยันภาคสนาม จึงไม่ควรสรุปว่าเกิดบลูมแล้ว");
  });

  it("builds a watch-band narrative and protocol for score 56", () => {
    const presentation = buildWatchPresentation(stateFor(56));

    expect(presentation.band.key).toBe("watch");
    expect(presentation.plainLanguageExplanation).toContain("เฝ้าระวัง");
    expect(presentation.farmerResponseProtocol).toContain("เพิ่มความถี่ในการดูบ่อหรือพื้นที่");
    expect(presentation.farmerResponseProtocol).toContain("เพิ่มการตรวจภาคสนาม เพราะหลักฐานดาวเทียมยังไม่พร้อมหรือไม่สดใหม่");
  });

  it("builds an urgent protocol for score 82", () => {
    const presentation = buildWatchPresentation(stateFor(82));

    expect(presentation.band.key).toBe("urgent");
    expect(presentation.plainLanguageExplanation).toContain("รีบตรวจเพิ่ม");
    expect(presentation.farmerResponseProtocol).toContain("ตรวจ DO, pH, อุณหภูมิ และความเค็ม หากมีอุปกรณ์");
    expect(presentation.farmerResponseProtocol).toContain("ห้ามสรุปว่าเป็นพิษจากข้อมูลโมเดลอย่างเดียว");
  });

  it("reorders top-factor cards when SHAP ranking changes", () => {
    const factors = stateFor(56).factors;
    expect(getTopFactors(factors).map((factor) => factor.displayName)).toEqual([
      "ความเร็วลม",
      "อุณหภูมิผิวน้ำทะเล",
      "สัญญาณสีของน้ำจากดาวเทียม",
    ]);

    factors[2].shap_value = 8.4;
    expect(getTopFactors(factors).map((factor) => factor.displayName)).toEqual([
      "สัญญาณสีของน้ำจากดาวเทียม",
      "ความเร็วลม",
      "อุณหภูมิผิวน้ำทะเล",
    ]);
  });

  it("updates factor language when a feature value changes", () => {
    const factors = stateFor(56).factors;
    const calmWindDescription = getTopFactors(factors)[0].description;

    factors[0].value = 16;
    const strongWindDescription = getTopFactors(factors)[0].description;

    expect(calmWindDescription).toContain("ลมค่อนข้างอ่อน");
    expect(strongWindDescription).toContain("ลมค่อนข้างแรง");
  });

  it("builds farmer headlines for all four score states", () => {
    expect(getFarmerHeadline(49)).toBe("เฝ้าดูตามปกติ");
    expect(getFarmerHeadline(50)).toBe("ควรตรวจน้ำเพิ่มวันนี้");
    expect(getFarmerHeadline(69)).toBe("ควรตรวจน้ำเพิ่มวันนี้");
    expect(getFarmerHeadline(70)).toBe("ควรตรวจน้ำทันที");
    expect(getFarmerHeadline(null)).toBe("ข้อมูลยังไม่พอ—ให้ตรวจน้ำหน้างาน");
  });

  it("keeps immediate actions and plain-language factors safe when score is missing", () => {
    const presentation = buildWatchPresentation({
      ...stateFor(30),
      score: null,
      factors: [],
      evidence: { satelliteStatus: "unavailable", fieldVerificationCount: 0, apiStatus: "error" },
    });

    expect(presentation.farmerStatus).toBe("insufficient");
    expect(presentation.immediateActions).toHaveLength(3);
    expect(presentation.plainLanguageFactors).toHaveLength(0);
    expect(presentation.plainLanguageExplanation).toContain("ข้อมูลยังไม่พอ");
  });

  it("describes freshness without treating loading or stale data as safe", () => {
    expect(getFreshnessMessage({ updatedAt: null, dataAgeHours: null, apiStatus: "connecting", satelliteStatus: "simulated", loading: true })).toContain("กำลังรอข้อมูลล่าสุด");
    expect(getFreshnessMessage({ updatedAt: "2026-07-27T01:00:00Z", dataAgeHours: 50, apiStatus: "connected", satelliteStatus: "stale" })).toContain("ภาพดาวเทียมเก่า");
    expect(getFreshnessMessage({ updatedAt: "2026-07-27T01:00:00Z", dataAgeHours: null, apiStatus: "error", satelliteStatus: "unavailable" })).toContain("เชื่อมต่อข้อมูลล่าสุดไม่สำเร็จ");
  });
});
