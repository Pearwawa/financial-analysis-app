import streamlit as st
import pandas as pd
import plotly.express as px

# --- [1. Configuration & Styling] ---
st.set_page_config(layout="wide", page_title="ระบบวิเคราะห์ข้อมูลการขายและลูกหนี้")

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E1E1E; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #666; margin-bottom: 20px; }
    .kpi-card { background-color: #fdfdfb; padding: 20px; border-radius: 12px; border: 1px solid #eeeeee; }
    </style>
""", unsafe_allow_html=True)

# --- [2. Data Processing] ---
def load_data(file):
    df = pd.read_excel(file)
    df.columns = [c.strip() for c in df.columns] # ลบช่องว่างชื่อคอลัมน์
    # แปลงคอลัมน์ตัวเลข
    num_cols = ['เงินก่อนภาษี', 'รวมทั้งสิ้น', 'ยอดคงเหลือ', 'ยอดเงินมัดจำ']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    # แปลงวันที่
    if 'วันที่ออกเอกสาร' in df.columns:
        df['วันที่ออกเอกสาร'] = pd.to_datetime(df['วันที่ออกเอกสาร'])
        df['เดือน'] = df['วันที่ออกเอกสาร'].dt.strftime('%b') # สร้างคอลัมน์เดือน
    return df

# --- [3. Main UI] ---
st.markdown('<div class="main-title">ระบบวิเคราะห์ข้อมูลการขายและลูกหนี้</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Sales Order & AR Dashboard — ปี 2026</div>', unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("โยนไฟล์ Excel ที่นี่ค่ะ", type=['xlsx'])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # ระบบ Navigation ปุ่มกด
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "ภาพรวม"

    menu = ["ภาพรวม", "สถานะ SO", "แยกตาม Jobs", "พนักงานขาย", "รายเดือน", "ยอดคงค้าง"]
    cols = st.columns(len(menu))
    for i, item in enumerate(menu):
        btn_type = "primary" if st.session_state.active_page == item else "secondary"
        if cols[i].button(item, use_container_width=True, type=btn_type):
            st.session_state.active_page = item
            st.rerun()

    st.markdown("---")

    # --- [4. Display Logic ตามปุ่มที่กด] ---
    
    if st.session_state.active_page == "ภาพรวม":
        c1, c2 = st.columns(2)
        with c1:
            total_vat = df['เงินก่อนภาษี'].sum()
            st.metric("มูลค่ารวมก่อน VAT", f"฿{total_vat/1e6:.1f}M", f"{len(df):,}")
        with c2:
            paid_df = df[df['สถานะ'] == 'ชำระเงินครบแล้ว']
            st.metric("ชำระเงินครบแล้ว", f"฿{paid_df['รวมทั้งสิ้น'].sum()/1e6:.1f}M", f"{len(paid_df):,}")
        
        # กราฟ Donut สัดส่วนสถานะ
        fig = px.pie(df, values='รวมทั้งสิ้น', names='สถานะ', hole=0.5, 
                     title="สัดส่วนมูลค่าแยกตามสถานะ",
                     color_discrete_sequence=['#10A37F', '#4A90E2', '#9B51E0', '#D18227'])
        st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.active_page == "แยกตาม Jobs":
        st.subheader("📊 วิเคราะห์มูลค่าแยกตาม Jobs")
        job_data = df.groupby('Jobs')['รวมทั้งสิ้น'].sum().reset_index().sort_values('รวมทั้งสิ้น', ascending=False)
        fig_job = px.bar(job_data, x='รวมทั้งสิ้น', y='Jobs', orientation='h',
                         title="Top Jobs by Value", color_discrete_sequence=['#10A37F'])
        st.plotly_chart(fig_job, use_container_width=True)
        st.dataframe(job_data, use_container_width=True)

    elif st.session_state.active_page == "พนักงานขาย":
        st.subheader("👤 ผลงานพนักงานขาย")
        sales_data = df.groupby('ชื่อพนักงานขาย')['รวมทั้งสิ้น'].sum().reset_index().sort_values('รวมทั้งสิ้น', ascending=False)
        fig_sales = px.bar(sales_data, x='ชื่อพนักงานขาย', y='รวมทั้งสิ้น', color='ชื่อพนักงานขาย')
        st.plotly_chart(fig_sales, use_container_width=True)

    elif st.session_state.active_page == "รายเดือน":
        st.subheader("📅 ยอดขายรายเดือน")
        if 'เดือน' in df.columns:
            monthly = df.groupby('เดือน')['รวมทั้งสิ้น'].sum().reset_index()
            fig_monthly = px.line(monthly, x='เดือน', y='รวมทั้งสิ้น', markers=True)
            st.plotly_chart(fig_monthly, use_container_width=True)

    elif st.session_state.active_page == "ยอดคงค้าง":
        st.subheader("💸 วิเคราะห์ยอดลูกหนี้คงเหลือ")
        ar_total = df['ยอดคงเหลือ'].sum()
        st.warning(f"ยอดลูกหนี้คงเหลือรวมทั้งหมด: ฿{ar_total:,.2f}")
        st.dataframe(df[df['ยอดคงเหลือ'] > 0][['ชื่อลูกค้า', 'ยอดคงเหลือ', 'สถานะ', 'RV Date']])

else:
    st.info("👈 กรุณาอัปโหลดไฟล์ Excel เพื่อเริ่มต้นระบบวิเคราะห์ค่ะ")
