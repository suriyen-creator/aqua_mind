# AquaMind — แผนปิดงานก่อนส่งรายงานฉบับสมบูรณ์

**อัปเดตล่าสุด:** 17 กรกฎาคม 2569  
**กำหนดส่ง:** 17 กรกฎาคม 2569  
**สถานะภาพรวม:** โค้ดพร้อมสาธิตในระดับ Technical Prototype งานวิกฤตที่เหลือคือรายงาน หลักฐาน และข้อมูลที่ทีมต้องกรอก

## 1. ความพร้อมปัจจุบัน

| ส่วนงาน | สถานะ | สิ่งที่พิสูจน์ได้ |
|---|---|---|
| Backend/API | ✅ พร้อมสาธิต | FastAPI, Model loading, Assessment gate และ API ทำงาน |
| XGBoost inference | ✅ Technical Demo | คำนวณ Probability จากโมเดลจริงบน Feature สังเคราะห์ |
| SHAP | ✅ Technical Demo | คำนวณ Contribution ต่อคำขอและผ่าน Additivity test |
| Frontend Dashboard | ✅ พร้อมสาธิต | เชื่อม API, Loading/Error/Retry, lint/build ผ่าน |
| Bangsaen vertical slice | ✅ Real-data readiness | ดึง Sentinel-2 L2A, NDCI/NDWI และ Weather/Ocean forecast จริง |
| No-image behavior | ✅ Safety gate | ไม่มี Input ภาพที่ตรงกับโมเดลแล้ว `risk_score=null` |
| Sentinel-2 AOI pipeline | ✅ Prototype | Earth Search COG + SCL water mask + NDCI/NDWI + Data lineage |
| Forecast backfill | ✅ Prototype | Open-Meteo Single Runs ก่อน Decision time ป้องกัน Future leakage |
| Ground truth dataset | 🔴 ยังไม่มีข้อมูล | มี Contract/Template แล้ว แต่ VERIFIED rows = 0 |
| Field validation/calibration | 🔴 ยังไม่มี | ห้ามกล่าวอ้าง Accuracy หรือความแม่นยำ 3–5 วัน |
| รายงาน V2 | 🟡 กำลังปรับ | ต้องลบสถานะเก่าและเพิ่มผลล่าสุด |
| สไลด์ | 🟡 ผู้จัดทำกำลังทำ | ต้องใช้ข้อเท็จจริงเดียวกับรายงานและ UI |
| ข้อมูลติดต่อ | 🔴 ทีมต้องกรอก | ห้ามสร้างข้อมูลส่วนบุคคลขึ้นเอง |

## 2. สิ่งที่ทำเสร็จแล้ว

### Backend และโมเดล

- [x] FastAPI `/api/health`, `/api/stations`, `/api/risk/current`
- [x] โหลด `backend/xgboost_model.json`
- [x] สร้าง Low/Medium/High synthetic technical scenarios
- [x] XGBoost inference ให้ค่าประมาณ 11.1%, 58.7% และ 94.8%
- [x] คำนวณ SHAP จริงด้วย XGBoost `pred_contribs=True`
- [x] แสดง Top 3 factors และระบุ `shap_output_space=raw_margin`
- [x] แยก `model_demo` ออกจาก `insufficient_data`
- [x] เพิ่มคำแนะนำตรวจ DO, pH, สีของน้ำ และเก็บตัวอย่าง
- [x] เพิ่ม Earth Search Sentinel-2 และ Open-Meteo Weather/Marine adapter สำหรับบางแสน
- [x] เพิ่ม SCL water mask, NDCI/NDWI, Valid-pixel ratio และตัด Tile ซ้ำ
- [x] เพิ่ม Archived forecast single-run backfill และ Processing latency 8 ชั่วโมง
- [x] เพิ่ม Ground-truth contract และห้ามนับ Missing report เป็น Negative
- [x] เพิ่ม Temporal Train/Calibration/Test, Baselines, Calibration และ Operational gate
- [x] ใช้ cache/snapshot เมื่อบริการภายนอกขัดข้อง
- [x] ยกเลิก Rule-based risk score ของ Live context
- [x] เมื่อ Feature ภาพไม่ตรงกับโมเดล ส่ง `risk_score=null` และไม่รัน SHAP

