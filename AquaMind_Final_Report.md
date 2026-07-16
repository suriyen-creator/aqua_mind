# รายงานฉบับสมบูรณ์

## โครงการ AquaMind

### แพลตฟอร์มพยากรณ์การเกิดแพลงก์ตอนบลูมและวิเคราะห์คุณภาพน้ำแบบ End-to-End จากภาพถ่ายดาวเทียม

**ชื่อภาษาอังกฤษ:** AquaMind: End-to-End Algal Bloom Prediction and Water Quality Analysis Platform via Satellite Imagery  
**การแข่งขัน:** การแข่งขันพัฒนาโปรแกรมคอมพิวเตอร์แห่งประเทศไทย ครั้งที่ 28 (NSC 2026)  
**หมวด:** โปรแกรมเพื่องานการพัฒนาด้านวิทยาศาสตร์และเทคโนโลยี  
**ธีม:** นวัตกรรมเพื่อความยั่งยืน (Sustainable Innovation)  
**เป้าหมายการพัฒนาที่ยั่งยืน:** SDG 14 — Life Below Water

---

## ข้อมูลเอกสาร

| รายการ | รายละเอียด |
|---|---|
| ชื่อเอกสาร | รายงานฉบับสมบูรณ์โครงการ AquaMind |
| เวอร์ชัน | 1.0 |
| วันที่จัดทำ | 16 กรกฎาคม 2569 |
| สถานะระบบที่รายงาน | MVP v1.0 ใช้ข้อมูลจำลองและสถานการณ์สาธิต |
| สถานะการตรวจภาคสนาม | ยังไม่แล้วเสร็จ ต้องเก็บ Ground Truth และทดสอบกับเหตุการณ์จริงเพิ่มเติม |

> **หมายเหตุสำคัญ:** รายงานนี้แยกผลที่ทดสอบได้จากซอร์สโค้ดปัจจุบันออกจากเป้าหมายของระบบฉบับใช้งานจริงอย่างชัดเจน ตัวเลขจากข้อมูลจำลองไม่ใช้ยืนยันความแม่นยำในการเกิดแพลงก์ตอนบลูมภาคสนาม

---

# กิตติกรรมประกาศ (Acknowledgement)

โครงการ **“AquaMind: แพลตฟอร์มพยากรณ์การเกิดแพลงก์ตอนบลูมและวิเคราะห์คุณภาพน้ำแบบ End-to-End จากภาพถ่ายดาวเทียม”** ได้รับทุนอุดหนุนโครงการการแข่งขันพัฒนาโปรแกรมคอมพิวเตอร์แห่งประเทศไทย ครั้งที่ 28 จาก **สำนักงานพัฒนาวิทยาศาสตร์และเทคโนโลยีแห่งชาติ (สวทช.)** คณะผู้พัฒนาขอขอบพระคุณสำนักงานพัฒนาวิทยาศาสตร์และเทคโนโลยีแห่งชาติที่ให้การสนับสนุนทุนและเปิดโอกาสให้เยาวชนพัฒนาผลงานด้านวิทยาศาสตร์ เทคโนโลยี และนวัตกรรมเพื่อแก้ปัญหาสิ่งแวดล้อมและชุมชน

คณะผู้พัฒนาขอขอบพระคุณอาจารย์ที่ปรึกษาที่ให้คำแนะนำด้านการกำหนดขอบเขตโครงการ การออกแบบกระบวนการพัฒนาซอฟต์แวร์ และการนำเสนอผลงาน ตลอดจนหน่วยงานด้านประมง ทรัพยากรทางทะเล อุตุนิยมวิทยา และภูมิสารสนเทศที่เผยแพร่ข้อมูลและองค์ความรู้ซึ่งเป็นพื้นฐานสำคัญของโครงการ

สุดท้ายนี้ คณะผู้พัฒนาขอขอบคุณเกษตรกรผู้เพาะเลี้ยงสัตว์น้ำและผู้ใช้งานเป้าหมาย ซึ่งข้อเสนอแนะและประสบการณ์ภาคสนามจะมีส่วนสำคัญต่อการทดสอบ ปรับปรุง และพัฒนา AquaMind ให้เป็นเครื่องมือสนับสนุนการตัดสินใจที่เหมาะสมกับบริบทของประเทศไทยต่อไป

---

# 1. บทคัดย่อ คำสำคัญ และ Abstract

## 1.1 บทคัดย่อภาษาไทย

ปรากฏการณ์แพลงก์ตอนบลูมและภาวะออกซิเจนละลายในน้ำต่ำส่งผลกระทบต่อการเพาะเลี้ยงสัตว์น้ำชายฝั่ง โดยเกษตรกรมักได้รับข้อมูลไม่ทันต่อการเตรียมอุปกรณ์ ตรวจคุณภาพน้ำ หรือวางแผนลดความเสียหาย ระบบเฝ้าระวังที่มีอยู่บางส่วนมีความละเอียดเชิงพื้นที่ไม่เหมาะกับบริเวณฟาร์ม ขณะที่การลงพื้นที่เก็บตัวอย่างมีต้นทุนสูงและไม่สามารถทำได้ต่อเนื่องทุกจุด โครงการ AquaMind จึงมุ่งพัฒนาเครื่องมือสนับสนุนการตัดสินใจที่รวมข้อมูลภาพดาวเทียม ข้อมูลอากาศ ข้อมูลสมุทรศาสตร์ และข้อมูลภาคสนาม เพื่อประเมินความเสี่ยงการเกิดแพลงก์ตอนบลูมล่วงหน้า 3–5 วัน พร้อมอธิบายปัจจัยที่สัมพันธ์กับผลประเมินและเสนอขั้นตอนตรวจสอบหลังได้รับการแจ้งเตือน

แนวทางระบบฉบับเป้าหมายใช้ข้อมูล Sentinel-2 ซึ่งมีแถบคลื่นความละเอียด 10–20 เมตร โดยดัชนี NDCI ใช้ Band 5 และ Band 4 จึงมีความละเอียดเชิงสารสนเทศ 20 เมตร ระบบออกแบบให้ตรวจหาภาพใหม่ทุกวัน แต่ไม่สมมติว่าจะมีภาพที่ใช้งานได้ทุกวัน เนื่องจากดาวเทียมมีรอบกลับมาถ่ายพื้นที่เดิมตามปกติประมาณ 5 วันและภาพอาจถูกเมฆบัง ระหว่างรอภาพใหม่ ระบบจะใช้ภาพล่าสุดที่ผ่านการตรวจคุณภาพร่วมกับข้อมูลอากาศและอุณหภูมิผิวน้ำทะเลระดับภูมิภาค พร้อมแสดงอายุข้อมูล โหมดการประเมิน และระดับความเชื่อมั่น หากข้อมูลเก่าเกินเกณฑ์ ระบบจะแจ้งว่า “ข้อมูลไม่เพียงพอ” แทนการนำแผนที่เดิมมาแสดงเสมือนเป็นข้อมูลปัจจุบัน

MVP ที่พัฒนาแล้วประกอบด้วยสคริปต์สร้างข้อมูลจำลองจำนวน 1,000 ระเบียน กระบวนการฝึก XGBoost ร่วมกับ SMOTE, FastAPI สำหรับข้อมูลสถานีและผลความเสี่ยง และ Dashboard ที่พัฒนาด้วย Next.js สำหรับสาธิตสถานการณ์ระดับต่ำ ปานกลาง และสูง การทดสอบวันที่ 16 กรกฎาคม 2569 พบว่าโมเดลให้ Precision, Recall, F1-score และ ROC-AUC เท่ากับ 1.00 บนชุดข้อมูลจำลอง อย่างไรก็ตามผลดังกล่าวเกิดจากป้ายกำกับที่สร้างด้วยกฎจากตัวแปรชุดเดียวกันและการแบ่งข้อมูลแบบสุ่ม จึงใช้ยืนยันได้เพียงว่ากระบวนการฝึกทำงานครบ ไม่ใช่หลักฐานความแม่นยำภาคสนาม API ผ่านการทดสอบเส้นทางหลักและตอบรหัส 404 สำหรับสถานีที่ไม่มีอยู่ ส่วน Frontend ยังมีข้อผิดพลาด ESLint 2 รายการ คำเตือน 4 รายการ และ Production build ในสภาพแวดล้อมทดสอบไม่สำเร็จจากการดาวน์โหลด Google Fonts

การพิสูจน์ประสิทธิภาพขั้นถัดไปจะใช้ Ground Truth ที่จับคู่วันเวลาและพิกัดกับภาพดาวเทียม แบ่ง Train/Validation/Test ตามเวลาและพื้นที่ ใช้ SMOTE เฉพาะชุดฝึก และรายงาน Recall, Precision, F1-score, PR-AUC, Calibration, Brier Score, False Alarm และช่วงความเชื่อมั่น 95% เพื่อให้การกล่าวถึงความแม่นยำมีหลักฐานรองรับ

**คำสำคัญ:** แพลงก์ตอนบลูม, Sentinel-2, NDCI, ระบบเตือนภัยล่วงหน้า, XGBoost, Explainable AI, SHAP, ระบบสนับสนุนการตัดสินใจ

## 1.2 English Abstract

Algal blooms and low dissolved oxygen can cause substantial losses to coastal aquaculture. Farmers often receive information too late to inspect water quality, prepare aeration equipment, or plan risk-reduction actions. Existing monitoring products may lack sufficient spatial detail for farm areas, while field sampling is costly and cannot continuously cover every location. AquaMind is therefore designed as a decision-support platform that integrates satellite imagery, weather, regional oceanographic information, and field observations to estimate algal-bloom risk three to five days ahead. The system also explains the factors associated with each estimate and provides a verification-and-response checklist for farmers.

The target operational design uses Sentinel-2 bands at 10–20 m resolution. Since NDCI combines Band 5 and Band 4, its effective information resolution is 20 m. The pipeline checks daily for new imagery but does not assume that usable imagery is available every day: Sentinel-2 normally revisits an area approximately every five days, and cloud cover can extend the gap between valid observations. While awaiting a new image, AquaMind uses the latest quality-controlled observation together with weather and regional sea-surface-temperature information. Every output includes the satellite observation time, data mode, and confidence level. If the data age exceeds a validation-derived threshold, the system reports insufficient data instead of presenting an old map as current conditions.

The current MVP contains a generator for 1,000 synthetic records, an XGBoost training pipeline with SMOTE, a FastAPI service for station and risk data, and a Next.js dashboard with low-, medium-, and high-risk demonstration scenarios. Tests performed on 16 July 2026 produced Precision, Recall, F1-score, and ROC-AUC values of 1.00 on the synthetic test set. These values only verify that the training pipeline executes as intended: labels were generated from deterministic rules based on the same features and the records were randomly split. They do not demonstrate real-world predictive accuracy. The API passed its primary route tests and correctly returned HTTP 404 for an unknown station. The frontend currently reports two ESLint errors and four warnings, while the production build could not download Google Fonts in the test environment.

The next validation phase will pair satellite observations with time- and location-matched ground truth, apply spatial and temporal Train/Validation/Test separation, restrict SMOTE to training folds, and report Recall, Precision, F1-score, PR-AUC, calibration, Brier score, false alarms, and 95% confidence intervals. This process is required before AquaMind can make a supported claim about field accuracy.

**Keywords:** Algal Bloom, Sentinel-2, NDCI, Early Warning, XGBoost, Explainable AI, SHAP, Decision Support System

---

# 2. บทนำ

## 2.1 แนวคิดของโครงการ

