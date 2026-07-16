# AquaMind Final Report V2 — รายการที่ต้องเพิ่มและแก้ไข

**อัปเดตล่าสุด:** 17 กรกฎาคม 2569  
**เอกสารต้นทางด้านแนวคิด:** `AquaMind_Proposal_Formatted.md`  
**หลักการ:** คงแกน Sentinel-2 + NDCI/NDWI + XGBoost + SHAP ตามข้อเสนอ และแยกสิ่งที่พิสูจน์แล้วออกจากสิ่งที่ยังเป็นเป้าหมาย

## 1. สถานะระบบที่ต้องเขียนให้ตรงกัน

| องค์ประกอบ | สถานะจริง | วิธีเขียนในรายงาน V2 |
|---|---|---|
| XGBoost inference | ทำงานแล้วกับโมเดลและ Feature สังเคราะห์ | เรียก `XGBoost Technical Demo` ไม่เรียกผลภาคสนาม |
| SHAP | คำนวณจริงต่อคำขอด้วย XGBoost `pred_contribs` | ระบุว่าเป็น SHAP ใน Raw-margin space และยังไม่ผ่าน Field validation |
| Sentinel-2/NDCI/NDWI pipeline | พัฒนาแล้วระดับ AOI prototype | Earth Search L2A + B03/B04/B05/B08 + SCL water mask; ยังไม่ผ่าน Field validation |
| Bangsaen vertical slice | เชื่อม Sentinel-2 และ Weather/Ocean forecast แล้ว | เรียก `Live Data Readiness` จนกว่าโมเดลจริงผ่าน Validation |
| กรณีไม่มีภาพที่ตรงกับโมเดล | ทำ Assessment gate แล้ว | ส่ง `risk_score=null`, ไม่รันโมเดล และแจ้งข้อมูลไม่เพียงพอ |
| Rule-based | ไม่ใช่แกนคำนวณความเสี่ยง | ใช้เฉพาะเกณฑ์ Data readiness/คำแนะนำความปลอดภัย ไม่แทน XGBoost |
| Frontend–Backend | เชื่อมผ่าน `/backend-api` แล้ว | ระบุ Loading/Error/Retry และ API integration |
| คุณภาพโค้ด | Backend 12 tests, Frontend lint/build ผ่าน | ใส่ผลวันที่ 17 กรกฎาคม 2569 |

## 2. ข้อความที่ต้องลบหรือแก้

- ลบข้อความว่า AquaMind ปัจจุบันเป็น “Rule-based risk screening”
- ลบตัวอย่าง `risk_score=49%` ของบางแสน เพราะข้อมูล Live context ยังไม่ครบ Feature schema
- แก้ข้อความว่า SHAP เป็น Preset/Rule เป็น “คำนวณจาก XGBoost จริงใน Technical Demo”
- แก้ข้อความว่า Frontend ยังไม่เชื่อม Backend, lint ไม่ผ่าน หรือ build ไม่ผ่าน
- แก้ข้อความว่า Weather/SST API ยังไม่มี เป็น “มี Current forecast และ Archived single-run backfill แล้ว โดยควบคุม Future leakage”
- ห้ามนำ NOAA VIIRS มาเรียกแทน Sentinel-2 NDCI/NDWI

## 3. ภาพรวมระบบที่ต้องเพิ่ม

```text
เส้นทางเป้าหมายตามข้อเสนอ
Sentinel-2 → Cloud mask → NDCI/NDWI + temporal features ─┐
Weather / Regional SST / Wind ──────────────────────────┤
Ground truth ────────────────────────────────────────────┘
                         ↓
                 Versioned XGBoost model
                         ↓
         Probability + Calibration + SHAP top 3
                         ↓
          Data age / Confidence / Assessment gate
                         ↓
       Dashboard + แนวทางตอบสนองของเกษตรกร 3–5 วัน

เส้นทางที่ทำงานใน MVP ปัจจุบัน
Synthetic feature scenario → XGBoost → SHAP → Dashboard
Earth Search Sentinel-2 + Open-Meteo → NDCI/NDWI/Forecast features
Ground truth gate → ไม่มี VERIFIED label จึงงด Probability และ SHAP
```

