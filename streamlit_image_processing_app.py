import io
import time
import cv2
import numpy as np
import requests
import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image


# Config หน้าเว็บ
st.set_page_config(page_title="Image Processing", layout="wide")
st.title("Image Processing — Streamlit")


# Utilities
def ensure_rgb(pil_img: Image.Image) -> Image.Image:
    """แปลงภาพให้เป็น RGB เสมอ"""
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    return pil_img


def pil_to_cv(pil_img: Image.Image) -> np.ndarray:
    """PIL(Image) -> OpenCV (BGR)"""
    rgb = np.array(pil_img)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return bgr


def cv_to_pil(bgr: np.ndarray) -> Image.Image:
    """OpenCV (BGR) -> PIL(Image)"""
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def fetch_image_from_url(url: str) -> Image.Image:
    """โหลดรูปจาก URL -> PIL Image (RGB)"""
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content))
    return ensure_rgb(img)


def resize_max_side(img_bgr: np.ndarray, max_side: int = 1280) -> np.ndarray:
    """ลดขนาดภาพโดยรักษาสัดส่วน ให้ด้านยาวสุดไม่เกิน max_side"""
    h, w = img_bgr.shape[:2]
    if max(h, w) <= max_side:
        return img_bgr
    scale = max_side / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def apply_brightness_contrast(bgr: np.ndarray, brightness: int = 0, contrast: float = 1.0) -> np.ndarray:
    """ปรับความสว่างและคอนทราสต์ด้วยสูตร new = alpha*img + beta (alpha=contrast, beta=brightness)"""
    # brightness [-100, 100] -> beta
    # contrast [0.5, 2.0] -> alpha
    alpha = float(contrast)
    beta = int(brightness)
    out = cv2.convertScaleAbs(bgr, alpha=alpha, beta=beta)
    return out


def odd_kernel(k: int) -> int:
    """บังคับให้เป็นเลขคี่ >= 1"""
    k = max(1, int(k))
    if k % 2 == 0:
        k += 1
    return k


def unsharp_mask(bgr: np.ndarray, radius: int = 3, amount: float = 1.0) -> np.ndarray:
    radius = odd_kernel(radius)
    blurred = cv2.GaussianBlur(bgr, (radius, radius), 0)
    # out = bgr + amount*(bgr - blurred)
    out = cv2.addWeighted(bgr, 1 + amount, blurred, -amount, 0)
    return out


# Sidebar Controls
with st.sidebar:
    st.header("Config")
    src = st.radio(
        "เลือกรูปจาก",
        ["Webcam (ถ่ายภาพ)", "อัปโหลดไฟล์", "URL (รูปจากอินเทอร์เน็ต)"],
        index=0,
    )

    st.markdown("---")
    st.subheader("Pre-processing")
    brightness = st.slider("Brightness (β)", -100, 100, 0, help="ปรับความสว่าง")
    contrast = st.slider("Contrast (α)", 0.50, 2.00, 1.00, 0.01, help="ปรับคอนทราสต์")

    st.markdown("---")
    st.subheader("การประมวลผลหลัก")
    op = st.selectbox(
        "Operation",
        [
            "None",
            "Grayscale",
            "Gaussian Blur",
            "Sharpen (Unsharp Mask)",
            "Canny Edge",
            "Threshold (Binary)",
        ],
        index=0,
    )

    # พารามิเตอร์ของแต่ละ Operation
    if op == "Gaussian Blur":
        k = st.slider("Kernel size", 1, 51, 9, step=2)
        sigma = st.slider("SigmaX", 0.0, 10.0, 0.0, 0.1)
    elif op == "Sharpen (Unsharp Mask)":
        radius = st.slider("Radius (kernel)", 1, 31, 5, step=2)
        amount = st.slider("Amount", 0.0, 3.0, 1.0, 0.05)
    elif op == "Canny Edge":
        low = st.slider("Low threshold", 0, 255, 100)
        high = st.slider("High threshold", 1, 255, 200)
        if high <= low:
            high = low + 1
        aperture = st.select_slider("Aperture size", options=[3, 5, 7], value=3)
    elif op == "Threshold (Binary)":
        thr = st.slider("Threshold", 0, 255, 128)
        inv = st.checkbox("Invert (THRESH_BINARY_INV)")


