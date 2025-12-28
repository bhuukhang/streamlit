import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px

st.title("💡 Tối ưu hóa doanh thu")

# =========================
# Load dữ liệu & model
# =========================
@st.cache_data
def load_data():
    category_next_month = pd.read_csv("data/predicted_category_revenue_next_month.csv")
    high_potential_customers = pd.read_csv("data/high_potential_customers.csv")
    revenue_by_state = pd.read_csv("data/predicted_revenue_by_state.csv")
    bundle_values = pd.read_csv("data/rq4_bundle_order_values.csv")
    price_analysis = pd.read_csv("data/price_analysis.csv")
    linear_models = joblib.load("model/linear_models_by_category.pkl")
    scaler = joblib.load("model/scaler.pkl")
    monthly_category_revenue = pd.read_csv("data/monthly_category_revenue.csv")
     # load model (để chứng minh backend ML tồn tại)
    linear_models = joblib.load("model/linear_models_by_category.pkl")
    scaler = joblib.load("model/scaler.pkl")

    return (
        category_next_month,
        high_potential_customers,
        revenue_by_state,
        bundle_values,
        price_analysis,
        monthly_category_revenue,
        linear_models,
        scaler
    )

(
    category_next_month,
    high_potential_customers,
    revenue_by_state,
    bundle_values,
    price_analysis,
    monthly_category_revenue,
    linear_models,
    scaler,
) = load_data()
# =========================
# 1️⃣ Dự báo danh mục bán chạy – What-If
# =========================
st.header("1️⃣ Dự báo danh mục bán chạy tháng tới")

# ---- Input ----
selected_category = st.selectbox(
    "Chọn danh mục sản phẩm",
    category_next_month["product_category_name"].unique()
)

price_change = st.slider(
    "Thay đổi giá bán (%)",
    -50, 50, 0, 5,
    help="Tăng giá có thể làm giảm nhu cầu mua"
)

quantity_change = st.slider(
    "Kỳ vọng thay đổi số lượng bán (%)",
    -50, 50, 0, 5,
    help="Đây là kỳ vọng, không đảm bảo đạt được nếu cầu không đủ"
)

# ---- Base prediction ----
row = category_next_month[
    category_next_month["product_category_name"] == selected_category
].iloc[0]

base_revenue = row["predicted_revenue_next_month"]

# ---- Elasticity (độ nhạy cầu theo giá) ----
# Có thể học từ data sau, hiện dùng giả lập hợp lý
elasticity = -0.6  

price_pct = price_change / 100
qty_pct = quantity_change / 100

# ---- Cầu thực tế bị giới hạn bởi giá ----
real_demand_factor = max(
    0,
    1 + elasticity * price_pct
)

# ---- Số lượng bán thực tế ----
# Không thể vượt cầu thực tế
real_quantity_factor = min(
    1 + qty_pct,
    real_demand_factor
)

# ---- Doanh thu thực tế ----
adjusted_revenue_realistic = (
    base_revenue
    * (1 + price_pct)
    * real_quantity_factor
)

percent_change = (
    (adjusted_revenue_realistic - base_revenue)
    / base_revenue * 100
)

# ---- Output ----
st.markdown(f"- **Doanh thu dự báo gốc:** {base_revenue:,.0f}")
st.markdown(f"- **Doanh thu sau điều chỉnh:** {adjusted_revenue_realistic:,.0f}")
st.markdown(f"- **Thay đổi doanh thu:** {percent_change:.1f}%")

# ---- Decision feedback ----
if price_change > 0 and quantity_change > 0:
    st.warning(
        "⚠ **Mâu thuẫn chiến lược**: Tăng giá nhưng kỳ vọng bán nhiều. "
        "Cầu thực tế bị giới hạn bởi giá."
    )

elif price_change > 0 and percent_change < 0:
    st.error(
        "🔻 **Rủi ro cao**: Tăng giá làm cầu giảm mạnh, doanh thu đi xuống."
    )

elif price_change < 0 and percent_change > 0:
    st.success(
        "✅ **Kịch bản tốt**: Giảm giá kích cầu hiệu quả, doanh thu tăng."
    )

elif percent_change < 0:
    st.warning(
        "⚠ **Kịch bản không tối ưu**: Doanh thu giảm so với dự báo gốc."
    )

else:
    st.success(
        "✅ **Kịch bản khả thi** theo điều kiện thị trường."
    )

# ---- Visual: Thực tế vs Dự báo ----
df_hist = monthly_category_revenue[
    monthly_category_revenue["product_category_name"] == selected_category
].sort_values("time_index")

fig = px.line(
    df_hist,
    x="year_month",
    y="order_value",
    title=f"Xu hướng doanh thu – {selected_category}",
    labels={"order_value": "Doanh thu", "year_month": "Tháng"}
)