AquaMind มีแนวคิดหลักคือเปลี่ยนข้อมูลสิ่งแวดล้อมหลายแหล่งให้เป็นข้อมูลประกอบการตัดสินใจที่เกษตรกรเข้าใจและนำไปตรวจสอบต่อได้ ระบบไม่ได้มีเป้าหมายตัดสินใจแทนมนุษย์หรือยืนยันการเกิด Bloom แบบ 100% แต่ทำหน้าที่คัดกรองพื้นที่และช่วงเวลาที่ควรเพิ่มการเฝ้าระวัง พร้อมสื่อสารข้อจำกัดของข้อมูลอย่างตรงไปตรงมา

วงจรการทำงานประกอบด้วยการรับข้อมูล การตรวจคุณภาพ การสร้างคุณลักษณะ การประเมินความเสี่ยง การอธิบายผล การแจ้งเตือน การตอบสนองของเกษตรกร และการรับผลที่เกิดขึ้นจริงกลับมาเป็น Ground Truth เพื่อประเมินและปรับปรุงโมเดล

## 2.2 ความสำคัญของปัญหา

เมื่อแพลงก์ตอนเพิ่มจำนวนมากหรือสลายตัว ปริมาณออกซิเจนละลายในน้ำอาจลดลงและส่งผลต่อสัตว์น้ำ นอกจากนี้แพลงก์ตอนบางชนิดอาจสร้างสารพิษหรือกระทบเหงือกของสัตว์น้ำ ความรุนแรงและระยะเวลาของเหตุการณ์ขึ้นกับหลายปัจจัย เช่น อุณหภูมิน้ำ แสง สารอาหาร ความเค็ม ลม และกระแสน้ำ จึงไม่ควรประเมินจากค่าตัวแปรเดียว

เกษตรกรต้องการข้อมูลที่ตอบคำถามมากกว่าคำว่า “เสี่ยง” ได้แก่ ข้อมูลมาจากเมื่อใด เหตุใดระบบจึงประเมินเช่นนั้น ระดับความเชื่อมั่นเป็นเท่าใด และควรตรวจสอบหรือเตรียมการอย่างไร การออกแบบ AquaMind จึงให้ความสำคัญกับ Data Freshness, Explainability และ Farmer Response Protocol ควบคู่กับประสิทธิภาพของโมเดล

## 2.3 ความเป็นมาของโครงการ

พื้นที่ศึกษาเบื้องต้นคือชายฝั่งอ่าวไทยตอนบน ตั้งแต่อ่าวบางปะกง จังหวัดฉะเชิงเทรา ถึงอ่าวศรีราชา จังหวัดชลบุรี ซึ่งมีการเพาะเลี้ยงสัตว์น้ำชายฝั่งและมีรายงานเหตุการณ์น้ำเปลี่ยนสี โครงการเริ่มจากการพัฒนา MVP แบบ Mock Data First เพื่อพิสูจน์การไหลของข้อมูลตั้งแต่การสร้างตัวแปร การฝึกโมเดล การให้บริการ API ไปจนถึง Dashboard ก่อนเชื่อมต่อแหล่งข้อมูลจริง

MVP ทำให้ทีมสามารถตรวจสอบโครงสร้างข้อมูล การแบ่งระดับความเสี่ยง การแสดงแนวโน้ม และคำแนะนำตามสถานการณ์ได้เร็ว อย่างไรก็ตามข้อมูลจำลองไม่ครอบคลุม Noise, Domain Shift, เมฆ ตะกอน ความแตกต่างของชนิดแพลงก์ตอน และการเปลี่ยนแปลงตามฤดูกาล จึงต้องมีขั้นตอนเปลี่ยนผ่านจาก Demo ไปสู่ระบบที่ใช้ข้อมูลจริงอย่างเป็นลำดับ

## 2.4 ช่องว่างที่โครงการต้องการแก้ไข

1. ผลิตภัณฑ์ระดับสากลบางรายการมีความละเอียดหลายร้อยเมตรและอาจไม่เหมาะกับบริเวณฟาร์มขนาดเล็ก
2. Sentinel-2 มีรายละเอียดสูงกว่า แต่ไม่ได้ให้ภาพที่ใช้ได้ทุกวันและอาจถูกเมฆบัง
3. การตรวจน้ำภาคสนามครอบคลุมพื้นที่จำกัดและมีต้นทุนต่อครั้ง
4. ระบบแผนที่ทั่วไปไม่ได้อธิบายปัจจัยหรือขั้นตอนรับมือที่เหมาะกับผู้ใช้ไทย
5. การรายงาน Accuracy เพียงค่าเดียวไม่เพียงพอสำหรับเหตุการณ์ที่เกิดไม่บ่อยและอาจซ่อน False Negative

---

# 3. สารบัญ