## 4. บทคัดย่อไทยและอังกฤษ

เพิ่มข้อเท็จจริงต่อไปนี้ทั้งสองภาษา:

- FastAPI และ Next.js ทำงานครบเส้นทาง
- Technical Demo โหลดโมเดล XGBoost และคำนวณ SHAP จริงต่อคำขอ
- Feature และโมเดลชุดนี้ยังอิงข้อมูลสังเคราะห์ จึงไม่ใช่หลักฐานความแม่นยำภาคสนาม
- Bangsaen vertical slice เชื่อมข้อมูลภายนอกเพื่อแสดง Data age และ provenance
- เมื่อไม่มี Sentinel-2/NDCI/NDWI ที่ตรงกับโมเดล ระบบไม่แสดงเปอร์เซ็นต์และไม่คำนวณ SHAP
- เป้าหมาย 3–5 วันยังต้องยืนยันด้วย Ground truth ที่แยกเวลาและพื้นที่

ตัวอย่างประโยคภาษาอังกฤษ:

> The MVP executes XGBoost inference and computes request-level SHAP contributions on synthetic technical scenarios. The Bangsaen live integration is used as a data-readiness layer; when model-compatible Sentinel-2 features are unavailable, AquaMind suppresses the probability and reports insufficient data.

## 5. รายละเอียด Software Specification ที่ต้องเพิ่ม

### Input ของ Model Technical Demo

- `ndci_mean_7d`
- `ndci_slope_7d`
- `sst_anomaly`
- `wind_speed_3d`
- `ndci_x_wind`

### Output สำคัญ

| ฟิลด์ | ความหมาย |
|---|---|
| `assessment_status` | `model_demo` หรือ `insufficient_data` |
| `risk_score` | Probability × 100; เป็น `null` เมื่อข้อมูลไม่พอ |
| `data_status` | `synthetic_model_demo` หรือ `live_context` |
| `analysis_method` | `xgboost_shap_demo` หรือ `insufficient_data` |
| `data_age_hours` | อายุข้อมูล Live context; ไม่มีความหมายกับ Scenario สังเคราะห์ |
| `confidence_score` | ไม่แสดงจนกว่าจะมีการ Validate/Calibrate |
| `imagery_status` | simulated/available/stale/unavailable |
| `features[].shap_value` | ผลของ Feature ต่อ Raw margin |
| `shap_output_space` | `raw_margin` ใน Technical Demo |
| `limitations` | ข้อจำกัดที่ต้องแสดงพร้อมผล |

## 6. การอธิบาย SHAP ที่ถูกต้อง

SHAP กลับมาเป็นส่วนหลักตามข้อเสนอ ไม่ใช่ข้อความที่กฎสร้างขึ้น โค้ดปัจจุบันใช้ XGBoost Booster คำนวณ `pred_contribs=True` แล้วตรวจว่า Base value + ผลรวม SHAP เมื่อนำผ่าน Sigmoid ให้ Probability เดียวกับโมเดล

ต้องเขียนกำกับว่า:

- SHAP ใน UI มีหน่วยเป็น Raw margin ไม่ใช่ “เปอร์เซ็นต์ที่เพิ่มขึ้น”
- ใช้แสดงทิศทางและอันดับปัจจัยของโมเดลเท่านั้น
- Technical Demo ยังไม่ยืนยันว่าปัจจัยดังกล่าวเป็นสาเหตุของ Bloom
- Live context จะไม่มี SHAP หาก Model inference ไม่ได้ทำงาน

## 7. กรณีไม่มีภาพ

Flow ที่ใช้อยู่:

