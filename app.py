import streamlit as st

st.set_page_config(
    page_title="Olist Business Dashboard",
    page_icon="📊",
    layout="wide"
)

# ===== Header ======
st.markdown(
    """
    <h1 style="text-align:center;">📊 Olist Business Dashboard</h1>
    <p style="text-align:center; color:gray; font-size:16px;">
        Hệ thống phân tích dữ liệu bán hàng Olist
    </p>
    <br>
    """,
    unsafe_allow_html=True
)

# ===== DASHBOARD =====
col1, col2, col3 = st.columns(3)

# --- Card 1 ---
with col1:
    st.markdown(
        """
        <div style="text-align:center; font-size:80px;">💰</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h4 style='text-align:center;'>Tổng quan doanh thu</h4>", unsafe_allow_html=True)
    if st.button("Xem chi tiết", key="rev"):
        st.switch_page("pages/1_revenue_overview.py")
with col2:
    st.markdown(
        """
        <div style="text-align:center; font-size:80px;">👥</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h4 style='text-align:center;'>Chăm sóc khách hàng </h4>", unsafe_allow_html=True)
    if st.button("Xem chi tiết", key="cus"):
        st.switch_page("pages/2_customer.py")
with col3:
    st.markdown(
        """
        <div style="text-align:center; font-size:80px;">📊</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h4 style='text-align:center;'>Tối ưu hóa </h4>", unsafe_allow_html=True)
    if st.button("Xem chi tiết", key="rfm"):
        st.switch_page("pages/3_revenue_optimization.py")