1. [บทคัดย่อ คำสำคัญ และ Abstract](#1-บทคัดย่อ-คำสำคัญ-และ-abstract)
2. [บทนำ](#2-บทนำ)
3. [สารบัญ](#3-สารบัญ)
4. [วัตถุประสงค์และเป้าหมาย](#4-วัตถุประสงค์และเป้าหมาย)
5. [รายละเอียดของการพัฒนา](#5-รายละเอียดของการพัฒนา)
   - [5.1 เนื้อเรื่องย่อ Story Board และแบบจำลอง](#51-เนื้อเรื่องย่อ-story-board-ภาพประกอบ-แบบจำลอง-และตัวอย่างผลงาน)
   - [5.2 ทฤษฎี หลักการ และเทคโนโลยี](#52-ทฤษฎี-หลักการ-และเทคนิคหรือเทคโนโลยีที่ใช้)
   - [5.3 เครื่องมือที่ใช้ในการพัฒนา](#53-เครื่องมือที่ใช้ในการพัฒนา)
   - [5.4 รายละเอียดโปรแกรมเชิงเทคนิค](#54-รายละเอียดโปรแกรมที่พัฒนาในเชิงเทคนิค-software-specification)
   - [5.5 ขอบเขตและข้อจำกัด](#55-ขอบเขตและข้อจำกัดของโปรแกรมที่พัฒนา)
   - [5.6 คุณลักษณะอุปกรณ์](#56-คุณลักษณะของอุปกรณ์ที่ใช้กับโปรแกรม)
6. [กลุ่มผู้ใช้โปรแกรม](#6-กลุ่มผู้ใช้โปรแกรม)
7. [ผลของการทดสอบโปรแกรม](#7-ผลของการทดสอบโปรแกรม)
8. [ปัญหาและอุปสรรค](#8-ปัญหาและอุปสรรค)
9. [แนวทางพัฒนาและประยุกต์ใช้](#9-แนวทางในการพัฒนาและประยุกต์ใช้ร่วมกับงานอื่นในขั้นต่อไป)
10. [ข้อสรุปและข้อเสนอแนะ](#10-ข้อสรุปและข้อเสนอแนะ)
11. [เอกสารอ้างอิง](#11-เอกสารอ้างอิง-reference)
12. [สถานที่ติดต่อ](#12-สถานที่ติดต่อของผู้พัฒนาและอาจารย์ที่ปรึกษา)
13. [ภาคผนวก](#13-ภาคผนวก-appendix)

---

# 4. วัตถุประสงค์และเป้าหมาย

## 4.1 วัตถุประสงค์

1. พัฒนา Data Pipeline สำหรับรับ ตรวจคุณภาพ และประมวลผลข้อมูลภาพดาวเทียม ข้อมูลอากาศ ข้อมูลสมุทรศาสตร์ และข้อมูลภาคสนาม
2. พัฒนาโมเดลประเมินความเสี่ยงการเกิดแพลงก์ตอนบลูมล่วงหน้า 3–5 วัน พร้อมกลไกจัดการข้อมูลขาดหาย
3. แสดงอายุข้อมูล โหมดการประเมิน และระดับความเชื่อมั่น เพื่อไม่ให้ผู้ใช้เข้าใจข้อมูลเก่าว่าเป็นข้อมูลปัจจุบัน
4. ใช้ SHAP อธิบายทิศทางและอันดับปัจจัยที่สัมพันธ์กับผลพยากรณ์ โดยไม่ตีความเป็นเหตุและผล
5. พัฒนา Web Dashboard ภาษาไทยสำหรับแสดงระดับความเสี่ยง แนวโน้ม พื้นที่ และขั้นตอนรับมือ
6. ตรวจสอบโมเดลด้วยข้อมูลภาคสนามและเหตุการณ์ที่ไม่ถูกใช้ฝึก พร้อมรายงาน Metric ที่เหมาะกับ Rare Event
7. ทดสอบความสามารถในการใช้งานกับกลุ่มเป้าหมายอย่างน้อย 30 ราย ด้วย SUS และคำถามวัดความเข้าใจ

## 4.2 เป้าหมายเชิงผลงาน

| ระดับ | เป้าหมาย |
|---|---|
| MVP | ให้ข้อมูลจำลองไหลผ่าน Model → API → Dashboard และสาธิต 3 ระดับความเสี่ยงได้ |
| Prototype with real data | เชื่อม Sentinel-2, Weather API, Regional SST และ Ground Truth พร้อม Data Freshness |
| Model validation | Recall ≥ 80%, Precision ≥ 60% บน Independent Test Set และ Brier Score ดีกว่า Baseline |
| User validation | SUS ≥ 70 และผู้ใช้เข้าใจว่า Forecast ไม่ใช่การยืนยันเหตุการณ์ 100% |
| Operational transparency | ผลลัพธ์ทุกครั้งแสดงเวลาภาพล่าสุด โหมดข้อมูล และความเชื่อมั่น |

## 4.3 เป้าหมายเชิงพื้นที่และผู้ใช้

- พื้นที่นำร่อง: ชายฝั่งอ่าวไทยตอนบน จังหวัดฉะเชิงเทราถึงจังหวัดชลบุรี
- การแสดงผลเชิงพื้นที่: ระดับบริเวณฟาร์ม โดยไม่อ้างว่าสามารถจำแนกกระชังเดี่ยวทุกขนาด
- ผู้ใช้หลัก: เกษตรกรเพาะเลี้ยงสัตว์น้ำชายฝั่ง
- ผู้ใช้สนับสนุน: เจ้าหน้าที่ประมง นักวิจัย และหน่วยงานทรัพยากรทางทะเล

---

# 5. รายละเอียดของการพัฒนา

## 5.1 เนื้อเรื่องย่อ (Story Board) ภาพประกอบ แบบจำลอง และตัวอย่างผลงาน

### 5.1.1 เรื่องราวการใช้งาน

1. เกษตรกรเปิด AquaMind และเลือกบริเวณฟาร์มของตน
2. ระบบแสดงระดับความเสี่ยง พร้อมเวลาที่ระบบคำนวณและเวลาของภาพดาวเทียมล่าสุด
3. หากมีภาพ Sentinel-2 ใหม่ที่ผ่านการตรวจเมฆ ระบบใช้โหมด **Fresh satellite**
4. หากยังไม่มีภาพใหม่แต่ภาพเดิมยังอยู่ในช่วงอายุที่ผ่าน Validation ระบบใช้โหมด **Forecast-assisted** และลดความเชื่อมั่น
5. หากภาพเก่าหรือข้อมูลหลักไม่ครบ ระบบใช้โหมด **Insufficient data** และไม่สร้างแผนที่ระดับฟาร์มใหม่
6. ระบบแสดง Top factors และขั้นตอนที่เกษตรกรควรตรวจสอบ เช่น สีและกลิ่นน้ำ พฤติกรรมสัตว์ และค่า DO
7. เกษตรกรส่งผลตรวจ ภาพถ่าย หรือเหตุการณ์ที่เกิดขึ้นจริงกลับเข้าสู่ระบบ
8. ผู้ดูแลตรวจสอบข้อมูลก่อนนำไปใช้เป็น Ground Truth สำหรับประเมินและปรับโมเดล

### 5.1.2 ภาพรวมระบบฉบับเป้าหมาย

```text
Sentinel-2 ─┐
Weather ────┼─> Quality & Freshness Check ─> Feature Store
Regional SST┤                                  │
Ground Truth┘                                  v
                                    Risk Model + Calibration
                                               │
                                               v
                       Risk + Confidence + SHAP + Data Age
                                               │
                                               v
                             Dashboard / Alert / Action Checklist
                                               │
                                               v
                            Farmer Feedback and Verified Outcomes
                                               │
                                               └──> Model Evaluation
```

### 5.1.3 ภาพรวมระบบ MVP ที่พัฒนาแล้ว

```text
Synthetic Data Generator
        │
        ├──> mock_data.csv ─> SMOTE ─> XGBoost ─> xgboost_model.json
        │
        └──> 30-day Scenario CSV ─> FastAPI response
                                      │
                                      └──> API station/risk endpoints

Next.js Dashboard
        └──> Local preset scenarios: Low / Medium / High
```

> MVP ปัจจุบันยังไม่ได้เชื่อม API เข้ากับ Dashboard และยังไม่ได้ดึง Sentinel-2, Weather API หรือ Copernicus Marine จริง การแสดงผล Frontend ใช้ State และ Preset ภายในไฟล์ `frontend/app/page.tsx`

### 5.1.4 ตัวอย่างการ์ดผลลัพธ์ที่ระบบเป้าหมายต้องแสดง

```text
┌──────────────────────────────────────────────────────┐
│ ความเสี่ยง: สูง                     โอกาสเสี่ยง: 73% │
│ ภาพดาวเทียมล่าสุด: 2 วันที่แล้ว                     │
│ โหมด: Forecast-assisted          ความเชื่อมั่น: กลาง │
├──────────────────────────────────────────────────────┤
│ ปัจจัยที่ผลักคะแนนขึ้น                               │
│ 1. SST ระดับภูมิภาคสูงกว่าค่าฤดูกาล                │
│ 2. ความเร็วลมลดลงต่อเนื่อง                           │
│ 3. แนวโน้ม NDCI จากภาพล่าสุดเพิ่มขึ้น                │
├──────────────────────────────────────────────────────┤
│ ขั้นแรก: ตรวจสี/กลิ่นน้ำและวัด DO                   │
│ หาก DO ต่ำหรือสัตว์ลอยหัว ให้เพิ่มออกซิเจน          │
│ ไม่เปลี่ยนน้ำจนกว่าจะยืนยันแหล่งน้ำภายนอกปลอดภัย    │
└──────────────────────────────────────────────────────┘
```

### 5.1.5 Farmer Response Protocol

| ระดับ | การตรวจสอบและการเตรียมการ | เงื่อนไขความปลอดภัย |
|---|---|---|
| ต่ำ | ตรวจเวลาข้อมูลล่าสุดและเฝ้าสังเกตตามปกติ | ไม่เพิ่มต้นทุนจากผล AI เพียงอย่างเดียว |
| ปานกลาง | ตรวจสี/กลิ่นน้ำ พฤติกรรมสัตว์ วัด DO เตรียมเครื่องให้อากาศ และพิจารณาลดอาหารสะสม | ยืนยันภาคสนามก่อนดำเนินการที่มีต้นทุนสูง |
| สูง | ตรวจยืนยันทันที เพิ่มความถี่การวัด DO เปิดเครื่องให้อากาศเมื่อ DO ต่ำหรือสัตว์มีอาการ ลด/งดอาหารชั่วคราวตามสภาพ และติดต่อเจ้าหน้าที่ | ไม่สูบหรือเปลี่ยนน้ำจนยืนยันน้ำภายนอกปลอดภัย การย้ายกระชังหรือจับก่อนกำหนดต้องพิจารณาร่วมกับผู้เชี่ยวชาญ |
| ข้อมูลไม่เพียงพอ | ลงพื้นที่ตรวจน้ำและติดตามประกาศหน่วยงานรัฐ | ไม่ตีความแผนที่เก่าว่าเป็นสถานการณ์ปัจจุบัน |

คำแนะนำต้องปรับตามชนิดสัตว์ ระบบบ่อหรือกระชัง สภาพน้ำ และคำแนะนำของเจ้าหน้าที่ในพื้นที่

## 5.2 ทฤษฎี หลักการ และเทคนิคหรือเทคโนโลยีที่ใช้

### 5.2.1 Remote Sensing และข้อจำกัดด้านเวลา

Sentinel-2 มี Multi-Spectral Instrument จำนวน 13 แถบคลื่น โดยแถบที่เกี่ยวข้องกับโครงการมีทั้งความละเอียด 10 และ 20 เมตร ระบบใช้ Scene Classification Layer เพื่อช่วยกรองเมฆ เงาเมฆ และพิกเซลที่ไม่เหมาะสม การตรวจหาภาพทำได้ทุกวัน แต่ภาพที่ใช้ได้อาจห่างกันมากกว่ารอบกลับมาถ่ายประมาณ 5 วัน เนื่องจากเมฆ หมอกควัน หรือสัดส่วนพิกเซลน้ำที่ใช้ได้ต่ำ

ระบบจึงแยกเวลาอย่างน้อย 2 ค่า:

- `prediction_generated_at`: เวลาที่ระบบคำนวณความเสี่ยง
- `satellite_observed_at`: เวลาที่ดาวเทียมสังเกตข้อมูลที่นำมาใช้

ตัวแปร `satellite_age_days` และ `valid_pixel_ratio` ถูกนำมาใช้ทั้งในโมเดลและการสื่อสาร Confidence โดยไม่สร้างภาพสมมติแล้วนำเสนอเสมือนเป็นภาพจริง

### 5.2.2 NDCI

Normalized Difference Chlorophyll Index ใช้ประมาณการเปลี่ยนแปลงของคลอโรฟิลล์ในน้ำ:

```text
NDCI = (ρRedEdge - ρRed) / (ρRedEdge + ρRed)
```

สำหรับ Sentinel-2 ใช้ Band 5 (Red Edge, 20 m) และ Band 4 (Red, 10 m) ดังนั้น NDCI มีความละเอียดเชิงสารสนเทศ 20 เมตร การ Resample Band 5 ไปยังกริด 10 เมตรไม่ได้เพิ่มรายละเอียดจริง ค่าแบ่งระดับ NDCI ต้องปรับจาก Ground Truth ในพื้นที่ เพราะค่าดังกล่าวได้รับผลจากชนิดแพลงก์ตอน ตะกอน ความขุ่น และสภาพแสง

### 5.2.3 NDWI

Normalized Difference Water Index ใช้แยกพื้นที่น้ำออกจากพื้นดิน:

```text
NDWI = (ρGreen - ρNIR) / (ρGreen + ρNIR)
```

Sentinel-2 ใช้ Band 3 และ Band 8 ซึ่งมีความละเอียด 10 เมตร NDWI ใช้สร้าง Water Mask ก่อนคำนวณดัชนีคุณภาพน้ำ แต่ยังต้องตรวจพื้นที่น้ำตื้น ชายฝั่ง และตะกอนซึ่งอาจทำให้เกิดค่าคลาดเคลื่อน

### 5.2.4 Feature Engineering

| Feature | ความหมาย | แหล่งข้อมูลเป้าหมาย |
|---|---|---|
| `ndci_current` | ค่า NDCI รอบล่าสุดที่ใช้ได้ | Sentinel-2 |
| `ndci_median_history` | ค่ามัธยฐานย้อนหลังหลายรอบ | Sentinel-2 |
| `ndci_slope` | แนวโน้มเพิ่มหรือลด | คำนวณจากอนุกรมเวลา |
| `valid_pixel_ratio` | สัดส่วนพิกเซลน้ำที่ผ่าน QC | Sentinel-2 SCL/Cloud mask |
| `satellite_age_days` | อายุภาพล่าสุด | Metadata |
| `air_temperature` | อุณหภูมิอากาศ | Weather API |
| `wind_speed_direction` | ความเร็วและทิศทางลม | Weather API |
| `precipitation` | ปริมาณฝน | Weather API |
| `regional_sst_anomaly` | SST ระดับภูมิภาคเทียบฤดูกาล | Copernicus Marine |
| `field_do` | DO จากการตรวจภาคสนาม | เกษตรกร/หน่วยงาน |

ข้อมูล SST ระดับภูมิภาคประมาณ 10 กิโลเมตรใช้เป็นบริบท ไม่ขยายแล้วอ้างเป็นค่าระดับฟาร์ม และ Sentinel-2 ไม่มีแถบ Thermal สำหรับวัดอุณหภูมิผิวน้ำโดยตรง

### 5.2.5 Random Forest และ XGBoost

Random Forest เป็น Ensemble ของ Decision Trees เหมาะสำหรับใช้เป็น Baseline ที่รองรับความสัมพันธ์ไม่เชิงเส้น ส่วน XGBoost สร้างต้นไม้แบบ Boosting และมี Regularization รวมทั้งรองรับการถ่วงน้ำหนักคลาส โครงการจะเปรียบเทียบทั้งสองโมเดลด้วย Validation เดียวกันโดยไม่สรุปล่วงหน้าว่าโมเดลใดดีกว่า

MVP ปัจจุบันใช้ `XGBClassifier` จำนวน 100 estimators, `max_depth=4`, `learning_rate=0.1` และ objective แบบ `binary:logistic`

### 5.2.6 Imbalanced Learning และ SMOTE

เหตุการณ์ Bloom เป็น Rare Event การดู Accuracy อย่างเดียวอาจทำให้โมเดลที่ทาย “ไม่เกิด” เกือบทั้งหมดดูเหมือนมีประสิทธิภาพ SMOTE สร้างตัวอย่างสังเคราะห์ในกลุ่ม Minority จากเพื่อนบ้านใน Feature Space การใช้งานที่ถูกต้องต้องแบ่งข้อมูลก่อนและใช้ SMOTE เฉพาะ Training fold เพื่อป้องกัน Data Leakage จากตัวอย่างสังเคราะห์เข้าสู่ Validation/Test

### 5.2.7 SHAP และข้อจำกัดของการอธิบาย

SHAP ใช้ Shapley values เพื่ออธิบายว่าตัวแปรแต่ละตัวผลักผลพยากรณ์จากค่าพื้นฐานไปในทิศทางใด ระบบจะแสดงทิศทางและอันดับความสำคัญของปัจจัย พร้อมเก็บ `shap_output_space` ว่าเป็น Raw score, Log-odds หรือ Probability ไม่แปล SHAP เป็นสาเหตุหรือเปอร์เซ็นต์ความเสียหาย

Frontend MVP ปัจจุบันใช้ข้อความอธิบายและป้าย `+SHAP/-SHAP` ที่กำหนดจาก Scenario/Rule ยังไม่ได้คำนวณ SHAP จริงจากโมเดลในแต่ละคำขอ จึงต้องพัฒนา Explainability service เพิ่มเติม

### 5.2.8 การตรวจสอบความแม่นยำ

การประเมินระบบแบ่งเป็น 2 ส่วน:

1. **Retrieval validation:** ค่าที่ประมาณจากภาพ เช่น Chlorophyll-a สอดคล้องกับตัวอย่างน้ำจริงเพียงใด ใช้ MAE, RMSE, R² และ Bias
2. **Event prediction validation:** ระบบเตือน Bloom ล่วงหน้าได้ดีเพียงใด ใช้ Recall, Precision, F1-score, PR-AUC, ROC-AUC, Confusion Matrix, False Alarms และ Missed Events

แผน Validation ที่กำหนดมีดังนี้:

1. จับคู่ Ground Truth กับภาพตามวันเวลาและพิกัด
2. แบ่ง Train/Validation/Test ตามเวลาและพื้นที่ ไม่สุ่มพิกเซลข้างเคียงข้ามชุด
3. ทำ Rolling-origin validation เพื่อจำลองการทำนายอนาคต
4. กันเหตุการณ์จริงอย่างน้อยหนึ่งช่วงเป็น Independent Test Event เมื่อข้อมูลเพียงพอ
5. ปรับ Threshold จาก Validation Set เท่านั้น
6. ตรวจ Calibration ด้วย Calibration curve และ Brier Score
7. รายงานช่วงความเชื่อมั่น 95% ด้วย Bootstrap
8. แยกผลตามอายุภาพ 0–5, 6–10 และมากกว่า 10 วัน
9. เปรียบเทียบกับ Baseline ได้แก่ Majority class, NDCI threshold และ Weather-only model

## 5.3 เครื่องมือที่ใช้ในการพัฒนา

### 5.3.1 เครื่องมือที่ใช้ใน MVP ปัจจุบัน

| กลุ่ม | เครื่องมือ/เวอร์ชันตามไฟล์โครงการ | หน้าที่ |
|---|---|---|
| ภาษา | Python 3.11 | สร้างข้อมูล ฝึกโมเดล และ Backend |
| Data/ML | pandas, NumPy, scikit-learn, imbalanced-learn, XGBoost | เตรียมข้อมูล SMOTE ฝึกและประเมินโมเดล |
| Backend | FastAPI, Pydantic | API และ Data validation |
| Frontend | Next.js 16.2.9, React 19.2.4, TypeScript | Dashboard |
| UI | Tailwind CSS 4, Lucide React | รูปแบบหน้าจอและไอคอน |
| Deployment tooling | npm, Next.js build tools | ติดตั้งและ Build Frontend |
| Version control | Git/GitHub | จัดการซอร์สโค้ด |

### 5.3.2 เครื่องมือสำหรับระบบฉบับเชื่อมข้อมูลจริง

| เครื่องมือ | หน้าที่ |
|---|---|
| Google Earth Engine | ค้นหา กรองเมฆ และประมวลผล Sentinel-2 |
| rasterio/GDAL | ประมวลผล Raster และพิกัด |
| xarray | อ่านข้อมูล NetCDF สมุทรศาสตร์ |
| Copernicus Marine | SST รายวันระดับภูมิภาค |
| Weather API/กรมอุตุนิยมวิทยา | ข้อมูลอากาศและพยากรณ์ |
| SHAP | คำนวณคำอธิบายโมเดลจริง |
| PostgreSQL/PostGIS | เก็บข้อมูลผู้ใช้ ฟาร์ม ผลพยากรณ์ และข้อมูลเชิงพื้นที่ |
| Docker/CI | ทำสภาพแวดล้อมซ้ำได้และทดสอบอัตโนมัติ |

> ไฟล์ `backend/requirements.txt` ปัจจุบันว่างอยู่ จึงยังไม่สามารถใช้เป็นรายการ Dependency ที่ทำซ้ำได้ ต้องจัดทำและตรึงเวอร์ชันก่อนส่งมอบ

## 5.4 รายละเอียดโปรแกรมที่พัฒนาในเชิงเทคนิค (Software Specification)

### 5.4.1 สถานะส่วนประกอบ

| ส่วนประกอบ | สถานะ | หลักฐานในโครงการ |
|---|---|---|
| Synthetic data generator | พัฒนาแล้ว | `backend/generate_mock_data.py` |
| XGBoost + SMOTE training | พัฒนาแล้ว | `backend/train_model.py` |
| Model artifact | พัฒนาแล้วจาก Mock data | `backend/xgboost_model.json` |
| Station/risk API | พัฒนาแล้วระดับ MVP | `backend/main.py` |
| Time-series scenario data | พัฒนาแล้วแบบจำลอง | `backend/data/chonburi_station_a1_30d.csv` |
| Dashboard scenarios | พัฒนาแล้ว | `frontend/app/page.tsx` |
| Dashboard เชื่อม API | ยังไม่พัฒนา | Frontend ไม่มี `fetch()` หรือ API client |
| Sentinel-2 pipeline | ยังไม่พัฒนา | ยังไม่มี GEE/raster pipeline ในซอร์สโค้ด |
| Weather/Regional SST pipeline | ยังไม่พัฒนา | ยังไม่มี API client ในซอร์สโค้ด |
| SHAP computation service | ยังไม่พัฒนา | ปัจจุบันเป็นข้อความ/ป้ายจาก Rule และ Preset |
| Authentication/Database/Notification | ยังไม่พัฒนา | ยังไม่มีโมดูลในซอร์สโค้ด |

### 5.4.2 Input Specification ของ MVP

#### A. Training CSV

| Field | Type | ความหมาย |
|---|---|---|
| `ndci_mean_7d` | float | ค่าเฉลี่ย NDCI จำลอง |
| `ndci_slope_7d` | float | แนวโน้ม NDCI จำลอง |
| `sst_anomaly` | float | SST anomaly จำลอง |
| `wind_speed_3d` | float | ความเร็วลมจำลอง |
| `ndci_x_wind` | float | Interaction feature |
| `is_bloom` | integer 0/1 | ป้ายกำกับที่สร้างจากกฎ |

ไฟล์ `backend/mock_data.csv` มี 1,000 ระเบียน แบ่งเป็น Non-bloom 898 และ Bloom 102 ระเบียน

#### B. Time-series CSV

ประกอบด้วย `date`, `ndci`, `ndci_mean_7d`, `ndci_slope_7d`, `sst_anomaly`, `wind_speed_3d`, `risk_score`, `risk_level`, `alert_status` และ `do_value` จำนวน 14 แถว

#### C. API input

```http
GET /api/stations
GET /api/risk/current?station_id=chonburi_01
```

`station_id` ที่กำหนดใน MVP ได้แก่ `chonburi_01`, `chonburi_02` และ `chonburi_03`

### 5.4.3 Output Specification ของ MVP

```json
{
  "station_id": "chonburi_01",
  "risk_score": 58.5,
  "risk_level": "ปานกลาง",
  "alert_status": "Watch",
  "shap_explanation": "ข้อความอธิบายจาก Rule",
  "location": "Chonburi Coast (Station A1)",
  "lat": 13.3611,
  "lon": 100.9234,
  "timestamp": "ข้อความสถานะ",
  "recommendations": ["..."],
  "features": [
    {"name": "...", "value": 0.0, "unit": "...", "impact": "increase"}
  ],
  "history_trend": [18.5, 19.2]
}
```

### 5.4.4 Output Specification ที่ต้องเพิ่มในระบบฉบับจริง

```json
{
  "prediction_generated_at": "ISO8601",
  "satellite_observed_at": "ISO8601|null",
  "satellite_age_days": 2,
  "valid_pixel_ratio": 0.82,
  "data_mode": "FRESH_SATELLITE|FORECAST_ASSISTED|INSUFFICIENT_DATA",
  "confidence_level": "HIGH|MEDIUM|LOW",
  "risk_probability": 0.73,
  "model_version": "string",
  "shap_output_space": "raw|probability",
  "action_checklist": ["verify_water", "measure_do", "prepare_aeration"]
}
```

### 5.4.5 Functional Specification

#### ฟังก์ชันที่ทำงานแล้ว

1. สร้าง Mock dataset แบบ Class imbalance
2. แบ่ง Train/Test แบบ Stratified random split
3. ใช้ SMOTE กับชุดฝึก
4. ฝึก XGBoost และบันทึก Model artifact
5. แสดง Classification report และ ROC-AUC
6. คืนรายการสถานีผ่าน FastAPI
7. คืน Risk response พร้อมคำแนะนำและ Time series
8. คืน HTTP 404 เมื่อไม่พบสถานี
9. สลับ Scenario ต่ำ/ปานกลาง/สูงบน Dashboard
10. แสดง Risk gauge, Feature list, Trend และ Debug panel

#### ฟังก์ชันที่ต้องพัฒนาต่อ

1. รับข้อมูล Sentinel-2 และทำ Cloud/Shadow mask
2. คำนวณ NDWI/NDCI จากข้อมูลจริง
3. รับ Weather และ Regional SST
4. ตรวจ Data freshness และเปลี่ยนโหมด A/B/C
5. Load model artifact เพื่อ Inference จริงใน API
6. คำนวณ SHAP จริงตามคำขอ
7. เชื่อม Dashboard กับ API
8. รับ Feedback ภาคสนามพร้อมการตรวจสอบ
9. Authentication, Database, Notification และ Audit log
10. Export รายงานและรองรับหลายฟาร์ม

### 5.4.6 โครงสร้างซอฟต์แวร์ปัจจุบัน

```text
aqua_mind/
├── AquaMind_Proposal_Formatted.md
├── AquaMind_Final_Report.md
├── mvp_task.md
├── backend/
│   ├── main.py
│   ├── generate_mock_data.py
│   ├── train_model.py
│   ├── mock_data.csv
│   ├── xgboost_model.json
│   ├── requirements.txt
│   └── data/
│       └── chonburi_station_a1_30d.csv
└── frontend/
    ├── app/
    │   ├── page.tsx
    │   ├── layout.tsx
    │   └── globals.css
    ├── package.json
    ├── package-lock.json
    └── next.config.ts
```

### 5.4.7 โครงสร้างซอฟต์แวร์เป้าหมาย

```text
External data sources
       │
       v
Scheduled ingestion and quality control
       │
       v
Feature store / PostgreSQL-PostGIS
       │
       ├──> Training and validation pipeline
       │
       └──> Versioned inference service ─> SHAP/Calibration
                                          │
                                          v
                              FastAPI ─> Dashboard/Notification
                                          │
                                          v
                                  Verified field feedback
```

### 5.4.8 ส่วนที่ทีมพัฒนาขึ้นเอง

1. การกำหนดปัญหาและ User flow สำหรับระบบเฝ้าระวังแพลงก์ตอนบลูม
2. สคริปต์สร้างข้อมูลจำลองตาม Feature ของโครงการ
3. กระบวนการฝึก XGBoost และ SMOTE สำหรับ MVP
4. โครงสร้าง API และ Rule-based recommendation
5. Dashboard, Scenario presets, Risk gauge, Trend display และ Debug panel
6. แนวคิด Data mode, Data freshness, Confidence และ Farmer Response Protocol ในเอกสารออกแบบ

### 5.4.9 Source Code และองค์ประกอบจากภายนอก

| องค์ประกอบ | แหล่งที่มา/สัญญาอนุญาตที่ต้องตรวจในรุ่นส่งมอบ | การใช้งาน |
|---|---|---|
| Python | Python Software Foundation License | Runtime |
| FastAPI | MIT License | Backend framework |
| Pydantic | MIT License | Schema validation |
| pandas | BSD 3-Clause | Data processing |
| NumPy | BSD 3-Clause | Numerical computing |
| scikit-learn | BSD 3-Clause | Split/Metrics |
| imbalanced-learn | MIT License | SMOTE |
| XGBoost | Apache License 2.0 | ML model |
| Next.js | MIT License | Frontend framework |
| React | MIT License | UI library |
| Tailwind CSS | MIT License | Styling |
| Lucide | ISC License | Icons |
| Sentinel-2/Copernicus data | Copernicus data terms | Remote sensing data |

ทีมไม่ได้คัดลอก Source Code ของบุคคลภายนอกมาแนบในรายงาน รายการ Dependency จริงต้องสร้างจาก Lock file/Environment และตรวจ License ซ้ำก่อนเผยแพร่หรือให้บริการเชิงพาณิชย์

## 5.5 ขอบเขตและข้อจำกัดของโปรแกรมที่พัฒนา

### 5.5.1 ขอบเขต MVP ปัจจุบัน

- สาธิตพื้นที่อ้างอิง 3 สถานีในจังหวัดชลบุรี
- ประเมินและแสดงความเสี่ยง 3 ระดับ
- ใช้ข้อมูล CSV จำลองและ Scenario presets
- ให้บริการ API แบบไม่มี Authentication
- แสดงผลผ่าน Web Dashboard แบบ Responsive
- สาธิตคำอธิบายและคำแนะนำด้วย Rule/ข้อความที่กำหนดไว้

### 5.5.2 ข้อจำกัด MVP

1. ยังไม่รับภาพ Sentinel-2 หรือข้อมูลอากาศจริง
2. ค่า NDCI, SST, DO, Chlorophyll-a และ Risk ใน Demo ไม่ใช่การตรวจวัดปัจจุบัน
3. API ยังไม่ได้โหลด `xgboost_model.json` เพื่อ Inference
4. คำว่า `shap_explanation` ใน API ยังเป็น Rule-based text ไม่ใช่ SHAP ที่คำนวณจากโมเดล
5. Frontend ยังไม่เชื่อม Backend
6. ตำแหน่งสถานีเป็นข้อมูลสาธิตและต้องยืนยันก่อนใช้งานจริง
7. Path ของ CSV ใน Backend ผูกกับ Current working directory หากรันจาก `backend/` จะใช้ Fallback array
8. ข้อความ Timestamp ใน API ระบุว่า “Real-time” ทั้งที่ข้อมูลมาจาก Scenario CSV ต้องแก้ก่อนสาธิตอย่างเป็นทางการ
9. `requirements.txt` ว่าง ทำให้ติดตั้ง Backend แบบทำซ้ำไม่ได้
10. ยังไม่มี Automated test suite, CI, Authentication, Database และระบบแจ้งเตือนจริง

### 5.5.3 ข้อจำกัดระบบเป้าหมาย

1. Sentinel-2 ไม่ให้ภาพใหม่ทุกวันและเมฆอาจทำให้ช่วงว่างยาวขึ้น
2. NDCI ไม่สามารถยืนยันชนิดหรือความเป็นพิษของแพลงก์ตอนได้
3. ความละเอียด NDCI คือ 20 เมตร ไม่รับประกันการแยกกระชังเดี่ยว
4. SST ระดับภูมิภาคไม่ใช่อุณหภูมิน้ำระดับฟาร์ม
5. Forecast เป็น Probability ไม่ใช่คำยืนยันเหตุการณ์
6. ความแม่นยำขึ้นกับปริมาณและคุณภาพ Ground Truth
7. คำแนะนำต้องปรับตามชนิดสัตว์และระบบเลี้ยง
8. ระบบเป็น Decision Support ไม่แทนการตรวจน้ำหรือคำสั่งเจ้าหน้าที่

## 5.6 คุณลักษณะของอุปกรณ์ที่ใช้กับโปรแกรม

### 5.6.1 อุปกรณ์สำหรับผู้ใช้

| อุปกรณ์ | ขั้นต่ำที่แนะนำ |
|---|---|
| สมาร์ตโฟน/แท็บเล็ต | Browser รุ่นปัจจุบัน, หน้าจออย่างน้อย 360 px, อินเทอร์เน็ต 4G/Wi-Fi |
| คอมพิวเตอร์ | Browser รุ่นปัจจุบัน, RAM 4 GB ขึ้นไป, ความละเอียด 1366×768 ขึ้นไป |
| GPS | ใช้ GPS ในอุปกรณ์หรือเลือกตำแหน่งบนแผนที่ |

### 5.6.2 อุปกรณ์สำหรับพัฒนา/ให้บริการ

| อุปกรณ์ | ขั้นต่ำสำหรับ MVP | แนะนำสำหรับประมวลผลข้อมูลจริง |
|---|---|---|
| CPU | 2 cores | 4–8 cores |
| RAM | 4 GB | 8–16 GB |
| Storage | 2 GB | 50 GB ขึ้นไปหรือ Object storage |
| GPU | ไม่จำเป็น | ไม่จำเป็นสำหรับ MVP; ใช้เมื่อฝึกข้อมูลขนาดใหญ่ |
| OS | Windows/macOS/Linux | Linux server/Container |

### 5.6.3 อุปกรณ์ภาคสนาม (ถ้ามี)

- เครื่องวัด DO ที่สอบเทียบแล้ว
- เครื่องวัด pH/อุณหภูมิ/ความเค็มตามแผน Sampling
- ขวดเก็บตัวอย่างและ Cold chain สำหรับ Chlorophyll-a laboratory analysis
- สมาร์ตโฟนสำหรับบันทึกพิกัด เวลา และภาพสีน้ำ

อุปกรณ์ภาคสนามต้องบันทึกรุ่น วิธีสอบเทียบ หน่วยวัด และเวลาที่ตรวจ เพื่อใช้ประเมินคุณภาพ Ground Truth

---

# 6. กลุ่มผู้ใช้โปรแกรม

## 6.1 ผู้ใช้หลัก

**เกษตรกรผู้เพาะเลี้ยงสัตว์น้ำชายฝั่ง** ใช้ตรวจสอบความเสี่ยงบริเวณฟาร์ม ดูความสดใหม่ของข้อมูล อ่านปัจจัยที่เกี่ยวข้อง และทำ Checklist ยืนยันสภาพน้ำก่อนตัดสินใจ

## 6.2 ผู้ใช้รอง

- เจ้าหน้าที่กรมประมงและสำนักงานประมงจังหวัด ใช้ดูภาพรวมพื้นที่และติดตามรายงานภาคสนาม
- เจ้าหน้าที่ทรัพยากรทางทะเลและชายฝั่ง ใช้ประกอบการคัดกรองพื้นที่ตรวจสอบ
- นักวิจัย ใช้ตรวจข้อมูลย้อนหลัง ประเมินโมเดล และ Export ข้อมูลตามสิทธิ์
- ผู้ดูแลระบบ ใช้ตรวจคุณภาพข้อมูล รุ่นโมเดล และ Feedback ก่อนรับเป็น Ground Truth

## 6.3 ความต้องการของผู้ใช้

1. ภาษาไทยและคำอธิบายที่ไม่ใช้ศัพท์เทคนิคเกินจำเป็น
2. เห็นเวลาข้อมูลล่าสุดและความเชื่อมั่นทันที
3. แยก “สิ่งที่ดาวเทียมเห็น” จาก “สิ่งที่โมเดลคาดการณ์”
4. คำแนะนำที่ทำได้จริงและไม่ผลักให้ดำเนินการเสี่ยงจาก AI เพียงอย่างเดียว
5. ใช้งานบนมือถือในพื้นที่อินเทอร์เน็ตไม่เสถียร
6. ติดต่อหน่วยงานที่เกี่ยวข้องได้เมื่อความเสี่ยงสูง

---

# 7. ผลของการทดสอบโปรแกรม

## 7.1 สภาพแวดล้อมและวันที่ทดสอบ

การทดสอบในรายงานนี้ดำเนินการวันที่ **16 กรกฎาคม 2569** บนระบบ Windows/PowerShell ภายใน Workspace ของโครงการ โดยใช้ Python 3.11 และ Dependency ที่ติดตั้งอยู่ในเครื่องทดสอบ สำหรับ Frontend ใช้คำสั่งจาก `package.json` ของโครงการ

## 7.2 ผลทดสอบข้อมูลและโมเดลจำลอง

### 7.2.1 ชุดข้อมูล

| รายการ | ผล |
|---|---:|
| จำนวนข้อมูลทั้งหมด | 1,000 ระเบียน |
| Non-bloom | 898 ระเบียน |
| Bloom | 102 ระเบียน |
| Test set | 200 ระเบียน |
| Non-bloom ใน Test set | 180 ระเบียน |
| Bloom ใน Test set | 20 ระเบียน |

### 7.2.2 ผลจาก `backend/train_model.py`

| Metric | Class 0 | Class 1 | ภาพรวม |
|---|---:|---:|---:|
| Precision | 1.00 | 1.00 | 1.00 |
| Recall | 1.00 | 1.00 | 1.00 |
| F1-score | 1.00 | 1.00 | 1.00 |
| Accuracy | — | — | 1.00 |
| ROC-AUC | — | — | 1.0000 |

Model artifact หลังรันทดสอบมี Hash เดิม แสดงว่าการฝึกด้วย Seed และข้อมูลเดิมให้ผลซ้ำได้ในสภาพแวดล้อมนี้

### 7.2.3 การตีความผล

ผล 1.00 **ไม่ใช่หลักฐานว่าโมเดลแม่นยำ 100% ในสถานการณ์จริง** เนื่องจาก:

1. ป้าย `is_bloom` ถูกสร้างด้วยกฎ Deterministic จากตัวแปรในชุดข้อมูลเดียวกัน
2. ไม่มี Noise จากเมฆ ตะกอน ความคลาดเคลื่อนของเซนเซอร์ หรือ Sampling
3. แบ่งข้อมูลแบบสุ่ม ไม่ได้แยกตามเวลาและพื้นที่
4. ไม่มีเหตุการณ์จริงที่โมเดลไม่เคยเห็น
5. Distribution ของข้อมูลจำลองถูกควบคุมด้วยโค้ดเดียวกัน

ผลนี้ยืนยันได้เพียงว่า Data loading, Train/Test split, SMOTE, XGBoost, Metric calculation และ Model saving ทำงานครบตาม Pipeline

## 7.3 ผลทดสอบ Backend/API

| Test case | ผลที่คาดหวัง | ผลที่ได้ | สถานะ |
|---|---|---|---|
| `GET /api/stations` | HTTP 200 และ 3 สถานี | HTTP 200, 3 สถานี | ผ่าน |
| Risk ของ `chonburi_01` | HTTP 200 | HTTP 200, score 58.5, ระดับปานกลาง | ผ่าน |
| Time series เมื่อรันจาก Project root | 14 จุดจาก CSV | 14 จุด | ผ่าน |
| สถานี `missing` | HTTP 404 | HTTP 404 | ผ่าน |
| Python bytecode compilation | ไม่มี Syntax error | Exit code 0 | ผ่าน |
| รัน API จากโฟลเดอร์ `backend/` | อ่าน CSV เดียวกัน | ใช้ Fallback 13 จุดเพราะ Relative path | ไม่ผ่าน/พบข้อบกพร่อง |

## 7.4 ผลทดสอบ Frontend

### 7.4.1 ESLint

คำสั่ง `npm run lint` จบด้วย Exit code 1:

- Errors 2 รายการ: `react/jsx-no-comment-textnodes` ที่บรรทัดประมาณ 313 และ 334 ของ `frontend/app/page.tsx`
- Warnings 4 รายการ: import `useEffect`, `RefreshCw`, `ShieldCheck` และ `HelpCircle` แต่ยังไม่ได้ใช้งาน

สรุป: Frontend แสดงโครงสร้างได้ในระดับ Source แต่ยังไม่ผ่านเกณฑ์ Lint สำหรับการส่งมอบ

### 7.4.2 Production build

คำสั่ง `npm run build` จบด้วย Exit code 1 เนื่องจาก Next.js พยายามดาวน์โหลดฟอนต์ `Geist` และ `Geist Mono` จาก Google Fonts แต่สภาพแวดล้อมทดสอบไม่สามารถเชื่อมต่อได้ การทดสอบนี้ยังไม่ยืนยันว่า Source compile ผ่านหลังแก้ปัญหาเครือข่าย เพราะ Build หยุดที่ขั้นตอน Font fetch

### 7.4.3 Functional UI

จากการตรวจ Source พบว่า Dashboard รองรับการสลับ Preset ต่ำ ปานกลาง และสูง พร้อมเปลี่ยน Risk gauge, สี,ข้อความอธิบาย, Feature, Recommendation และ Trend อย่างสอดคล้องกัน แต่ยังไม่มี Automated browser test และ Frontend ยังไม่เรียก Backend API

## 7.5 สรุปสถานะการทดสอบ

| ด้าน | สถานะ |
|---|---|
| Data generation | ผ่านบนข้อมูลจำลอง |
| Model training | ผ่านบนข้อมูลจำลอง |
| Model field accuracy | ยังไม่ทดสอบ |
| API primary routes | ผ่าน |
| API path portability | พบข้อบกพร่อง |
| Frontend lint | ไม่ผ่าน |
| Frontend production build | ไม่ผ่านในสภาพแวดล้อมปัจจุบัน |
| Frontend–Backend integration | ยังไม่พัฒนา |
| User testing/SUS | ยังไม่ดำเนินการ |
| Field validation | ยังไม่ดำเนินการ |

## 7.6 แผน Acceptance Test ก่อนประกาศความพร้อม

1. Backend unit/integration tests ผ่านทั้งหมด
2. Frontend lint และ production build ผ่าน
3. Dashboard เรียก API และจัดการ Loading/Error/Insufficient data ได้
4. Path และ Configuration ไม่ขึ้นกับ Current working directory
5. ไม่มีข้อความ “Real-time” เมื่อข้อมูลไม่ใช่ข้อมูลเวลาจริง
6. Validation บน Independent field test ผ่านเกณฑ์ Recall/Precision/Calibration
7. ทดสอบผู้ใช้ 30 รายและ SUS ≥ 70
8. ทดสอบคำแนะนำกับผู้เชี่ยวชาญด้านการเพาะเลี้ยงสัตว์น้ำ

---

# 8. ปัญหาและอุปสรรค

## 8.1 ปัญหาด้านข้อมูลดาวเทียม

Sentinel-2 ไม่ได้สังเกตพื้นที่เดิมทุกวัน และภาพอาจใช้ไม่ได้จากเมฆ เงาเมฆ หรือหมอกควัน การแก้ปัญหาไม่ควรนำค่าที่ Interpolate มาแสดงเป็นภาพจริง AquaMind จึงกำหนดโหมดข้อมูลและแสดงอายุภาพ โดยใช้ข้อมูลอากาศและ SST ระดับภูมิภาคเพื่อช่วยประเมินแนวโน้มเท่านั้น

**แนวทางจัดการ:** ตรวจหาภาพทุกวัน, ทำ Pixel-level quality control, เก็บภาพล่าสุดที่ใช้ได้, ใส่อายุข้อมูลเป็น Feature, ลด Confidence และเปลี่ยนเป็น Insufficient data เมื่อเกินเกณฑ์จาก Validation

## 8.2 Ground Truth มีจำกัด

เหตุการณ์ Bloom เกิดไม่บ่อยและการตรวจ Chlorophyll-a ต้องใช้กระบวนการภาคสนาม/ห้องปฏิบัติการ หากมีตัวอย่างเพียง 10–15 จุดในวันเดียวจะไม่ครอบคลุมฤดูกาลหรือเหตุการณ์ที่หลากหลาย

**แนวทางจัดการ:** เก็บ 10–15 จุดต่อ Campaign หลายรอบเวลา ครอบคลุมช่วงปกติ ช่วงเริ่มเสี่ยง และ Bloom จับคู่พิกัด/เวลาให้ใกล้ดาวเทียมผ่าน และประสานหน่วยงานที่มีข้อมูลย้อนหลัง

## 8.3 Class imbalance และ Data leakage

ข้อมูล Bloom มีสัดส่วนน้อย การใช้ Random split กับพิกเซลหรือวันที่อยู่ใกล้กันอาจทำให้ Train/Test คล้ายกันมากเกินไป และการทำ SMOTE ก่อนแบ่งข้อมูลทำให้เกิด Leakage

**แนวทางจัดการ:** แบ่งข้อมูลตามเวลา/พื้นที่ก่อนทำ Resampling ใช้ Rolling-origin validation และประเมิน PR-AUC, Recall, Precision และ False Alarm ร่วมกัน

## 8.4 Domain shift

ความสัมพันธ์ระหว่างค่าการสะท้อนแสง คลอโรฟิลล์ ตะกอน และชนิดแพลงก์ตอนอาจต่างกันตามฤดูกาลและพื้นที่ โมเดลจากพื้นที่หนึ่งไม่ควรถูกนำไปใช้กับอีกพื้นที่โดยไม่ตรวจสอบ

**แนวทางจัดการ:** ทำ External validation, ตรวจ Drift ของ Feature, Version โมเดลตามพื้นที่ และกำหนดเงื่อนไข Out-of-distribution

## 8.5 ข้อจำกัดของ MVP และโค้ดปัจจุบัน

1. Backend ใช้ Relative path `backend/data/...` ทำให้ผลต่างตาม Directory ที่ใช้รัน
2. Backend ยังไม่ใช้โมเดลที่ฝึกแล้วในการตอบ API
3. `requirements.txt` ว่างและยังไม่มี Environment lock สำหรับ Python
4. Frontend ใช้ Preset ภายใน ไม่เชื่อม API
5. “SHAP” บน UI ยังเป็นป้ายตาม Scenario ไม่ใช่ค่าจาก Explainer
6. Frontend มี Lint errors และ unused imports
7. Build พึ่ง Google Fonts ผ่านเครือข่าย ทำให้ Offline build ไม่ได้
8. API เปิด CORS `*` และยังไม่มี Authentication จึงไม่เหมาะกับ Production
9. ไม่มี Automated tests และ CI gate
10. ข้อความ API บางส่วนอ้าง “Real-time” เกินสถานะข้อมูลจริง

## 8.6 ความเสี่ยงจากคำแนะนำ

การเปิดเครื่องให้อากาศ การลดอาหาร การเปลี่ยนน้ำ การย้ายกระชัง หรือการจับสัตว์ก่อนกำหนดมีผลต่างกันตามชนิดสัตว์ ระบบเลี้ยง และสภาพพื้นที่ คำแนะนำที่ไม่ผ่านผู้เชี่ยวชาญอาจเพิ่มต้นทุนหรือความเสี่ยง

**แนวทางจัดการ:** ใช้ Checklist เพื่อยืนยันภาคสนามก่อน แยกคำแนะนำตามชนิดฟาร์ม บังคับแสดง Disclaimer และให้ผู้เชี่ยวชาญ/เจ้าหน้าที่รับรอง Protocol ก่อนใช้งานจริง

---

# 9. แนวทางในการพัฒนาและประยุกต์ใช้ร่วมกับงานอื่นในขั้นต่อไป

## 9.1 ระยะที่ 1: ทำ MVP ให้เป็นระบบที่ทำซ้ำได้

1. จัดทำ `requirements.txt` หรือ `pyproject.toml` พร้อมตรึงเวอร์ชัน
2. แก้ Path ให้ยึดตำแหน่งไฟล์ด้วย `Path(__file__)`
3. แยก Configuration ออกจาก Source และใช้ Environment variables
4. แก้ ESLint errors/warnings และเปลี่ยน Google Fonts เป็น Local/self-hosted font
5. เพิ่ม Backend tests, Frontend component tests และ End-to-end tests
6. เชื่อม Dashboard กับ API พร้อม Error state
7. เปลี่ยนข้อความ Real-time เป็น Scenario/Mock data อย่างชัดเจน

## 9.2 ระยะที่ 2: เชื่อมข้อมูลจริง

1. สร้าง GEE pipeline สำหรับ Sentinel-2 L2A และ SCL cloud mask
2. คำนวณ NDWI/NDCI ที่ Resolution ถูกต้อง
3. เชื่อม Weather API และ Copernicus Marine SST
4. ออกแบบ Data catalog และ Metadata ของแหล่งข้อมูล
5. เพิ่ม Data freshness, Valid pixel ratio และ Data mode ใน API/UI
6. สร้างฐานข้อมูล PostgreSQL/PostGIS
7. แยก Mock, Staging และ Production environment

## 9.3 ระยะที่ 3: Validation ภาคสนาม

1. ทำ Sampling protocol ร่วมกับผู้เชี่ยวชาญ
2. เก็บ Chlorophyll-a, DO, pH, อุณหภูมิ, ความเค็ม และภาพสีน้ำ
3. จับคู่ข้อมูลตามพิกัดและเวลา
4. สร้าง Spatial/Temporal split และ Independent Event test
5. ทำ Calibration และกำหนด Threshold ตามต้นทุน False Negative/False Positive
6. ตีพิมพ์ Model card และ Data sheet

## 9.4 ระยะที่ 4: ทดสอบผู้ใช้และการแจ้งเตือน

1. ทดสอบกับเกษตรกรและเจ้าหน้าที่อย่างน้อย 30 ราย
2. วัด SUS และ Task completion rate
3. ทดสอบว่าผู้ใช้เข้าใจ Data age, Confidence และ Forecast
4. ทดสอบข้อความแจ้งเตือนระดับต่ำ/ปานกลาง/สูง
5. ประเมิน Alert fatigue และค่าใช้จ่ายจาก False Alarm
6. ปรับ Farmer Response Protocol ตามข้อเสนอแนะผู้เชี่ยวชาญ

## 9.5 การประยุกต์ใช้ร่วมกับงานอื่น

- ระบบติดตามคุณภาพน้ำสำหรับบ่อกุ้ง บ่อปลา และกระชัง
- การสนับสนุนการจัดลำดับพื้นที่เก็บตัวอย่างของหน่วยงานรัฐ
- Dashboard สถานการณ์สิ่งแวดล้อมชายฝั่งระดับจังหวัด
- ระบบประกันภัยสัตว์น้ำแบบใช้ดัชนี เมื่อผ่านการรับรองข้อมูลและกฎหมาย
- การติดตามความขุ่น ตะกอน หรือการเปลี่ยนแปลงสีของแหล่งน้ำ
- ระบบ Citizen science สำหรับรับรายงานสีน้ำและสัตว์น้ำผิดปกติ
- งานวิจัยเปรียบเทียบ Remote sensing indices กับข้อมูลห้องปฏิบัติการ

การประยุกต์ทุกกรณีต้องประเมินข้อมูลใหม่ ไม่ใช้โมเดลเดิมโดยอัตโนมัติ

---

# 10. ข้อสรุปและข้อเสนอแนะ

## 10.1 ข้อสรุป

AquaMind มีกรอบแนวคิดที่เชื่อมปัญหาภาคสนามกับ Remote sensing, Machine learning, Explainable AI และการออกแบบเพื่อผู้ใช้ โดยให้ความสำคัญกับข้อจำกัดด้านรอบภาพดาวเทียมและความโปร่งใสของข้อมูล ระบบเป้าหมายไม่ได้อ้างว่าเป็น Satellite monitoring แบบ Real-time แต่ใช้การตรวจข้อมูลรายวันและลดความเชื่อมั่นตามอายุภาพ

MVP ปัจจุบันพิสูจน์องค์ประกอบเบื้องต้นของการสร้างข้อมูล ฝึกโมเดล ให้บริการ API และแสดง Dashboard ได้บางส่วน ผลโมเดล 1.00 บนข้อมูลจำลองเป็นผลของโครงสร้างการสร้างป้ายและไม่ใช้ยืนยันความแม่นยำจริง API หลักทำงานได้ แต่ยังมีปัญหา Relative path ส่วน Frontend ยังไม่ผ่าน Lint/Build และยังไม่เชื่อม Backend ดังนั้นระบบยังอยู่ในระดับ Prototype และไม่ควรถูกใช้ตัดสินใจด้านการเพาะเลี้ยงจริง

## 10.2 ข้อเสนอแนะ

1. ให้ความสำคัญลำดับแรกกับการเก็บ Ground Truth และการออกแบบ Validation ก่อนปรับโมเดลให้ซับซ้อน
2. แก้ข้อบกพร่องซอฟต์แวร์และสร้าง Automated tests ก่อนเพิ่ม Feature
3. ใช้ NDCI 20 เมตรอย่างถูกต้องและไม่อ้างความละเอียด 10 เมตรจากการ Resample
4. แสดง Data age, Data source, Confidence และ Model version ทุกผลลัพธ์
5. แยกค่าที่ตรวจวัดจริง ค่าที่ประมาณ และค่าที่พยากรณ์ด้วยสี/ป้ายที่ชัดเจน
6. ให้ผู้เชี่ยวชาญรับรองคำแนะนำตามชนิดสัตว์และระบบเลี้ยง
7. เผยแพร่ Model card ที่บอกข้อมูลฝึก Metric ข้อจำกัด และเงื่อนไขห้ามใช้
8. หลีกเลี่ยงคำว่า “แม่นยำ” จนกว่าจะผ่าน Independent field test พร้อมช่วงความเชื่อมั่น

---

# 11. เอกสารอ้างอิง (Reference)

[1] Thai PBS. (2566). *กรมทะเลชายฝั่ง ชี้แจง “แพลงก์ตอนบลูม” เกาะล้าน จ.ชลบุรี*. https://www.thaipbs.or.th/news/content/330148

[2] GISTDA. (2566). *การติดตามคุณภาพน้ำทะเลและปรากฏการณ์น้ำเปลี่ยนสีด้วยข้อมูลดาวเทียม*. http://coastalradar.gistda.or.th/

[3] European Space Agency. (2023). *Sentinel-2 User Handbook*.

[4] Gorelick, N., et al. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27.

[5] Pahlevan, N., et al. (2020). Sentinel-2/Landsat-8 product consistency and implications for monitoring aquatic systems. *Remote Sensing of Environment*, 240, 111664.

[6] Chen, Y., et al. (2019). Machine learning algorithms for estimating chlorophyll-a concentration using Sentinel-2 data. *International Journal of Remote Sensing*, 40(22), 8685–8704.

[7] Ali, A., et al. (2022). Predicting chlorophyll-a concentration from Sentinel-2 imagery using machine learning models. *Environmental Monitoring and Assessment*, 194(3), 1–15.

[8] McFeeters, S. K. (1996). The Use of the Normalized Difference Water Index (NDWI). *International Journal of Remote Sensing*, 17(7), 1425–1432.

[9] Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *NeurIPS*, 30.

[10] Mishra, S., & Mishra, D. (2012). Normalized Difference Chlorophyll Index (NDCI). *Remote Sensing of Environment*, 117, 394–406.

[11] Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5–32.

[12] Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *ACM SIGKDD*, 785–794.

[13] Brooke, J. (1996). SUS: A quick and dirty usability scale. *Usability Evaluation in Industry*, 189–194.

[14] Chawla, N. V., et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. *Journal of Artificial Intelligence Research*, 16, 321–357.

[15] United Nations. (2015). *Sustainable Development Goal 14: Life Below Water*.

[16] สำนักงานประมงจังหวัดสระบุรี กรมประมง. (2568). *ลงพื้นที่ตรวจสอบกรณีปลาลอยหัวและให้คำแนะนำด้านการเพิ่มออกซิเจนและลดอาหาร*. https://www4.fisheries.go.th/local/index.php/main/view_activities/9/246642

[17] Copernicus Marine Service. (2025). *Product User Manual for the Global Sea Surface Temperature Level-4 Near Real-Time Product (SST_GLO_PHY_L4_NRT_010_043)*. https://documentation.marine.copernicus.eu/PUM/CMEMS-SST-PUM-010-043.pdf

[18] NOAA National Ocean Service. (2025). *Harmful Algal Blooms (Red Tide): Frequently Asked Questions*. https://oceanservice.noaa.gov/hazards/hab/

[19] FastAPI. *FastAPI Documentation*. https://fastapi.tiangolo.com/

[20] Next.js. *Next.js Documentation*. https://nextjs.org/docs

[21] XGBoost Developers. *XGBoost Documentation*. https://xgboost.readthedocs.io/

---

# 12. สถานที่ติดต่อของผู้พัฒนาและอาจารย์ที่ปรึกษา

> **ต้องกรอกก่อนส่งรายงาน:** เอกสารต้นทางมีชื่อและบทบาท แต่ไม่มีโทรศัพท์ อีเมล และที่อยู่ จึงเว้นช่องไว้เพื่อป้องกันการสร้างข้อมูลส่วนบุคคลขึ้นเอง

## 12.1 อาจารย์ที่ปรึกษา

| รายการ | ข้อมูล |
|---|---|
| ชื่อ | ศ. ดร. ปิยะ มหาวิทยาลัย *(โปรดตรวจสอบชื่อ-สกุลและคำนำหน้า)* |
| บทบาท | Project Lead & Advisor |
| สถานศึกษา/หน่วยงาน | [กรอกข้อมูล] |
| ที่อยู่ไปรษณีย์ | [กรอกข้อมูล] |
| โทรศัพท์ | [กรอกข้อมูล] |
| โทรศัพท์มือถือ | [กรอกข้อมูล] |
| อีเมล | [กรอกข้อมูล] |

## 12.2 ผู้พัฒนา

| ชื่อ | หน้าที่ | โทรศัพท์มือถือ | อีเมล |
|---|---|---|---|
| นาย อิทธิพล เดชะผล | Data Engineer | [กรอกข้อมูล] | [กรอกข้อมูล] |
| นาย ชาตรี พิมพ์สิทธิ | ML Engineer | [กรอกข้อมูล] | [กรอกข้อมูล] |
| นาย ธวัน ตันติสิรกุล | Backend Developer | [กรอกข้อมูล] | [กรอกข้อมูล] |
| นาย เทวนาถ สระทองแดง | Full-Stack Developer | [กรอกข้อมูล] | [กรอกข้อมูล] |

## 12.3 สถานที่ติดต่อโครงการ

| รายการ | ข้อมูล |
|---|---|
| ชื่อสถานศึกษา/หน่วยงาน | [กรอกข้อมูล] |
| ภาควิชา/คณะ/แผนการเรียน | [กรอกข้อมูล] |
| ที่อยู่ | [กรอกข้อมูล] |
| โทรศัพท์หน่วยงาน | [กรอกข้อมูล] |
| อีเมลกลางโครงการ | [กรอกข้อมูล] |
| GitHub Repository | [กรอก URL] |
| Live Demo | [กรอก URL] |

---

# 13. ภาคผนวก (Appendix)

## ภาคผนวก ก: คู่มือการติดตั้งอย่างละเอียด

### ก.1 สิ่งที่ต้องมี

1. Git
2. Python 3.11 หรือรุ่นที่ทีมทดสอบแล้ว
3. Node.js รุ่นที่รองรับ Next.js 16 และ npm
4. พื้นที่ว่างอย่างน้อย 2 GB สำหรับ MVP
5. Internet สำหรับติดตั้ง Dependency; Production build ปัจจุบันยังต้องเข้าถึง Google Fonts

### ก.2 ดาวน์โหลดซอร์สโค้ด

```powershell
git clone <repository-url>
Set-Location aqua_mind
```

หากได้รับไฟล์โครงการโดยตรง ให้เปิด PowerShell ที่โฟลเดอร์รากซึ่งมี `backend` และ `frontend`

### ก.3 สร้าง Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

หาก PowerShell ไม่อนุญาตให้ Activate script ให้ตรวจ Execution Policy ตามนโยบายของเครื่องหรือเรียก Python ผ่าน `.venv\Scripts\python.exe` โดยตรง

### ก.4 ติดตั้ง Backend dependencies

ไฟล์ `backend/requirements.txt` ปัจจุบันว่าง จึงต้องปรับปรุงก่อนส่งมอบ รุ่น MVP สามารถติดตั้งชุดขั้นต่ำดังนี้:

```powershell
python -m pip install fastapi uvicorn pydantic pandas numpy scikit-learn imbalanced-learn xgboost httpx
```

หลังยืนยันเวอร์ชันที่ทำงานได้ ให้ทีมสร้างไฟล์ Dependency ที่ตรึงเวอร์ชัน เช่น:

```powershell
python -m pip freeze | Select-String -Pattern "fastapi|uvicorn|pydantic|pandas|numpy|scikit-learn|imbalanced-learn|xgboost|httpx"
```

ควรตรวจผลและเขียนเวอร์ชันที่จำเป็นลง `backend/requirements.txt` โดยไม่คัดลอก Package ที่ไม่เกี่ยวข้องทั้ง Environment

### ก.5 สร้างข้อมูลจำลองใหม่ (ไม่จำเป็นหากใช้ไฟล์ที่ให้มา)

```powershell
Set-Location backend
python generate_mock_data.py
Set-Location ..
```

คำสั่งนี้สร้าง `backend/mock_data.csv` เมื่อรันจากโฟลเดอร์ `backend`

### ก.6 ฝึกโมเดล MVP

```powershell
Set-Location backend
python train_model.py
Set-Location ..
```

ผลที่ได้คือ Classification report, ROC-AUC และ `backend/xgboost_model.json` ผลนี้มาจากข้อมูลจำลองและห้ามนำไปกล่าวเป็นความแม่นยำภาคสนาม

### ก.7 เปิด Backend API

ให้รันจาก **Project root** เพื่อให้ Relative path ในโค้ดปัจจุบันอ่าน CSV ได้:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

ตรวจ API documentation ที่:

```text
http://127.0.0.1:8000/docs
```

ตรวจ Endpoint:

```text
http://127.0.0.1:8000/api/stations
http://127.0.0.1:8000/api/risk/current?station_id=chonburi_01
```

### ก.8 ติดตั้ง Frontend

เปิด PowerShell อีกหน้าต่าง:

```powershell
Set-Location frontend
npm install
```

หากต้องการติดตั้งตาม Lock file ใน CI ให้ใช้:

```powershell
npm ci
```

### ก.9 เปิด Frontend แบบ Development

```powershell
npm run dev
```

เปิด Browser ที่:

```text
http://localhost:3000
```

Frontend MVP ยังใช้ Preset ภายในและไม่จำเป็นต้องเปิด Backend เพื่อสลับสถานการณ์ อย่างไรก็ตามนี่คือข้อจำกัด ไม่ใช่สถาปัตยกรรมเป้าหมาย

### ก.10 ตรวจคุณภาพก่อนใช้งาน

```powershell
npm run lint
npm run build
```

ณ วันที่รายงาน คำสั่งทั้งสองยังไม่ผ่าน ต้องแก้ ESLint และจัดการ Google Fonts ก่อนถือว่าติดตั้ง Production สำเร็จ

### ก.11 การตั้งค่าสำหรับระบบข้อมูลจริงในอนาคต

สร้างไฟล์ `.env` จาก Template โดยไม่ Commit Secret:

```text
GEE_PROJECT_ID=
WEATHER_API_KEY=
COPERNICUS_USERNAME=
COPERNICUS_PASSWORD=
DATABASE_URL=
ALERT_EMAIL_FROM=
```

ควรใช้ Secret manager ใน Production และจำกัด CORS เฉพาะ Domain ที่อนุญาต

### ก.12 การหยุดระบบ

กด `Ctrl+C` ใน Terminal ของ Backend และ Frontend จากนั้น Deactivate virtual environment:

```powershell
deactivate
```

## ภาคผนวก ข: คู่มือการใช้งานอย่างละเอียด

### ข.1 การเข้าสู่ Dashboard

1. เปิด `http://localhost:3000`
2. ตรวจป้าย `MVP v1.0` ที่ส่วนหัว
3. อ่านข้อความว่าเป็นระบบประเมินความเสี่ยงและสนับสนุนการตัดสินใจ

MVP ยังไม่มีระบบ Login หรือการเลือกฟาร์มจริง

### ข.2 การสลับสถานการณ์สาธิต

ใช้ปุ่มด้านบนของ Dashboard:

- **1. สภาวะปกติ:** Risk ต่ำ แสดงการติดตามตามรอบปกติ
- **2. เริ่มเฝ้าระวัง:** Risk ปานกลาง แสดงการตรวจ DO และเฝ้าระวัง
- **3. วิกฤตบลูม:** Risk สูง แสดงการแจ้งเตือนและการตรวจสอบเร่งด่วน

ค่าทั้งหมดเป็น Preset เพื่อสาธิต UI ไม่ใช่ข้อมูลปัจจุบันจากสถานี

### ข.3 การอ่านการ์ดพื้นที่

- ชื่อพื้นที่ใน MVP คือสถานีอ้างอิง Chonburi Coast (Station A1)
- จุดบนแผนที่เป็น SVG สาธิต ไม่ใช่ Web Map จริง
- พิกัดต้องได้รับการตรวจสอบก่อนใช้ภาคสนาม

### ข.4 การอ่าน Risk gauge

| สี | ความหมายใน Demo |
|---|---|
| เขียว | ความเสี่ยงต่ำ |
| เหลือง | ความเสี่ยงปานกลาง |
| แดง | ความเสี่ยงสูง |

Risk score ใน MVP ไม่ได้มาจาก API หรือ Model inference แบบเวลาจริง

### ข.5 การอ่านคำอธิบาย

ช่อง “เหตุผลเชิงลึกโดยโมเดล” ใน MVP เป็นข้อความตาม Preset/Rule ไม่ใช่ผล SHAP จริง ผู้ใช้ควรตีความว่าเป็นตัวอย่างรูปแบบการสื่อสารเท่านั้น

ระบบฉบับจริงต้องแสดง:

1. เวลาที่คำนวณ
2. เวลาภาพดาวเทียม
3. โหมดข้อมูล
4. ความเชื่อมั่น
5. ทิศทางและอันดับ Feature
6. Model version

### ข.6 การอ่านแนวโน้ม

กราฟแสดง `history_trend` ของ Scenario ที่เลือก จุดท้ายควรตรงกับ Risk score ปัจจุบัน ในระบบจริงต้องแยกเส้น Historical observation และ Forecast อย่างชัดเจน

### ข.7 การอ่านคำแนะนำ

คำแนะนำใน Demo ใช้สาธิต Workflow เท่านั้น ก่อนดำเนินการจริงให้:

1. ตรวจเวลาข้อมูลล่าสุด
2. ตรวจสี กลิ่น และพฤติกรรมสัตว์
3. วัด DO และตัวแปรที่เกี่ยวข้องหากมีเครื่องมือ
4. ตรวจประกาศหน่วยงานรัฐ
5. ติดต่อเจ้าหน้าที่เมื่อมีความเสี่ยงสูงหรือสัตว์ผิดปกติ

ห้ามเปลี่ยนน้ำ ย้ายกระชัง หรือจับขายก่อนกำหนดจากผล Demo เพียงอย่างเดียว

### ข.8 Debug Model

กด “เปิด Debug Model” เพื่อดู Feature vector และ Inference output ที่ใช้สาธิต ป้าย `+SHAP/-SHAP` ยังไม่ใช่ค่าที่คำนวณจาก SHAP library และค่า Inference delay เป็นข้อความคงที่ใน UI

### ข.9 การเรียก API โดยตรง

เมื่อเปิด Backend แล้ว สามารถใช้ Browser หรือ PowerShell:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/stations'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/risk/current?station_id=chonburi_01'
```

หากใช้สถานีที่ไม่มีอยู่ API ควรคืน HTTP 404

### ข.10 การรายงานปัญหา

บันทึกข้อมูลต่อไปนี้:

- วันเวลาและ Timezone
- URL/Endpoint
- Browser และ OS
- ขั้นตอนที่ทำก่อนเกิดปัญหา
- Screenshot หรือ Error message
- Commit/Version ของระบบ
- ห้ามแนบ API key, Password หรือข้อมูลส่วนบุคคล

## ภาคผนวก ค: ข้อตกลงในการใช้ซอฟต์แวร์ (Disclaimer)

### ค.1 สถานะของซอฟต์แวร์

AquaMind เวอร์ชันที่อธิบายในรายงานนี้เป็นซอฟต์แวร์ต้นแบบเพื่อการศึกษา วิจัย และสาธิต ยังไม่ได้รับรองเป็นระบบเตือนภัยทางการ ระบบควบคุมอัตโนมัติ เครื่องมือวินิจฉัย หรือผลิตภัณฑ์เชิงพาณิชย์

### ค.2 ข้อจำกัดของข้อมูล

ข้อมูลอาจล่าช้า ขาดหาย ถูกเมฆบัง หรือมีความคลาดเคลื่อน การพยากรณ์เป็นค่าความน่าจะเป็น ไม่รับประกันว่าจะเกิดหรือไม่เกิดเหตุการณ์ ข้อมูลดาวเทียมไม่สามารถยืนยันชนิด ความเป็นพิษ หรือความเข้มข้นของแพลงก์ตอนได้โดยไม่ตรวจภาคสนาม/ห้องปฏิบัติการ

### ค.3 การตัดสินใจของผู้ใช้

ผู้ใช้ต้องตรวจสภาพน้ำ พฤติกรรมสัตว์ และข้อมูลจากหน่วยงานที่เกี่ยวข้องก่อนตัดสินใจ การเปิดเครื่องให้อากาศ ลดอาหาร เปลี่ยนน้ำ ย้ายกระชัง จับสัตว์ก่อนกำหนด หรือดำเนินการอื่นต้องพิจารณาตามชนิดสัตว์ ระบบเลี้ยง และคำแนะนำผู้เชี่ยวชาญ

### ค.4 ความรับผิด

คณะผู้พัฒนาและผู้สนับสนุนไม่รับรองความครบถ้วน ความพร้อมใช้งาน หรือความเหมาะสมของซอฟต์แวร์สำหรับวัตถุประสงค์เฉพาะ และไม่รับผิดชอบต่อความเสียหายโดยตรงหรือโดยอ้อมที่เกิดจากการใช้ ตีความ หรือพึ่งพาผลลัพธ์ของระบบ ทั้งนี้ให้อยู่ภายใต้กฎหมายที่ใช้บังคับ

### ค.5 ความเป็นส่วนตัวและข้อมูล

ระบบฉบับ Production ต้องแจ้งวัตถุประสงค์การเก็บข้อมูล พิกัดฟาร์ม ภาพถ่าย เบอร์โทรศัพท์ และข้อมูลผู้ใช้ ขอความยินยอมตามฐานกฎหมายที่เหมาะสม กำหนดระยะเวลาเก็บ และควบคุมสิทธิ์เข้าถึงตาม PDPA ผู้ใช้ไม่ควรส่งข้อมูลส่วนบุคคลหรือข้อมูลธุรกิจที่อ่อนไหวเข้าสู่ MVP ปัจจุบัน

### ค.6 ทรัพย์สินทางปัญญาและสัญญาอนุญาต

การใช้ซอฟต์แวร์ต้องเป็นไปตาม License ของโครงการและ Dependency แต่ละรายการ ข้อมูล Copernicus, แผนที่, API และชุดข้อมูลภายนอกอยู่ภายใต้เงื่อนไขของเจ้าของข้อมูล ผู้แจกจ่ายระบบต้องเก็บ Copyright/License notices ที่จำเป็น

### ค.7 ความปลอดภัย

MVP เปิด CORS กว้างและไม่มี Authentication ห้ามนำไปเปิดเป็น Public production service โดยไม่เพิ่ม Authentication, Authorization, HTTPS, Secret management, Rate limiting, Logging และ Security review

### ค.8 การอ้างอิงผล

ห้ามนำ Metric จาก Mock data หรือ Scenario presets ไปอ้างว่าเป็นประสิทธิภาพในพื้นที่จริง การเผยแพร่ค่าความแม่นยำต้องระบุ Dataset, Sample size, Event count, Split method, Metric definition และ Confidence interval

## ภาคผนวก ง: รายการตรวจสอบก่อนส่งมอบ

### ง.1 เอกสาร

- [ ] กรอกข้อมูลติดต่อครบถ้วน
- [ ] ตรวจชื่อโครงการและชื่อสมาชิก
- [ ] ตรวจข้อความรับทุนกับแบบฟอร์ม NSC
- [ ] แนบภาพหน้าจอและเลขรูป/ตาราง
- [ ] ตรวจ Citation และ URL
- [ ] ตรวจภาษาและเลขหัวข้อ

### ง.2 ซอฟต์แวร์

- [ ] สร้าง Python dependency file ที่ตรึงเวอร์ชัน
- [ ] Backend tests ผ่าน
- [ ] Frontend lint ผ่าน
- [ ] Frontend production build ผ่านแบบไม่พึ่งเครือข่ายภายนอก
- [ ] Frontend เชื่อม API
- [ ] ลบ/แก้ข้อความ Real-time ที่ไม่ตรงสถานะ
- [ ] แก้ Relative path
- [ ] จำกัด CORS และเพิ่ม Security controls
- [ ] เพิ่ม `.env.example` โดยไม่มี Secret
- [ ] ตรวจ License inventory

### ง.3 วิทยาศาสตร์และการทดสอบ

- [ ] มี Ground Truth หลายรอบเวลา
- [ ] ระบุวิธีจับคู่ภาพและตัวอย่างน้ำ
- [ ] ใช้ Temporal/Spatial split
- [ ] SMOTE อยู่เฉพาะ Training fold
- [ ] รายงาน Recall, Precision, F1, PR-AUC และ Calibration
- [ ] รายงานช่วงความเชื่อมั่น
- [ ] แยกผลตามอายุภาพ
- [ ] ผ่านการทบทวน Farmer Response Protocol โดยผู้เชี่ยวชาญ
- [ ] ทดสอบ SUS กับผู้ใช้เป้าหมาย

---

**สิ้นสุดรายงานฉบับสมบูรณ์โครงการ AquaMind**
