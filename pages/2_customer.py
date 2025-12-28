import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import joblib
import numpy as np

if st.button("⬅ Quay lại trang chính"):
    st.switch_page("app.py")

st.title("👥 Chăm sóc khách hàng")

# Load dữ liệu clusters
df = pd.read_csv("data/clusters.csv")

# Tạo cột Segment_Name trực tiếp
cluster_names = {
    0: 'Khách hàng tiềm năng',
    1: 'Khách hàng rời bỏ',
    2: 'Khách hàng mới',
    3: 'Khách hàng trung thành'
}
df['Segment_Name'] = df['Cluster'].map(cluster_names)

# ================= KPI =================
c1, c2, c3 = st.columns(3)

c1.metric("Tổng khách hàng", f"{df.shape[0]:,}")
c2.metric("Số phân khúc", df["Segment_Name"].nunique())
# Khách VIP ở đây mình tạm lấy nhóm "Khách hàng trung thành"
c3.metric("Khách hàng trung thành", (df["Segment_Name"] == "Khách hàng trung thành").sum())

st.divider()

segment_counts = df['Segment_Name'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Số lượng']
# ================= BIỂU ĐỒ =================
col1, col2 = st.columns(2)

with col1:
    fig_count = px.pie(
        segment_counts, 
        names="Segment",
        values="Số lượng",
        title="Tỷ lệ khách hàng theo phân khúc",
        hole=0.4,
        color="Segment",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_count, use_container_width=True)

with col2:
    seg_value = df.groupby("Segment_Name", observed=True)["Monetary"].mean().reset_index()
    fig_money = px.bar(
        seg_value,
        x="Segment_Name",
        y="Monetary",
        title="Chi tiêu trung bình theo phân khúc",
        color="Segment_Name",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_money, use_container_width=True)

st.divider()

# ===== Thống kê số lượng khách theo phân khúc =====
segment_counts = df['Segment_Name'].value_counts().reset_index()
segment_counts.columns = ['Phân khúc', 'Số lượng khách']

st.markdown("### Số lượng khách hàng theo phân khúc")
fig, ax = plt.subplots(figsize=(8,5))
sns.barplot(
    data=segment_counts,
    x='Phân khúc',
    y='Số lượng khách',
    palette='Accent',
    ax=ax
)
ax.set_xlabel('')
ax.set_ylabel('Số lượng khách')
for p in ax.patches:
    ax.text(p.get_x() + p.get_width()/2, p.get_height(), int(p.get_height()),
            ha='center', va='bottom')
st.pyplot(fig)

# ===== Snake plot so sánh RFM giữa các nhóm =====
rfm_scaled_plot = df[['Recency','Frequency','Monetary']].copy()
# chuẩn hóa lại dữ liệu để snake plot trực quan hơn
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
rfm_scaled_plot[['Recency','Frequency','Monetary']] = scaler.fit_transform(rfm_scaled_plot)

rfm_scaled_plot['Segment_Name'] = df['Segment_Name']

df_melt = pd.melt(rfm_scaled_plot,
                  id_vars=['Segment_Name'],
                  value_vars=['Recency','Frequency','Monetary'],
                  var_name='Attribute',
                  value_name='Value')

st.markdown("### So sánh hành vi RFM giữa các nhóm khách hàng")
fig2, ax2 = plt.subplots(figsize=(12,6))
sns.lineplot(x="Attribute", y="Value", hue="Segment_Name", data=df_melt,
             palette="bright", marker="o", linewidth=2, ax=ax2)
ax2.axhline(0, color='black', linestyle='--', linewidth=0.8)
ax2.set_ylabel('Giá trị chuẩn hóa')
ax2.set_xlabel('Chỉ số RFM')
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(title='Phân khúc khách hàng', loc='upper left', bbox_to_anchor=(1,1))
st.pyplot(fig2)

# ===== Biểu đồ 3D RFM =====
st.markdown("### Biểu đồ phân khúc khách hàng 3D")
fig3 = px.scatter_3d(
    df,
    x='Recency',
    y='Frequency',
    z='Monetary',
    color='Segment_Name',
    opacity=0.8,
    labels={'Recency':'Recency','Frequency':'Frequency','Monetary':'Monetary'}
)
fig3.update_traces(marker=dict(size=3))
fig3.update_layout(width=900, height=650)
st.plotly_chart(fig3)

# ================= Load model & imputer =================
best_rf_balanced = joblib.load("best_rf_model_balanced.pkl")
imputer = joblib.load("imputer_master.joblib")

# ================= Tiêu đề =================
st.title("📊 Dự đoán mức độ hài lòng khách hàng")

# ================= Nhập dữ liệu =================
price = st.number_input("Giá sản phẩm", min_value=0.0, step=1.0)
freight_value = st.number_input("Phí vận chuyển", min_value=0.0, step=1.0)
delivery_days = st.number_input("Số ngày giao hàng", min_value=0, step=1)
is_late = st.selectbox("Giao trễ?", [0, 1])
product_weight_g = st.number_input("Khối lượng (gram)", min_value=0.0, step=1.0)
product_length_cm = st.number_input("Chiều dài (cm)", min_value=0.0, step=1.0)
product_width_cm = st.number_input("Chiều rộng (cm)", min_value=0.0, step=1.0)
product_height_cm = st.number_input("Chiều cao (cm)", min_value=0.0, step=1.0)

# ================= Tính thể tích =================
product_volume_cm3 = product_length_cm * product_width_cm * product_height_cm
st.write(f"Thể tích sản phẩm (cm³): {product_volume_cm3:.2f}")

# ================= Nút dự đoán =================
if st.button("Dự đoán"):
    # Validate
    if product_length_cm < product_width_cm:
        st.error("Chiều dài sản phẩm phải lớn hơn chiều rộng!")
    else:
        # Tạo dataframe
        df = pd.DataFrame([{
            'price': price,
            'freight_value': freight_value,
            'delivery_days': delivery_days,
            'is_late': is_late,
            'product_weight_g': product_weight_g,
            'product_volume_cm3': product_length_cm * product_width_cm * product_height_cm
        }])
        
        df_imp = pd.DataFrame(imputer.transform(df), columns=df.columns)
        cls = best_rf_balanced.predict(df_imp)[0]
        prob = best_rf_balanced.predict_proba(df_imp)[0][1]
        
        result = "Hài lòng" if cls == 1 else "Không hài lòng"
        st.success(f"💡 Dự đoán: {result} (Xác suất: {prob:.2f})")
