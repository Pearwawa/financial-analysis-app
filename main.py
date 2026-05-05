import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้ากระดาษให้กว้าง
st.set_page_config(layout="wide")

# --- 1. ส่วนหัว (Header) ---
st.title("Sales Order Dashboard — ปี 2026")
st.caption("ข้อมูลจากไฟล์ SO_ป__2026 | รายการทั้งหมด 11,899 รายการ | ม.ค. - เม.ย. 2569")

# --- 2. เมนูเลือกหน้า (Tabs) ---
tab_titles = ["ภาพรวม", "สถานะ SO", "แยกตาม Jobs", "พนักงานขาย", "รายเดือน", "ยอดคงค้าง"]
tabs = st.tabs(tab_titles)

with tabs[5]: # สมมติว่าเราทำหน้า "ยอดคงค้าง" ตามรูป
    
    # --- 3. KPI Cards (4 คอลัมน์) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ยอดคงค้างรวม", "฿55.0M", "1,592 รายการ", delta_color="off")
    with col2:
        st.metric("ยอดคงค้าง 7-11", "฿36.3M", "65.9% ของค้างทั้งหมด", delta_color="off")
    with col3:
        st.metric("ยอดคงค้างรายอื่นๆ", "฿18.7M", "34.1% ของค้างทั้งหมด", delta_color="off")
    with col4:
        st.metric("ยังไม่ออก Invoice", "฿54.4M", "1,582 รายการ รอดำเนินการ", delta_color="normal")

    st.divider()

    # --- 4. กราฟ (2 คอลัมน์) ---
    g_col1, g_col2 = st.columns([1, 1])
    
    with g_col1:
        st.subheader("ยอดคงค้างแยกตาม Jobs")
        # ตัวอย่างข้อมูลกราฟวงกลม
        df_pie = pd.DataFrame({"Jobs": ["7-11", "Suratthani", "Chains"], "Value": [17, 7, 8]})
        fig_pie = px.pie(df_pie, names="Jobs", values="Value", hole=0.5, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    with g_col2:
        st.subheader("สถานะที่ยังรอดำเนินการ")
        # ตัวอย่างข้อมูลกราฟแท่ง
        df_bar = pd.DataFrame({"Status": ["ยังไม่ออก INV", "เปิด INV ยังไม่วางบิล"], "Value": [54.4, 105]})
        fig_bar = px.bar(df_bar, x="Status", y="Value", color="Status",
                         color_discrete_map={"ยังไม่ออก INV": "#B87333", "เปิด INV ยังไม่วางบิล": "#9370DB"})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 5. ตารางข้อมูลด้านล่าง ---
    st.subheader("ยอดคงค้างแยกตาม Jobs (จากข้อมูล Summary)")
    # ในส่วนนี้คุณสามารถใช้ st.dataframe หรือสร้าง HTML table เพื่อใส่แถบ Progress bar ได้ครับ
