import streamlit as st
import pandas as pd

# --- [1. Configuration & Styling] ---
st.set_page_config(layout="wide", page_title="AI Sales Dashboard")

# CSS สำหรับตกแต่ง Card ให้เหมือนในรูปภาพ
st.markdown("""
    <style>
    .kpi-card {
        background-color: #fdfdfb;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #eeeeee;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    .kpi-title { font-size: 14px; color: #555; margin-bottom: 8px; }
    .kpi-value { font-size: 26px; font-weight: bold; margin-bottom: 4px; }
    .kpi-count { font-size: 12px; color: #888; }
    </style>
""", unsafe_allow_html=True)

# --- [2. Data Processing Logic] ---
def process_data(file):
    try:
        df = pd.read_excel(file)
        # ทำความสะอาดชื่อคอลัมน์
        df.columns = [c.strip() for c in df.columns]
        # แปลงตัวเลขให้ถูกต้อง
        if 'รวมทั้งสิ้น' in df.columns:
            df['รวมทั้งสิ้น'] = pd.to_numeric(df['รวมทั้งสิ้น'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# --- [3. UI Helper Functions] ---
def render_kpi_card(title, amount, count, color):
    # ฟังก์ชันสร้าง HTML สำหรับ Card
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value" style="color: {color};">฿{amount:,.1f}M</div>
            <div class="kpi-count">{count:,} รายการ</div>
        </div>
    """, unsafe_allow_html=True)

# --- [4. Main Application] ---
st.title("📊 ระบบวิเคราะห์ข้อมูลการขายและลูกหนี้")

# ส่วนอัปโหลดไฟล์ที่ Sidebar
uploaded_file = st.sidebar.file_uploader("เลือกไฟล์ test_4.xlsx", type=['xlsx'])

if uploaded_file:
    df = process_data(uploaded_file)
    
    if df is not None:
        # ระบบ Navigation แบบปุ่มกด (Active State)
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = "สถานะ SO"

        menu = ["ภาพรวม", "สถานะ SO", "แยกตาม Jobs", "พนักงานขาย", "รายเดือน", "ยอดคงค้าง"]
        cols = st.columns(len(menu))
        
        for i, item in enumerate(menu):
            # ปุ่มที่เลือกจะเป็นสีเข้ม (primary) ปุ่มอื่นจะเป็นสีเทาปกติ
            btn_type = "primary" if st.session_state.active_tab == item else "secondary"
            if cols[i].button(item, use_container_width=True, type=btn_type):
                st.session_state.active_tab = item
                st.rerun()

        st.markdown("---")

        # แสดงเนื้อหาตามหน้าที่เลือก
        if st.session_state.active_tab == "สถานะ SO":
            # รายการสถานะที่ต้องการแสดงตามรูปภาพ
            status_targets = [
                {"name": "ชำระเงินครบแล้ว", "color": "#10A37F"},
                {"name": "วางบิลแล้ว", "color": "#4A90E2"},
                {"name": "เปิด INV ยังไม่วางบิล", "color": "#9B51E0"},
                {"name": "ยังไม่ได้เปิดอินวอย", "color": "#D18227"},
                {"name": "ชำระแล้วบางส่วน", "color": "#E67E22"},
                {"name": "ยกเลิก", "color": "#7F8C8D"}
            ]

            # วนลูปสร้าง Card 4 คอลัมน์ต่อแถว
            for i in range(0, len(status_targets), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(status_targets):
                        target = status_targets[i + j]
                        # กรองข้อมูลตามสถานะ
                        sub_df = df[df['สถานะ'] == target['name']]
                        total_m = sub_df['รวมทั้งสิ้น'].sum() / 1_000_000 # แปลงเป็นหน่วยล้าน (M)
                        count = len(sub_df)
                        
                        with cols[j]:
                            render_kpi_card(target['name'], total_m, count, target['color'])
        else:
            st.info(f"ยินดีต้อนรับสู่หน้า: {st.session_state.active_tab} (ส่วนนี้สามารถเพิ่มกราฟหรือตารางได้ตามต้องการค่ะ)")
else:
    st.warning("👈 กรุณาอัปโหลดไฟล์ Excel เพื่อเริ่มต้นการวิเคราะห์ค่ะ")