### Frontend

- [x] เชื่อม FastAPI ผ่าน Next.js proxy `/backend-api`
- [x] แก้ Cross-origin HMR, hydration mismatch และ ChunkLoad issue
- [x] แสดง XGBoost + SHAP เป็นแกน Technical Demo
- [x] แสดงป้าย Synthetic และข้อจำกัดชัดเจน
- [x] แสดง SHAP top 3 พร้อมหน่วย Raw margin
- [x] แยก Bangsaen เป็น `Live Data Readiness`
- [x] โหมดข้อมูลไม่พอไม่แสดง Gauge/เปอร์เซ็นต์
- [x] แสดง Data age, provenance, imagery status และ limitations
- [x] แสดงขั้นตอนตอบสนองของเกษตรกร
- [x] Frontend lint และ production build ผ่าน

### การทดสอบ

- [x] Backend tests 12 รายการผ่าน
- [x] Model asset/health test ผ่าน
- [x] XGBoost + SHAP response test ผ่าน
- [x] SHAP additivity test ผ่าน
- [x] Low < Medium < High test ผ่าน
- [x] Live context risk suppression test ผ่าน
- [x] Unknown station HTTP 404 test ผ่าน
- [x] Frontend ESLint ผ่าน
- [x] Frontend Production build ผ่าน

## 3. สิ่งที่ระบบพิสูจน์ได้

- โครงสร้าง XGBoost inference และ SHAP explanation ทำงานครบจาก API ถึง UI
- SHAP ที่แสดงมาจากโมเดล ไม่ใช่ป้ายหรือข้อความจากกฎ
- ระบบแยกข้อมูลสังเคราะห์ออกจากข้อมูล Live context
- ระบบไม่สร้าง Probability เมื่อไม่มี Input ที่ตรงกับ Feature schema
- ข้อมูลภายนอกของบางแสนใช้ตรวจ Data readiness และแสดง provenance ได้
- UI สื่อสารสิ่งที่เกษตรกรควรทำหลังได้รับระดับเตือนได้

## 4. สิ่งที่ยังพิสูจน์ไม่ได้

- [ ] ความแม่นยำภาคสนามและความแม่นยำล่วงหน้า 3–5 วัน
- [ ] Precision, Recall, PR-AUC, Brier score และ Calibration บนข้อมูลจริง
- [ ] ประสิทธิภาพของ No-image model เพราะปัจจุบันยังไม่มีโมเดลดังกล่าว
- [ ] Generalization ข้ามฤดูกาลและพื้นที่
- [ ] ความถูกต้องของตำแหน่ง/ชนิดแพลงก์ตอนจาก Ground truth
- [ ] ประสิทธิผลของคำแนะนำต่อความเสียหายของเกษตรกร
- [ ] Willingness-to-pay, Paid pilot และ Unit economics
- [ ] LINE/SMS/Email notification จริง

> ข้อความหลัก: **Technical Demo แสดงว่าระบบทำงาน ไม่ได้แสดงว่าระบบแม่นภาคสนาม** และ **SHAP อธิบายโมเดล ไม่ได้ยืนยันเหตุและผล**

## 5. งานที่ต้องทำก่อนส่งวันนี้

### Priority 1 — รายงาน

- [ ] ตรวจ `AquaMind_Final_ReportV2.md` ให้ไม่มีข้อความว่า Frontend/Build/API ยังไม่ทำ
- [ ] ใส่ภาพรวมระบบ Sentinel-2 → XGBoost → SHAP → Dashboard
- [ ] อธิบาย Technical Demo กับ Live Data Readiness แยกจากกัน
- [ ] ใส่ผลทดสอบ 12 passed, lint passed และ build passed
- [ ] ระบุว่า Live Bangsaen มี Sentinel-2 features แล้ว แต่ไม่มี Risk probability เพราะ Ground truth/Validation ยังไม่ผ่าน
- [ ] แก้คู่มือการใช้งานให้ตรง Dashboard ใหม่
- [ ] เติมข้อมูลติดต่อและข้อมูลสถานศึกษาที่บังคับ
- [ ] ตรวจบทคัดย่อไทย/อังกฤษให้สถานะตรงกัน

### Priority 2 — หลักฐาน

