# ข้อเสนอโครงการ
## การแข่งขันพัฒนาโปรแกรมคอมพิวเตอร์แห่งประเทศไทย ครั้งที่ 28 (NSC 2026)

**หมวด:** โปรแกรมเพื่องานการพัฒนาด้านวิทยาศาสตร์และเทคโนโลยี  
**ธีมหลัก:** นวัตกรรมเพื่อความยั่งยืน (Sustainable Innovation)  
**SDG ที่เกี่ยวข้อง:** SDG 14 — Life Below Water

---

# ส่วนที่ 1: สาระสำคัญของโครงการ และ คำสำคัญ

## 1.1 สาระสำคัญของโครงการ (Executive Summary)

| | |
|---|---|
| **ปัญหา** | ปรากฏการณ์แพลงก์ตอนบลูมในอ่าวไทยตอนบนสร้างความเสียหายต่ออุตสาหกรรมเพาะเลี้ยงสัตว์น้ำหลักร้อยล้านบาทต่อปี เกษตรกรขาดระบบเตือนภัยล่วงหน้าที่มีความละเอียดระดับฟาร์มและเข้าถึงได้ง่าย |
| **ทางแก้** | **AquaMind** คือเครื่องมือสนับสนุนการตัดสินใจ (Decision Support System) แบบ End-to-End บูรณาการภาพดาวเทียม Sentinel-2 (10–20m/pixel ตามแถบคลื่นและดัชนี) กับข้อมูลอากาศและสมุทรศาสตร์ที่อัปเดตรายวัน เพื่อประเมินความเสี่ยงการเกิดแพลงก์ตอนบลูมล่วงหน้า 3–5 วัน ระบบจัดการช่วงที่ไม่มีภาพใหม่ด้วยข้อมูลภาพล่าสุดที่ผ่านการตรวจคุณภาพร่วมกับแนวโน้มสิ่งแวดล้อม พร้อมแสดงอายุข้อมูลและระดับความเชื่อมั่น ไม่อ้างว่าเป็นข้อมูลเรียลไทม์ รวมทั้งใช้ Explainable AI (SHAP) อธิบายสาเหตุและเสนอขั้นตอนรับมือที่เกษตรกรนำไปปฏิบัติได้ |
| **ผลกระทบ** | ลดความสูญเสียสัตว์น้ำจากการเตรียมตัวไม่ทัน และ**ลดต้นทุนการเฝ้าระวังเชิงพื้นที่ได้มากกว่า 10 เท่า** (ต้นทุน Cloud ~500 บาท/เดือน เทียบกับการลงพื้นที่เก็บตัวอย่าง ~5,000–10,000 บาท/ครั้ง) |

## 1.2 ชื่อโครงการและคำสำคัญ

**ชื่อภาษาไทย:**  
AquaMind: แพลตฟอร์มพยากรณ์การเกิดแพลงก์ตอนบลูมและวิเคราะห์คุณภาพน้ำแบบ End-to-End จากภาพถ่ายดาวเทียม

**ชื่อภาษาอังกฤษ:**  
AquaMind: End-to-End Algal Bloom Prediction and Water Quality Analysis Platform via Satellite Imagery

**คำสำคัญ (Keywords):**  
Decision Support System · Remote Sensing (Sentinel-2) · Explainable AI (SHAP) · Data Science Pipeline · Localized Early Warning System · Imbalanced Learning (SMOTE) · System Usability Scale (SUS)

---

# ส่วนที่ 2: หลักการและเหตุผล

## 2.1 ความเป็นมาและความสำคัญของปัญหา

ปรากฏการณ์แพลงก์ตอนบลูม (Algal Bloom) หรือปรากฏการณ์น้ำเปลี่ยนสี เกิดจากการเพิ่มจำนวนอย่างรวดเร็วของแพลงก์ตอนพืช (Phytoplankton) ในแหล่งน้ำ เมื่อแพลงก์ตอนตายและย่อยสลาย แบคทีเรียจะดึงออกซิเจนในน้ำไปใช้ ทำให้ปริมาณออกซิเจนที่ละลายในน้ำ (Dissolved Oxygen: DO) ลดลงอย่างเฉียบพลัน ส่งผลให้สัตว์น้ำขาดออกซิเจนและตายยกกระชัง

จากรายงานข่าวของ Thai PBS และข้อมูลดาวเทียมจาก GISTDA พบว่าในปี 2566 พื้นที่ชายฝั่งจังหวัดชลบุรีเกิดปรากฏการณ์น้ำเปลี่ยนสีหลายครั้ง สร้างความเสียหายต่อเกษตรกรผู้เลี้ยงสัตว์น้ำในกระชังเป็นวงกว้าง คิดเป็นมูลค่าความเสียหายรวมหลักร้อยล้านบาท [1], [2]

## 2.2 ช่องว่างของระบบที่มีอยู่ในปัจจุบัน

แม้จะมีระบบเฝ้าระวังระดับสากล แต่ยังมีข้อจำกัดสำคัญ 4 ประการ ดังนี้

**ข้อจำกัดที่ 1 — ความละเอียดไม่เพียงพอ:**  
ระบบ NOAA HABs ใช้ดาวเทียม Sentinel-3/MODIS ที่มีความละเอียด 300–500 เมตรต่อพิกเซล ซึ่งเพียงพอสำหรับการวิเคราะห์ระดับมหาสมุทร แต่ไม่สามารถแยกแยะพื้นที่ฟาร์มเพาะเลี้ยงสัตว์น้ำชายฝั่งที่มีขนาดเล็กในระดับหลักสิบเมตรได้

**ข้อจำกัดที่ 2 — ขาดการอธิบายเหตุผล:**  
ระบบปัจจุบันแสดงผลเป็นแผนที่ความหนาแน่น (Density Map) เท่านั้น ไม่สามารถบอกเกษตรกรได้ว่า "ทำไม" ความเสี่ยงถึงสูง เช่น มาจากอุณหภูมิน้ำ ความเร็วลม หรือปริมาณสารอาหาร ซึ่งทำให้เกษตรกรไม่สามารถตัดสินใจรับมือได้อย่างมีประสิทธิภาพ

**ข้อจำกัดที่ 3 — ต้นทุนการตรวจวัดแบบดั้งเดิมสูงมาก:**  
การเก็บตัวอย่างน้ำภาคสนาม 1 ครั้ง มีค่าใช้จ่ายเฉลี่ย 5,000–10,000 บาท ครอบคลุมได้เพียงไม่กี่จุด ทำให้ไม่สามารถเฝ้าระวังได้อย่างต่อเนื่องและครอบคลุมพื้นที่ขนาดใหญ่

**ข้อจำกัดที่ 4 — ภาพดาวเทียมไม่ได้มาอย่างต่อเนื่อง:**  
Sentinel-2 มีรอบกลับมาถ่ายพื้นที่เดิมตามปกติประมาณ 5 วัน และภาพบางรอบอาจใช้ไม่ได้เพราะเมฆหรือหมอกควัน ดังนั้นระบบที่พึ่งภาพดาวเทียมเพียงแหล่งเดียวจะมีช่วงว่างของข้อมูล AquaMind จึงแยก “เวลาที่ระบบคำนวณล่าสุด” ออกจาก “เวลาที่ภาพดาวเทียมใช้ได้ล่าสุด” ใช้ข้อมูลอากาศรายวันและแนวโน้มย้อนหลังช่วยประเมินระหว่างรอภาพใหม่ และลดระดับความเชื่อมั่นหรือแจ้งว่า “ข้อมูลไม่เพียงพอ” เมื่อภาพเก่าเกินเกณฑ์

## 2.3 ความจำเป็นในการพัฒนา (Why Now?)

อุณหภูมิน้ำ แสง สารอาหาร ความเค็ม ลม และกระแสน้ำล้วนมีผลต่อการเติบโตและการคงอยู่ของปรากฏการณ์แพลงก์ตอนบลูม [18] การเปลี่ยนแปลงของปัจจัยเหล่านี้ทำให้การเฝ้าระวังแบบหลายแหล่งข้อมูลมีความจำเป็น ขณะเดียวกัน ดาวเทียม Sentinel-2 ของ ESA มีข้อมูลหลายแถบคลื่นที่ความละเอียด 10–20 เมตรและเปิดให้ใช้งานฟรีผ่าน Google Earth Engine ทำให้สามารถพัฒนาระบบต้นแบบได้ด้วยต้นทุนต่ำ

---

# ส่วนที่ 3: วัตถุประสงค์

1. พัฒนา Automated Data Pipeline สำหรับดึงและประมวลผลข้อมูลภาพถ่ายดาวเทียม Sentinel-2 และข้อมูลพยากรณ์อากาศแบบอัตโนมัติ
2. พัฒนาระบบประเมินความเสี่ยง (Risk Estimation Model) ที่สามารถคาดการณ์แนวโน้มการเกิดแพลงก์ตอนบลูมล่วงหน้าได้ 3–5 วัน พร้อมกลไกจัดการข้อมูลดาวเทียมที่ขาดหายและแสดงระดับความเชื่อมั่นตามความสดใหม่ของข้อมูล
3. บูรณาการ Explainable AI (SHAP Analysis) เพื่ออธิบายปัจจัยเสี่ยงในรูปแบบที่ผู้ใช้งานเข้าใจได้ง่าย
4. พัฒนา Web Dashboard ภาษาไทยสำหรับแสดงผลความเสี่ยงและแผนที่เชิงพื้นที่แบบ Interactive
5. ตรวจสอบความแม่นยำกับข้อมูลภาคสนามและเหตุการณ์ที่ไม่ถูกใช้ฝึกโมเดล โดยวัด Recall, Precision, F1-score, PR-AUC และการสอบเทียบค่าความน่าจะเป็น (Calibration)
6. ทดสอบความพึงพอใจและการใช้งานได้จริงกับกลุ่มผู้ใช้เป้าหมาย 30 ราย ด้วยเกณฑ์มาตรฐาน System Usability Scale (SUS)

---

# ส่วนที่ 4: ปัญหาหรือประโยชน์ที่เป็นเหตุผลให้ควรพัฒนาโปรแกรม

## 4.1 ปัญหาหลัก

เกษตรกรผู้เพาะเลี้ยงสัตว์น้ำชายฝั่งในอ่าวไทยตอนบนประสบปัญหาหลักสามประการ:

1. **ขาดระบบเตือนภัยต่อเนื่องที่มีรายละเอียดเพียงพอสำหรับบริเวณฟาร์ม** — ระบบปัจจุบันมีความละเอียดในระดับหลายร้อยเมตรต่อพิกเซล ขณะที่ข้อมูลความละเอียดสูงไม่ได้มีภาพใหม่ทุกวัน จึงต้องมีระบบที่รวมหลายแหล่งข้อมูลและบอกความสดใหม่อย่างโปร่งใส
   
2. **การพลาดการเตือนภัยทำให้สัตว์น้ำตายหลักล้านบาทต่อครั้ง** — เมื่อแพลงก์ตอนบลูมเกิดขึ้น หากไม่ทันทำการเตรียมการ (เช่น เปิดปั๊มอากาศ หรือเปลี่ยนน้ำ) สัตว์น้ำทั้งกระชังจะตายในเวลา 12-24 ชั่วโมง
   
