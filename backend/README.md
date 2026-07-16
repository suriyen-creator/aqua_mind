# AquaMind backend and real-data pipeline

## ติดตั้ง

```powershell
python -m pip install -r backend/requirements.txt
```

## Refresh ข้อมูลจริง

```powershell
python -m backend.pipeline refresh-live --lookback-days 180 --max-scenes 6
```

คำสั่งนี้ทำงานดังนี้:

1. ค้น Sentinel-2 L2A จาก Earth Search STAC
2. อ่าน B03/B04/B05/B08 และ SCL เฉพาะกรอบ AOI บางแสน
3. ใช้ SCL class 6 เป็น Water/QC mask
4. คำนวณ NDCI, NDWI, valid-pixel ratio และแนวโน้ม 30 วัน
5. ดึง Weather/Ocean forecast จาก Open-Meteo
6. บันทึก Snapshot และ Data lineage

## Backfill Forecast ที่ทราบ ณ เวลาตัดสินใจ

```powershell
python -m backend.pipeline backfill-forecasts
```

Weather ใช้ Open-Meteo Single Runs ที่ออกก่อน Decision time เพื่อป้องกัน Future leakage ส่วน SST/คลื่น/กระแสน้ำใช้เฉพาะสถานะใกล้ Decision time ไม่ใช้ค่าจริงในอนาคต

## Ground truth

กรอก `backend/data/ground_truth.csv` ตาม `ground_truth_template.csv` และ `DATA_CONTRACT.md` เฉพาะแถว `verification_status=VERIFIED` จึงเข้าชุดฝึก การไม่มีรายงานไม่ใช่ Negative label

## สร้าง Dataset และ Validate

```powershell
python -m backend.pipeline build-dataset
python -m backend.pipeline train
python -m backend.pipeline status
```

Training เปรียบเทียบ Prevalence, Logistic regression, Satellite-only XGBoost, Weather-only XGBoost และ Full XGBoost โดยแบ่ง 60/20/20 ตามเวลา ส่วน 20% กลางใช้ Calibration และเลือก Threshold

Operational artifact จะถูกสร้างเมื่อผ่าน Policy เท่านั้น หากหลักฐานไม่พอ จะมีเพียง `validation_report.json` และ API จะส่ง `risk_score=null`

## เปิด API และทดสอบ

```powershell
python -m uvicorn backend.main:app --reload --port 8000
python -m pytest backend -q
```

เส้นทางสถานะ Pipeline: `GET /api/pipeline/status`

## สถานะข้อมูลวันที่ 17 กรกฎาคม 2569

- Sentinel-2 observations หลังตัด Tile ซ้ำ: 3 วัน
- Forecast rows: 6 (Archived single runs 3 วัน และ Current forecast snapshots 3 รอบ)
- Verified ground truth: 0
- Supervised rows: 0
- Operational model: ยังไม่อนุมัติ
- Live risk: ถูกระงับตาม Assessment gate