fig.add_scatter(
    x=[df_hist["year_month"].max()],
    y=[adjusted_revenue_realistic],
    mode="markers+text",
    name="Dự báo tháng tới",
    text=[f"{adjusted_revenue_realistic:,.0f}"],
    textposition="top center"
)

st.plotly_chart(fig, use_container_width=True)
# ---- Explanation ----
with st.expander("ℹ Giải thích & giả định mô hình"):
    st.markdown("""
    - **Doanh thu dự báo gốc**: Giá trị **ước lượng** từ mô hình học máy
      dựa trên dữ liệu lịch sử, **không phải cam kết doanh thu thực tế**.
      
    - **Elasticity (độ nhạy theo giá)**: Là **giả định mô phỏng** hành vi thị trường
      (tăng giá có thể làm giảm nhu cầu). Giá trị này có thể thay đổi theo từng ngành
      và chưa được khẳng định tuyệt đối.

    - **Số lượng bán thực tế**: Được **giới hạn bởi cầu mô phỏng**, nhằm phản ánh
      thực tế rằng kỳ vọng bán nhiều không đảm bảo đạt được khi điều chỉnh giá.

    - Phần What-if này dùng để **đánh giá kịch bản & rủi ro trước khi ra quyết định**,
      **không thay thế kết quả kinh doanh thực tế**.
    """)
# =========================
# 2️⃣ Khách hàng tiềm năng quay lại
# =========================
st.header("2️⃣ Khách hàng tiềm năng quay lại")

top_customers = (
    high_potential_customers
    .sort_values("repeat_purchase_prob", ascending=False)
    .head(20)
)

st.dataframe(
    top_customers[
        ["customer_unique_id", "repeat_purchase_prob", "marketing_segment"]
    ]
)

top_segment = top_customers['marketing_segment'].value_counts().idxmax()
st.markdown(
    f"🎯 **Segment nên ưu tiên marketing:** `{top_segment}`"
)

# =========================
# 3️⃣ Dự báo doanh thu theo bang
# =========================
st.header("3️⃣ Dự báo doanh thu theo bang")

selected_state = st.selectbox(
    "Chọn bang",
    revenue_by_state['customer_state'].unique()
)

state_revenue = revenue_by_state[
    revenue_by_state['customer_state'] == selected_state
]['predicted_revenue'].iloc[0]

avg_state_revenue = revenue_by_state['predicted_revenue'].mean()

st.markdown(
    f"- **Doanh thu dự kiến tại {selected_state}:** {state_revenue:,.0f}"
)

if state_revenue > 1.2 * avg_state_revenue:
    st.warning("⚠ Nhu cầu cao → rủi ro thiếu hàng.")
elif state_revenue < 0.8 * avg_state_revenue:
    st.info("ℹ Nhu cầu thấp → tránh tồn kho dư.")

# =========================
# 4️⃣ Gợi ý bundle tăng giá trị đơn hàng
# =========================
st.header("4️⃣ Gợi ý bundle bán chạy")

top_bundle = bundle_values.sort_values(
    "mean_with_bundle", ascending=False
).head(10)

st.dataframe(
    top_bundle[
        ["itemset", "mean_with_bundle", "mean_without_bundle"]
    ]
)

best_bundle = top_bundle.iloc[0]
st.markdown(
    f"📦 Bundle hiệu quả nhất: **{best_bundle['itemset']}**"
)

# =========================
# 5️⃣ Phân tích giá
# =========================
st.header("5️⃣ Phân tích nhóm giá")

best_price_band = price_analysis.sort_values(
    "total_revenue", ascending=False
).iloc[0]

st.markdown(
    f"💰 Nhóm giá tối ưu: **{best_price_band['price_band']}** "
    f"(Doanh thu: {best_price_band['total_revenue']:,.0f})"
)

# =========================
# 6️⃣ Tổng hợp insight tự động
# =========================
st.header("📌 Insight rút ra tự động")

top_categories = (
    category_next_month
    .sort_values("predicted_revenue_next_month", ascending=False)
    .head(2)['product_category_name']
    .tolist()
)

top_state = (
    revenue_by_state
    .sort_values("predicted_revenue", ascending=False)
    .iloc[0]['customer_state']
)

st.markdown(f"- 🚀 Danh mục tăng trưởng mạnh: **{', '.join(top_categories)}**")
st.markdown(f"- 📍 Khu vực ưu tiên logistics: **{top_state}**")
st.markdown(f"- 🎯 Nên tập trung marketing vào segment **{top_segment}**")
st.markdown(f"- 📦 Bundle nên triển khai: **{best_bundle['itemset']}**")
st.markdown(f"- 💰 Chiến lược giá nên tập trung vào **{best_price_band['price_band']}**")