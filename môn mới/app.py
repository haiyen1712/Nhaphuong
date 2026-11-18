"""
HỆ THỐNG AI AGENT XỬ LÝ CƠ HỘI BÁN HÀNG B2B - TRƯỜNG GIANG
Giao diện Chuẩn Hóa Theo Mẫu Stepper 5 Chặng & Quy Trình 8 Bước
Chặng 1: Nhập dữ liệu -> Chặng 2: Làm sạch & Đối chiếu -> Chặng 3: Xử lý AI Agent -> Chặng 4: Xác nhận kết quả -> Chặng 5: Báo cáo & Dashboard
"""

import io
import os
import datetime
import pandas as pd
import streamlit as st
import altair as alt

from config import (
    PRODUCT_CATALOG,
    DISCOUNT_TIERS,
    MANAGER_MAX_DISCOUNT_PCT,
    SALES_REPRESENTATIVES,
    SALES_MANAGER
)
from tools import format_currency_vnd, generate_html_report
import streamlit.components.v1 as components
from agent import SalesOpportunityAgent
from data_loader import (
    load_google_sheet,
    load_from_file,
    parse_unstructured_text,
    create_sample_dataset,
    dataframe_to_request_list
)

# 1. CẤU HÌNH TRANG STREAMLIT
st.set_page_config(
    page_title="Trường Giang — Xử Lý Cơ Hội Bán Hàng B2B",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. TOÀN BỘ CSS TÔNG HỒNG ROSE BLOSSOM LUXURY & DECORATIONS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #fff5f7;
  --bg-card: rgba(255, 255, 255, 0.94);
  --bg-hover: #fff1f2;
  --bg-muted: #fdf2f8;
  --border: #fbcfe8;
  --border-light: #fce7f3;
  --border-strong: #f9a8d4;
  --accent: #ec4899;
  --accent-dark: #db2777;
  --accent-deep: #be185d;
  --accent-light: #fce7f3;
  --accent-bg: rgba(236, 72, 153, 0.08);
  --gradient: linear-gradient(135deg, #ec4899 0%, #f43f5e 55%, #a855f7 100%);
  --gradient-hero: linear-gradient(135deg, #831843 0%, #be185d 45%, #ec4899 100%);
  --green: #16a34a;
  --blue: #db2777;
  --blue-light: #fce7f3;
  --orange: #e11d48;
  --orange-light: #ffe4e6;
  --purple: #9333ea;
  --purple-light: #f3e8ff;
  --red: #dc2626;
  --red-light: #fee2e2;
  --amber: #b45309;
  --amber-light: #fef3c7;
  --t1: #1e1b2e;
  --t2: #4a3b47;
  --t3: #7e6577;
  --t4: #a88fa1;
  --r: 16px;
  --r-sm: 10px;
  --shadow: 0 4px 20px rgba(236, 72, 153, 0.08), 0 1px 4px rgba(190, 24, 93, 0.04);
  --shadow-md: 0 10px 30px rgba(219, 39, 119, 0.16);
  --tr: 0.25s ease;
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

.stApp {
    background-color: var(--bg) !important;
    background-image:
        radial-gradient(at 10% 10%, rgba(244,114,182,0.22) 0px, transparent 50%),
        radial-gradient(at 90% 15%, rgba(192,132,252,0.18) 0px, transparent 50%),
        radial-gradient(#fbcfe8 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 24px 24px !important;
    color: var(--t1) !important;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1220px !important;
}

/* Nút Primary của Streamlit sang Tông Hồng */
button[kind="primary"] {
    background: var(--gradient) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 700 !important;
    border-radius: var(--r-sm) !important;
    box-shadow: 0 4px 14px rgba(236, 72, 153, 0.28) !important;
    transition: all 0.25s !important;
}
button[kind="primary"]:hover {
    filter: brightness(1.06) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(236, 72, 153, 0.38) !important;
}

/* TOPBAR */
.topbar {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(12px);
    border: 1.5px solid var(--border);
    padding: 0 28px;
    height: 68px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: var(--r);
    box-shadow: var(--shadow);
    margin-bottom: 18px;
}
.tb-left { display: flex; align-items: center; gap: 14px; }
.logo {
    width: 42px;
    height: 42px;
    background: var(--gradient);
    border-radius: 12px;
    display: grid;
    place-items: center;
    color: #fff;
    font-weight: 800;
    font-size: 15px;
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.35);
}
.topbar h1 { font-size: 1.12rem; font-weight: 800; color: var(--accent-deep); margin: 0; }
.tag {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 20px;
    background: var(--accent-light);
    color: var(--accent-deep);
    border: 1px solid var(--border-strong);
}
.tb-right { display: flex; align-items: center; gap: 14px; }
.tb-right .info { text-align: right; }
.tb-right .name { font-weight: 700; font-size: 0.9rem; color: var(--accent-deep); }
.tb-right .role { font-size: 0.76rem; color: var(--t3); }
.avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: var(--gradient);
    display: grid;
    place-items: center;
    color: #fff;
    font-weight: 800;
    font-size: 13px;
    border: 2px solid #fff;
    box-shadow: 0 0 0 2px var(--accent);
}

/* HERO BANNER */
.hero-banner {
    background: var(--gradient-hero);
    color: #fff;
    border-radius: var(--r);
    padding: 22px 26px;
    margin-bottom: 18px;
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: '🌸 ✨ 💼';
    position: absolute;
    right: 22px;
    top: 14px;
    font-size: 1.1rem;
    opacity: 0.55;
    letter-spacing: 4px;
}
.hero-banner h2 { font-size: 1.3rem; font-weight: 800; margin: 0 0 4px 0; color: #fff; }
.hero-banner p { font-size: 0.86rem; color: #fce7f3; margin: 0 0 14px 0; max-width: 780px; }
.hero-pills { display: flex; gap: 10px; flex-wrap: wrap; }
.hero-pill {
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    padding: 6px 12px;
    font-size: 0.76rem;
    font-weight: 700;
    color: #fff;
}

/* 8-STEP FLOW STRIP */
.flow-strip {
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: var(--r);
    padding: 14px 18px;
    margin-bottom: 18px;
    box-shadow: var(--shadow);
}
.flow-title { font-size: 0.75rem; font-weight: 800; color: var(--accent-deep); text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 10px; }
.flow-nodes { display: grid; grid-template-columns: repeat(8, 1fr); gap: 8px; }
.f-node {
    background: var(--bg-muted);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 8px 5px;
    text-align: center;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--t2);
}
.f-node.cur { background: var(--gradient); color: #fff; border-color: transparent; box-shadow: 0 4px 12px rgba(236,72,153,0.3); }
.f-node.passed { background: #dcfce7; border-color: #86efac; color: #15803d; }

/* STEPPER */
.stepper {
    background: var(--bg-card);
    border-radius: var(--r);
    box-shadow: var(--shadow);
    border: 1.5px solid var(--border);
    padding: 18px 24px;
    margin-bottom: 22px;
    display: flex;
}
.st-step {
    flex: 1;
    position: relative;
    text-align: center;
    user-select: none;
}
.st-step::after {
    content: '';
    position: absolute;
    top: 17px;
    left: calc(50% + 22px);
    right: calc(-50% + 22px);
    height: 3px;
    background: var(--border-light);
    z-index: 0;
}
.st-step:last-child::after { display: none; }
.st-step.done::after { background: var(--gradient); }

.st-dot {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: inline-grid;
    place-items: center;
    font-weight: 800;
    font-size: 0.85rem;
    position: relative;
    z-index: 1;
    background: var(--bg-muted);
    color: var(--t4);
    border: 2px solid var(--border);
    transition: all 0.3s;
}
.st-step.active .st-dot {
    background: var(--accent-light);
    color: var(--accent-deep);
    border-color: var(--accent);
    box-shadow: 0 0 0 6px rgba(236, 72, 153, 0.18);
}
.st-step.done .st-dot {
    background: var(--gradient);
    color: #fff;
    border-color: transparent;
}
.st-label {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--t2);
    margin-top: 8px;
}
.st-step.active .st-label { color: var(--accent-deep); }
.st-step.pending .st-label { color: var(--t4); }
.st-sub { font-size: 0.7rem; color: var(--t3); margin-top: 2px; }

/* PANEL & HEADERS */
.panel-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}
.panel-head h2 { font-size: 1.28rem; font-weight: 800; color: var(--t1); margin: 0; }
.panel-head p { color: var(--t3); font-size: 0.88rem; margin-top: 4px; max-width: 740px; margin-bottom: 0; }
.chip {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
    background: var(--accent-light);
    color: var(--accent-deep);
    border: 1px solid var(--border-strong);
    margin-bottom: 6px;
    letter-spacing: 0.4px;
}

/* CARDS */
.custom-card {
    background: var(--bg-card);
    border-radius: var(--r);
    box-shadow: var(--shadow);
    border: 1.5px solid var(--border);
    padding: 20px 22px;
    margin-bottom: 16px;
}
.custom-card h3 { font-size: 0.98rem; font-weight: 800; margin-bottom: 10px; color: var(--accent-deep); }

/* KPI GRID */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 18px;
}
.kpi {
    background: var(--bg-card);
    border-radius: var(--r);
    padding: 16px 18px;
    box-shadow: var(--shadow);
    border: 1.5px solid var(--border);
    position: relative;
    overflow: hidden;
}
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--gradient); }
.kpi-label { font-size: 0.74rem; color: var(--t3); margin-bottom: 5px; font-weight: 700; text-transform: uppercase; }
.kpi-val { font-size: 1.45rem; font-weight: 800; color: var(--t1); }
.kpi-sub { font-size: 0.75rem; color: var(--t3); margin-top: 4px; }

