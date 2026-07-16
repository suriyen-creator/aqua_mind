# AquaMind Frontend

Dashboard ของ AquaMind พัฒนาด้วย Next.js และเชื่อม AquaMind FastAPI ผ่าน proxy เส้นทาง `/backend-api`

## เริ่มใช้งาน

เปิด Backend จากโฟลเดอร์หลัก:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

จากนั้นเปิด Frontend อีกหน้าต่างหนึ่ง:

```powershell
cd frontend
npm install
npm run dev
```

เปิด `http://localhost:3000` หรือ URL แบบ LAN ที่ Next.js แสดง หาก Backend อยู่ URL อื่น ให้คัดลอก `.env.example` เป็น `.env.local` แล้วกำหนด `AQUAMIND_BACKEND_URL` ส่วน `NEXT_PUBLIC_API_BASE_URL` ควรคงเป็น `/backend-api`

## โหมดที่แสดงบน Dashboard

### 1. XGBoost + SHAP Technical Demo

สถานี `chonburi_01` และ `chonburi_02` ใช้สำหรับพิสูจน์เส้นทาง Model inference ตามข้อเสนอโครงการ:

- โหลด `backend/xgboost_model.json`
- รับ Feature จำลองที่มี NDCI, SST anomaly และลม
- คำนวณ Probability ด้วย XGBoost
- คำนวณ SHAP contribution จริงด้วย `pred_contribs=True`
- แสดงปัจจัยสำคัญ 3 อันดับใน Raw-margin space

ผลในโหมดนี้เป็นข้อมูลสังเคราะห์เพื่อสาธิตทางเทคนิค ไม่ใช่สถานการณ์จริงของชลบุรี ไม่ผ่าน Field validation และไม่ควรใช้ตัดสินใจภาคสนาม

### 2. Bangsaen Live Data Readiness

สถานี `chonburi_03` เชื่อม Sentinel-2 L2A จริงผ่าน Earth Search โดยอ่าน B03/B04/B05/B08 และ SCL เพื่อคำนวณ NDCI/NDWI พร้อมเชื่อม Weather/Ocean forecast จาก Open-Meteo

ปัจจุบันยังไม่มี Ground truth ที่ยืนยันแล้วและยังไม่มี Operational model artifact ระบบจึงตอบ `assessment_status=insufficient_data`, `risk_score=null` และไม่คำนวณ SHAP แม้มี Input จริงแล้ว เมื่อโมเดลผ่าน Temporal/spatial validation และ Calibration ระบบจึงจะเปลี่ยนเป็น `operational_model`

## หลักการสำคัญ

- แกนระบบตามข้อเสนอคือ Sentinel-2 → NDCI/NDWI → XGBoost → SHAP → คำแนะนำ 3–5 วัน
- Rule-based ใช้ได้กับเกณฑ์ตรวจความพร้อมข้อมูลและคำแนะนำด้านความปลอดภัย แต่ไม่ใช้แทน Model probability
- Confidence ไม่ใช่ Accuracy; โหมดสังเคราะห์ไม่แสดง Confidence เชิงปฏิบัติการ
- หากข้อมูลภาพไม่ผ่าน QC หรือโมเดลยังไม่ผ่าน Validation ระบบงด Risk probability และแจ้งให้ตรวจภาคสนาม
- SHAP อธิบายพฤติกรรมโมเดล ไม่ได้พิสูจน์ความเป็นเหตุและผลทางชีววิทยา

## ตรวจสอบคุณภาพ

```powershell
npm run lint
npm run build
```

สถานะ ณ 17 กรกฎาคม 2569: ESLint และ Production build ผ่าน; Live UI แสดง Sentinel-2 จริงแต่ระงับ Risk จนกว่าจะมีหลักฐาน Validation
