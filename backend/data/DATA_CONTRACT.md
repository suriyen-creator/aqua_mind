# AquaMind real-data contract

## Ground truth

กรอกข้อมูลใน `ground_truth_template.csv` โดยหนึ่งแถวต้องเป็นผลตรวจที่มีวันเวลาและพิกัดจริง

- `bloom_status`: `1` เมื่อผ่านนิยาม Bloom ที่ทีมและผู้เชี่ยวชาญกำหนด, `0` เมื่อมีการตรวจแล้วและไม่ผ่านนิยาม
- `verification_status`: เฉพาะ `VERIFIED` เท่านั้นที่เข้าสู่ชุดฝึก
- `measurement_method`: วิธีตรวจ เช่น microscopy, cell count, laboratory chlorophyll-a
- การไม่มีรายงานไม่ถือเป็น `bloom_status=0`
- เหตุการณ์เดียวกันต้องใช้ `event_id` เดียวกันเพื่อป้องกันข้อมูลซ้ำข้าม Train/Test

## Prediction sample

หนึ่งแถวของชุดฝึกหมายถึงการตัดสินใจ ณ `issue_time`:

1. Satellite features ใช้เฉพาะภาพที่สังเกตไม่เกิน `issue_time` และเผื่อ Processing latency 8 ชั่วโมง
2. Weather features ต้องมาจาก Single forecast run ที่ออกไม่เกิน `issue_time`; SST/คลื่น/กระแสน้ำใช้เฉพาะสถานะ ณ `issue_time` ไม่ใช้ค่าจริงในอนาคต
3. Label คือผลตรวจ `VERIFIED` ระหว่าง `t+3` ถึงสิ้นสุด `t+5`
4. ถ้าไม่มีผลตรวจในช่วง Label จะตัดแถวนั้นออก ไม่สร้าง Negative อัตโนมัติ

## Data lineage

ต้องเก็บ Sentinel item ID, Asset URL, Processing level, Cloud mask, Forecast issue time, Provider/model และ Ground-truth event IDs ทุกครั้ง