# Input Source
img_pil = None

if src == "Webcam (ถ่ายภาพ)":
    picture = st.camera_input("ถ่ายภาพจากกล้อง")
    if picture is not None:
        try:
            img_pil = ensure_rgb(Image.open(picture))
        except Exception as e:
            st.error(f"ไม่สามารถอ่านภาพจากกล้องได้: {e}")

elif src == "อัปโหลดไฟล์":
    file = st.file_uploader("อัปโหลดรูปภาพ (PNG/JPG/JPEG/BMP/WEBP)", type=["png", "jpg", "jpeg", "bmp", "webp"])
    if file is not None:
        try:
            img_pil = ensure_rgb(Image.open(file))
        except Exception as e:
            st.error(f"ไม่สามารถอ่านไฟล์รูปได้: {e}")

elif src == "URL (รูปจากอินเทอร์เน็ต)":
    url = st.text_input("วางลิงก์รูปภาพ (URL)")
    fetch_btn = st.button("apply")
    if fetch_btn and url:
        try:
            with st.spinner("กำลังดึงรูป..."):
                img_pil = fetch_image_from_url(url)
        except Exception as e:
            st.error(f"ดึงรูปไม่สำเร็จ: {e}")


if img_pil is None:
    st.stop()


# Processing Pipeline
col_left, col_right = st.columns([1, 1])

# แสดงต้นฉบับ
with col_left:
    st.subheader("รูปต้นฉบับ (Original)")
    st.image(img_pil, use_container_width=True)

# แปลงไป OpenCV BGR เพื่อประมวลผล
img_bgr = pil_to_cv(img_pil)
img_bgr = resize_max_side(img_bgr, max_side=1280)

# 1 ปรับ Brightness/Contrast
proc = apply_brightness_contrast(img_bgr, brightness=brightness, contrast=contrast)

# 2 Operation หลัก
if op == "None":
    out_bgr = proc
elif op == "Grayscale":
    gray = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
    out_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
elif op == "Gaussian Blur":
    out_bgr = cv2.GaussianBlur(proc, (odd_kernel(k), odd_kernel(k)), sigma)
elif op == "Sharpen (Unsharp Mask)":
    out_bgr = unsharp_mask(proc, radius=radius, amount=amount)
elif op == "Canny Edge":
    gray = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1=low, threshold2=high, apertureSize=aperture)
    out_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
elif op == "Threshold (Binary)":
    gray = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
    ttype = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
    _, th = cv2.threshold(gray, thr, 255, ttype)
    out_bgr = cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)
else:
    out_bgr = proc

# แสดงผลลัพธ์
with col_right:
    st.subheader("รูปหลังประมวลผล (Output)")
    st.image(cv_to_pil(out_bgr), use_container_width=True)


# สถิติ & กราฟคุณสมบัติรูป
with st.container(border=True):
    st.subheader("คุณสมบัติของรูปภาพ & กราฟฮิสโตแกรม")

    h, w = out_bgr.shape[:2]
    gray_for_stats = cv2.cvtColor(out_bgr, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(gray_for_stats))
    std_val = float(np.std(gray_for_stats))

    m1, m2, m3 = st.columns(3)
    m1.metric("ความกว้าง (px)", f"{w}")
    m2.metric("ความสูง (px)", f"{h}")
    m3.metric("ความสว่างเฉลี่ย", f"{mean_val:.1f}")

    # กราฟฮิสโตแกรมของความเข้มแสง (0..255)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(gray_for_stats.ravel(), bins=256, range=(0, 255))
    ax.set_title("Histogram of Intensity (Grayscale)")
    ax.set_xlabel("Intensity")
    ax.set_ylabel("Count")
    st.pyplot(fig, use_container_width=True)

st.success("เสร็จสิ้น (สามารถลองเปลี่ยนพารามิเตอร์เพื่อดูผลลัพธ์แบบเรียลไทม์)")
