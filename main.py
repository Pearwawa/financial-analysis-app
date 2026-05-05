import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- [1. การตั้งค่าหน้าจอและสไตล์] ---
st.set_page_config(layout="wide", page_title="ระบบวิเคราะห์ข้อมูลการขายและลูกหนี้")

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #1E1E1E; }
    .kpi-card {
        background-color: #fdfdfb;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f0f0f0;
        min-height: 130px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

def render_metric(label, value, sub_text, color="#1E1E1E"):
    st.markdown(f"""
        <div class="kpi-card">
            <p style="margin:0; font-size:13px; color: #666; font-weight: 500;">{label}</p>
            <h2 style="margin:10px 0; color: {color}; font-size: 24px; line-height: 1.2;">{value}</h2>
            <p style="margin:0; font-size:12px; color: gray;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

# --- [2. ฟังก์ชันจัดการข้อมูล] ---
def load_data(file):
    df = pd.read_excel(file)
    df.columns = [c.strip() for c in df.columns]
    
    # แปลงตัวเลข
    num_cols = ['เงินก่อนภาษี', 'รวมทั้งสิ้น', 'ยอดคงเหลือ']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # แปลงวันที่และสร้างคอลัมน์ช่วยวิเคราะห์
    if 'วันที่ออกเอกสาร' in df.columns:
        df['วันที่ออกเอกสาร'] = pd.to_datetime(df['วันที่ออกเอกสาร'])
        df['Month_Num'] = df['วันที่ออกเอกสาร'].dt.month
        df['Month_Name'] = df['วันที่ออกเอกสาร'].dt.strftime('%b')
        df['Year'] = df['วันที่ออกเอกสาร'].dt.year
    
    # ทำความสะอาดคอลัมน์สถานะ
    if 'สถานะ' in df.columns:
        df['สถานะ'] = df['สถานะ'].astype(str).str.strip()
        
    return df

# --- [3. ส่วนประกอบหลักของ UI] ---
st.markdown('<div class="main-title">ระบบวิเคราะห์ข้อมูลการขายและลูกหนี้</div>', unsafe_allow_html=True)
st.caption("ข้อมูลจากไฟล์วิเคราะห์การขาย — ปี 2026")

uploaded_file = st.sidebar.file_uploader("โยนไฟล์ Excel ที่นี่ค่ะ", type=['xlsx'])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "ภาพรวม"

    menu = ["ภาพรวม", "สถานะ SO", "แยกตาม Jobs", "พนักงานขาย", "รายเดือน", "ยอดคงค้าง"]
    cols_menu = st.columns(len(menu))
    for i, item in enumerate(menu):
        btn_type = "primary" if st.session_state.active_tab == item else "secondary"
        if cols_menu[i].button(item, use_container_width=True, type=btn_type):
            st.session_state.active_tab = item
            st.rerun()

    st.markdown("---")

    # --- [4. เนื้อหาแต่ละหน้า] ---
    
    if st.session_state.active_tab == "ภาพรวม":
        # ส่วนที่ 1: KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            val = df['เงินก่อนภาษี'].sum() / 1e6
            render_metric("มูลค่ารวมก่อน VAT", f"฿{val:.1f}M", f"{len(df):,} รายการ")
        with c2:
            sub = df[df['สถานะ'].str.contains('ชำระเงินครบแล้ว', na=False)]
            render_metric("ชำระเงินครบแล้ว", f"฿{sub['รวมทั้งสิ้น'].sum()/1e6:.1f}M", f"{len(sub):,} รายการ", "#10A37F")
        with c3:
            sub = df[df['สถานะ'].str.contains('วางบิลแล้ว', na=False)]
            render_metric("วางบิลแล้ว / รอเก็บ", f"฿{sub['รวมทั้งสิ้น'].sum()/1e6:.1f}M", f"{len(sub):,} รายการ", "#4A90E2")
        with c4:
            val = df['ยอดคงเหลือ'].sum() / 1e6
            render_metric("ยอดคงค้างรวม", f"฿{val:.1f}M", "มูลค่าลูกหนี้รวม", "#D32F2F")

        # ส่วนที่ 2: ข้อความวิเคราะห์ (Insights)
        total_val = df['รวมทั้งสิ้น'].sum()
        top_job = df.groupby('Jobs')['รวมทั้งสิ้น'].sum().idxmax()
        peak_month = df.groupby('Month_Name')['รวมทั้งสิ้น'].sum().idxmax()
        cancel_val = df[df['สถานะ'].str.contains("ยกเลิก", na=False)]['รวมทั้งสิ้น'].sum()
        
        st.info("### สิ่งที่น่าสนใจ:")
        st.markdown(f"""
        *   **{top_job} คือลูกค้าหลัก** และมียอดสั่งซื้อสูงสุดในภาพรวม
        *   **{peak_month} เป็นเดือนที่มียอดสูงสุด** แนะนำให้ตรวจสอบกำลังการผลิตในช่วงนี้ของปีถัดไป
        *   **ยกเลิกเพียง ฿{cancel_val/1e6:.2f}M** ถือว่าอยู่ในเกณฑ์ที่ต่ำมาก
        """)

        # ส่วนที่ 3: กราฟ
        g1, g2 = st.columns(2)
        with g1:
            st.write("**มูลค่าแยกตามสถานะ**")
            fig_pie = px.pie(df, values='รวมทั้งสิ้น', names='สถานะ', hole=0.6)
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            st.write("**มูลค่าแยกตาม Jobs (Top 10)**")
            top_jobs = df.groupby('Jobs')['รวมทั้งสิ้น'].sum().nlargest(10).reset_index()
            fig_job = px.bar(top_jobs, x='รวมทั้งสิ้น', y='Jobs', orientation='h', color_discrete_sequence=['#10A37F'])
            fig_job.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_job, use_container_width=True)

    elif st.session_state.active_tab == "สถานะ SO":
        status_counts = df['สถานะ'].value_counts().reset_index()
        fig_status = px.bar(status_counts, x='count', y='สถานะ', orientation='h', color='สถานะ')
        st.plotly_chart(fig_status, use_container_width=True)

    elif st.session_state.active_tab == "แยกตาม Jobs":
        job_summary = df.groupby('Jobs').agg({'เงินก่อนภาษี': 'sum', 'เลขที่เอกสาร': 'count'}).reset_index()
        job_summary = job_summary.sort_values('เงินก่อนภาษี', ascending=False)
        st.dataframe(job_summary, use_container_width=True)

    elif st.session_state.active_tab == "พนักงานขาย":
        sales_summary = df.groupby('พนักงานขาย')['รวมทั้งสิ้น'].sum().sort_values(ascending=False).reset_index()
        fig_sales = px.bar(sales_summary.head(10), x='รวมทั้งสิ้น', y='พนักงานขาย', orientation='h')
        st.plotly_chart(fig_sales, use_container_width=True)

    elif st.session_state.active_tab == "รายเดือน":
        monthly = df.groupby(['Month_Num', 'Month_Name'])['รวมทั้งสิ้น'].sum().reset_index()
        fig_month = px.line(monthly, x='Month_Name', y='รวมทั้งสิ้น', markers=True)
        st.plotly_chart(fig_month, use_container_width=True)

    elif st.session_state.active_tab == "ยอดคงค้าง":
        unpaid = df[df['ยอดคงเหลือ'] > 0]
        st.write(f"พบรายการค้างชำระทั้งหมด {len(unpaid)} รายการ")
        st.dataframe(unpaid[['เลขที่เอกสาร', 'Jobs', 'ยอดคงเหลือ', 'สถานะ']], use_container_width=True)

else:
    st.warning("👈 กรุณาอัปโหลดไฟล์เพื่อเริ่มต้นการวิเคราะห์ค่ะ")
