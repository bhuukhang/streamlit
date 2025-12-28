import streamlit as st
import pandas as pd

if st.button("⬅ Quay lại trang chính"):
    st.switch_page("app.py")

st.title("📊 Tổng quan kinh doanh")


# ===== UPLOAD FILE =====
uploaded_file = st.file_uploader(
    "📂 Tải dữ liệu bán hàng (CSV / Excel)", type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.warning("Vui lòng tải file dữ liệu để xem báo cáo")
    st.stop()

# ===== LOAD DATA =====
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# ===== XỬ LÝ TỐI THIỂU =====
required_cols = ["order_id", "customer_id", "price", "order_purchase_timestamp"]
missing_cols = [c for c in required_cols if c not in df.columns]

if missing_cols:
    st.error(f"File thiếu các cột bắt buộc: {missing_cols}")
    st.stop()

# Convert kiểu dữ liệu
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")

# Drop những dòng quan trọng bị thiếu
initial_rows = len(df)
df = df.dropna(subset=["order_id", "customer_id", "price", "order_purchase_timestamp"])
removed_rows = initial_rows - len(df)

if removed_rows > 0:
    st.info(f"ℹ️ Đã loại bỏ {removed_rows} dòng dữ liệu không hợp lệ.")

# ===== KPI =====
total_revenue = df["price"].sum()
total_orders = df["order_id"].nunique()
total_customers = df["customer_unique_id"].nunique()
avg_rating = df["review_score"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Tổng doanh thu", f"{total_revenue:,.0f} BRL")
col2.metric("🧾 Số đơn hàng", total_orders)
col3.metric("👥 Số khách hàng", total_customers)
col4.metric("⭐ Đánh giá TB", f"{avg_rating:.1f}")

st.markdown("---")

# ===== DOANH THU THEO THÁNG =====
st.subheader("📈 Doanh thu theo tháng")
df["month"] = df["order_purchase_timestamp"].dt.to_period("M")
revenue_by_month = df.groupby("month")["price"].sum()
st.line_chart(revenue_by_month)

top_month = revenue_by_month.idxmax()
top_value = revenue_by_month.max()
bottom_month = revenue_by_month.idxmin()
bottom_value = revenue_by_month.min()
st.info(f"📈 Doanh thu cao nhất: {top_value:,.0f} BRL vào {top_month}")
st.info(f"📉 Doanh thu thấp nhất: {bottom_value:,.0f} BRL vào {bottom_month}")

# ===== TOP DANH MỤC SẢN PHẨM =====
st.subheader("🏆 Top danh mục bán chạy")
top_categories = df.groupby("product_category_name")["price"].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_categories)
category_revenue_pct = top_categories / df["price"].sum() * 100
st.info(f"🔎 Top 3 danh mục chiếm {category_revenue_pct.head(3).sum():.1f}% tổng doanh thu: {', '.join(top_categories.index[:3])}")

# ===== TOP SẢN PHẨM =====
st.subheader("🏆 Top sản phẩm bán chạy")
top_products = (
    df.groupby("product_name_lenght")["price"]  # dùng cột tên sản phẩm nếu có
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(top_products)

# Tính % doanh thu từng danh mục
category_revenue = df.groupby("product_category_name")["price"].sum()
category_revenue_pct = category_revenue / category_revenue.sum() * 100

top_cat = category_revenue_pct.sort_values(ascending=False).head(3)
st.info(f"🔎 Top 3 danh mục chiếm {top_cat.sum():.1f}% tổng doanh thu: {', '.join(top_cat.index)}")
# ===== DOANH THU THEO BANG =====
st.subheader("🗺️ Doanh thu theo bang")
revenue_by_state = df.groupby("customer_state")["price"].sum().sort_values(ascending=False)
st.bar_chart(revenue_by_state)
top_state = revenue_by_state.idxmax()
bottom_state = revenue_by_state.idxmin()
st.info(f"🗺️ Bang có doanh thu cao nhất: {top_state} ({revenue_by_state.max():,.0f} BRL)")
st.info(f"🗺️ Bang có doanh thu thấp nhất: {bottom_state} ({revenue_by_state.min():,.0f} BRL)")
