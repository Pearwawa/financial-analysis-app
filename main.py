import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ตั้งค่าหน้าเว็บให้กว้างและสวยงาม
st.set_page_config(layout="wide", page_title="Sales Order Dashboard 2026")

# --- ส่วนที่ 1: หัวข้อแอป (Header) ---
st.title("Sales Order Dashboard — ปี 2026")
st.write("ข้อมูลจากไฟล์ SO_ป__2026 | รายการทั้งหมด 11,899 รายการ | ม.ค. - เม.ย. 2569")

# --- ส่วนที่ 2: เมนูหลัก (Navigation Tabs) ---
tabs = st.tabs(["ภาพรวม", "สถานะ SO", "แยกตาม Jobs", "พนักงานขาย", "รายเดือน", "ยอดคงค้าง"])

with tabs[5]:  # หน้า "ยอดคงค้าง"
    # --- ส่วนที่ 3: KPI Cards (4 ช่อง) ---
    c1, c2, c3, c4 = st.columns(4)
    
    # ฟังก์ชันช่วยสร้าง Card (จำลองข้อมูลตามรูป)
    c1.metric("ยอดคงค้างรวม", "฿55.0M", "1,592 รายการ", delta_color="off")
    c2.metric("ยอดคงค้าง 7-11", "฿36.3M", "65.9% ของทั้งหมด", delta_color="off")
    c3.metric("ยอดคงค้างรายอื่นๆ", "฿18.7M", "34.1% ของทั้งหมด", delta_color="off")
    c4.metric("ยังไม่ออก Invoice", "฿54.4M", "1,582 รายการ รอดำเนินการ")

    st.markdown("---")

    # --- ส่วนที่ 4: กราฟ Donut และ Bar Chart (จัดวางคู่กัน) ---
    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        st.subheader("ยอดคงค้างแยกตาม Jobs")
        # สร้างกราฟ Donut ด้วย Plotly Go เพื่อความเป๊ะของสี
        labels = ['7-11', 'Suratthani', '7-Project', 'Chains', 'Khonkaen', 'General', 'Other']
        values = [17.1, 6.8, 6.4, 8.1, 5.8, 4.0, 5.0]
        colors = ['#10A37F', '#D18227', '#4A90E2', '#A37F10', '#9B51E0', '#7F7F7F', '#A5D6A7']
        
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=colors)])
        fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_graph2:
        st.subheader("สถานะที่ยังรอดำเนินการ")
        # กราฟแท่งแสดงยอดเงิน
        bar_data = pd.DataFrame({
            'สถานะ': ['ยังไม่ออก INV', 'เปิด INV ยังไม่วางบิล'],
            'มูลค่า (ล้าน)': [54.4, 105.0]
        })
        fig_bar = px.bar(bar_data, x='สถานะ', y='มูลค่า (ล้าน)', color='สถานะ',
                         color_discrete_map={'ยังไม่ออก INV': '#D18227', 'เปิด INV ยังไม่วางบิล': '#9B51E0'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- ส่วนที่ 5: ตารางสรุปด้านล่าง ---
    st.subheader("ยอดคงค้างแยกตาม Jobs (จากข้อมูล Summary)")
    
    # สร้างตารางจำลอง (คุณสามารถเปลี่ยนเป็นข้อมูลจาก df จริงได้)
    table_data = {
        "Jobs": ["7-Eleven", "Suratthani", "7-Project", "Chains", "Khonkaen"],
        "ยอดคงค้าง (฿)": ["17,139,958", "6,858,329", "6,420,422", "8,148,601", "5,839,203"],
        "สัดส่วน": [0.8, 0.4, 0.35, 0.45, 0.3],
        "สถานะ": ["ค้างสูง", "ติดตาม", "ติดตาม", "ติดตาม", "ปกติ"]
    }
    df_table = pd.DataFrame(table_data)
    
    # แสดงตารางด้วย Column Configuration (มีแถบ Progress)
    st.data_editor(
        df_table,
        column_config={
            "สัดส่วน": st.column_config.ProgressColumn(
                "สัดส่วน", help="เปอร์เซ็นต์ยอดคงค้างเทียบกับยอดขาย",
                format="%.2f", min_value=0, max_value=1
            ),
        },
        hide_index=True,
        use_container_width=True
    )
