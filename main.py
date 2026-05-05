import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- [1. การตั้งค่าหน้าจอและสไตล์] ---
st.set_page_config(layout="wide", page_title="ระบบวิเคราะห์ข้อมูลการขายและลูกหนี้")

# CSS สำหรับสร้าง Card และปรับแต่ง UI ให้เหมือนต้นฉบับ
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #1E1E1E; }
    .kpi-card {
        background-color: #fdfdfb;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f0f0f0;
        height: 110px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันช่วยสร้าง KPI Card
def render_metric(label, value, sub_text, color="#1E1E1E"):
    st.markdown(f"""
        <div class="kpi-card">
            <p style="margin:0; font-size:13px; color: #666;">{label}</p>
            <h2 style="margin:5px 0; color: {color}; font-size: 26px;">฿{value}</h2>
            <p style="margin:0; font-size:11px; color: gray;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

# --- [2. ฟังก์ชันจัดการข้อมูล] ---
def load_data(file):
    df = pd.read_excel(file)
    df.columns = [c.strip() for c in df.columns]
    # แปลงคอลัมน์ตัวเลข
    num_cols = ['เงินก่อนภาษี', 'รวมทั้งสิ้น', 'ยอดคงเหลือ']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    # แปลงวันที่
    if 'วันที่ออกเอกสาร' in df.columns:
        df['วันที่ออกเอกสาร'] = pd.to_datetime(df['วันที่ออกเอกสาร'])
    return df

# --- [3. ส่วนประกอบหลักของ UI] ---
st.markdown('<div class="main-title">ระบบวิเคราะห์ข้อมูลการขายและลูกหนี้</div>', unsafe_allow_html=True)
st.caption("ข้อมูลจากไฟล์วิเคราะห์การขาย — ปี 2026")

uploaded_file = st.sidebar.file_uploader("โยนไฟล์ Excel ที่นี่ค่ะ", type=['xlsx'])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # ระบบ Navigation
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "ภาพรวม"

    menu = ["ภาพรวม", "สถานะ SO", "แยกตาม Jobs", "พนักงานขาย", "รายเดือน", "ยอดคงค้าง"]
    cols = st.columns(len(menu))
    for i, item in enumerate(menu):
        btn_type = "primary" if st.session_state.active_tab == item else "secondary"
        if cols[i].button(item, use_container_width=True, type=btn_type):
            st.session_state.active_tab = item
            st.rerun()

    st.markdown("---")

    # --- [4. เนื้อหาหน้า "ภาพรวม" ตามภาพ image_034230.png] ---
    if st.session_state.active_tab == "ภาพรวม":
        # แถวที่ 1: KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            val = df['เงินก่อนภาษี'].sum() / 1e6
            render_metric("มูลค่ารวมก่อน VAT", f"{val:.1f}M", f"{len(df):,} รายการ")
        with c2:
            sub = df[df['สถานะ'] == 'ชำระเงินครบแล้ว']
            render_metric("ชำระเงินครบแล้ว", f"{sub['รวมทั้งสิ้น'].sum()/1e6:.1f}M", f"{len(sub):,} รายการ", "#10A37F")
        with c3:
            sub = df[df['สถานะ'] == 'วางบิลแล้ว']
            render_metric("วางบิลแล้ว / รอเก็บ", f"{sub['รวมทั้งสิ้น'].sum()/1e6:.1f}M", f"{len(sub):,} รายการ", "#4A90E2")
        with c4:
            val = df['ยอดคงเหลือ'].sum() / 1e6
            render_metric("ยอดคงค้างรวม", f"{val:.1f}M", "มูลค่าลูกหนี้รวม", "#D32F2F")

        c1_2, c2_2, c3_2, c4_2 = st.columns(4)
        with c1_2:
            sub = df[df['สถานะ'] == 'ยังไม่ได้เปิดอินวอย']
            render_metric("ยังไม่ออก Invoice", f"{sub['รวมทั้งสิ้น'].sum()/1e6:.1f}M", f"{len(sub):,} รายการ", "#D18227")
        with c2_2:
            sub = df[df['สถานะ'] == 'ยกเลิก']
            render_metric("ยกเลิก", f"{sub['รวมทั้งสิ้น'].sum()/1e6:.1f}M", f"{len(sub):,} รายการ", "#7F8C8D")

        st.write("")
        # แถวที่ 2: กราฟ Donut และ Bar (แนวนอน)
        g1, g2 = st.columns(2)
        with g1:
            st.write("**มูลค่าแยกตามสถานะ**")
            fig_pie = px.pie(df, values='รวมทั้งสิ้น', names='สถานะ', hole=0.6,
                             color_discrete_sequence=['#10A37F', '#4A90E2', '#9B51E0', '#D18227', '#E67E22'])
            fig_pie.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            st.write("**มูลค่าแยกตาม Jobs (Top 10)**")
            top_jobs = df.groupby('Jobs')['รวมทั้งสิ้น'].sum().nlargest(10).reset_index()
            fig_job = px.bar(top_jobs, x='รวมทั้งสิ้น', y='Jobs', orientation='h', color_discrete_sequence=['#10A37F'])
            fig_job.update_layout(xaxis_title="", yaxis_title="", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_job, use_container_width=True)

        # แถวที่ 3: กราฟแท่งรายเดือน
        st.write("**มูลค่า SO รายเดือน**")
        df['Month'] = df['วันที่ออกเอกสาร'].dt.strftime('%m') # ดึงเลขเดือน
        monthly = df.groupby('Month')['รวมทั้งสิ้น'].sum().reset_index()
        fig_month = px.bar(monthly, x='Month', y='รวมทั้งสิ้น', color='Month',
                           color_discrete_sequence=['#9B51E0', '#4A90E2', '#10A37F', '#D18227'])
        st.plotly_chart(fig_month, use_container_width=True)

    else:
        st.info(f"คุณกำลังอยู่ที่หน้า: {st.session_state.active_tab} (รอการเชื่อมข้อมูลรายละเอียด)")

else:
    st.warning("👈 กรุณาอัปโหลดไฟล์เพื่อเริ่มต้นการวิเคราะห์ค่ะ")
