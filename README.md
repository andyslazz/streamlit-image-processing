# Streamlit Image Processing 

โปรเจกต์นี้เป็น **Web App ด้วย Streamlit** สำหรับการทดลองทำ Image Processing แบบง่าย ๆ  
สามารถเปิดกล้องจาก Notebook / Webcam / URL จากอินเทอร์เน็ต ปรับแต่งพารามิเตอร์ และดูผลลัพธ์แบบโต้ตอบ (Interactive) ได้ทันที  

---

## ฟีเจอร์
- รองรับ **3 แหล่งข้อมูลภาพ**
  - ถ่ายภาพจาก **Webcam**
  - อัปโหลดไฟล์จากเครื่อง
  - ดึงรูปจาก **URL** (Auto-refresh ได้)
- การประมวลผลภาพ
  - ปรับ **Brightness / Contrast**
  - เลือก **Operation**:
    - Grayscale
    - Gaussian Blur
    - Sharpen (Unsharp Mask)
    - Canny Edge Detection
    - Threshold (Binary)
- สามารถปรับ **พารามิเตอร์** ของแต่ละ Operation ได้ผ่าน GUI
- แสดงผล **Original vs Processed** ข้างกัน
- แสดง **Histogram** ของค่าความเข้ม พร้อมข้อมูล Width / Height / Mean Intensity

---

## การติดตั้ง
1. Clone repository
   ```bash
   git clone https://github.com/your-username/streamlit-image-processing.git
   cd streamlit-image-processing
   ```

2. สร้าง virtual environment 
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows
   ```

3. ติดตั้ง dependencies
   ```bash
   pip install -r requirements.txt
   ```

---

## การรันแอป
```bash
streamlit run streamlit_image_processing_app.py
```

จากนั้นเปิดเบราว์เซอร์ที่ URL ที่ Streamlit แสดง (ปกติจะเป็น `http://localhost:8501`)

---

## Deploy บน Streamlit Cloud
1. Push โค้ดขึ้น GitHub  
2. เข้า [Streamlit Community Cloud](https://streamlit.io/cloud)  
3. กด **New app** → เลือก repo → ระบุไฟล์หลัก `streamlit_image_processing_app.py`  
4. กด Deploy 

---

## Requirements
- Python >= 3.8
- Streamlit
- OpenCV (opencv-python-headless)
- Pillow
- NumPy
- Matplotlib
- Requests

---