1. ตรวจว่า Input มี Feature ภาพที่ตรงกับเวอร์ชันโมเดลหรือไม่
2. หากไม่มี ให้กำหนด `assessment_status=insufficient_data`
3. ตั้ง `risk_score=null`, `model_name=null`, `shap_output_space=null`
4. แสดง Data age และ provenance ของข้อมูลบริบทที่มี
5. แจ้งผู้ใช้ให้ตรวจ DO, pH, สีของน้ำ และเก็บตัวอย่างภาคสนาม
6. รอภาพ Sentinel-2 ที่ผ่าน Cloud mask หรือใช้ No-image model ที่ผ่าน Validation แยกในอนาคต

ข้อความตอบกรรมการ:

> ปัจจุบันยังไม่มีหลักฐานว่าโมเดลแม่นเมื่อไม่มีภาพ ระบบจึงไม่คำนวณเปอร์เซ็นต์จาก Weather/SST อย่างเดียว แต่ใช้ข้อมูลดังกล่าวตรวจความพร้อมและแจ้งให้ยืนยันภาคสนาม

## 8. ผลทดสอบล่าสุด

```text
Backend tests: 12 passed
Frontend ESLint: passed
Frontend production build: passed
XGBoost inference: passed
SHAP additivity check: passed
Scenario ordering low < medium < high: passed
Bangsaen insufficient-data suppression: passed
Sentinel duplicate-tile QC: passed
Missing report is not a negative label: passed
Archived forecast backfill without future leakage: passed
```

ค่าประมาณของ Technical Demo จากข้อมูลสังเคราะห์:

- Low ≈ 11.1%
- Medium ≈ 58.7%
- High ≈ 94.8%

ตัวเลขนี้ใช้แสดงว่า Model และ UI ทำงาน ไม่ใช่ Accuracy และไม่ใช่สถานการณ์บางแสนปัจจุบัน

## 9. หลักฐานที่ควรใส่ในรายงาน

- [ ] ภาพ XGBoost Technical Demo ที่มีป้าย Synthetic
- [ ] ภาพ SHAP top 3 และคำว่า Raw-margin
- [ ] ภาพ Bangsaen Live Data Readiness ที่ไม่แสดงเปอร์เซ็นต์
- [ ] ภาพ Data age, provenance และข้อจำกัด
- [ ] ตัวอย่าง JSON ที่ `risk_score` เป็น `null` เมื่อข้อมูลไม่ครบ
- [ ] ผล `pytest`, `npm run lint` และ `npm run build`

## 10. สิ่งที่ยังห้ามกล่าวอ้าง

- ยังไม่มีความแม่นยำภาคสนามของการพยากรณ์ 3–5 วัน
- ยังไม่มี Ground truth ที่จับคู่วัน เวลา พิกัด และชนิด/ความหนาแน่นแพลงก์ตอน
- ยังไม่มี Independent temporal/spatial validation และ Probability calibration
- มี Sentinel-2 ingestion/QC ระดับ AOI prototype แล้ว แต่ยังไม่มี Optical correction และ Field calibration ครบวงจร
- ยังไม่มี No-image model ที่ผ่าน Validation
- ยังไม่มีระบบแจ้งเตือน LINE/SMS/Email ใช้งานจริง
- SHAP ไม่ใช่หลักฐานเหตุและผล

## 11. ข้อมูลที่ทีมต้องกรอกเอง

- [ ] โทรศัพท์และอีเมลผู้พัฒนา
- [ ] ข้อมูลอาจารย์ที่ปรึกษา
- [ ] สถานศึกษาและที่อยู่
- [ ] GitHub/Live demo URL ถ้ามี
- [ ] ภาพหน้าจอและวันที่ทดสอบจริง

## 12. ข้อสรุปสำหรับ V2

V2 ควรนำเสนอ AquaMind เป็น **Prototype ตามสถาปัตยกรรม Sentinel-2 + XGBoost + SHAP** ที่ปัจจุบันพิสูจน์ Model/Explainability pipeline ด้วยข้อมูลสังเคราะห์ และพิสูจน์ Live data integration ที่บางแสนในระดับ Data readiness แล้ว เมื่อข้อมูลไม่ครบระบบจะงดผล แทนการเปลี่ยนแกนโครงการเป็น Rule-based scoring