/* UPLOAD BOX */
.upload-box {
    background: var(--bg-card);
    border: 2.5px dashed var(--border-strong);
    border-radius: var(--r);
    padding: 36px 28px;
    text-align: center;
    margin-bottom: 18px;
    box-shadow: var(--shadow);
}
.upload-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--accent-light);
    color: var(--accent-deep);
    border: 2px solid var(--border-strong);
    display: inline-grid;
    place-items: center;
    font-size: 26px;
    margin-bottom: 12px;
}

/* ALERTS */
.alert-custom {
    border-radius: var(--r);
    padding: 14px 18px;
    margin-bottom: 16px;
    font-size: 0.88rem;
    line-height: 1.55;
}
.alert-ok { background: #f0fdf4; color: #14532d; border: 1.5px solid #bbf7d0; }
.alert-err { background: var(--red-light); color: #991b1b; border: 1.5px solid #fecaca; }
.alert-warn { background: var(--amber-light); color: var(--amber); border: 1.5px solid #fde68a; }
.alert-info { background: var(--accent-soft); color: var(--accent-deep); border: 1.5px solid var(--border-strong); }
</style>
""", unsafe_allow_html=True)

# 3. QUẢN LÝ TRẠNG THÁI (SESSION STATE)
if "stage" not in st.session_state:
    st.session_state.stage = 1
if "batch_result" not in st.session_state:
    st.session_state.batch_result = None
if "selected_opp_id" not in st.session_state:
    st.session_state.selected_opp_id = "REQ-001"
if "approval_decisions" not in st.session_state:
    st.session_state.approval_decisions = {}
if "clean_options" not in st.session_state:
    st.session_state.clean_options = {
        "norm_code": True,
        "clean_currency": True,
        "check_qty": True,
        "multi_item": True,
        "flag_missing": True
    }
if "confirmed_by_user" not in st.session_state:
    st.session_state.confirmed_by_user = False

agent = SalesOpportunityAgent()

# Nạp sẵn 10 mẫu chuẩn nếu chưa có
if st.session_state.batch_result is None:
    df_sample = create_sample_dataset()
    requests_to_process = dataframe_to_request_list(df_sample)
    st.session_state.batch_result = agent.process_batch(requests_to_process)

batch_res = st.session_state.batch_result
counts = batch_res["counts"]
dossiers = batch_res["dossiers"]

# 4. TOPBAR CHUẨN TÔNG HỒNG ROSE LUXURY
st.markdown("""
<div class="topbar">
    <div class="tb-left">
        <div class="logo">TG</div>
        <div>
            <h1>Trường Giang — Xử Lý Cơ Hội Bán Hàng B2B</h1>
        </div>
        <span class="tag">🌸 Pink Luxury Edition</span>
    </div>
    <div class="tb-right">
        <div class="info">
            <div class="name">Trường Giang</div>
            <div class="role">Trưởng phòng Kinh doanh</div>
        </div>
        <div class="avatar">TG</div>
    </div>
</div>
""", unsafe_allow_html=True)

# HERO BANNER TRANG TRÍ & TỔNG QUAN HỆ THỐNG
st.markdown("""
<div class="hero-banner">
    <h2>🌸 AI Data Analytics Agent — Tự Động Hóa Quy Trình Bán Hàng B2B</h2>
    <p style="margin-bottom: 0;">Tiếp nhận dữ liệu đa kênh, kiểm tra &amp; làm sạch thông minh (Profiling &amp; Cleaning), thẩm định tồn kho &amp; chính sách giá với chốt chặn Human-in-the-loop, xuất Báo cáo HTML trực tiếp.</p>
</div>
""", unsafe_allow_html=True)

# 5. STEPPER 5 CHẶNG & THANH SƠ ĐỒ 8 BƯỚC
st_num = st.session_state.stage

def get_cls(idx):
    if idx < st_num:
        return "done"
    elif idx == st_num:
        return "active"
    return "pending"

def get_flow_cls(step_no):
    stage_map = {1: [1], 2: [2, 3, 4], 3: [6], 4: [5], 5: [7, 8]}
    if step_no in stage_map.get(st_num, []):
        return "cur"
    for s_idx, steps in stage_map.items():
        if s_idx < st_num and step_no in steps:
            return "passed"
    return ""

st.markdown(f"""
<div class="flow-strip">
    <div class="flow-title">🧭 Bản đồ Quy trình 8 Bước chuẩn — Trường Giang (Đang ở Chặng {st_num} / 5)</div>
    <div class="flow-nodes">
        <div class="f-node {get_flow_cls(1)}">📥<br>1. Tải dữ liệu</div>
        <div class="f-node {get_flow_cls(2)}">🔍<br>2. Data Profiling</div>
        <div class="f-node {get_flow_cls(3)}">🧹<br>3. Làm sạch</div>
        <div class="f-node {get_flow_cls(4)}">📊<br>4. So sánh KQ</div>
        <div class="f-node {get_flow_cls(5)}">💎<br>5. Xác nhận?</div>
        <div class="f-node {get_flow_cls(6)}">⚙️<br>6. Phân tích AI</div>
        <div class="f-node {get_flow_cls(7)}">📈<br>7. Tổng hợp</div>
        <div class="f-node {get_flow_cls(8)}">🌐<br>8. Xuất HTML</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<nav class="stepper">
    <div class="st-step {get_cls(1)}">
        <div class="st-dot">{'✓' if st_num > 1 else '1'}</div>
        <div class="st-label">Nhập dữ liệu</div>
        <div class="st-sub">File CSV/Excel &amp; Link Sheet</div>
    </div>
    <div class="st-step {get_cls(2)}">
        <div class="st-dot">{'✓' if st_num > 2 else '2'}</div>
        <div class="st-label">Làm sạch</div>
        <div class="st-sub">Profiling &amp; Cleaning</div>
    </div>
    <div class="st-step {get_cls(3)}">
        <div class="st-dot">{'✓' if st_num > 3 else '3'}</div>
        <div class="st-label">Xử lý Agent</div>
        <div class="st-sub">Kho, Lead-time, Giá</div>
    </div>
    <div class="st-step {get_cls(4)}">
        <div class="st-dot">{'✓' if st_num > 4 else '4'}</div>
        <div class="st-label">Xác nhận</div>
        <div class="st-sub">Chốt chặn kiểm soát</div>
    </div>
    <div class="st-step {get_cls(5)}">
        <div class="st-dot">{'✓' if st_num > 5 else '5'}</div>
        <div class="st-label">Báo cáo &amp; HTML</div>
        <div class="st-sub">Dashboard &amp; Xuất HTML</div>
    </div>
</nav>
""", unsafe_allow_html=True)

# ==============================================================================
# CHẶNG 1: NHẬP DỮ LIỆU ĐẦU VÀO (DATA INTAKE)
# ==============================================================================
if st_num == 1:
    st.markdown("""
    <div class="panel-head">
        <div>
            <span class="chip">CHẶNG 1 / 5</span>
            <h2>Nhập dữ liệu đầu vào</h2>
            <p>Tải lên file Excel (.xlsx), CSV hoặc dán liên kết Google Sheets công khai. Hệ thống kiểm tra cấu trúc dữ liệu trước khi chuyển sang làm sạch.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_up1, c_up2 = st.columns([1.3, 1], gap="medium")

    with c_up1:
        st.markdown("""
        <div class="upload-box">
            <div class="upload-icon">☁️</div>
            <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 6px;">Tải lên file dữ liệu yêu cầu</h3>
            <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 16px;">Hỗ trợ định dạng .csv hoặc .xlsx theo cấu trúc chuẩn</p>
        </div>
        """, unsafe_allow_html=True)

        up_file = st.file_uploader("Chọn file dữ liệu từ máy tính:", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
        if up_file:
            try:
                loaded = load_from_file(up_file, up_file.name)
                st.session_state.batch_result = agent.process_batch(loaded)
                st.markdown(f"""
                <div class="alert-custom alert-ok">
                    <b>✓ Đã nạp thành công file "{up_file.name}"!</b>
                    Phát hiện {len(loaded)} dòng yêu cầu cơ hội bán hàng. Bạn có thể chuyển sang bước tiếp theo.
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div class="alert-custom alert-err">
                    <b>✗ Lỗi đọc file:</b> {str(e)}
                </div>
                """, unsafe_allow_html=True)

    with c_up2:
        st.markdown("""
        <div class="custom-card">
            <h3>🔗 Hoặc Nhập Link Google Sheets:</h3>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">Đảm bảo link Sheet được chia sẻ 'Bất kỳ ai có liên kết đều có thể xem'.</p>
        </div>
        """, unsafe_allow_html=True)
        gs_link = st.text_input("Dán link Google Sheet:", placeholder="https://docs.google.com/spreadsheets/d/.../edit?usp=sharing")
        if st.button("📥 Nạp từ Google Sheet", type="secondary", use_container_width=True):
            if gs_link:
                with st.spinner("Đang tải dữ liệu từ Google Sheets..."):
                    try:
                        gs_res = load_google_sheet(gs_link)
                        st.session_state.batch_result = agent.process_batch(gs_res)
                        st.toast("Đã nạp xong từ Google Sheet!", icon="✔")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {str(e)}")

        st.markdown("<hr style='margin: 14px 0;'>", unsafe_allow_html=True)
        st.markdown("<b>⚡ Hoặc sử dụng bộ 10 kịch bản mẫu chuẩn:</b>", unsafe_allow_html=True)
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            if st.button("🔄 Nạp 10 Mẫu Demo", type="primary", use_container_width=True):
                df_s = create_sample_dataset()
                st.session_state.batch_result = agent.process_batch(dataframe_to_request_list(df_s))
                st.toast("Đã nạp 10 kịch bản kiểm thử chuẩn!", icon="🚀")
                st.rerun()
        with c_m2:
            df_sample = create_sample_dataset()
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_sample.to_excel(writer, index=False, sheet_name="Data")
            st.download_button(
                label="⬇ Tải Excel Mẫu",
                data=buf.getvalue(),
                file_name="TruongGiang_Sample_Requests.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("🌸 Chuyển sang Chặng 2: Kiểm tra & Làm sạch dữ liệu →", type="primary", use_container_width=True):
        st.session_state.stage = 2
        st.rerun()

# ==============================================================================
# CHẶNG 2: KIỂM TRA & LÀM SẠCH DỮ LIỆU (DATA PROFILING & CLEANING)
# ==============================================================================
elif st_num == 2:
    st.markdown("""
    <div class="panel-head">
        <div>
            <span class="chip">CHẶNG 2 / 5</span>
            <h2>Làm sạch & Chuẩn hóa dữ liệu (Profiling & Cleaning)</h2>
            <p>Bật hoặc tắt các quy tắc làm sạch để chuẩn hóa dữ liệu yêu cầu. Khi thấy dữ liệu đã đúng ý, bấm <b>Dữ liệu đã ổn</b> để chuyển sang bước xử lý của AI Agent.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 KPI Cards trước & sau làm sạch theo đúng mockup
    total_raw = len(dossiers)
    missing_count = sum(1 for d in dossiers if d.get("needs_info"))
    clean_ready = total_raw - missing_count

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Yêu cầu ban đầu</div>
            <div class="kpi-val">{total_raw}</div>
            <div class="kpi-sub">Tổng số dòng tiếp nhận</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Dữ liệu hoàn chỉnh</div>
            <div class="kpi-val" style="color: var(--accent);">{clean_ready}</div>
            <div class="kpi-sub">Đủ điều kiện thẩm định</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Dòng thiếu thông tin</div>
            <div class="kpi-val" style="color: var(--orange);">{missing_count}</div>
            <div class="kpi-sub">Cần bổ sung ngân sách/thời hạn</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Quy tắc chuẩn hóa</div>
            <div class="kpi-val" style="color: var(--blue);">5/5</div>
            <div class="kpi-sub">Đã áp dụng tự động</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_rule_col, c_preview_col = st.columns([1, 1.6], gap="medium")

    with c_rule_col:
        st.markdown("""
        <div class="custom-card">
            <h3>Quy tắc làm sạch & chuẩn hóa</h3>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">Các quy tắc được thực hiện tự động trước khi Agent tính toán:</p>
        </div>
        """, unsafe_allow_html=True)

        st.checkbox("✓ Chuẩn hóa mã sản phẩm (SP01 - SP07) & viết hoa", value=True, key="c1")
        st.checkbox("✓ Xóa ký tự lạ trong trường Ngân sách (VNĐ, dấu phẩy, chấm)", value=True, key="c2")
        st.checkbox("✓ Kiểm tra và phát hiện số lượng sản phẩm không hợp lệ (≤ 0)", value=True, key="c3")
        st.checkbox("✓ Tách và nhận diện các yêu cầu có nhiều thiết bị (Multi-item)", value=True, key="c4")
        st.checkbox("✓ Tự động gắn cờ các đơn thiếu ngân sách hoặc thiếu thời hạn", value=True, key="c5")

        if st.button("↻ Chạy lại quy tắc làm sạch", use_container_width=True):
            st.toast("Đã áp dụng lại các quy tắc làm sạch!", icon="✔")

    with c_preview_col:
        st.markdown("""
        <div class="custom-card">
            <h3>So sánh dữ liệu trước & sau khi chuẩn hóa</h3>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">Hiển thị danh sách dữ liệu sau bước làm sạch:</p>
        </div>
        """, unsafe_allow_html=True)

        clean_preview_rows = []
        for d in dossiers:
            clean_preview_rows.append({
                "Mã yêu cầu": d["opportunity_id"],
                "Doanh nghiệp": d["customer_name"][:20],
                "Sản phẩm / Dịch vụ": str(d.get("items", "Đã chuẩn hóa"))[:25],
                "Ngân sách": format_currency_vnd(d.get("customer_budget")),
                "Hạn giao": f"{d.get('requested_lead_days')} ngày" if d.get('requested_lead_days') else "Thiếu",
                "Trạng thái": "Hợp lệ" if not d.get("needs_info") else "Thiếu dữ kiện"
            })
        st.dataframe(pd.DataFrame(clean_preview_rows), hide_index=True, use_container_width=True)

    st.markdown("<hr style='margin: 22px 0; border-color: #fbcfe8;'>", unsafe_allow_html=True)
    c_ref1, c_ref2 = st.columns([1.3, 1], gap="medium")
    with c_ref1:
        st.markdown("""
        <div class="custom-card">
            <h3>📦 Danh mục 7 Sản phẩm &amp; Tồn kho thực tế (SP01–SP07)</h3>
        </div>
        """, unsafe_allow_html=True)
        cat_rows = [
            {
                "Mã": code,
                "Tên thiết bị / Dịch vụ": info["name"],
                "Giá niêm yết": format_currency_vnd(info["list_price"]),
                "Tồn kho": f"{info['stock_available']} {info['unit']}",
                "Lead-time nhập": f"{info['restock_lead_days']} ngày"
            }
            for code, info in PRODUCT_CATALOG.items()
        ]
        st.dataframe(pd.DataFrame(cat_rows), hide_index=True, use_container_width=True)

    with c_ref2:
        tier_html = "".join([
            f"<div style='background:#fdf2f8; border:1px solid #fbcfe8; border-radius:8px; padding:8px 12px; margin-bottom:8px; font-size:0.82rem; display:flex; justify-content:space-between;'><span>{t['description']}</span><b style='color:#be185d;'>Max {t['sales_rep_max_pct']:g}%</b></div>"
            for t in DISCOUNT_TIERS
        ])
        rep_html = " · ".join([f"<b>{r['id']}</b>: {r['name']}" for r in SALES_REPRESENTATIVES])
        st.markdown(f"""
        <div class="custom-card">
            <h3>⚖️ Chính sách Chiết khấu &amp; Phân quyền</h3>
            {tier_html}
            <div style="background:#fce7f3; border:1px solid #f9a8d4; border-radius:8px; padding:9px 12px; font-size:0.8rem; font-weight:700; color:#9d174d; margin-top:8px;">
                👑 Trần tối đa công ty: ≤ {MANAGER_MAX_DISCOUNT_PCT:g}% (Trưởng phòng {SALES_MANAGER['name']} duyệt)
            </div>
            <div style="margin-top:12px; font-size:0.78rem; color:#4a3b47; line-height:1.6;">
                <b>👥 6 NVKD phụ trách luân phiên:</b><br>{rep_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 18px 0;'>", unsafe_allow_html=True)
    c_b1, c_b2 = st.columns([1, 1])
    with c_b1:
        if st.button("← Quay lại: Nhập file khác", use_container_width=True):
            st.session_state.stage = 1
            st.rerun()
    with c_b2:
        if st.button("Dữ liệu đã ổn, tiếp tục sang Chặng 3: Xử lý dữ liệu →", type="primary", use_container_width=True):
            st.session_state.stage = 3
            st.rerun()

# ==============================================================================
# CHẶNG 3: XỬ LÝ & THẨM ĐỊNH AI AGENT (AGENT PROCESSING)
# ==============================================================================
elif st_num == 3:
    st.markdown("""
    <div class="panel-head">
        <div>
            <span class="chip">CHẶNG 3 / 5</span>
            <h2>Xử lý & Thẩm định Đa Kỹ Năng (AI Sales Agent)</h2>
            <p>Hệ thống AI Agent tự động gọi các công cụ nghiệp vụ: Thẩm định tồn kho & Lead-time, Báo giá & Chiết khấu theo chính sách, và Phân định thẩm quyền duyệt.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-custom alert-info">
        <b>🤖 AI Agent đang phối hợp 4 kỹ năng nghiệp vụ liên hoàn:</b>
        <ul style="margin: 6px 0 0 18px;">
            <li><b>Kỹ năng 1:</b> Phân loại thông tin & Tự động phân bổ luân phiên cho 1 trong 6 NVKD phụ trách.</li>
            <li><b>Kỹ năng 2:</b> Gọi công cụ tra cứu CSDL kho, tính toán Lead-time khả thi thực tế (2 ngày nếu đủ kho, hoặc Max nhập hàng + 2 ngày).</li>
            <li><b>Kỹ năng 3:</b> Áp bảng giá niêm yết hiện hành, tính chiết khấu bậc thang theo doanh số.</li>
            <li><b>Kỹ năng 4:</b> Kiểm tra trần thẩm quyền tự quyết của NVKD (≤ 5%) và lập Phiếu trình duyệt Trưởng phòng nếu vượt quyền.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Kết Quả Thẩm Định Sơ Bộ Của AI Agent:")
    proc_rows = []
    for d in dossiers:
        p_val = d.get("pricing", {}).get("final_proposed_price") if d.get("pricing") else None
        proc_rows.append({
            "Mã cơ hội": d["opportunity_id"],
            "Khách hàng": d["customer_name"],
            "NVKD phụ trách": f"{d['sales_rep']['name']} ({d['sales_rep']['id']})",
            "Phân loại của Agent": d["final_status"],
            "Giá trị đề xuất": format_currency_vnd(p_val) if p_val else "Chưa xác định",
            "Căn cứ tiếp theo": d["next_action"]
        })
    st.dataframe(pd.DataFrame(proc_rows), hide_index=True, use_container_width=True)

    st.markdown("<hr style='margin: 18px 0;'>", unsafe_allow_html=True)
    c_b1, c_b2 = st.columns([1, 1])
    with c_b1:
        if st.button("← Quay lại: Làm sạch dữ liệu", use_container_width=True):
            st.session_state.stage = 2
            st.rerun()
    with c_b2:
        if st.button("Tiếp tục: Xác nhận kết quả ở Chặng 4 →", type="primary", use_container_width=True):
            st.session_state.stage = 4
            st.rerun()

# ==============================================================================
# CHẶNG 4: XÁC NHẬN KẾT QUẢ (HUMAN-IN-THE-LOOP CONFIRMATION)
# ==============================================================================
elif st_num == 4:
    st.markdown("""
    <div class="panel-head">
        <div>
            <span class="chip">CHẶNG 4 / 5</span>
            <h2>Xác nhận kết quả thẩm định (Human-in-the-loop Checkpoint)</h2>
            <p>Kiểm tra số liệu trước khi xuất báo cáo chính thức. Nếu thấy chưa đúng hoặc cần điều chỉnh quy tắc, bạn có thể quay lại bước làm sạch hoặc chọn file khác.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-custom alert-warn">
        <b>⚖️ Chốt chặn kiểm soát của con người (Decision Diamond theo sơ đồ quy trình):</b>
        Tại đây, người quản lý hoặc chuyên viên xác nhận số liệu phân loại. Nếu đồng ý ("Có") -> Xuất Báo cáo & Đề xuất kinh doanh. Nếu không đồng ý ("Không") -> Quay lại điều chỉnh quy tắc làm sạch.
    </div>
    """, unsafe_allow_html=True)

    c_sum1, c_sum2, c_sum3, c_sum4 = st.columns(4)
    with c_sum1:
        st.metric("Có thể tiếp tục", f"{counts['CÓ THỂ TIẾP TỤC']} cơ hội", "Đạt chuẩn NVKD")
    with c_sum2:
        st.metric("Chờ duyệt", f"{counts['CHỜ DUYỆT']} cơ hội", "Vượt quyền chiết khấu")
    with c_sum3:
        st.metric("Cần bổ sung TT", f"{counts['CẦN BỔ SUNG THÔNG TIN']} cơ hội", "Thiếu dữ kiện")
    with c_sum4:
        st.metric("Chưa đáp ứng", f"{counts['CHƯA ĐÁP ỨNG']} cơ hội", "Kho / Ngân sách / Trần giá")

    st.markdown("<hr style='margin: 14px 0;'>", unsafe_allow_html=True)

    confirm_chk = st.checkbox(
        "Tôi đã kiểm tra đối chiếu và xác nhận các kết quả thẩm định trên là chính xác (cho phép phát hành báo cáo).",
        value=st.session_state.confirmed_by_user
    )
    st.session_state.confirmed_by_user = confirm_chk

    c_b1, c_b2 = st.columns([1, 1])
    with c_b1:
        if st.button("← Không xác nhận, quay lại sửa quy tắc làm sạch", use_container_width=True):
            st.session_state.stage = 2
            st.rerun()
    with c_b2:
        if st.button("Đã xác nhận, Xuất Báo Cáo & Dashboard (Chặng 5) →", type="primary", disabled=not confirm_chk, use_container_width=True):
            st.session_state.stage = 5
            st.rerun()

# ==============================================================================
# CHẶNG 5: BÁO CÁO & DASHBOARD HOÀN CHỈNH (REPORT & DASHBOARD)
# ==============================================================================
elif st_num == 5:
    st.markdown("""
    <div class="panel-head">
        <div>
            <span class="chip" style="background: var(--accent-light); color: var(--accent);">CHẶNG 5 / 5 · ĐÃ XÁC NHẬN</span>
            <h2>Báo cáo Phân Tích & Đề Xuất Kinh Doanh B2B</h2>
            <p>Kết quả xử lý cơ hội bán hàng hoàn chỉnh của hệ thống Trường Giang. Đã phân loại chính xác 4 nhóm trạng thái và tính toán giá trị đề xuất theo đúng chính sách.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 KPI Cards
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">CÓ THỂ TIẾP TỤC</div>
            <div class="kpi-val" style="color: var(--green);">{counts['CÓ THỂ TIẾP TỤC']}</div>
            <div class="kpi-sub">Đủ điều kiện &amp; Thẩm quyền</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">CHỜ TRƯỞNG PHÒNG DUYỆT</div>
            <div class="kpi-val" style="color: var(--amber);">{counts['CHỜ DUYỆT']}</div>
            <div class="kpi-sub">Vượt hạn mức chiết khấu NVKD</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">CẦN BỔ SUNG THÔNG TIN</div>
            <div class="kpi-val" style="color: var(--accent-deep);">{counts['CẦN BỔ SUNG THÔNG TIN']}</div>
            <div class="kpi-sub">Thiếu ngân sách/thời hạn/SL</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">CHƯA ĐÁP ỨNG</div>
            <div class="kpi-val" style="color: var(--red);">{counts['CHƯA ĐÁP ỨNG']}</div>
            <div class="kpi-sub">Kho thiếu/Vượt trần 15%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # BANNER DOANH SỐ TIỀM NĂNG NỔI BẬT TÔNG HỒNG RUBY
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #831843 0%, #be185d 50%, #ec4899 100%); border-radius: var(--r); padding: 22px 28px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px; box-shadow: var(--shadow-md); position: relative;">
        <div>
            <div style="font-size: 0.85rem; font-weight: 800; color: #fbcfe8; text-transform: uppercase; letter-spacing: 0.5px;">
                💎 TỔNG GIÁ TRỊ CÁC CƠ HỘI ĐỦ ĐIỀU KIỆN TIẾP TỤC HOẶC CHỜ DUYỆT:
            </div>
            <div style="font-size: 0.83rem; color: #fce7f3; margin-top: 4px;">
                Bao gồm {counts['CÓ THỂ TIẾP TỤC']} cơ hội Đạt chuẩn và {counts['CHỜ DUYỆT']} cơ hội Chờ duyệt. Không tự ý tính cơ hội thiếu dữ kiện.
            </div>
        </div>
        <div style="font-size: 2rem; font-weight: 800; color: #ffffff; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            {format_currency_vnd(batch_res['total_eligible_value'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sinh báo cáo HTML hoàn chỉnh phục vụ xuất trực tiếp trên giao diện (Bước 8)
    html_report_code = generate_html_report(batch_res, manager_name=SALES_MANAGER["name"])

    tab_report0, tab_report1, tab_report2, tab_report3, tab_report4 = st.tabs([
        "🌐 Báo Cáo HTML Trực Tiếp (Bước 8)",
        "📋 Danh Sách & Bảng Tổng Hợp",
        "📑 Chi Tiết Hồ Sơ Cơ Hội",
        "⚖️ Phiếu Trình Duyệt (TPKD)",
        "🕵️ Nhật Ký Truy Vết (Audit Log)"
    ])

    with tab_report0:
        st.markdown("### 🌐 Báo Cáo Quản Trị Kinh Doanh B2B (Xuất Trực Tiếp Trên Giao Diện)")
        st.markdown(f"""
        Bản báo cáo quản trị tổng hợp toàn bộ quy trình: Dữ liệu đã làm sạch, kết quả thẩm định 4 kỹ năng của AI Agent,
        đối soát tài chính, và chữ ký số điện tử của Trưởng phòng **{SALES_MANAGER['name']}**.
        """)

        c_act1, c_act2 = st.columns([1, 1])
        with c_act1:
            st.download_button(
                label="⬇ Tải File Báo Cáo HTML (.html)",
                data=html_report_code,
                file_name=f"Bao_Cao_Kinh_Doanh_B2B_{SALES_MANAGER['name']}.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
        with c_act2:
            st.info("💡 Bạn có thể cuộn xem trực tiếp bên dưới, hoặc bấm nút tải file để mở toàn màn hình / in ấn sang PDF chuẩn A4.")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        # Hiển thị trực tiếp bản báo cáo HTML trên giao diện Agent
        components.html(html_report_code, height=920, scrolling=True)

    with tab_report1:
        st.markdown("### Bảng Tổng Hợp Cơ Hội Bán Hàng:")
        c_f1, c_f2 = st.columns([1, 2])
        with c_f1:
            f_filter = st.selectbox("Lọc theo nhóm:", ["Tất cả", "CÓ THỂ TIẾP TỤC", "CHỜ DUYỆT", "CẦN BỔ SUNG THÔNG TIN", "CHƯA ĐÁP ỨNG"], key="rep_filter")
        with c_f2:
            f_search = st.text_input("🔍 Tìm theo tên công ty hoặc mã cơ hội:", key="rep_search")

        tbl_data = []
        for d in dossiers:
            if f_filter != "Tất cả" and d["final_status"] != f_filter:
                continue
            if f_search:
                if f_search.lower() not in d["opportunity_id"].lower() and f_search.lower() not in d["customer_name"].lower():
                    continue

            p_val = d.get("pricing", {}).get("final_proposed_price") if d.get("pricing") else None
            b_val = d.get("customer_budget")
            lead = d.get("requested_lead_days")

            tbl_data.append({
                "Mã cơ hội": d["opportunity_id"],
                "Doanh nghiệp": d["customer_name"],
                "NVKD phụ trách": f"{d['sales_rep']['name']} ({d['sales_rep']['id']})",
                "Trạng thái": d["final_status"],
                "Giá trị đề xuất": format_currency_vnd(p_val) if p_val else "Chưa xác định",
                "Ngân sách": format_currency_vnd(b_val) if b_val else "Chưa có",
                "Hạn giao": f"{lead} ngày" if lead else "Chưa rõ",
                "Hành động tiếp theo": d["next_action"]
            })

        df_rep = pd.DataFrame(tbl_data)

        def style_status(val):
            if val == "CÓ THỂ TIẾP TỤC":
                return "background-color: var(--accent-light); color: var(--accent); font-weight: 700;"
            elif val == "CHỜ DUYỆT":
                return "background-color: var(--amber-light); color: var(--amber); font-weight: 700;"
            elif val == "CẦN BỔ SUNG THÔNG TIN":
                return "background-color: var(--orange-light); color: var(--orange); font-weight: 700;"
            elif val == "CHƯA ĐÁP ỨNG":
                return "background-color: var(--red-light); color: var(--red); font-weight: 700;"
            return ""

        if not df_rep.empty:
            if hasattr(df_rep.style, "map"):
                st_df = df_rep.style.map(style_status, subset=["Trạng thái"])
            else:
                st_df = df_rep.style.applymap(style_status, subset=["Trạng thái"])
            st.dataframe(st_df, use_container_width=True, hide_index=True)
        else:
            st.info("Không có cơ hội nào khớp với bộ lọc.")

        c_dl1, c_dl2 = st.columns([1, 1])
        with c_dl1:
            csv_rep = df_rep.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇ Tải Báo Cáo CSV",
                data=csv_rep,
                file_name="Bao_cao_co_hoi_TruongGiang.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_dl2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_rep.to_excel(writer, index=False, sheet_name="BaoCao")
            st.download_button(
                "⬇ Tải Báo Cáo Excel (.xlsx)",
                data=buf.getvalue(),
                file_name="Bao_cao_co_hoi_TruongGiang.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    with tab_report2:
        st.markdown("### Chi Tiết Từng Hồ Sơ Cơ Hội:")
        sel_opp = st.selectbox("Chọn Mã cơ hội:", [d["opportunity_id"] for d in dossiers], key="sel_dossier")
        curr_d = next((d for d in dossiers if d["opportunity_id"] == sel_opp), None)

        if curr_d:
            c_d1, c_d2 = st.columns([1.2, 1], gap="medium")
            with c_d1:
                st.markdown(f"#### #{curr_d['opportunity_id']} - {curr_d['customer_name']}")
                st.markdown(f"- **Trạng thái:** `{curr_d['final_status']}`")
                st.markdown(f"- **Người phụ trách:** `{curr_d['sales_rep']['name']}` ({curr_d['sales_rep']['phone']} - {curr_d['sales_rep']['email']})")
                st.markdown(f"- **Hành động tiếp theo:** **{curr_d['next_action']}**")

                if curr_d.get("inventory"):
                    st.markdown("##### 📦 1. Thẩm định tồn kho & tiến độ:")
                    st.info(f"{curr_d['inventory']['fulfillment_verdict']}\n\n*Căn cứ:* {curr_d['inventory']['lead_time_basis']}")
                    inv_items = []
                    for it in curr_d["inventory"].get("item_analysis", []):
                        inv_items.append({
                            "Mã SP": it["product_id"],
                            "Tên thiết bị": it["product_name"][:22],
                            "SL cần": it["requested_qty"],
                            "Tồn kho": it["stock_available"],
                            "Tình trạng": "Đủ hàng" if it["is_in_stock"] else f"Thiếu {it['shortage_qty']}"
                        })
                    st.dataframe(pd.DataFrame(inv_items), hide_index=True, use_container_width=True)

                if curr_d.get("pricing"):
                    p = curr_d["pricing"]
                    st.markdown("##### 💰 2. Báo giá & chính sách chiết khấu:")
                    st.markdown(f"- Tổng giá niêm yết: `{format_currency_vnd(p.get('total_list_price'))}`")
                    st.markdown(f"- Chiết khấu áp dụng: `{p.get('applied_discount_pct')}%` (-{format_currency_vnd(p.get('discount_amount'))})")
                    st.markdown(f"- **GIÁ ĐỀ XUẤT CUỐI CÙNG:** `{format_currency_vnd(p.get('final_proposed_price'))}`")
                    st.markdown(f"- Ngân sách khách hàng: `{format_currency_vnd(p.get('customer_budget'))}` ({p.get('budget_verdict')})")

            with c_d2:
                st.markdown("#### ✉️ Bản Nháp Email Phản Hồi Khách Hàng")
                st.text_area("Nội dung email tự động sinh:", curr_d.get("customer_email_draft", ""), height=350)

    with tab_report3:
        st.markdown("### Phiếu Trình Duyệt Vượt Thẩm Quyền (Trưởng Phòng Trường Giang):")
        pending_list = [d for d in dossiers if d["final_status"] == "CHỜ DUYỆT" or d.get("requires_approval")]

        if not pending_list:
            st.success("✔ Không có cơ hội nào đang chờ phê duyệt.")
        else:
            for pd_d in pending_list:
                o_id = pd_d["opportunity_id"]
                st.markdown(f"#### 📝 Phiếu Trình Duyệt #{o_id} - {pd_d['customer_name']}")
                st.text_area(f"Nội dung phiếu #{o_id}:", pd_d.get("approval_ticket", ""), height=200, key=f"tk_{o_id}")

                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button("✅ KÝ DUYỆT (APPROVE)", key=f"app_{o_id}", type="primary"):
                        st.session_state.approval_decisions[o_id] = "ĐÃ DUYỆT"
                        st.success(f"Đã duyệt thành công cho #{o_id}!")
                with b2:
                    if st.button("❌ TỪ CHỐI (REJECT)", key=f"rej_{o_id}"):
                        st.session_state.approval_decisions[o_id] = "TỪ CHỐI"
                        st.error(f"Đã từ chối #{o_id}!")

                if o_id in st.session_state.approval_decisions:
                    st.info(f"📌 Quyết định hiện tại: **{st.session_state.approval_decisions[o_id]}**")

    with tab_report4:
        st.markdown("### Nhật Ký Truy Vết Thực Thi Của Agent (Audit Trail):")
        for idx, l in enumerate(curr_d.get("audit_logs", []), 1):
            with st.expander(f"Bước {idx}: {l['step']} ➔ {l['action']} ({l['timestamp']})"):
                st.markdown(f"**Căn cứ quy tắc:** `{l['rule']}`")
                st.json(l["details"])

    st.markdown("<hr style='margin: 24px 0;'>", unsafe_allow_html=True)
    if st.button("＋ Phân tích bộ dữ liệu mới (Quay lại Chặng 1)", use_container_width=True):
        st.session_state.stage = 1
        st.session_state.confirmed_by_user = False
        st.rerun()

# FOOTER
st.markdown("""
<div style="text-align: center; color: #9d174d; font-size: 0.8rem; margin-top: 36px; padding-top: 14px; border-top: 1.5px solid #fbcfe8;">
    🌸 Trường Giang — AI Data Analytics Agent B2B • Pink Blossom Luxury Edition
</div>
""", unsafe_allow_html=True)
