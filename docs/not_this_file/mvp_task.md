# Project: AquaMind MVP

## Tech Stack
- Data Processing & ML: Python, Pandas, Scikit-learn, XGBoost, SHAP, Imbalanced-learn (SMOTE)
- Backend/API: FastAPI
- Frontend: Next.js, Tailwind CSS, Leaflet (สำหรับ Web Map)

ส่วนที่ 8: รายละเอียดทางเทคนิค (Technical Details)

8.1 ทฤษฎีและหลักการของเทคนิคที่ใช้

8.1.1 NDCI — Normalized Difference Chlorophyll Index

คือ: ดัชนีที่ใช้ประมาณค่าความเข้มข้นของคลอโรฟิลล์-a (Chl-a) ในน้ำ

ซึ่งเป็นตัวชี้วัดหลักของการเพิ่มจำนวนของแพลงก์ตอนพืช

สูตรคำนวณ:

NDCI = (ρ_RedEdge − ρ_Red) / (ρ_RedEdge + ρ_Red)

โดย ρ_RedEdge คือค่าการสะท้อนแสงในช่วง Band 5 (705nm) และ ρ_Red คือ Band 4 (665nm) ของ

Sentinel-2

ทำไมถึงเลือก: เมื่อคลอโรฟิลล์เพิ่มสูงขึ้น การดูดซับแสงในช่วง Red จะสูงขึ้น แต่การสะท้อนแสงในช่วง Red-

Edge จะสูงขึ้นเช่นกัน ทำให้ค่า NDCI เพิ่มขึ้นตามปริมาณแพลงก์ตอน [9]

เกณฑ์ความเสี่ยง:

- NDCI < 0.0 → ความเสี่ยงต่ำ (น้ำสะอาด)

- NDCI 0.0–0.2 → ความเสี่ยงปานกลาง (เฝ้าระวัง)

- NDCI > 0.2 → ความเสี่ยงสูง (แจ้งเตือน)

8.1.2 NDWI — Normalized Difference Water Index

คือ: ดัชนีที่ใช้แยกแยะพื้นที่น้ำออกจากพื้นที่บก เพื่อ Mask เฉพาะพิกเซลที่เป็นน้ำออกมาก่อนวิเคราะห์คุณภาพน้ำ

สูตรคำนวณ:

NDWI = (ρ_Green − ρ_NIR) / (ρ_Green + ρ_NIR)

โดย ρ_Green คือ Band 3 (560nm) และ ρ_NIR คือ Band 8 (842nm) ของ Sentinel-2

ทำไมถึงเลือก: น้ำดูดซับแสง NIR ได้ดีมาก ทำให้ค่า NDWI ของพื้นที่น้ำเป็นบวก (> 0)

ขณะที่พื้นดินและพืชพรรณมีค่าเป็นลบ ช่วยให้กรองพื้นที่วิเคราะห์ได้อย่างแม่นยำ [8]

8.1.3 Random Forest

คือ: อัลกอริทึม Machine Learning แบบ Ensemble ที่สร้างต้นไม้ตัดสินใจ (Decision Tree) หลายต้นพร้อมกัน

แล้วนำผลการพยากรณ์มาโหวตรวมกัน

ทำไมถึงเลือก: เหมาะกับข้อมูลสิ่งแวดล้อมที่มีหลายตัวแปร (Multi-variate) ทนต่อ Noise และ Outlier ได้ดี

และสามารถคำนวณ Feature Importance ได้โดยตรง ซึ่งเป็นพื้นฐานสำคัญสำหรับ SHAP Analysis [5]

8.1.4 XGBoost (Extreme Gradient Boosting)

คือ: อัลกอริทึม Gradient Boosting ที่สร้างโมเดลใหม่ทีละโมเดลเพื่อแก้ข้อผิดพลาดของโมเดลก่อนหน้า

(Boosting Strategy)

ทำไมถึงเลือก: มีประสิทธิภาพสูงกว่า Random Forest ในข้อมูลที่มีความสัมพันธ์เชิงซับซ้อนระหว่างตัวแปร

และสามารถจัดการข้อมูลที่มีค่าหายไป (Missing Values) ได้โดยอัตโนมัติ

ซึ่งเกิดบ่อยในข้อมูลดาวเทียมที่ถูกเมฆบัง [6]

8.1.5 SHAP — SHapley Additive exPlanations

คือ: เทคนิค Explainable AI ที่อ้างอิงทฤษฎี Game Theory (Shapley Values) เพื่อคำนวณว่าแต่ละ Feature

มีส่วนร่วมต่อผลลัพธ์การพยากรณ์มากน้อยเพียงใด

สูตรพื้นฐาน:

f(x) = ϕ₀ + Σ ϕᵢ

