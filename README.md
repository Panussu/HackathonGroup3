# 🕵️ THE SILENT THREAT — Hackathon Mission (hackathon#1)

> *"Behind the screen, a silent war is raging."*
> ภารกิจสืบสวน Incident Response — วิเคราะห์ Access Log ของระบบ **NexusCart** ขนาด **1.4 GB / 21,146,398 บรรทัด** เพื่อตามล่ากลุ่มแฮกเกอร์ และถอดชื่อจริงของคนร้าย

![status](https://img.shields.io/badge/status-solved-brightgreen)
![log](https://img.shields.io/badge/log-21M%20lines-blue)
![tools](https://img.shields.io/badge/tools-awk%20%7C%20grep%20%7C%20sed-orange)
![suspect](https://img.shields.io/badge/suspect-GOEMON-ff3366)

---

## 👥 HackathonGroup3 — Group Members

### 🎓 ชั้นปี 3
| ชื่อ–สกุล | รหัสนักศึกษา |
|-----------|--------------|
| นาย ปาณัสม์ ตูพานิช | 6710301011 |
| นาย ธนัท จงธีรธนโชติ | 6710301032 |
| นาย ภากร กาเงิน | 6710301037 |
| นาย มูฮัมหมัดฮาซัน อุเซ็ง | 6710301025 |
| นาย เจตน์  -     |6710301022|

### 🎓 ชั้นปี 2
| ชื่อ–สกุล | รหัสนักศึกษา |
|-----------|--------------|
| นาย สุวิจักขณ์ ไพศาลภาณุมาศ | 6850301003 |
| นาย ธารา งามสง่า | 6810301030 |
| นาย Souvanhpheng Sydavong | 6810301029 |
| นาย ณัฐภัทร ศรีคชไกร | 6810301024 |

---

## 🎯 ภารกิจ (Mission Objectives)

| # | ภารกิจ | คำตอบ |
|---|--------|-------|
| 1 | **WHO ARE THEY?** — ระบุ IP ทั้งหมดของกลุ่มแฮกเกอร์ | **19 IP** (botnet) |
| 2 | **WHEN & HOW?** — หา Pattern และช่วงเวลาที่ระบบผิดปกติ | 412 วัน · ล่ม 302 / หน่วง 131 |
| 3 | **TELL PEOPLE** — แสดงผลเป็น Web App (Dashboard) | `dashboard.html` |
| 4 | **HIDDEN BONUS** — ตามหาชื่อจริงของคนร้าย | **`GOEMON`** |

---

## 📂 โครงสร้างไฟล์ (Files)

| ไฟล์ | คำอธิบาย |
|------|----------|
| `dashboard.html` | 🌐 เว็บแดชบอร์ดนำเสนอผล (เปิดได้เลย ออฟไลน์ 100% รองรับ TH/EN) |
| `solution.sh` | 🐚 สคริปต์ bash วิเคราะห์ทั้งหมด รันซ้ำได้ |
| `attackers.csv` | ข้อมูล 19 IP คนร้าย + สถิติ status / ช่วงเวลา |
| `attackers_ip_list.txt` | รายชื่อ IP คนร้ายล้วน (19 รายการ) |
| `timeline_daily.csv` | ข้อมูลการโจมตีรายวัน 731 วัน |

> ⚠️ ไฟล์ข้อมูลดิบ `cart_web.log` (1.4 GB) ไม่ได้รวมไว้ในรีโพเพราะมีขนาดใหญ่

---

## 🔬 วิธีการสืบสวน (Methodology)

วิเคราะห์ด้วย **command-line ของ Linux ล้วน** (`awk`, `grep`, `sed`) — ไม่ใช้ฐานข้อมูลหรือ AI
**แนวคิดหลัก:** *"request ปกติ → ตอบเร็ว + status 200 · request โจมตี → ตอบช้า + error"*

โครงสร้าง log (6 fields คั่นด้วย ` | `):
```
2024-06-10 04:17:43 | 39.3.141.152 | POST | /checkout | 200 | 122
   timestamp         |      IP       | method|   url    |status| response_time(ms)
```

### STEP 00 — ตามหาไฟล์ที่อาจารย์ซ่อนไว้
ไฟล์ถูกซ่อนใน path `/home/bootcamp/clmystery/mystery/streets/locked` — ใช้ `ls -lt` หาไฟล์ที่เพิ่งถูกเพิ่ม แล้วยืนยันด้วย keyword
```bash
cd /home/bootcamp/clmystery/mystery/streets/locked
ls -lt                                 # เรียงตามเวลาล่าสุด → เจอ cart_web.log
grep -an "hackathon#1" cart_web.log    # ยืนยันว่าเป็นไฟล์เป้าหมายจริง
```

### STEP 01 — WHO: หากลุ่ม IP คนร้าย
กรอง error (status ≥ 500) แล้วนับต่อ IP
```bash
awk -F' [|] ' '$5>=500{c[$2]++} END{for(i in c)print c[i],i}' cart_web.log | sort -rn | head -25
```
✅ พบ **19 IP** ที่ยิงเท่ากันหมด (~283,000 error/ตัว) → botnet ทีมเดียวกัน

### STEP 02 — WHEN & HOW: วิเคราะห์ Pattern ตามเวลา
แยกนับ "ล่ม" (500/504) และ "หน่วง" (200 + response > 5000ms)
```bash
# วันที่ระบบล่ม
awk -F' [|] ' '$5>=500{c[substr($1,1,10)]++} END{for(d in c)print d,c[d]}' cart_web.log | sort
# วันที่ระบบหน่วง
awk -F' [|] ' '$5==200 && $6>5000{c[substr($1,1,10)]++} END{for(d in c)print d,c[d]}' cart_web.log | sort
```
✅ โจมตี **412 วัน** → ล่ม 302 วัน + หน่วง 131 วัน (เกิดทั้งสองในวันเดียว 21 วัน) · พีคชั่วโมง **10:00–15:00**

### STEP 03 — VERIFY: ยืนยันไฟล์จริง + หาหัวโจก
```bash
grep -an "hackathon#1" cart_web.log
```
✅ keyword `hackathon#1` ฝังในไฟล์แค่ **บรรทัดเดียว** ผูกกับ IP **`197.82.237.190`** = หัวโจก

### STEP 04 — HIDDEN BONUS: ถอดชื่อคนร้าย
คนร้ายฝัง "ลายเซ็นดิจิทัล" โดยเติมตัวอักษร 1 ตัวท้าย URL (`/productsE`) ยิงซ้ำแบบ **Run-Length Encoding** → ดึงตัวท้ายมาต่อกัน แล้วยุบตัวซ้ำด้วย `sed`
```bash
grep -a "| 197.82.237.190 |" cart_web.log \
 | awk -F' [|] ' '{u=$4; sub(/\.html$/,"",u);
     b=substr(u,1,length(u)-1);
     if(b ~ /^\/(search|cart|checkout|products|index|api\/v1\/user)$/)
        printf "%s", substr(u,length(u),1)}' \
 | sed 's/\(.\)\1*/\1/g' | tr '_' ' '
```
✅ ถอดได้ข้อความ:
```
NEXUS CART WAS TOO EASY ... IT WAS ME — GOEMON
```

---

## 🏴‍☠️ คำตอบสุดท้าย (Final Answer)

| ภารกิจ | ผลลัพธ์ |
|--------|---------|
| 🔍 **WHO** | 19 IP — หัวโจก `197.82.237.190` |
| ⏰ **WHEN & HOW** | 2024-06-13 → 2026-06-10 · DDoS botnet · ล่ม 302 วัน / หน่วง 131 วัน · พีค 10:00–15:00 |
| 🏴‍☠️ **HIDDEN BONUS** | ชื่อคนร้าย = **`GOEMON`** |

### 🎯 รายชื่อ IP คนร้ายทั้ง 19 ตัว
```
209.103.8.44     162.240.218.117  197.82.237.190 ★  215.143.100.205
199.242.130.73   119.123.55.141   148.9.19.27       187.91.79.110
196.45.2.86      199.71.56.65     14.121.165.122    202.129.225.117
211.92.75.1      95.125.101.128   14.252.124.193    80.130.43.26
139.94.203.41    12.104.185.44    131.33.12.73
```
> ★ = หัวโจก (ringleader) ที่ซ่อนชื่อ `GOEMON` ไว้

---

## 🚀 วิธีเปิด Dashboard

```bash
# macOS
open dashboard.html
# หรือดับเบิลคลิกไฟล์ใน File Explorer ได้เลย
```

**Dashboard features:**
- 📊 กราฟวิเคราะห์ครบ (IP, timeline, ชั่วโมง, HTTP status)
- 🎬 อนิเมชันถอดรหัส Secret Message แบบ live
- 🌐 ปุ่มสลับภาษา **TH / EN**
- 📴 **ออฟไลน์ 100%** — ฝัง Chart.js + ฟอนต์ในไฟล์ ไม่ต้องต่อเน็ต

---

## 🛠️ Tech Stack
`bash` · `awk` · `grep` · `sed` · `Chart.js` · `HTML/CSS/JS`

---
# 👃 E-Nose Odor Intensity Evaluation & Anomaly Detection

โปรเจกต์วิเคราะห์ข้อมูลและสร้างโมเดล Machine Learning เพื่อประเมินความเข้มขิ่นของกลิ่น (Dilution-to-Threshold: D/T Ratio) จากสถานีตรวจวัดกลิ่นต่อเนื่อง (Electronic Nose) เพื่อตรวจจับเหตุการณ์ผิดปกติ (Anomaly Detection) และสนับสนุนการตัดสินใจของหน้างาน (โรงงาน/โรงบำบัดน้ำเสีย) ในการตอบสนองต่อข้อร้องเรียนของชุมชนรอบข้างได้อย่างมีหลักฐานและรวดเร็ว

## 📌 บริบทและเป้าหมายของโครงการ (Research Goal)
หน้างานประสบปัญหาชุมชนรอบข้างร้องเรียนเรื่องกลิ่นรบกวนบ่อยครั้ง ผู้บริหารและผู้จัดการจึงต้องการเครื่องมือที่ช่วยให้:
1. เข้าใจสถานการณ์ความรุนแรงของกลิ่นจากข้อมูล Sensor ทั้ง 8 ตัว และปัจจัยสภาพอากาศ
2. ตอบข้อร้องเรียนจากชุมชนได้อย่างมีหลักฐานอ้างอิงทางวิทยาศาสตร์
3. ตัดสินใจแก้ปัญหาได้ทันท่วงทีว่าควรเข้าตรวจสอบและแก้ไขที่จุดใด เมืิ่อใด

**เป้าหมายสูงสุด:** *"ประเมินความเข้มกลิ่น (D/T) จากค่าของ sensor ทั้ง 8 ตัว และตรวจจับช่วงเวลาที่กลิ่นผิดปกติ เพื่อสนับสนุนการตัดสินใจของหน้างาน"*

---

## 🛠️ กระบวนการทำงาน (Data Science Process)

โครงการนี้ดำเนินการตามกระบวนการ Data Science Process ทั้งหมด 6 ขั้นตอน ดังนี้:

### Step 1 — Setting the Research Goal
* กำหนดโจทย์ธุรกิจและตัวชี้วัด แปลงปัญหาเรื่องกลิ่นรบกวนให้เป็นโจทย์การทำ Regression เพื่อทำนายค่าความเข้มกลิ่น (D/T) 

### Step 2 — Retrieving Data
* ข้อมูลดิบมาจากไฟล์ `Export.csv` ซึ่งบันทึกค่าจากสถานี ENose ทุกๆ **1 นาที** ต่อเนื่องเป็นเวลาประมาณ **91 วัน**
* ขนาดข้อมูลเริ่มต้น: `130,343 แถว, 17 คอลัมน์` (ช่วงเวลา 2026-02-12 ถึง 2026-05-14)
* **สิ่งที่พบจากการสำรวจเบื้องต้น (Initial Exploration):**
  * พบ Excel Dialect (`sep=,`) ในบรรทัดแรกของไฟล์
  * มีข้อมูลสูญหาย (Missing Values) ของกลุ่ม Sensor อยู่ประมาณ 0.32% (421 แถว)
  * คอลัมน์ `Smell Prediction` มีข้อมูลเป็น NaN ถึง 34% และมีเพียงค่าเดี่ยวคือ "Ambient" ไม่สะท้อนโปรไฟล์กลิ่นอื่น จึงตัดสินใจใช้ `D/T` เป็น Target Variable แทน

### Step 3 — Data Preparation & Cleaning
* ทำการ Skip Row แรกเพื่อโหลดข้อมูลให้ถูกต้อง และตัดช่องว่าง (Whitespace) ออกจากชื่อคอลัมน์
* แปลงคอลัมน์ `Time` ให้เป็น Datetime object และคอลัมน์ที่เหลือให้เป็น Numeric type
* ลบแถวที่เป็นข้อมูลประเภท Marker ซึ่งไม่ใช่ข้อมูลจริงออก (เช่น แถวที่มีค่า `hackathon#2`)
* จัดการกับแถวที่ Sensor ทั้ง 8 ตัวว่างพร้อมกัน (`NaN`) โดยการลบออกเนื่องจากเป็นสัญญาณรบกวนหรือช่วงเครื่องดับ (ระบบ Error)

### Step 4 — Data Exploration (EDA)
* วิเคราะห์แนวโน้มค่าความเข้มกลิ่น (D/T) ตามช่วงเวลาเพื่อหา Pattern และ Cycle ของกลิ่น
* ตรวจสอบช่วงเวลาที่ค่าความเข้มกลิ่นพุ่งสูงผิดปกติ (Spike) เพื่อระบุเหตุการณ์ Anomaly
* วิเคราะห์ความสัมพันธ์ (Correlation Matrix) ระหว่างค่าจาก Sensor ทั้ง 8 ตัว, สภาพอากาศ (ทิศทางลม, ความเร็วลม, อุณหภูมิ, ความชื้น, ความกดอากาศ, PM 2.5) และค่า Target D/T

### Step 5 — Data Modeling & Evaluation
* พัฒนาโมเดล Machine Learning เพื่อทำนายค่า D/T Ratio โดยใช้ Features จากค่า Sensor, ข้อมูลสภาพอากาศ และข้อมูลกลุ่มเวลา (Time-based features)
* เปรียบเทียบประสิทธิภาพของโมเดลหลากประเภท และประเมินผลด้วย Metrics มาตรฐาน:
  * Mean Absolute Error (MAE)
  * Root Mean Squared Error (RMSE)
  * R-squared ($R^2$) เพื่อเลือกโมเดลที่ดีที่สุดไปใช้งาน

### Step 6 — Presentation, Automation & Action
* นำเสนอผลลัพธ์ผ่านกราฟเปรียบเทียบค่าจริง (Actual) และค่าทำนาย (Predicted) เพื่อดูความแม่นยำ
* Export ผลลัพธ์การทำนายออกมาเป็นไฟล์ `.csv` สำหรับระบบอื่นนำไปใช้งานต่อ
* **สร้างฟังก์ชันอัตโนมัติ (Automation Function):** สำหรับรับข้อมูลชุดใหม่ (New data entry) เข้ามาทำนายค่า D/T ทันที พร้อมแปลงผลลัพธ์เป็นระดับการแจ้งเตือนกลิ่น (Odor Alert Levels) ได้แก่ **Low, Medium, และ High**

---

## 📊 โครงสร้างข้อมูล (Data Features)

| ชื่อฟีเจอร์ | รายละเอียด |
|---|---|
| `Time` | วันและเวลาที่บันทึกข้อมูล (บันทึกทุก 1 นาที) |
| `D/T` | Dilution-to-Threshold (ค่าความเข้มข้นของกลิ่น - **Target**) |
| `Sensor 1 - 8` | ค่าสัญญาณจากเซนเซอร์ตรวจวัดก๊าซทั้ง 8 ตัวของระบบ E-Nose |
| `Wind Direction` / `Wind Speed` | ทิศทางและความเร็วลม ณ ขณะนั้น |
| `Temperature` / `Relative Humidity` | อุณหภูมิและความชื้นสัมพัทธ์ในอากาศ |
| `PM 2.5` / `Atmospheric Pressure` | ปริมาณฝุ่น PM2.5 และความกดอากาศ |

---

## 💻 การติดตั้งและเริ่มต้นใช้งาน (Getting Started)

### Prerequisites
โปรแกรมและไลบรารีที่จำเป็นต้องใช้:
```bash
python >= 3.8
pandas
numpy
scikit-learn
matplotlib
seaborn
jupyterlab
<div align="center">

**Together, we secure tomorrow.** 🛡️

*HackathonGroup3 · The Silent Threat · NexusCart Incident Response*

</div>
