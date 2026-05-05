import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. เอกสารประกอบ: ตั้งค่าการแสดงผลหน้าเว็บ ---
st.set_page_config(page_title="Financial AI Analysis", layout="wide")

def main():
    st.title("📊 ระบบวิเคราะห์การเงินธุรกิจผลิตชั้นวาง")
    st.markdown("วิเคราะห์ข้อมูล P&L, สภาพคล่อง และความพร้อม IPO จากไฟล์ Excel")

    # --- 2. เอกสารประกอบ: ฟังก์ชันอัปโหลดไฟล์ ---
    uploaded_file = st.file_uploader("อัปโหลดไฟล์ test.xlsx ของคุณที่นี่", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # อ่านข้อมูลจาก Sheet 'SO 2026'
            df = pd.read_excel(uploaded_file, sheet_name='SO 2026')
            
            # --- 3. เอกสารประกอบ: คำนวณตัวชี้วัดการเงิน (Finance Logic) ---
            total_sales = df['รวมทั้งสิ้น'].sum()
            total_balance = df['ยอดคงเหลือ'].sum()
            collection_rate = ((total_sales - total_balance) / total_sales) * 100 if total_sales > 0 else 0

            # แสดงผล Metric สำคัญ
            m1, m2, m3 = st.columns(3)
            m1.metric("ยอดขายรวม (Revenue)", f"฿{total_sales:,.2f}")
            m2.metric("ยอดค้างชำระ (AR)", f"฿{total_balance:,.2f}", delta_color="inverse")
            m3.metric("อัตราการเก็บเงิน", f"{collection_rate:.2f}%")

            # --- 4. เอกสารประกอบ: สร้างกราฟ Interactive Dashboard ---
            st.subheader("📈 วิเคราะห์ยอดขายรายลูกค้า")
            fig = px.bar(df.groupby('ชื่อลูกค้า')['รวมทั้งสิ้น'].sum().reset_index(), 
                         x='ชื่อลูกค้า', y='รวมทั้งสิ้น', color='รวมทั้งสิ้น',
                         title="รายได้แยกตามรายชื่อลูกค้า (Top Customers)")
            st.plotly_chart(fig, use_container_width=True)

            # --- 5. เอกสารประกอบ: วิเคราะห์ความพร้อม IPO (IPO Readiness) ---
            st.divider()
            st.subheader("🏛️ การประเมินความพร้อมสู่ตลาดหลักทรัพย์ (IPO)")
            ipo_threshold = 50000000  # สมมติเกณฑ์รายได้ 50 ล้านบาท
            progress = min(total_sales / ipo_threshold, 1.0)
            
            st.write(f"เป้าหมายรายได้ขั้นต่ำ: {ipo_threshold:,.2f} บาท")
            st.progress(progress)
            
            if total_sales >= ipo_threshold:
                st.success("✅ ด้านรายได้: ผ่านเกณฑ์เบื้องต้นสำหรับการพิจารณา IPO")
            else:
                st.warning(f"⚠️ ด้านรายได้: ยังขาดอีก {ipo_threshold - total_sales:,.2f} บาท")

        except Exception as e:
            st.error(f"กรุณาตรวจสอบโครงสร้างไฟล์ Excel: {e}")

# รันแอปพลิเคชัน
if __name__ == "__main__":
    main()