3. **ต้นทุนการตรวจสอบแบบดั้งเดิมสูงและไม่ต่อเนื่อง** — การเก็บตัวอย่างน้ำและวิเคราะห์ในห้องแล็บต้องใช้เวลาหลายวันและเสียค่าใช้จ่ายสูง

## 4.2 ประโยชน์ที่คาดหวัง

การพัฒนา AquaMind จะให้ประโยชน์ดังนี้:

1. **ลดความสูญเสียทางเศรษฐกิจ** — เกษตรกรได้รับการประเมินความเสี่ยงล่วงหน้า 3–5 วัน พร้อมระดับความเชื่อมั่นและขั้นตอนตรวจสอบ เพื่อเตรียมการรับมือได้เร็วขึ้น
   
2. **ลดต้นทุนการเฝ้าระวังมากกว่า 10 เท่า** — ต้นทุน Cloud ประมาณ 500 บาท/เดือน เทียบกับการเก็บตัวอย่างแบบดั้งเดิม 5,000-10,000 บาท/ครั้ง
   
3. **เพิ่มประสิทธิภาพในการตัดสินใจ** — ระบบแปลผล SHAP เป็นภาษาที่อ่านง่ายเพื่อแสดงทิศทางและอันดับปัจจัยสำคัญ แล้วทดสอบความเข้าใจกับผู้ใช้จริงก่อนสรุปว่าใช้งานได้
   
4. **รองรับการใช้งานของหน่วยงานสาธารณะ** — กรมประมงและหน่วยงานทะเลชายฝั่งสามารถใช้ระบบเป็นกลไกสนับสนุนนโยบายการคุ้มครองสัตว์น้ำ

---

# ส่วนที่ 5: เป้าหมายและขอบเขตของโครงการ

## 5.1 เป้าหมายของโครงการ

1. **ระดับชาติ (National Scale):** นำเสนอวิธีการติดตามคุณภาพน้ำ และการพยากรณ์แพลงก์ตอนบลูมแบบ Data-Driven ที่สามารถปรับใช้ได้กับพื้นที่อื่นๆ ในประเทศไทย

2. **ระดับภูมิภาค (Regional Scale):** ระบุพื้นที่เสี่ยงสูงในอ่าวไทยตอนบน (จากจ.ฉะเชิงเทรา ถึง จ.ชลบุรี) และจัดทำแผนที่ความเสี่ยงแบบ Interactive

3. **ระดับฟาร์ม (Farm-level Scale):** ให้เกษตรกรตรวจสอบความเสี่ยงของบริเวณฟาร์มด้วยข้อมูล 10–20 เมตรต่อพิกเซล โดยไม่อ้างว่าสามารถแยกกระชังเดี่ยวทุกขนาดได้

## 5.2 ขอบเขตของโครงการ

**ขอบเขตเชิงพื้นที่:**
- Area of Interest (AOI): ชายฝั่งอ่าวไทยตอนบน ตั้งแต่ อ่าวบางปะกง จ.ฉะเชิงเทรา ถึง อ่าวศรีราชา จ.ชลบุรี

**ขอบเขตเชิงวิทยาศาสตร์:**
- ใช้ข้อมูล Sentinel-2 (ความละเอียด 10–20 เมตรตามแถบคลื่น; NDCI ใช้ Band 5 ที่ 20 เมตร) เป็นข้อมูลหลัก
- บูรณาการข้อมูลพยากรณ์อากาศ และข้อมูลสภาพทางกายภาพน้ำ
- จำกัดการคาดการณ์ไว้ 3-5 วันล่วงหน้า (เนื่องจากความแม่นยำของข้อมูลพยากรณ์อากาศ)

**ขอบเขตเชิงตัวชี้วัด:**
- จำนวนผู้ใช้ทดสอบ 30 ราย (เกษตรกร + เจ้าหน้าที่ทางภูมิศาสตร์)
- เป้าหมาย System Usability Score (SUS) ≥ 70

---

# ส่วนที่ 6: รายละเอียดของการพัฒนา

## 6.0 ภาพรวมของระบบ (System Overview)

AquaMind ทำงานเป็นวงจรตั้งแต่รับข้อมูลจนถึงการตอบสนองและนำผลจริงกลับมาปรับปรุงโมเดล โดยแยก **การสังเกตจากดาวเทียม** ออกจาก **การพยากรณ์ความเสี่ยง** อย่างชัดเจน ภาพ Sentinel-2 ใช้อัปเดตสภาพเชิงพื้นที่เมื่อมีภาพที่ผ่านการตรวจคุณภาพ ส่วนข้อมูลอากาศและคุณลักษณะแนวโน้มใช้ปรับค่าความเสี่ยงรายวันระหว่างรอภาพรอบใหม่ ทุกผลลัพธ์ต้องระบุเวลาของข้อมูลล่าสุด แหล่งข้อมูล โหมดการประเมิน และระดับความเชื่อมั่น

```text
แหล่งข้อมูล
Sentinel-2 + อากาศ/พยากรณ์ + SST ระดับภูมิภาค + ตัวอย่างน้ำ + รายงานจากเกษตรกร
                              ↓
ตรวจคุณภาพและความสดใหม่ของข้อมูล
Cloud mask + Missing-data check + Satellite data age
                              ↓
สร้างคุณลักษณะ
NDCI/NDWI + แนวโน้มย้อนหลัง + ลม/ฝน/อุณหภูมิ + พื้นที่ข้างเคียง
                              ↓
โมเดลประเมินความเสี่ยง 3–5 วัน + คำนวณความไม่แน่นอน
                              ↓
ผลลัพธ์เพื่อการตัดสินใจ
ระดับ/โอกาสเสี่ยง + SHAP Top-3 + อายุข้อมูล + ความเชื่อมั่น
                              ↓
Dashboard/การแจ้งเตือน → ขั้นตอนตรวจสอบและรับมือของเกษตรกร
                              ↓
ผลที่เกิดขึ้นจริง/ค่าตรวจน้ำ/ภาพถ่าย → ฐานข้อมูล Ground Truth → ประเมินและปรับโมเดล
```

ระบบมีโหมดการทำงาน 3 ระดับ เพื่อไม่สร้างความมั่นใจเกินจริงในช่วงที่ไม่มีภาพดาวเทียมใหม่:

| โหมด | เงื่อนไขข้อมูล | วิธีแสดงผล |
|---|---|---|
| **A: Fresh satellite** | มีภาพ Sentinel-2 ล่าสุดที่ผ่าน Cloud mask | แสดงความเสี่ยงระดับฟาร์มและความเชื่อมั่นตามผลโมเดล |
| **B: Forecast-assisted** | ยังไม่มีภาพใหม่ แต่ภาพล่าสุดยังไม่เก่าเกินเกณฑ์ | อัปเดตความเสี่ยงด้วยข้อมูลอากาศและแนวโน้ม พร้อมแสดงจำนวนวันตั้งแต่ภาพล่าสุดและลดความเชื่อมั่น |
| **C: Insufficient data** | ภาพล่าสุดเก่าเกินเกณฑ์ที่กำหนดจากผล Validation หรือข้อมูลหลักขาดหาย | ไม่สร้างแผนที่ความละเอียดระดับฟาร์มใหม่ แสดงว่า “ข้อมูลไม่เพียงพอ” และแนะนำให้ตรวจวัดภาคสนาม |

## 6.1 เนื้อเรื่องย่อ (Story Board)

### 6.1.1 ภาพประกอบและแบบจำลอง