โดย ϕ₀ คือค่าพยากรณ์พื้นฐาน (Base value) และ ϕᵢ คือ SHAP value ของ Feature ที่ i

ผลลัพธ์ที่ผู้ใช้เห็นบน Dashboard:"⚠️ ความเสี่ยงสูง (Risk Score: 78/100)

สาเหตุหลัก: อุณหภูมิผิวน้ำสูงกว่าปกติ +2.3°C (ส่งผลบวก 34%) · ความเร็วลมลดลงต่อเนื่อง 4 วัน (ส่งผลบวก

28%) · ค่า NDCI เพิ่มขึ้นต่อเนื่อง 7 วัน (ส่งผลบวก 22%)"

ทำไมถึงเลือก: เป็น Gold Standard ของ Explainable AI ในงานวิจัยปัจจุบัน [9]

และสามารถใช้ได้กับโมเดลทุกประเภท (Model-agnostic)

8.1.6 SMOTE — Synthetic Minority Oversampling Technique

คือ: เทคนิคสำหรับแก้ปัญหา Class Imbalance ในชุดข้อมูล โดยการสร้างตัวอย่างข้อมูล Minority Class

(เหตุการณ์ Bloom จริง) ขึ้นมาใหม่แบบ Synthetic

ทำไมจำเป็น: แพลงก์ตอนบลูมเป็น Rare Event ที่เกิดไม่บ่อย ทำให้ในชุดข้อมูลมีตัวอย่าง "ไม่เกิด Bloom"

มากกว่า "เกิด Bloom" หลายเท่า หากไม่แก้ปัญหานี้ โมเดลจะ Bias ไปทาย "ไม่เกิด Bloom" ตลอดเวลา

ซึ่งเป็นอันตรายสำหรับระบบเตือนภัย

วิธีการทำงาน: SMOTE สร้างตัวอย่างใหม่โดยการ Interpolate ระหว่าง k-nearest neighbors ของตัวอย่าง

Minority Class ที่มีอยู่ ทำให้โมเดลเรียนรู้ Pattern ของการเกิด Bloom ได้อย่างสมดุล

8.2 โครงสร้างข้อมูล (Data Structure)

ระบบ AquaMind จัดการข้อมูล 4 รูปแบบ ดังนี้

รูปแบบข้อมูล คำอธิบาย ตัวอย่าง

Raster Data ข้อมูลภาพถ่ายดาวเทียมในรูปแบบ

Grid Pixel

ภาพ Sentinel-2 (Band 3, 4, 5,

8)

Tabular Data ข้อมูลสภาพอากาศและ Feature

สำหรับ ML

อุณหภูมิ, ความเร็วลม, ค่า NDCI

รายวัน

GeoJSON ข้อมูลเชิงพื้นที่สำหรับแสดงผลบน

Web Map

ขอบเขต AOI, จุด Sampling

Time-Series ข้อมูลตามลำดับเวลาสำหรับวิเครา

ะห์แนวโน้ม

NDCI ย้อนหลัง 30 วัน

8.3 Feature Engineering

ระบบสกัด Feature สำคัญสำหรับโมเดล ML ดังนี้

Feature คำอธิบาย แหล่งข้อมูล

ndci_mean_7d ค่าเฉลี่ย NDCI ย้อนหลัง 7 วัน Sentinel-2

ndci_slope_7d ความชันของแนวโน้ม NDCI ใน 7 วัน

(บอกว่ากำลังเพิ่มหรือลด)

Sentinel-2

sst_anomaly ส่วนต่างระหว่างอุณหภูมิผิวน้ำปัจจุบั

นกับค่าเฉลี่ยปกติ

OpenWeather API

wind_speed_3d ความเร็วลมเฉลี่ย 3 วันล่วงหน้า OpenWeather API

ndci × wind Interaction Feature ระหว่าง

NDCI และความเร็วลม

คำนวณ

เหตุผลที่ `ndci_slope_7d` สำคัญ: ค่า NDCI ที่กำลังเพิ่มขึ้นต่อเนื่อง (Positive slope)

เป็นสัญญาณเตือนล่วงหน้าที่สำคัญกว่าค่า NDCI ณ วันนั้นๆ เพราะบ่งบอกถึงแนวโน้มที่กำลังเกิดขึ้น

## ข้อกำหนดสำคัญสำหรับ MVP (Mock Data First)
ในเวอร์ชัน MVP นี้ ยังไม่ต้องดึงข้อมูล Sentinel-2 หรือ OpenWeather API จริง ให้เขียนสคริปต์ Python สร้าง "Mock Data" แบบ Tabular ย้อนหลัง 30 วันขึ้นมาทดสอบโมเดลก่อน เพื่อให้ระบบต้นแบบทำงานได้ตั้งแต่ต้นน้ำยันปลายน้ำ (End-to-end)