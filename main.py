import streamlit as st
import pandas as pd
import plotly.express as px

# --- ตั้งค่าหน้าจอและโทนสี ---
st.set_page_config(layout="wide", page_title="Sales Order Dashboard 2026")

# Custom CSS เพื่อความสวยงาม (สีปุ่มและ Card)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #f0f2f6; }
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- ส่วนของการโยนไฟล์ ---
uploaded_file = st.sidebar.file_uploader("โยนไฟล์ Excel ที่นี่ค่ะ", type=['xlsx'])

if uploaded_file:
    # อ่านข้อมูล (สมมติว่าเป็นไฟล์ Excel)
    df = pd.read_excel(uploaded_file)
    
    # --- ส่วนหัวและปุ่มเมนู ---
    st.title("Sales Order Dashboard — ปี 2026")
    
    menu = ["ภาพรวม", "สถานะ SO", "แยกตาม Jobs", "พนักงานขาย", "รายเดือน", "ยอดคงค้าง"]
    selected_tab = st.segmented_control("เลือกมุมมองวิเคราะห์:", menu, default="ภาพรวม")

    st.markdown("---")

    if selected_tab == "ภาพรวม":
        # สร้าง 4 คอลัมน์สำหรับ KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("มูลค่ารวมก่อน VAT", "฿416.1M", "11,899 รายการ")
        with col2:
            st.metric("ชำระเงินครบแล้ว", "฿145.7M", "4,472 รายการ", delta_color="normal")
        
        # แสดงกราฟ (ตัวอย่าง Donut Chart)
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df, values='ยอดเงิน', names='สถานะ', hole=0.5, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
    # (ส่วนของ Tab อื่นๆ จะใส่ Logic ตามข้อมูลในไฟล์จริงของคุณค่ะ)

else:
    st.info("กรุณาอัปโหลดไฟล์ Excel เพื่อเริ่มการวิเคราะห์สวยๆ แบบในรูปค่ะ!")