**ขั้นตอนการทำงาน End-to-End:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION & PROCESSING                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Sentinel-2 Imagery      Weather/Ocean Data       Ground Truth  │
│  (Google Earth Engine)       (APIs)              (Water Samples)│
│        ↓                          ↓                    ↓        │
│  Band Extraction & Index Calculation (NDCI, NDWI)              │
│        ↓                                                        │
│        └─────────────────────────┬─────────────────────────┘   │
│                                  ↓                              │
│                    FEATURE ENGINEERING                         │
│                                  ↓                              │
│     ┌──────────────────────────────────────────────┐           │
│     │  Temporal Features (3-5 day trends)          │           │
│     │  Spatial Features (neighborhood analysis)    │           │
│     │  Environmental Features (wind, temp, DO)     │           │
│     └──────────────────────────────────────────────┘           │
│                                  ↓                              │
│            MACHINE LEARNING MODEL (Random Forest/XGBoost)      │
│            (with SMOTE for handling imbalanced data)           │
│                                  ↓                              │
│              EXPLAINABILITY (SHAP Analysis)                    │
│              (ระบุ Top-3 Risk Factors)                          │
│                                  ↓                              │
│           ┌──────────────────────────────────────────┐         │
│           │  RISK ASSESSMENT OUTPUT                   │         │
│           │  - Risk Level (Low/Medium/High)           │         │
│           │  - Risk Probability (0-100%)              │         │
│           │  - Contributing Factors (with SHAP)       │         │
│           │  - 3-5 Day Forecast Trend                │         │
│           └──────────────────────────────────────────┘         │
│                                  ↓                              │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
                       VISUALIZATION LAYER
                                  ↓
            ┌──────────────────────────────────────────┐
            │    WEB DASHBOARD (React + Mapbox)        │
            │    - Interactive Risk Map                │
            │    - Time-series Charts                  │
            │    - SHAP Explanation Cards              │
            │    - Alert Notifications                 │
            │    - Export Reports (PNG/PDF)            │
            └──────────────────────────────────────────┘
                                  ↓
                    END USER (Farmer's Mobile/PC)
```

### 6.1.2 ตัวอย่างผลลัพธ์ที่นำเสนอ

**ประเภท 1: Risk Overview Card (แสดงต่อเกษตรกรเมื่อเข้าแอป)**

```
┌────────────────────────────────────────────────┐
│  ⚠️ ความเสี่ยง: สูง (High Risk)                │
│  ────────────────────────────────────────────  │
│                                                 │
│  ความเสี่ยง:           73%                     │
│  ████████░░░░░░░░░░░                          │
│                                                 │
│  สาเหตุหลัก (Top Factors):                     │
│  ① อุณหภูมิผิวน้ำ: +2.1°C (ผิดปกติสูง)        │
│  ② ความเร็วลม: ลดลง 40% (ล่าสุด 3 วัน)       │
│  ③ ปริมาณเคลื่อนไหว: ขึ้น 25% (Chlorophyll)  │
│                                                 │
│  📅 การพยากรณ์ 5 วันข้างหน้า:                 │
│  วันนี้   ⚠️ High    วันพรุ่งนี้  ⚠️ High      │
│  +1 วัน  ⚠️ Medium   +2 วัน     🟢 Low       │
│  +3 วัน  🟢 Low      +4 วัน     🟢 Low       │
│                                                 │
│  💡 คำแนะนำ:                                   │
│  ลงพื้นที่ตรวจสอบ + เปิดระบายอากาศเพิ่มเติม   │
│                                                 │
│  [ แสดงแผนที่ ]  [ ดูรายละเอียด ]              │
└────────────────────────────────────────────────┘
```

**ประเภท 2: Interactive Spatial Map (แสดงบนแผนที่)**

```
Sentinel-2 NDCI Map (รวม AOI อ่าวศรีราชา)

NDCI Color Scale (ตัวอย่างสำหรับ Mockup; ค่าแบ่งระดับต้องปรับจาก Ground Truth ในพื้นที่):
🟢 < 0.0     = ความเสี่ยงต่ำ (สีเขียว)
🟡 0.0-0.2   = ความเสี่ยงปานกลาง (สีส้ม)
🔴 > 0.2     = ความเสี่ยงสูง (สีแดง)

[แสดงแผนที่จริง: สามารถ Zoom เข้าถึงระดับแต่ละฟาร์ม]
[สามารถซ้อนทับข้อมูลปัจจัยเสี่ยงอื่นๆ (Wind, Temp)]
```

**ประเภท 3: Time-Series Trend Chart**

```
Risk Level Trend (7 days)

100% |                  
 90% |      ┌─────┐    
 80% |     /       \   
 70% |    /         \─┐
 60% |   /             
 50% |  /              
 40% |_/________________
     Day-3  Day-2  Day-1  Today  +1  +2  +3
     
Historical Data (gray)  |  Forecast (blue)
```

---

## 6.2 เทคนิคหรือเทคโนโลยีที่ใช้

### 6.2.1 Remote Sensing

**เทคนิค: NDCI (Normalized Difference Chlorophyll Index)**

คือ ดัชนีที่ใช้ประมาณค่าความเข้มข้นของคลอโรฟิลล์-a (Chl-a) ในน้ำ ซึ่งเป็นตัวชี้วัดหลักของการเพิ่มจำนวนของแพลงก์ตอนพืช

**สูตรคำนวณ:**
```
NDCI = (ρ_RedEdge − ρ_Red) / (ρ_RedEdge + ρ_Red)
```

โดย ρ_RedEdge คือค่าการสะท้อนแสงในช่วง Band 5 (705nm) และ ρ_Red คือ Band 4 (665nm) ของ Sentinel-2

**ทำไมถึงเลือก:** เมื่อคลอโรฟิลล์เพิ่มสูงขึ้น การดูดซับแสงในช่วง Red จะสูงขึ้น แต่การสะท้อนแสงในช่วง Red-Edge จะสูงขึ้นเช่นกัน ทำให้ค่า NDCI เพิ่มขึ้นตามปริมาณแพลงก์ตอน [10] เนื่องจาก Band 5 มีความละเอียดดั้งเดิม 20 เมตร แผนที่ NDCI จึงรายงานที่ความละเอียดเชิงสารสนเทศ 20 เมตร แม้จะ Resample เพื่อจัดกริดร่วมกับ Band 4 ก็ตาม

**เกณฑ์ความเสี่ยงเบื้องต้นสำหรับการออกแบบหน้าจอ:**
- NDCI < 0.0 → ระดับต่ำ
- NDCI 0.0–0.2 → ระดับปานกลาง
- NDCI > 0.2 → ระดับสูง

ค่าแบ่งระดับข้างต้นไม่ใช่เกณฑ์สากลที่ยืนยัน Bloom ได้ทันที เพราะ NDCI ได้รับผลจากชนิดแพลงก์ตอน ความขุ่น ตะกอน และสภาพแสง เกณฑ์ใช้งานจริงจะเลือกจาก ROC/Precision-Recall curve บน Validation Set ที่จับคู่กับ Chlorophyll-a และเหตุการณ์ภาคสนามใน AOI แล้วจึงทดสอบซ้ำบน Independent Test Set

---

**เทคนิค: NDWI (Normalized Difference Water Index)**

คือ ดัชนีที่ใช้แยกแยะพื้นที่น้ำออกจากพื้นที่บก เพื่อ Mask เฉพาะพิกเซลที่เป็นน้ำออกมาก่อนวิเคราะห์คุณภาพน้ำ

**สูตรคำนวณ:**
```
NDWI = (ρ_Green − ρ_NIR) / (ρ_Green + ρ_NIR)
```

โดย ρ_Green คือ Band 3 (560nm) และ ρ_NIR คือ Band 8 (842nm) ของ Sentinel-2

**ทำไมถึงเลือก:** น้ำดูดซับแสง NIR ได้ดีมาก ทำให้ค่า NDWI ของพื้นที่น้ำเป็นบวก (> 0) ขณะที่พื้นดินและพืชพรรณมีค่าเป็นลบ ช่วยให้กรองพื้นที่วิเคราะห์ได้อย่างแม่นยำ [8]

---

### 6.2.2 Machine Learning Algorithms

**เทคนิค: Random Forest**

คือ อัลกอริทึม Machine Learning แบบ Ensemble ที่สร้างต้นไม้ตัดสินใจ (Decision Tree) หลายต้นพร้อมกัน แล้วนำผลการพยากรณ์มาโหวตรวมกัน

**ทำไมถึงเลือก:** เป็นโมเดลฐานแบบ Ensemble ที่รองรับความสัมพันธ์ไม่เชิงเส้นและข้อมูลหลายตัวแปร สามารถเปรียบเทียบ Feature Importance และอธิบายผลรายกรณีด้วย SHAP ได้ โดยประสิทธิภาพจริงต้องตัดสินจาก Validation [11]

---

**เทคนิค: XGBoost (Extreme Gradient Boosting)**

คือ อัลกอริทึม Gradient Boosting ที่สร้างโมเดลใหม่ทีละโมเดลเพื่อแก้ข้อผิดพลาดของโมเดลก่อนหน้า (Boosting Strategy)

**ทำไมถึงเลือก:** เป็นโมเดลผู้สมัครที่มี Regularization รองรับการถ่วงน้ำหนักคลาสและการเร่งความเร็วด้วย GPU จึงนำมาเปรียบเทียบกับ Random Forest โดยไม่สรุปล่วงหน้าว่าจะดีกว่าในชุดข้อมูลของโครงการ [12]

---

### 6.2.3 Handling Imbalanced Data

**เทคนิค: SMOTE (Synthetic Minority Over-sampling Technique)**

ปัญหา: ในธรรมชาติ แพลงก์ตอนบลูมเกิดขึ้นได้ไม่บ่อย (อาจ 10-20% ของช่วงเวลาที่ศึกษา) ส่งผลให้ข้อมูลไม่สมดุล โมเดลมีแนวโน้มที่จะเรียนรู้ได้ไม่ดี

วิธีแก้: SMOTE สร้างตัวอย่าง (Synthetic samples) ใหม่โดยการสอดแทรกค่าจากกลุ่มไมโนริตี้ในพื้นที่ Feature Space เพื่อจำลองการกระจายของข้อมูลจริง

**ผลลัพธ์ที่คาดหวัง:** ทดลองเปรียบเทียบ Class Weight กับ SMOTE โดยใช้ SMOTE เฉพาะ Training fold แล้วเลือกวิธีจากผล Validation เป้าหมายคือ Recall ≥ 80% โดยต้องรายงาน Precision และ PR-AUC ร่วมด้วย ไม่สรุปล่วงหน้าว่า SMOTE จะทำให้ผ่านเป้าหมายเสมอ [14]

---

### 6.2.4 Explainable AI

**เทคนิค: SHAP (SHapley Additive exPlanations)**

คือ วิธีการอธิบายการพยากรณ์ของโมเดล โดยคำนวณ "Contribution" ของแต่ละปัจจัย (Feature) ต่อผลลัพธ์ สูตรคำนวณอิงมาจากทฤษฎีเกม (Game Theory) Shapley Value

**ตัวอย่างผลลัพธ์:**

```
Risk Score: 73% (HIGH)

Top 3 Factors Pushing Risk UP (Red):
① Regional SST anomaly: +2.1°C  → increases risk | relative rank 45%
② Wind Speed: -0.5 m/s          → increases risk | relative rank 30%
③ Chlorophyll Trend: +8%/day    → increases risk | relative rank 25%

Model probability: 73%
Note: relative rank is normalized among the displayed factors; it is not a causal effect or percentage-point increase.
```

**ทำไมถึงเลือก:** SHAP ช่วยแสดงทิศทางและขนาดอิทธิพลของตัวแปรต่อผลพยากรณ์แต่ละครั้ง [9] ส่วนความเข้าใจ ความเชื่อใจ และการยอมรับของเกษตรกรจะวัดจริงด้วยการทดสอบผู้ใช้ ไม่สรุปจากการมีกราฟ SHAP เพียงอย่างเดียว

---

### 6.2.5 การจัดการช่วงที่ไม่มีภาพดาวเทียมใหม่ (Temporal Gap Management)

Sentinel-2 ไม่ได้ส่งภาพพื้นที่เดิมแบบต่อเนื่องทุกวัน และภาพตามรอบประมาณ 5 วันอาจถูกเมฆบัง AquaMind จึงไม่ใช้วิธีเติมภาพสมมติแล้วนำเสนอเสมือนเป็นภาพจริง แต่ใช้กระบวนการดังนี้:

1. **ตรวจภาพทุกครั้งก่อนใช้:** ทำ Cloud/Shadow Mask ตรวจสัดส่วนพิกเซลน้ำที่ใช้งานได้ และบันทึก `satellite_observed_at` แยกจาก `prediction_generated_at`
2. **เก็บภาพที่ใช้ได้ล่าสุด:** สร้างค่าคุณลักษณะย้อนหลัง เช่น ค่ามัธยฐานและอัตราการเปลี่ยนแปลง 3–5 รอบ เพื่อลดผลของ Noise จากภาพเพียงครั้งเดียว
3. **อัปเดตความเสี่ยงระหว่างรอภาพ:** ใช้ข้อมูลอากาศและอุณหภูมิผิวน้ำทะเล (SST) ระดับภูมิภาครายวันร่วมกับคุณลักษณะล่าสุดที่ยังอยู่ในช่วงอายุที่ผ่านการทดสอบแล้ว โดยเพิ่ม `satellite_age_days` และ `valid_pixel_ratio` เป็นตัวแปรของโมเดล ข้อมูล SST ความละเอียดระดับกิโลเมตรใช้เป็นบริบทของแนวโน้มเท่านั้น ไม่ใช้สร้างแผนที่ระดับฟาร์มแทน Sentinel-2 [17]
4. **ลดความเชื่อมั่นตามอายุข้อมูล:** แสดง Data Freshness และ Confidence Badge ทุกครั้ง หากภาพเก่าเกินเกณฑ์จากผล Validation ระบบเปลี่ยนเป็นโหมด “ข้อมูลไม่เพียงพอ” แทนการคงแผนที่เดิมโดยไม่เตือนผู้ใช้
5. **รับข้อมูลยืนยันจากภาคสนาม:** เกษตรกรสามารถส่งภาพสีน้ำ ค่าความโปร่งใส และค่า DO (ถ้ามีเครื่องมือ) เพื่อช่วยยืนยันสถานการณ์ แต่ข้อมูลดังกล่าวจะแสดงแหล่งที่มาแยกจากค่าดาวเทียม

ดังนั้น ระบบสามารถ **คำนวณความเสี่ยงใหม่ได้รายวัน** เมื่อข้อมูลอากาศเข้ามา แต่แผนที่ NDCI ความละเอียด 20 เมตรจะอัปเดตเฉพาะเมื่อมีภาพ Sentinel-2 ที่ใช้ได้ ไม่เรียกการทำงานลักษณะนี้ว่า Real-time satellite monitoring

---

### 6.2.6 วิธีตรวจสอบความแม่นยำและความน่าเชื่อถือ

การประเมินผลจะตอบ 2 คำถามแยกกัน คือ (1) ค่าที่ประมาณจากภาพสอดคล้องกับค่าคุณภาพน้ำจริงเพียงใด และ (2) การแจ้งเตือนล่วงหน้าทำนายเหตุการณ์ Bloom ได้ดีเพียงใด โดยใช้แผนดังนี้:

1. **จับคู่ Ground Truth:** เก็บ Chlorophyll-a, DO, วันเวลา และพิกัดภาคสนามให้ใกล้เวลาที่ดาวเทียมผ่านมากที่สุด พร้อมบันทึกสภาพเมฆและวิธีตรวจวัด
2. **แยกชุดข้อมูลแบบไม่รั่วไหล:** แบ่ง Train/Validation/Test ตามช่วงเวลาและพื้นที่ ไม่สุ่มพิกเซลข้างเคียงไปอยู่คนละชุด และใช้ SMOTE เฉพาะ Training fold เท่านั้น
3. **ทดสอบย้อนหลังแบบ Rolling-origin:** ฝึกด้วยข้อมูลในอดีตแล้วทำนายช่วงเวลาถัดไป เพื่อจำลองการใช้งานจริง และกันเหตุการณ์ Bloom อย่างน้อยหนึ่งช่วงไว้เป็น Independent Test Event หากจำนวนข้อมูลเพียงพอ
4. **วัดทั้งการตรวจพบและการเตือนเกิน:** รายงาน Recall, Precision, F1-score, PR-AUC, Confusion Matrix และ False Alarms ต่อช่วงเวลา โดยให้ Recall เป็นตัวชี้วัดหลักแต่ไม่ละเลย Precision
5. **ตรวจค่าความน่าจะเป็น:** ใช้ Calibration curve และ Brier Score เพื่อตรวจว่าความเสี่ยง 70% เกิดจริงใกล้เคียง 70% หรือไม่ พร้อมรายงานช่วงความเชื่อมั่น 95% ด้วย Bootstrap
6. **เปรียบเทียบ Baseline/Ablation:** เปรียบเทียบกับกฎ NDCI threshold, โมเดลอากาศอย่างเดียว และโมเดลที่ไม่ใช้การจัดการข้อมูลขาดหาย เพื่อพิสูจน์ว่าส่วนประกอบของ AquaMind เพิ่มประสิทธิภาพจริง
7. **วิเคราะห์ตามความสดใหม่:** แยกผลเมื่อภาพมีอายุ 0–5, 6–10 และมากกว่า 10 วัน เพื่อนำผลจริงไปกำหนดจุดตัดของโหมด A/B/C และไม่กำหนดเกณฑ์อายุแบบคาดเดาล่วงหน้า

ค่าตัวเลขที่แสดงใน Story Board เป็น **เป้าหมายหรือข้อมูลตัวอย่างสำหรับออกแบบหน้าจอ** ไม่ใช่ผลการทดลองจริง ผลฉบับสุดท้ายจะรายงานจำนวนตัวอย่าง สัดส่วน Bloom/Non-bloom วิธีแบ่งชุดข้อมูล และช่วงความเชื่อมั่นควบคู่กับทุก Metric

---

## 6.3 เครื่องมือที่ใช้ในการพัฒนา

### 6.3.1 ภาษาโปรแกรม

| ภาษา | การใช้งาน |
|---|---|
| **Python** | AI/ML Model, Data Pipeline, Backend API |
| **JavaScript** | Frontend Dashboard, Web Map Interactive Features |
| **HTML/CSS** | UI Design and Styling |

### 6.3.2 Framework และ Libraries

| Library | การใช้งาน |
|---|---|
| `scikit-learn` | Random Forest, Cross-validation, SMOTE |
| `xgboost` | Gradient Boosting Model with GPU Support |
| `shap` | Explainable AI Analysis and Visualization |
| `rasterio`, `GDAL` | Satellite Image Processing (georeferencing, resampling) |
| `pandas`, `numpy` | Data Manipulation and Numerical Computation |
| `xarray` | Regional oceanographic NetCDF processing |
| `FastAPI` | Backend RESTful API with async support |
| `React.js` | Frontend Dashboard Framework |
| `Mapbox GL` | Interactive Web Map and Spatial Visualization |
| `Docker` | Container Deployment and Environment Consistency |
| `ee` (Google Earth Engine Python API) | Automated satellite data retrieval |
| `requests` | HTTP calls to weather and oceanographic APIs |

### 6.3.3 Cloud Services และ Tools

| Tool | การใช้งาน |
|---|---|
| **Google Earth Engine** | ดึงและประมวลผลข้อมูล Sentinel-2 อย่างอัตโนมัติ (Free tier) |
| **Copernicus Marine** | ดึงข้อมูล SST รายวันระดับภูมิภาคสำหรับ Environmental Features |
| **Google Colab** | ทดลองและฝึกโมเดล ML (Free GPU/TPU) |
| **GitHub + GitHub Actions** | Version Control, Automated Testing, CI/CD Pipeline |
| **AWS Lambda / Google Cloud Functions** | Serverless Backend สำหรับ Automated Data Pipeline |
| **AWS S3 / Google Cloud Storage** | Data Storage (satellite imagery, models, logs) |
| **Jupyter Notebook** | ทดลองและวิเคราะห์โมเดล Interactive |
| **Visual Studio Code** | Code Editor |

---

## 6.4 รายละเอียดโปรแกรมที่จะพัฒนา (Software Specification)

### 6.4.1 Input Specification

**ข้อมูลอินพุต:**

1. **Satellite Imagery (Sentinel-2)**
   - Source: Google Earth Engine
   - Selected bands: B2, B3, B4, B5, B8, B8A, B11, B12 และ Scene Classification Layer (SCL)
   - Spatial Resolution: 10m/pixel (Bands 2,3,4,8), 20m/pixel (Bands 5,6,7,8A,11,12); NDCI ใช้ความละเอียดเชิงสารสนเทศ 20m
   - Temporal Resolution: รอบกลับมาถ่ายพื้นที่เดิมตามปกติประมาณ 5 วัน แต่ช่วงห่างของ “ภาพที่ใช้ได้” อาจนานกว่านั้นเมื่อมีเมฆบัง
   - Format: GeoTIFF (georeferenced)
   - Preprocessing: Atmospheric correction (Bottom-of-Atmosphere reflectance)

2. **Weather Data**
   - Source: OpenWeather API + กรมอุตุนิยมวิทยา
   - Parameters: Air Temperature, Wind Speed & Direction, Relative Humidity, Precipitation
   - Temporal Resolution: Hourly forecasts (3–5 days ahead ตามความพร้อมของแหล่งข้อมูล)
   - Format: JSON

3. **Regional Oceanographic Data**
   - Source: Copernicus Marine Global Sea Surface Temperature (SST) หรือชุดข้อมูลสมุทรศาสตร์ที่ผ่านการตรวจคุณภาพเทียบเท่า
   - Parameters: Daily gap-free SST และ anomaly จากค่าเฉลี่ยตามฤดูกาล
   - Spatial role: ความละเอียดระดับภูมิภาค (ประมาณ 10 km สำหรับผลิตภัณฑ์อ้างอิง) ใช้เป็น Feature เชิงบริบท ไม่ใช้แทนแผนที่ NDCI ระดับฟาร์ม [17]
   - Format: NetCDF/API

4. **Ground Truth (Water Quality Samples)**
   - Chlorophyll-a concentration (mg/m³) via laboratory analysis
   - Dissolved Oxygen (DO) level (mg/L)
   - Sampling locations: 10-15 points per field campaign across AOI
   - Sampling frequency: หลายรอบเวลา ครอบคลุมทั้งช่วงปกติ ช่วงเริ่มเสี่ยง และช่วง Bloom เท่าที่สามารถเก็บได้

5. **User Input (from Farmer)**
   - Farm location (Latitude/Longitude) or select on map
   - Farm size (hectare) — for context
   - Aquaculture type (Shrimp pond, Fish cage, etc.)

---

### 6.4.2 Output Specification

**ข้อมูลเอาต์พุต:**

1. **Risk Assessment Card (สำหรับแต่ละฟาร์มหรือ AOI)**
   ```
   {
     "farm_id": "string",
     "location": { "lat": float, "lng": float },
     "prediction_generated_at": "ISO8601",
     "satellite_observed_at": "ISO8601",
     "satellite_age_days": int,
     "data_mode": "FRESH_SATELLITE|FORECAST_ASSISTED|INSUFFICIENT_DATA",
     "confidence_level": "HIGH|MEDIUM|LOW",
     "valid_pixel_ratio": float (0-1),
     "risk_level": "LOW|MEDIUM|HIGH",
     "risk_probability": float (0-1),
     "ndci_value": float,
     "chlorophyll_a_estimated": float (mg/m³),
     "top_risk_factors": [
       {
         "factor_name": "Temperature",
         "value": float,
         "shap_value": float,
         "shap_output_space": "raw|probability",
         "relative_importance": float (0-100),
         "direction": "INCREASE|DECREASE"
       },
       { ... },
       { ... }
     ],
     "forecast_5_days": [
       { "day": int, "risk_level": "string", "risk_prob": float },
       ...
     ],
     "recommendation": "string (ภาษาไทย)",
     "action_checklist": ["verify_water", "measure_do", "prepare_aeration", "contact_officer"]
   }
   ```

2. **Spatial Map (GeoJSON)**
   - Risk heatmap overlay on base map (Mapbox)
   - Selectable farm locations
   - Color-coded by risk level

3. **Time-Series Data (for Trend Analysis)**
   ```json
   {
     "dates": ["2025-01-01", "2025-01-05", ...],
     "ndci_values": [0.05, 0.12, ...],
     "risk_probabilities": [30%, 65%, ...],
     "actual_bloom_observed": [false, true, ...]
   }
   ```

4. **Report Export (PNG/PDF)**
   - Summary card
   - Risk map
   - 5-day forecast chart
   - Top risk factors visualization
   - Recommendations (Thai language)

---

### 6.4.3 Functional Specification

**Primary Functions:**

1. **Data Ingestion & Processing Pipeline**
   - Run scheduler daily เพื่อตรวจหาภาพ Sentinel-2 ใหม่ โดยไม่สมมติว่าจะมีภาพที่ใช้ได้ทุก 5 วัน
   - Extract NDCI, NDWI, and other spectral indices
   - Aggregate weather and regional oceanographic data from APIs
   - Perform quality checks (cloud cover, valid water pixels, data completeness, data age)

2. **Risk Estimation Model**
   - Input: Feature vector (spectral indices + weather + regional SST + temporal trends + data age)
   - Process: Pass through trained Random Forest / XGBoost model
   - Output: Risk probability (0-100%) + risk class (LOW/MEDIUM/HIGH)

3. **Explainability Engine (SHAP)**
   - For each prediction, compute SHAP values
   - Identify top-3 contributing features
   - Show direction and relative rank, while retaining the SHAP output space and avoiding causal interpretation

4. **Web Dashboard (Frontend)**
   - Display risk assessment card for selected farm
   - Interactive map with risk heatmap
   - Time-series charts (NDCI, Risk Probability, Forecast)
   - Alert notifications (push or email)
   - Report generation and export

5. **Notification System**
   - Trigger alert when risk_probability ≥ 70%
   - Send via: In-app notification, Email, SMS (if available)
   - Include recommendation text in Thai, data freshness, confidence level และลิงก์ยืนยันผลภาคสนาม

6. **User Authentication & Multi-Farm Management**
   - Register multiple farms per user
   - Role-based access (Farmer, Admin, Researcher)
   - Save preferences (email alerts, language, etc.)

7. **Field Feedback & Outcome Tracking**
   - ให้ผู้ใช้บันทึกว่าสีน้ำ/กลิ่น/พฤติกรรมสัตว์น้ำผิดปกติหรือไม่ พร้อมแนบภาพและค่า DO หากมี
   - บันทึกการตอบสนองที่ทำและผลที่เกิดขึ้นจริง เพื่อใช้เป็น Ground Truth หลังผ่านการตรวจสอบโดยผู้ดูแลข้อมูล

**แนวทางปฏิบัติหลังได้รับการแจ้งเตือน (Farmer Response Protocol):**

| ระดับ | สิ่งที่ระบบให้เกษตรกรทำ | หลักการความปลอดภัย |
|---|---|---|
| **ต่ำ** | ดูเวลาภาพล่าสุด เฝ้าสังเกตสี/กลิ่นน้ำและพฤติกรรมสัตว์ตามปกติ | ยังไม่ต้องเพิ่มต้นทุนหรือเปลี่ยนการจัดการจากผล AI เพียงอย่างเดียว |
| **ปานกลาง** | ตรวจสภาพน้ำ ณ ฟาร์ม วัด DO หากมีเครื่องมือ เตรียมเครื่องให้อากาศ ตรวจอุปกรณ์สำรอง และพิจารณาลดอาหารที่เหลือสะสม | ใช้ผลภาคสนามยืนยันก่อนดำเนินการที่มีต้นทุนสูง |
| **สูง** | ตรวจยืนยันทันที เพิ่มความถี่การวัด DO เปิดเครื่องให้อากาศเมื่อ DO ต่ำหรือสัตว์มีอาการขาดออกซิเจน ลดหรืองดอาหารชั่วคราวตามสภาพสัตว์ และติดต่อเจ้าหน้าที่ประมงในพื้นที่ | ไม่สูบหรือเปลี่ยนน้ำจากแหล่งภายนอกจนกว่าจะตรวจว่าปลอดภัย เพราะอาจนำน้ำที่มี Bloom เข้าฟาร์ม; การย้ายกระชังหรือจับขายก่อนกำหนดให้ทำเมื่อสภาพพื้นที่ ชนิดสัตว์ และคำแนะนำผู้เชี่ยวชาญรองรับ |
| **ข้อมูลไม่เพียงพอ** | ลงพื้นที่ตรวจน้ำและติดตามประกาศหน่วยงานรัฐ โดยไม่ตีความแผนที่เก่าว่าเป็นสถานการณ์ปัจจุบัน | ระบบงดออกคำแนะนำเฉพาะเจาะจงจนกว่าจะมีข้อมูลยืนยัน |

คำแนะนำจะปรับตามระบบเลี้ยง (บ่อ/กระชัง) และชนิดสัตว์น้ำ ไม่ใช้ข้อความเดียวกับทุกฟาร์ม และระบุชัดว่าเป็นแนวทางสนับสนุนการตัดสินใจ ไม่แทนผลตรวจน้ำหรือคำสั่งของเจ้าหน้าที่ แนวทางเรื่องการสังเกตสัตว์ การเพิ่มออกซิเจน และการลดอาหารสอดคล้องกับคำแนะนำของกรมประมง [16]

---

### 6.4.4 Software Architecture (Design)

```
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND LAYER (Python)                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Data Pipeline (Daily check; update when data exists)   │    │
│  │  ├─ GEE Sentinel-2 Downloader                           │    │
│  │  ├─ Environmental Clients (Weather + Regional SST)      │    │
│  │  ├─ Spectral Index Calculator (NDCI, NDWI, etc)        │    │
│  │  ├─ Feature Engineering (Temporal, Spatial trends)      │    │
│  │  └─ Data Validation & QC                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ML Model Registry & Inference Engine                   │    │
│  │  ├─ Random Forest Model (trained)                       │    │
│  │  ├─ XGBoost Model (trained)                             │    │
│  │  ├─ SHAP Explainer (cached for efficiency)              │    │
│  │  └─ Ensemble voting logic                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  FastAPI Backend Service                                │    │
│  │  ├─ POST /api/risk-assessment                           │    │
│  │  ├─ GET /api/farm/{farm_id}/history                     │    │
│  │  ├─ GET /api/heatmap/{bbox}                             │    │
│  │  ├─ POST /api/user/register-farm                        │    │
│  │  ├─ GET /api/forecast/{farm_id}                         │    │
│  │  └─ GET /api/export-report/{farm_id}                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │  PostgreSQL Database │  │  Redis Cache         │             │
│  │  ├─ Users            │  │  ├─ Model weights    │             │
│  │  ├─ Farms            │  │  ├─ Predictions      │             │
│  │  ├─ Risk history     │  │  └─ API responses    │             │
│  │  └─ Alerts           │  └──────────────────────┘             │
│  └──────────────────────┘                                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                             ↕ (REST API)
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER (React.js)                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Landing Page (Public)                                   │   │
│  │  ├─ Project intro + features                             │   │
│  │  ├─ Demo map                                             │   │
│  │  └─ Sign up / Login                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Dashboard (Authenticated)                               │   │
│  │  ├─ Farm Selector (dropdown or list)                     │   │
│  │  ├─ Risk Card Component                                  │   │
│  │  │  ├─ Risk gauge + percentage                           │   │
│  │  │  ├─ Top 3 risk factors (SHAP explanation)             │   │
│  │  │  └─ Recommendation text (Thai)                        │   │
│  │  ├─ Map Component (Mapbox GL)                            │   │
│  │  │  ├─ NDCI heatmap                                      │   │
│  │  │  ├─ Farm location markers                             │   │
│  │  │  └─ Zoom / Layer toggle                               │   │
│  │  ├─ Time-Series Charts (Recharts)                        │   │
│  │  │  ├─ NDCI trend (7 days)                               │   │
│  │  │  ├─ Risk probability forecast (5 days)                │   │
│  │  │  └─ Historical alerts                                 │   │
│  │  ├─ Notification Panel                                   │   │
│  │  └─ Export / Share buttons                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Settings Page                                           │   │
│  │  ├─ Manage multiple farms                                │   │
│  │  ├─ Alert preferences (email/SMS)                        │   │
│  │  ├─ Language preference (Thai/English)                   │   │
│  │  └─ Profile management                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

### 6.4.5 Data Flow Diagram

```
User (Farmer with Mobile/Web Browser)
          ↓
  [Frontend Dashboard]
    ├─ Select Farm
    ├─ View Current Risk
    ├─ Check Forecast
    └─ Export Report
          ↓
  [FastAPI Backend]
    ├─ Authenticate user
    ├─ Query historical data
    ├─ Call inference API
    └─ Retrieve SHAP explanations
          ↓
  [ML Inference Layer]
    ├─ Load pre-trained models
    ├─ Prepare feature vector
    ├─ Run Random Forest/XGBoost
    ├─ Generate SHAP values
    └─ Return predictions
          ↓
  [Database + Cache]
    ├─ Store results
    ├─ Retrieve historical data
    └─ Cache model weights
          ↓
  [Scheduled Data Pipeline (Async)]
    ├─ Daily: Check for a new usable Sentinel-2 image
    ├─ Daily: Fetch weather forecast and regional SST
    ├─ Process spectral indices
    ├─ Update features
    └─ Trigger inference for all farms
          ↓
  [Notification Engine]
    ├─ Check if risk ≥ 70%
    ├─ Send email alert
    ├─ Update dashboard
    └─ Log event
```

---

### 6.4.6 Database Schema (PostgreSQL)

```sql
-- Users Table
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  phone_number VARCHAR(20),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  role ENUM('farmer', 'officer', 'admin'),
  language VARCHAR(10) DEFAULT 'th',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Farms Table
CREATE TABLE farms (
  farm_id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(user_id),
  farm_name VARCHAR(255) NOT NULL,
  location_lat DECIMAL(10, 8),
  location_lng DECIMAL(11, 8),
  area_hectare FLOAT,
  aquaculture_type VARCHAR(50),  -- e.g., 'shrimp', 'fish'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Risk Assessment Results
CREATE TABLE risk_assessments (
  assessment_id SERIAL PRIMARY KEY,
  farm_id INT REFERENCES farms(farm_id),
  assessment_date TIMESTAMP DEFAULT NOW(),
  ndci_value FLOAT,
  risk_level ENUM('LOW', 'MEDIUM', 'HIGH'),
  risk_probability FLOAT,  -- 0.0 to 1.0
  chlorophyll_a FLOAT,  -- mg/m³
  top_factors JSONB,  -- Store SHAP top 3 factors
  model_version VARCHAR(50),
  actual_bloom_observed BOOLEAN DEFAULT NULL  -- Ground truth
);

-- Alerts Table
CREATE TABLE alerts (
  alert_id SERIAL PRIMARY KEY,
  farm_id INT REFERENCES farms(farm_id),
  alert_date TIMESTAMP DEFAULT NOW(),
  risk_probability FLOAT,
  sent_via ENUM('email', 'sms', 'in_app'),
  recipient VARCHAR(255),
  acknowledged BOOLEAN DEFAULT FALSE
);

-- Time-Series Data (for trend analysis)
CREATE TABLE sentinel_time_series (
  ts_id SERIAL PRIMARY KEY,
  farm_id INT REFERENCES farms(farm_id),
  observation_date DATE,
  ndci FLOAT,
  ndwi FLOAT,
  band_red FLOAT,
  band_nir FLOAT,
  cloud_cover FLOAT  -- percentage
);

-- Weather Data Archive
CREATE TABLE weather_archive (
  weather_id SERIAL PRIMARY KEY,
  farm_id INT REFERENCES farms(farm_id),
  observation_date TIMESTAMP,
  temperature FLOAT,
  wind_speed FLOAT,
  wind_direction INT,  -- 0-360 degrees
  humidity FLOAT,
  precipitation FLOAT,
  source VARCHAR(50)  -- 'openweather', 'thai_met', etc.
);
```

---

## 6.5 ขอบเขตและข้อจำกัดของโปรแกรมที่พัฒนา

### 6.5.1 ขอบเขต (Scope)

1. **เชิงพื้นที่:** อ่าวไทยตอนบน (จ.ฉะเชิงเทรา - ชลบุรี) ตามพื้นที่ Area of Interest (AOI) ที่กำหนด

2. **เชิงข้อมูล:**
   - ใช้ข้อมูล Sentinel-2 ที่มีความละเอียด 10–20m/pixel ตามแถบคลื่นและดัชนี
   - บูรณาการข้อมูลพยากรณ์อากาศจากอย่างน้อย 2 แหล่ง (OpenWeather API + กรมอุตุนิยมวิทยา)
   - ใช้ SST รายวันระดับภูมิภาคเป็นบริบทของแนวโน้ม โดยไม่ Resample แล้วอ้างเป็นความละเอียดระดับฟาร์ม
   - ระยะเวลาการพยากรณ์: 3-5 วันล่วงหน้า
   - ตรวจข้อมูลใหม่รายวัน แต่แยกความถี่การคำนวณความเสี่ยงออกจากความถี่ของภาพดาวเทียมอย่างชัดเจน

3. **เชิงคุณลักษณะ:**
   - ประเมินความเสี่ยง 3 ระดับ (Low, Medium, High)
   - อธิบายปัจจัยเสี่ยง Top-3 โดยใช้ SHAP Analysis
   - แสดงอายุภาพ โหมดข้อมูล ระดับความเชื่อมั่น และสถานะข้อมูลไม่เพียงพอ
   - รองรับภาษาไทยในส่วน UI คำแนะนำ และขั้นตอนรับมือหลังได้รับแจ้งเตือน

4. **เชิงเทคนิค:**
   - Web-based application (Responsive design สำหรับ PC และ Mobile)
   - Backend: Python FastAPI + PostgreSQL
   - Frontend: React.js + Mapbox GL
   - Cloud deployment: Serverless (AWS Lambda / Google Cloud Functions)

---

### 6.5.2 ข้อจำกัด (Limitations)

1. **ข้อจำกัดด้านข้อมูล**
   - Sentinel-2 มีรอบกลับมาถ่ายพื้นที่เดิมตามปกติประมาณ 5 วัน และเมฆอาจทำให้ช่วงห่างของภาพที่ใช้ได้นานกว่านั้น ระบบจึงไม่สามารถแสดงสภาพผิวน้ำระดับ 10–20 เมตรแบบ Real-time
   - ความแม่นยำของพยากรณ์อากาศจากแหล่งข้อมูล (โดยทั่วไป 3-5 วันแรกมีความแม่นยำสูง หลังจากนั้นลดลง)
   - ข้อมูล Ground Truth ในระยะต้นมีจำนวนจำกัดทั้งเชิงพื้นที่และจำนวนเหตุการณ์ จึงต้องรายงานช่วงความเชื่อมั่นและหลีกเลี่ยงการอ้างว่าสามารถใช้แทนการตรวจน้ำได้

2. **ข้อจำกัดด้านเทคนิค**
   - ระบบต้นแบบ (Prototype) ในเวลานี้ยังไม่สามารถรันบน Edge devices (เช่น Raspberry Pi) ได้
   - หลังข้อมูลใหม่พร้อมใช้ การประมวลผลอาจใช้เวลา 5-15 นาที โดยเวลานี้ไม่รวมรอบการถ่ายและเผยแพร่ข้อมูลของดาวเทียม
   - การเข้าถึง Google Earth Engine API มีข้อจำกัดด้าน Rate Limiting

3. **ข้อจำกัดด้านองค์กร**
   - ระบบนี้ได้รับการศึกษาวิจัยในระดับ Proof-of-Concept ยังไม่ใช่ระบบเชิงพาณิชย์เต็มรูปแบบ
   - การแก้ไขบัค และการ Update ยังขึ้นอยู่กับทีมนักศึกษา/นักวิจัย

4. **ข้อจำกัดด้านการพยากรณ์**
   - การพยากรณ์เป็น Probabilistic Model (ไม่ใช่ Deterministic) ไม่สามารถยืนยัน 100% ว่าจะเกิด Bloom หรือไม่
   - ผลการพยากรณ์ขึ้นอยู่กับ Quality ของข้อมูล Training (Historical Data)
   - เมื่อภาพเก่า ความเสี่ยงที่คำนวณรายวันเป็น Forecast-assisted ไม่ใช่การสังเกตสภาพน้ำล่าสุดจากดาวเทียม

5. **ข้อจำกัดด้านการยอมรับ**
   - ระบบออกแบบเป็น "Decision Support Tool" ไม่ใช่ "Autonomous System" เกษตรกรจะต้องอาศัยการสังเกตภาคสนามและประสบการณ์ประกอบการตัดสินใจ

---

# ส่วนที่ 7: เนื้อเรื่องย่อ (Story Board) — ภาพประกอบและตัวอย่าง

### 7.1 Mockup ของ User Interface

**หน้า 1: Landing Page (สาธารณะ)**

```
┌──────────────────────────────────────────────────────────┐
│  🌊 AquaMind: Smart Algal Bloom Early Warning System      │
│     เครื่องมือระวังแพลงก์ตอนบลูม ด้วย AI และดาวเทียม     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  [ภาพสไลด์เนื้อเรื่อง: Farmer checking mobile phone]     │
│                                                           │
│  ✅ คาดการณ์ 3-5 วันล่วงหน้า                             │
│  ✅ เข้าใจสาเหตุด้วย AI Explanation (SHAP)              │
│  ✅ ลดต้นทุนการเฝ้าระวัง 10 เท่า                        │
│  ✅ ภาษาไทย ใช้งานง่าย                                  │
│                                                           │
│  [ 🔐 Login ]  [ 📝 Sign Up ]                            │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**หน้า 2: Main Dashboard (หลังเข้าสู่ระบบ)**

```
┌──────────────────────────────────────────────────────────────┐
│  ☰ Menu    AquaMind Dashboard    👤 User Profile     ⚙️ Settings
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  หลังเลือกฟาร์ม: [▼ ฟาร์มชลบุรี ชาย 1]                       │
│                                                               │
│  ┌─ ⚠️ ความเสี่ยง: สูง (HIGH) ───────────────────────┐     │
│  │                                                    │     │
│  │  ความเสี่ยง: 73%                                  │     │
│  │  ███████░░░ (Risk Gauge)                         │     │
│  │  ภาพดาวเทียมล่าสุด: 2 วันที่แล้ว                  │     │
│  │  โหมดข้อมูล: Forecast-assisted | เชื่อมั่น: ปานกลาง │     │
│  │                                                    │     │
│  │  สาเหตุหลัก (Top Factors):                        │     │
│  │  ① SST ภูมิภาค: +2.1°C → ดันความเสี่ยงขึ้น (อันดับ 1) │     │
│  │  ② ความเร็วลม: ลดลง 40% → ดันความเสี่ยงขึ้น (อันดับ 2) │     │
│  │  ③ Chlorophyll trend: ↑8%/day → ดันขึ้น (อันดับ 3) │     │
│  │                                                    │     │
│  │  💡 ขั้นแรก: ตรวจสี/กลิ่นน้ำและวัด DO             │     │
│  │  หาก DO ต่ำ/สัตว์ลอยหัว: เปิดเครื่องให้อากาศ      │     │
│  │  ⚠️ อย่าเปลี่ยนน้ำจนกว่าจะยืนยันน้ำภายนอกปลอดภัย  │     │
│  │                                                    │     │
│  │  [ 🗺️ ดูแผนที่ ]  [ 📊 ดูรายละเอียด ]             │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌─ 📅 การพยากรณ์ 5 วัน ─────────────────────────────┐     │
│  │                                                    │     │
│  │  วันนี้     ⚠️ High    วันพรุ่งนี้  ⚠️ High      │     │
│  │  +1 วัน    ⚠️ Medium   +2 วัน     🟢 Low       │     │
│  │  +3 วัน    🟢 Low      +4 วัน     🟢 Low       │     │
│  │                                                    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**หน้า 3: Interactive Map**

```
┌──────────────────────────────────────────────────────────────┐
│  🗺️ แผนที่ความเสี่ยง (Risk Heatmap) — อ่าวศรีราชา           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Zoom: 11x   |  [Layer: NDCI] [Weather] [Farms]             │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │     🌊 [NDCI Heatmap with color gradient]           │   │
│  │     🟢 Low / 🟡 Medium / 🔴 High                    │   │
│  │     Threshold calibrated from local validation data │   │
│  │                                                       │   │
│  │     📍 Farm markers (clickable)                      │   │
│  │     🌪️ Wind arrows                                   │   │
│  │     🌡️ Temperature overlay                           │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ℹ️ Click on farm marker to view detailed risk card         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**หน้า 4: Time-Series Analysis**

```
┌──────────────────────────────────────────────────────────────┐
│  📊 ประวัติความเสี่ยง 30 วัน                                 │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │ Risk Probability (%) ← Historical Data | Forecast   │   │
│  │                                                       │   │
│  │ 100%│                          ┌───┐                 │   │
│  │  80%│      ┌─────┐ Historical /   \ 5-day Forecast  │   │
│  │  60%│     /       \   trend    \     ─────────      │   │
│  │  40%│    /         \___________\   /                │   │
│  │  20%│___/                       \_/                 │   │
│  │   0%└─────────────────────────────────────────      │   │
│  │     Day-30  Day-20  Day-10  Today  +1  +2  +3      │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  📋 History Table:                                           │
│  Date       | Risk Level | NDCI   | Actual Bloom             │
│  2025-01-15 | HIGH       | 0.25   | ✓ Confirmed             │
│  2025-01-10 | MEDIUM     | 0.15   | ✗ Did not occur         │
│  2025-01-05 | LOW        | 0.05   | ✗ Did not occur         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 7.2 ตัวอย่างผลลัพธ์เชิงสถิติ (สำหรับ Validation)

**Table: ตัวอย่างรูปแบบรายงานผล (เป็นค่าเป้าหมายสำหรับออกแบบ ไม่ใช่ผลทดลองจริง)**

```
Metric                  | Random Forest | XGBoost  | Acceptance target
─────────────────────────────────────────────────
Recall (ลดลด False Neg) | 82%           | 85%      | ≥ 80%
Precision               | 65%           | 70%      | N/A
F1-Score                | 0.73          | 0.77     | N/A
ROC-AUC                 | 0.82          | 0.86     | N/A
─────────────────────────────────────────────────

Note: ตัวเลข RF/XGBoost เป็น mock data เท่านั้น; ผลจริงต้องมาจาก Independent Test Set และใช้ SMOTE เฉพาะ Training fold
```

รายงานผลจริงจะเพิ่ม Confusion Matrix, PR-AUC, Brier Score/Calibration curve, False Alarms ต่อเดือน, ช่วงความเชื่อมั่น 95% และผลแยกตามอายุภาพดาวเทียม พร้อมเปรียบเทียบกับ Baseline (กฎ NDCI threshold และโมเดลอากาศอย่างเดียว) หากชุดทดสอบมีเหตุการณ์จริงน้อย จะไม่สรุปว่าโมเดลแม่นยำจาก Accuracy เพียงค่าเดียว และจะระบุจำนวนเหตุการณ์ที่ใช้ทดสอบอย่างโปร่งใส

---

# ส่วนที่ 8: ความแปลกใหม่และนวัตกรรม (Novelty & Innovation Statement)

โครงการ AquaMind แตกต่างจากระบบที่มีอยู่ใน 4 มิติหลัก ดังนี้

## 8.1 High-Resolution Coastal Monitoring (ความละเอียดระดับฟาร์ม)

ยกระดับจาก 300m/pixel (ระดับมหาสมุทร) เป็น 10–20m/pixel ตามแถบคลื่นและดัชนี ช่วยวิเคราะห์บริเวณฟาร์มชายฝั่งได้ละเอียดขึ้น โดย NDCI มีความละเอียดเชิงสารสนเทศ 20 เมตรและต้องผ่านการยืนยันภาคสนามก่อนสรุประดับกระชัง

---

## 8.2 Explainable AI for Environmental Risk (AI ที่อธิบายได้)

ไม่ใช่แค่ "Black-box" ที่บอกว่าเสี่ยงหรือไม่เสี่ยง แต่ใช้ SHAP Analysis อธิบายว่า "เหตุใด" ระบบจึงประเมินความเสี่ยงสูง เช่น แสดงว่า "SST ระดับภูมิภาคสูงกว่าค่าเฉลี่ยและความเร็วลมลดลงต่อเนื่อง เป็นสองปัจจัยหลักที่ผลักคะแนนความเสี่ยงขึ้น" โดยไม่ตีความ SHAP เป็นเหตุและผลหรือเป็นเปอร์เซ็นต์ความเสียหาย

---

## 8.3 Decision Support Focus (เน้นสนับสนุนการตัดสินใจ ไม่ใช่ระบบอัตโนมัติ)

ออกแบบให้เป็นเครื่องมือประกอบการตัดสินใจของมนุษย์ ไม่ใช่ระบบอัตโนมัติที่ตัดสินใจแทน ซึ่งลดความเสี่ยงจากการพยากรณ์ผิดพลาด และสร้างความน่าเชื่อถือในกลุ่มผู้ใช้งาน

---

## 8.4 Thai-Localized Pipeline (ออกแบบเพื่อบริบทไทยโดยเฉพาะ)

Interface ภาษาไทย, AOI ที่ตรงกับพื้นที่เพาะเลี้ยงสัตว์น้ำชายฝั่งไทย, และ Feature Engineering ที่คำนึงถึงฤดูกาลและสภาพอากาศของอ่าวไทยโดยเฉพาะ

---

# ส่วนที่ 9: พื้นที่ศึกษาและกลุ่มเป้าหมาย

## 9.1 พื้นที่ศึกษา (Area of Interest: AOI)

ชายฝั่งอ่าวไทยตอนบน ตั้งแต่อ่าวบางปะกง จ.ฉะเชิงเทรา ถึง อ่าวศรีราชา จ.ชลบุรี ซึ่งเป็นพื้นที่เพาะเลี้ยงสัตว์น้ำชายฝั่งที่สำคัญของประเทศ

## 9.2 กลุ่มเป้าหมายหลัก (Primary Users)

- เกษตรกรผู้เพาะเลี้ยงสัตว์น้ำชายฝั่ง (ประสานงานผ่านสมาคมการประมงพื้นบ้านชลบุรี)
- เจ้าหน้าที่หน่วยงานภาครัฐด้านทรัพยากรทางทะเล (กรมประมง, ทช.)

---

# ส่วนที่ 10: การทบทวนวรรณกรรมและเปรียบเทียบเทคโนโลยี

## 10.1 ตารางเปรียบเทียบระบบที่มีอยู่กับ AquaMind

| คุณสมบัติ | การตรวจวัดแบบดั้งเดิม (In-situ) | ระบบสากล (NOAA HABs) | **AquaMind (โครงการนี้)** |
| :--- | :---: | :---: | :---: |
| **ความละเอียด (Resolution)** | เฉพาะจุด (Point) | 300m/pixel | **10–20m/pixel ตามแถบคลื่น/ดัชนี (Farm-area level)** |
| **ต้นทุนการเฝ้าระวัง** | สูงมาก (~5,000–10,000 บ./ครั้ง) | ฟรี (แต่สเกลระดับโลก) | **~500 บาท/เดือน** |
| **ความรวดเร็ว** | ใช้เวลาหลายวัน (รอผลแล็บ) | อัปเดตรายวัน | **คำนวณความเสี่ยงรายวัน; แผนที่ NDCI 20m อัปเดตเมื่อมีภาพที่ใช้ได้ (รอบปกติประมาณ 5 วัน)** |
| **การอธิบายผล (Explainability)** | ต้องอาศัยผู้เชี่ยวชาญ | แสดงเฉพาะแผนที่ | **AI อธิบาย Top-3 Risk Factors** |
| **รองรับภาษาไทย** | ขึ้นอยู่กับผู้ใช้ | ❌ | **✅ ออกแบบสำหรับเกษตรกรไทย** |
| **การพยากรณ์ล่วงหน้า** | ❌ | จำกัด | **3–5 วันล่วงหน้า** |

---

## 10.2 งานวิจัยที่เกี่ยวข้อง

งานของ Pahlevan et al. (2020) รายงานความสอดคล้องของผลิตภัณฑ์ Sentinel-2 และ Landsat-8 สำหรับการติดตามแหล่งน้ำ [5] ขณะที่ Chen et al. (2019) ศึกษาการใช้ Machine Learning ประมาณความเข้มข้นของคลอโรฟิลล์-a จาก Sentinel-2 [6] และ Lundberg & Lee (2017) เสนอวิธี SHAP สำหรับอธิบายอิทธิพลของตัวแปรต่อผลพยากรณ์ [9] โครงการนี้จะทดสอบประสิทธิภาพและการยอมรับของผู้ใช้ในบริบทอ่าวไทยโดยตรง แทนการถือว่าผลจากพื้นที่อื่นใช้ได้ทันที

โครงการ AquaMind จึงต่อยอดจากงานวิจัยเหล่านี้ โดยเพิ่มมิติ **Thai-Localized Pipeline** และ **Farm-level Resolution** ซึ่งยังไม่มีระบบใดในประเทศไทยทำได้ในปัจจุบัน

---

# ส่วนที่ 11: องค์ประกอบของทีมโครงการ

| ชื่อสมาชิก | บทบาท (Role) | ความรับผิดชอบหลัก |
|:---|:---|:---|
| **ศ. ดร. ปิยะ มหาวิทยาลัย** | Project Lead & Advisor | กำหนดทิศทาง, ประสานงานกับ Stakeholder |
| **นาย อิทธิพล เดชะผล** | Data Engineer | Sentinel-2 Pipeline, Google Earth Engine, Data Preprocessing |
| **นาย ชาตรี พิมพ์สิทธิ** | ML Engineer | Feature Engineering, Model Training (RF/XGBoost), SHAP Analysis |
| **นาย ธวัน ตันติสิรกุล** | Backend Developer | FastAPI Development, Database Design, API Integration |
| **นาย เทวนาถ สระทองแดง** | Full-Stack Developer | FastAPI Backend, React Frontend, Cloud Deployment |
| *(ทุกคน)* | Documentation & Pitch | รายงานฉบับสมบูรณ์, เตรียมการนำเสนอ |

---

# ส่วนที่ 12: แผนการดำเนินงาน (Gantt Chart — 12 สัปดาห์)

| เฟส | กิจกรรมหลัก | สัปดาห์ | ผู้รับผิดชอบ |
| :--- | :--- | :---: | :--- |
| **1. Data Setup** | วางแผนเก็บ Ground Truth หลายรอบเวลา, ตั้งค่า GEE API, พัฒนา ETL Pipeline | 1–2 | Data Engineer |
| **2. Model Dev** | Feature Engineering, Train RF/XGBoost, SMOTE เฉพาะชุดฝึก, Temporal/Spatial Validation, SHAP Analysis | 3–5 | ML Engineer |
| **3. Integration** | พัฒนา FastAPI Backend, React Dashboard, เชื่อมต่อโมเดล | 6–8 | Full-Stack Dev |
| **4. User Testing** | ทดสอบกับผู้ใช้ 30 ราย, วัด SUS Score, ปรับปรุง UI | 9–10 | ทั้งทีม |
| **5. Submission** | รายงานฉบับสมบูรณ์, วิดีโอสาธิต, เตรียม Pitch | 11–12 | ทั้งทีม |

---

# ส่วนที่ 13: ตัวชี้วัดความสำเร็จ (KPIs)

| KPI | เป้าหมาย | เหตุผล |
|---|---|---|
| **Recall (Technical)** | ≥ 80% | ระบบเตือนภัยต้องไม่พลาด Bloom Event จริง แม้จะมี False Alarm บ้าง (Minimize False Negatives) |
| **Precision** | ≥ 60% บน Independent Test Set | ควบคุมการแจ้งเตือนเกินจนผู้ใช้เกิด Alert Fatigue โดยปรับ Threshold จาก Validation Set เท่านั้น |
| **Calibration** | Brier Score ดีกว่า Baseline และแสดง Calibration curve | ทำให้ค่าความเสี่ยง 0–100% มีความหมาย ไม่ได้ดูเฉพาะการแบ่งคลาส |
| **System Latency** | ≤ 15 นาที | นับจากข้อมูลใหม่พร้อมใช้งานในแหล่งข้อมูลจนถึงแสดงผลบน Dashboard ไม่รวมเวลารอรอบดาวเทียม |
| **Data Transparency** | 100% ของผลลัพธ์แสดงเวลาภาพล่าสุด โหมดข้อมูล และความเชื่อมั่น | ป้องกันผู้ใช้เข้าใจแผนที่เก่าว่าเป็นข้อมูลปัจจุบัน |
| **Usability (SUS Score)** | ≥ 70 คะแนน | ระดับ "Good" ตามเกณฑ์มาตรฐาน SUS [13] |
| **Ground Truth Coverage** | 10–15 จุดต่อรอบ และเก็บหลายรอบเวลา | ครอบคลุมความแตกต่างทั้งเชิงพื้นที่และช่วงปกติ/ช่วงเสี่ยงสำหรับ Model Validation |

**หมายเหตุเรื่อง Recall vs Precision:**  
สำหรับระบบเตือนภัย การพลาดเหตุการณ์จริง (False Negative) อาจสร้างความเสียหายสูง จึงให้ Recall เป็นตัวชี้วัดหลัก อย่างไรก็ตาม False Positive ที่มากเกินไปทำให้เกษตรกรเสียค่าใช้จ่ายและเลิกเชื่อถือระบบ จึงกำหนด Precision, จำนวน False Alarm และ Calibration เป็นตัวชี้วัดร่วม การกล่าวว่าโมเดล “แม่นยำ” จะทำได้ต่อเมื่อผ่านชุดทดสอบอิสระและรายงานช่วงความเชื่อมั่นแล้วเท่านั้น

---

# ส่วนที่ 14: การยอมรับข้อจำกัดและการบริหารความเสี่ยง

| ข้อจำกัด/ความเสี่ยง | ระดับผลกระทบ | แผนจัดการ |
| :--- | :---: | :--- |
| **Rare Event Problem** — Bloom เกิดไม่บ่อย ทำให้ข้อมูลไม่สมดุล | สูง | ใช้ Class Weight/SMOTE เฉพาะ Training fold, เลือกวิธีจาก Validation และประเมินด้วย PR-AUC/Recall/Precision แทน Accuracy เพียงค่าเดียว |
| **รอบดาวเทียมห่างและเมฆบังภาพ** | สูง | ตรวจภาพทุกวัน, ใช้ภาพล่าสุดร่วมกับแนวโน้มอากาศ, ใส่อายุข้อมูลเป็น Feature, ลด Confidence และหยุดสร้างแผนที่ใหม่เมื่อข้อมูลเกินเกณฑ์ |
| **ความคลาดเคลื่อนของพยากรณ์อากาศ** | ปานกลาง | ใช้ข้อมูลจาก 2 แหล่ง (OpenWeather + กรมอุตุนิยมวิทยา) ถ่วงน้ำหนัก |
| **Data Leakage จากพื้นที่/เวลาใกล้กัน** | สูง | แบ่ง Train/Test ตามเวลาและพื้นที่, ทำ Rolling-origin validation และใช้ SMOTE หลังแบ่งข้อมูลแล้วเท่านั้น |
| **ความเสี่ยงจากการตัดสินใจผิดพลาด** | สูง | ระบบเป็น Decision-Support Tool แสดงความเชื่อมั่นและขั้นตอนยืนยันภาคสนาม; การเปลี่ยนน้ำ ย้ายกระชัง หรือจับขายต้องพิจารณากับผู้เชี่ยวชาญ |

---

# ส่วนที่ 15: เครื่องมือและเทคโนโลยีที่ใช้

## ภาษาโปรแกรม

| ภาษา | การใช้งาน |
|---|---|
| **Python** | AI/ML Model, Data Pipeline, Backend API |
| **JavaScript** | Frontend Dashboard, Web Map |
| **HTML/CSS** | UI Design |

## Framework และ Libraries

| Library | การใช้งาน |
|---|---|
| `scikit-learn` | Random Forest, Cross-validation, SMOTE |
| `xgboost` | Gradient Boosting Model |
| `shap` | Explainable AI Analysis |
| `rasterio`, `GDAL` | ประมวลผลภาพดาวเทียม |
| `pandas`, `numpy` | Data Manipulation |
| `xarray` | อ่านและประมวลผลข้อมูลสมุทรศาสตร์รูปแบบ NetCDF |
| `FastAPI` | Backend RESTful API |
| `React.js` + `Mapbox` | Frontend Dashboard |
| `Docker` | Container Deployment |

## Tools

| Tool | การใช้งาน |
|---|---|
| Google Earth Engine | ดึงและประมวลผลข้อมูล Sentinel-2 |
| Copernicus Marine | ข้อมูล SST รายวันระดับภูมิภาคสำหรับ Feature เชิงบริบท |
| GitHub + CI/CD | Version Control, Automated Testing |
| AWS/GCP Serverless | Cloud Deployment |
| Jupyter Notebook | ทดลองและวิเคราะห์โมเดล |

---

# ส่วนที่ 16: งบประมาณ

| รายการ | ค่าใช้จ่าย | หมายเหตุ |
|---|---|---|
| Water Quality Test Kit (Ground Truth) | ~2,000 บาท | อุปกรณ์ตรวจเบื้องต้นสำหรับการเก็บภาคสนามรอบนำร่อง; รอบเพิ่มเติมและ Chlorophyll-a laboratory analysis จะประสานหน่วยงานพันธมิตรหรือใช้ข้อมูลที่มีอยู่ |
| Cloud Computing (GCP/AWS) | ฟรี | ใช้ Free Tier และ Education Credits |
| Google Earth Engine | ฟรี | สิทธิ์การศึกษา |
| GitHub | ฟรี | GitHub Student Pack |
| **รวม** | **~2,000 บาท** | |

---

# ส่วนที่ 17: แผนการต่อยอดและความยั่งยืน (Sustainability)

**ระยะสั้น (หลัง NSC):**  
- ต้นทุน Cloud เฉลี่ย ~500 บาท/เดือน (Serverless Architecture) ทำให้ระบบสามารถรันต่อเนื่องได้โดยไม่ต้องมีงบประมาณมาก

**ระยะกลาง:**  
- นำโครงการต้นแบบที่สำเร็จไปสมัครทุน TED Youth Startup หรือ NSTDA Research Grant เพื่อขยายผลไปยังพื้นที่อื่น

**ระยะยาว (Business Model):**  
- Open Source สำหรับเกษตรกรรายย่อย (สร้าง Trust และ Community)
- Premium API Access สำหรับภาคเอกชน เช่น บริษัทประกันภัยสัตว์น้ำ หรือฟาร์มขนาดใหญ่
- Consulting กับหน่วยงานรัฐระดับจังหวัดหรือกรมประมง

---

# ส่วนที่ 18: จริยธรรมและสิ่งส่งมอบ

**จริยธรรม (Ethics & Legal Compliance):**
- ข้อมูลดาวเทียม Sentinel-2 เป็น Open-access ภายใต้สิทธิ์ Copernicus Programme
- ระบบแสดงเฉพาะข้อมูลสิ่งแวดล้อม ไม่มีการจัดเก็บข้อมูลส่วนบุคคล (PDPA Compliant)
- ซอร์สโค้ดทั้งหมดจะเผยแพร่เป็น Open Source บน GitHub

**สิ่งส่งมอบ (Deliverables):**
1. **GitHub Repository** — ซอร์สโค้ดฉบับสมบูรณ์พร้อม README และ CI/CD Pipeline
2. **Web Dashboard (Live Demo)** — URL สำหรับเข้าใช้งานระบบจริง
3. **วิดีโอสาธิต** — คลิป 3 นาที แสดงการทำงานของระบบแบบ End-to-End
4. **รายงานฉบับสมบูรณ์** — ตามรูปแบบที่ NSC กำหนด

---

# ส่วนที่ 19: ขอบเขตและข้อจำกัดของโปรแกรม

**ขอบเขต:**
1. วิเคราะห์และประเมินความเสี่ยงจากข้อมูลภาพถ่ายดาวเทียม Sentinel-2
2. แสดงผลผ่าน Web Dashboard ภาษาไทย พร้อม Interactive Map
3. อธิบายปัจจัยเสี่ยงด้วย SHAP Analysis
4. คาดการณ์ความเสี่ยงล่วงหน้า 3–5 วัน
5. รองรับการใช้งานผ่าน Web Browser ทั้งคอมพิวเตอร์และมือถือ
6. แสดงอายุภาพดาวเทียม โหมดข้อมูล และระดับความเชื่อมั่นของทุกผลการประเมิน
7. แสดงขั้นตอนตรวจสอบและรับมือหลังแจ้งเตือน พร้อมรับผลยืนยันจากเกษตรกรกลับเข้าสู่ระบบ

**ข้อจำกัด:**
1. ความแม่นยำขึ้นอยู่กับคุณภาพข้อมูลดาวเทียมและพยากรณ์อากาศ
2. Sentinel-2 ไม่ได้ให้ภาพใหม่ทุกวัน และเมฆหนาอาจทำให้ไม่มีภาพระดับ 10–20 เมตรที่ใช้ได้หลายรอบ ระบบจะลดความเชื่อมั่นหรือแจ้งว่าข้อมูลไม่เพียงพอ
3. ระบบต้นแบบครอบคลุมเฉพาะ AOI อ่าวไทยตอนบน
4. การพยากรณ์เป็นการประเมินความเสี่ยง ไม่สามารถยืนยันการเกิดเหตุการณ์ได้ 100%
5. ยังอยู่ในระดับ Prototype ยังไม่ใช่ระบบเชิงพาณิชย์เต็มรูปแบบ
6. คำแนะนำหลังแจ้งเตือนเป็นแนวทางทั่วไป ต้องปรับตามชนิดสัตว์ ระบบเลี้ยง ค่าตรวจน้ำ และคำแนะนำของเจ้าหน้าที่ในพื้นที่

---

# เอกสารอ้างอิง (References)

[1] Thai PBS. (2566). *กรมทะเลชายฝั่ง ชี้แจง "แพลงก์ตอนบลูม" เกาะล้าน จ.ชลบุรี*. สืบค้นจาก: https://www.thaipbs.or.th/news/content/330148

[2] GISTDA. (2566). *การติดตามคุณภาพน้ำทะเลและปรากฏการณ์น้ำเปลี่ยนสีด้วยข้อมูลดาวเทียม*. สืบค้นจาก: http://coastalradar.gistda.or.th/

[3] European Space Agency (ESA). (2023). *Sentinel-2 User Handbook*. Standard Document.

[4] Gorelick, N., et al. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27.

[5] Pahlevan, N., et al. (2020). Sentinel-2/Landsat-8 product consistency and implications for monitoring aquatic systems. *Remote Sensing of Environment*, 240, 111664.

[6] Chen, Y., et al. (2019). Machine learning algorithms for estimating chlorophyll-a concentration using Sentinel-2 data. *International Journal of Remote Sensing*, 40(22), 8685–8704.

[7] Ali, A., et al. (2022). Predicting chlorophyll-a concentration from Sentinel-2 imagery using machine learning models. *Environmental Monitoring and Assessment*, 194(3), 1–15.

[8] McFeeters, S.K. (1996). The Use of the Normalized Difference Water Index (NDWI). *International Journal of Remote Sensing*, 17(7), 1425–1432.

[9] Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions (SHAP). *NeurIPS*, 30.

[10] Mishra, S. & Mishra, D. (2012). Normalized Difference Chlorophyll Index (NDCI). *Remote Sensing of Environment*, 117, 394–406.

[11] Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5–32.

[12] Chen, T. & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *ACM SIGKDD*, 785–794.

[13] Brooke, J. (1996). SUS — A quick and dirty usability scale. *Usability evaluation in industry*, 189(194), 4–7.

[14] Chawla, N.V., et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. *JAIR*, 16, 321–357.

[15] United Nations. (2015). *Sustainable Development Goal 14: Life Below Water*.

[16] สำนักงานประมงจังหวัดสระบุรี กรมประมง. (2568). *ลงพื้นที่ตรวจสอบกรณีปลาลอยหัวและให้คำแนะนำด้านการเพิ่มออกซิเจนและลดอาหาร*. สืบค้นจาก: https://www4.fisheries.go.th/local/index.php/main/view_activities/9/246642

[17] Copernicus Marine Service. (2025). *Product User Manual for the Global Sea Surface Temperature Level-4 Near Real-Time Product (SST_GLO_PHY_L4_NRT_010_043)*. สืบค้นจาก: https://documentation.marine.copernicus.eu/PUM/CMEMS-SST-PUM-010-043.pdf

[18] NOAA National Ocean Service. (2025). *Harmful Algal Blooms (Red Tide): Frequently Asked Questions*. สืบค้นจาก: https://oceanservice.noaa.gov/hazards/hab/
