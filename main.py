import streamlit as st
import pandas as pd
import plotly.express as px

# 1. การตั้งค่าหน้าจอและหัวข้อ
st.set_page_config(page_title="Financial AI Dashboard", layout="wide")
st.title("📊 ระบบวิเคราะห์การเงินและประเมินความพร้อม IPO")
st.markdown("---")

# 2. ฟังก์ชันโหลดข้อมูล
def load_data(file):
    df = pd.read_excel(file, sheet_name='SO 2026')
    df['วันที่ออกเอกสาร'] = pd.to_datetime(df['วันที่ออกเอกสาร'])
    return df

# จำลองการอัปโหลดไฟล์ (ในที่นี้คือไฟล์ test.xlsx ที่คุณให้มา)
try:
    df = load_data('test.xlsx')
    
    # 3. ส่วนแสดงผลสรุป (Top Metrics)
    col1, col2, col3, col4 = st.columns(4)
    total_sales = df['รวมทั้งสิ้น'].sum()
    total_balance = df['ยอดคงเหลือ'].sum()
    total_customers = df['ชื่อลูกค้า'].nunique()
    
    col1.metric("ยอดขายรวม (Total Sales)", f"{total_sales:,.2f} บาท")
    col2.metric("ยอดคงค้าง (Outstanding)", f"{total_balance:,.2f} บาท", delta_color="inverse")
    col3.metric("จำนวนลูกค้า", f"{total_customers} ราย")
    col4.metric("เป้าหมาย IPO (จำลอง)", "65%", delta="5%")

    # 4. Interactive Dashboard
    st.subheader("📈 การวิเคราะห์ข้อมูลรายได้และยอดค้างชำระ")
    tab1, tab2 = st.tabs(["ยอดขายตามลูกค้า", "แนวโน้มรายเดือน"])
    
    with tab1:
        # กราฟแท่งแสดงยอดขายตามชื่อลูกค้า
        fig_cust = px.bar(df.groupby('ชื่อลูกค้า')['รวมทั้งสิ้น'].sum().reset_index(), 
                          x='ชื่อลูกค้า', y='รวมทั้งสิ้น', title="ยอดขายแยกตามรายชื่อลูกค้า")
        st.plotly_chart(fig_cust, use_container_width=True)
        
    with tab2:
        # กราฟเส้นแสดงแนวโน้มรายได้
        df_monthly = df.resample('M', on='วันที่ออกเอกสาร')['รวมทั้งสิ้น'].sum().reset_index()
        fig_trend = px.line(df_monthly, x='วันที่ออกเอกสาร', y='รวมทั้งสิ้น', title="แนวโน้มรายได้รายเดือน")
        st.plotly_chart(fig_trend, use_container_width=True)

    # 5. ส่วนวิเคราะห์ความพร้อม IPO (IPO Readiness)
    st.sidebar.header("📑 IPO Readiness Checklist")
    ipo_sales_threshold = 300000000  # สมมติเกณฑ์ยอดขาย 300 ล้าน
    is_sales_ok = total_sales > ipo_sales_threshold
    
    st.sidebar.write(f"ยอดขายถึงเกณฑ์: {'✅' if is_sales_ok else '❌'}")
    st.sidebar.progress(min(int((total_sales/ipo_sales_threshold)*100), 100))

    # 6. AI Analysis (Chat Interface)
    st.markdown("---")
    st.subheader("🤖 สอบถาม AI เกี่ยวกับวิเคราะห์ทางการเงิน")
    user_question = st.text_input("ตัวอย่าง: สรุปสถานะลูกหนี้ที่มียอดค้างชำระสูงที่สุดให้หน่อย")
    
    if user_question:
        # ส่วนนี้ในอนาคตจะเชื่อมต่อกับ OpenAI API
        st.info(f"AI กำลังวิเคราะห์ข้อมูลจากไฟล์ของคุณเพื่อตอบคำถาม: '{user_question}'")
        # ตัวอย่างการตอบแบบ Logic เบื้องต้น
        top_debtor = df.sort_values(by='ยอดคงเหลือ', ascending=False).iloc[0]
        st.write(f"**คำแนะนำเบื้องต้น:** จากข้อมูลพบว่า {top_debtor['ชื่อลูกค้า']} มียอดค้างสูงสุดที่ {top_debtor['ยอดคงเหลือ']:,.2f} บาท")

except Exception as e:
    st.error(f"กรุณาตรวจสอบไฟล์ข้อมูลของคุณ: {e}")