- [ ] ภาพหน้า XGBoost Technical Demo
- [ ] ภาพ SHAP top 3/Raw margin
- [ ] ภาพ Bangsaen “ข้อมูลไม่เพียงพอ” ที่ไม่มีเปอร์เซ็นต์
- [ ] ภาพ Data age/provenance/limitations
- [ ] ผล `python -m pytest backend -q`
- [ ] ผล `npm run lint`
- [ ] ผล `npm run build`
- [ ] JSON response ของ Model Demo และ Live context

### Priority 3 — ทีมต้องกรอกเอง

- [ ] ชื่อสถานศึกษา ภาควิชา/แผนการเรียน และที่อยู่
- [ ] โทรศัพท์และอีเมลผู้พัฒนา
- [ ] ข้อมูลติดต่ออาจารย์ที่ปรึกษา
- [ ] GitHub/Live Demo URL ถ้ามี
- [ ] ตรวจชื่อสมาชิก บทบาท และชื่อโครงการ
- [ ] ตรวจข้อความทุน NSC ครั้งที่ 28

## 6. สิ่งที่ต้องพูดในการนำเสนอ

### ทำไมไม่ใช้ Rule-based เป็นแกนหลัก

Rule-based โปร่งใสและเหมาะกับ Safety gate แต่ไม่สามารถแทนความสัมพันธ์หลายตัวแปรตามข้อเสนอโครงการ และไม่มี SHAP ของโมเดล ระบบจึงใช้ XGBoost + SHAP เป็นแกน Technical Demo ส่วนกฎใช้เฉพาะตรวจความพร้อมข้อมูลและแนวทางปฏิบัติ

### ถ้าไม่มีภาพยังแม่นหรือไม่

> ยังตอบว่าแม่นไม่ได้ เพราะยังไม่มี No-image model และ Validation แยก ระบบปัจจุบันจึงงดเปอร์เซ็นต์ ใช้ Weather/SST เป็นบริบท และขอให้ยืนยันภาคสนาม

### ทำไมค่าความเสี่ยงใน Demo สูง

> เป็น Probability ของ Synthetic scenario ที่ตั้งใจครอบคลุม Low/Medium/High เพื่อทดสอบ UI ไม่ใช่ค่าปัจจุบันของบางแสน และยังไม่ผ่าน Calibration กับข้อมูลจริง

## 7. Final submission checklist

- [ ] ไม่มีข้อความ Rule-based risk เป็นแกนหลัก
- [ ] ไม่มีค่า 49% ของบางแสนหรือเปอร์เซ็นต์ Live ที่ไม่มี Input ภาพ
- [ ] ทุกค่า Probability มีป้าย Synthetic Technical Demo
- [ ] SHAP ระบุ Raw-margin และข้อจำกัด
- [ ] บทคัดย่อไทย/อังกฤษตรงกับระบบ
- [ ] กิตติกรรมประกาศมีทุน NSC ครั้งที่ 28 และชื่อโครงการ
- [ ] รายงานมีหัวข้อครบตามเกณฑ์
- [ ] ข้อมูลติดต่อครบ ไม่มี Placeholder ที่บังคับ
- [ ] ภาพหน้าจอตรงกับโค้ดเวอร์ชันส่ง
- [ ] Backend tests, Frontend lint/build ผ่าน
- [ ] PDF ไม่มีหน้าขาด ตารางล้น หรือสารบัญผิด
- [ ] อัปโหลดเผื่อเวลาก่อนกำหนด

## 8. เกณฑ์พร้อมส่ง

พร้อมส่งเมื่อรายงานและสไลด์ใช้ข้อเท็จจริงเดียวกัน, ระบุ Synthetic/Live ชัด, ไม่กล่าวอ้าง Accuracy เกินหลักฐาน, ใส่ข้อมูลติดต่อครบ และแนบหลักฐานทดสอบแล้ว

**ข้อสรุป:** ณ วันที่ 17 กรกฎาคม 2569 ตัวระบบพร้อมสาธิตแนวคิดตามข้อเสนอในระดับ Technical Prototype แล้ว จุดเสี่ยงสูงสุดต่อการส่งคือเอกสารและข้อมูลที่ต้องกรอก ไม่ใช่การเพิ่ม Rule-based model หรือฟีเจอร์ใหม่
