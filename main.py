import streamlit as st
import pandas as pd
import datetime
import base64
import io
import os
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Điểm danh Vovinam - TH An Lạc 3",
    page_icon="🥋",
    layout="wide"
)

# Cấu hình icon khi thêm ra màn hình chính điện thoại
st.markdown("""
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/thaibaotoan148/VOVINAM-Ti-u-h-c-An-L-c-3/main/logo_anlac3.png">
    <link rel="icon" href="https://raw.githubusercontent.com/thaibaotoan148/VOVINAM-Ti-u-h-c-An-L-c-3/main/logo_anlac3.png">
""", unsafe_allow_html=True)


# Hàm tự động xóa nền trắng bên ngoài Logo
def remove_white_background(image_source):
    if isinstance(image_source, str):
        img = Image.open(image_source).convert("RGBA")
    else:
        img = Image.open(io.BytesIO(image_source)).convert("RGBA")
    w, h = img.size
    edge_points = (
            [(x, 0) for x in range(0, w, 2)] +
            [(x, h - 1) for x in range(0, w, 2)] +
            [(0, y) for y in range(0, h, 2)] +
            [(w - 1, y) for y in range(0, h, 2)]
    )
    for pt in edge_points:
        r, g, b, a = img.getpixel(pt)
        if a > 0 and r > 200 and g > 200 and b > 200:
            ImageDraw.floodfill(img, pt, (0, 0, 0, 0), thresh=70)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    cw, ch = img.size
    if 0.90 <= (cw / ch) <= 1.10:
        mask = Image.new("L", (cw, ch), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((1, 1, cw - 2, ch - 2), fill=255)
        img.putalpha(mask)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# SVG dự phòng khi chưa có ảnh
SVG_SHIELD_NO_BG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 310" width="110" height="135"><path d="M8,8 H232 V185 C232,255 178,298 120,302 C62,298 8,255 8,185 Z" fill="#FFF200" stroke="#0060B6" stroke-width="10"/></svg>'
SVG_CIRCLE_NO_BG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="130" height="130"><circle cx="150" cy="150" r="144" fill="#FFF200" stroke="#000" stroke-width="6"/></svg>'


def get_clean_logo_html(filenames, fallback_svg):
    for fn in filenames:
        if os.path.exists(fn):
            try:
                b64_clean = remove_white_background(fn)
                return f'<img src="data:image/png;base64,{b64_clean}" style="height:130px; width:auto; object-fit:contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));">'
            except Exception:
                pass
    return fallback_svg


# File dữ liệu riêng cho 2 ca học
FILE_HS_246 = "ds_vosinh_246.csv"
FILE_HS_357 = "ds_vosinh_357.csv"
FILE_LS = "lich_su_diem_danh_chung.csv"

# Danh sách mặc định ca Thứ 2-4-6 (11 em)
DANH_SACH_GOC_246 = [
    {"STT": 1, "Họ và tên": "Phạm An Nhiên"},
    {"STT": 2, "Họ và tên": "Lương Ngọc Hoàng Yến"},
    {"STT": 3, "Họ và tên": "Nguyễn Kỳ Xuân Thịnh"},
    {"STT": 4, "Họ và tên": "Thiên Bảo"},
    {"STT": 5, "Họ và tên": "Chu Đức Phát"},
    {"STT": 6, "Họ và tên": "Hồ Nguyễn Khoa Đông"},
    {"STT": 7, "Họ và tên": "Bùi Nguyễn Anh Huy"},
    {"STT": 8, "Họ và tên": "Lê Nguyễn Lam Phương"},
    {"STT": 9, "Họ và tên": "Nguyễn Minh Quốc Thuận"},
    {"STT": 10, "Họ và tên": "Vũ Ngọc Bảo Trâm"},
    {"STT": 11, "Họ và tên": "Vũ Ngọc An Nhiên"},
]


def load_students(file_path, default_data):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        df = pd.DataFrame(default_data)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return df
    try:
        return pd.read_csv(file_path, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(default_data)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return df


def load_history():
    if not os.path.exists(FILE_LS) or os.path.getsize(FILE_LS) == 0:
        df = pd.DataFrame(columns=["Ngày", "Thứ", "Ca học", "STT", "Họ và tên", "Trạng thái", "Ghi chú"])
        df.to_csv(FILE_LS, index=False, encoding="utf-8-sig")
        return df
    try:
        return pd.read_csv(FILE_LS, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["Ngày", "Thứ", "Ca học", "STT", "Họ và tên", "Trạng thái", "Ghi chú"])
        df.to_csv(FILE_LS, index=False, encoding="utf-8-sig")
        return df


df_ls = load_history()

# ================= SIDEBAR & CÀI ĐẶT =================
menu = st.sidebar.radio(
    "📌 DANH MỤC QUẢN LÝ:",
    ["📋 Điểm danh buổi tập", "📊 Lịch sử & Xuất Excel", "➕ Quản lý danh sách võ sinh"]
)

st.sidebar.markdown("---")
with st.sidebar.expander("🖼️ Cài đặt Logo (Tự xóa nền)"):
    up_shield = st.file_uploader("Logo Khiên Vovinam", type=["png", "jpg", "jpeg"], key="up1")
    if up_shield:
        b64_data = remove_white_background(up_shield.getvalue())
        with open("logo_vovinam.png", "wb") as f:
            f.write(base64.b64decode(b64_data))
        st.success("Đã cập nhật Logo Vovinam!")
    up_circle = st.file_uploader("Logo Tròn An Lạc 3", type=["png", "jpg", "jpeg"], key="up2")
    if up_circle:
        b64_data = remove_white_background(up_circle.getvalue())
        with open("logo_anlac3.png", "wb") as f:
            f.write(base64.b64decode(b64_data))
        st.success("Đã cập nhật Logo An Lạc 3!")

# Header Banner
left_logo_html = get_clean_logo_html(["logo_vovinam.png", "logo1.png"], SVG_SHIELD_NO_BG)
right_logo_html = get_clean_logo_html(["logo_anlac3.png", "logo2.png"], SVG_CIRCLE_NO_BG)

banner_html = f"""
<div style="
    background: linear-gradient(135deg, #072554 0%, #0d47a1 50%, #1565c0 100%);
    border-radius: 18px; padding: 18px 32px; display: flex; align-items: center; justify-content: space-between;
    border-bottom: 6px solid #FFF200; box-shadow: 0 8px 20px rgba(13, 71, 161, 0.25); font-family: 'Segoe UI', Arial, sans-serif;
">
    <div style="display:flex; align-items:center;">{left_logo_html}</div>
    <div style="text-align: center; color: white; flex: 1; padding: 0 15px;">
        <div style="color: #FFF200; font-size: 18px; font-weight: 800; letter-spacing: 2px;">VOVINAM - VIỆT VÕ ĐẠO</div>
        <div style="color: #FFFFFF; font-size: 30px; font-weight: 900; margin: 6px 0 10px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.35);">
            CLB TIỂU HỌC AN LẠC 3
        </div>
        <div style="background-color: #FFF200; color: #072554; padding: 6px 18px; border-radius: 30px; font-weight: 800; font-size: 14px; display: inline-block;">
            🥋 Lịch: 2-4-6 (16h45 - 18h15) &nbsp;|&nbsp; 3-5-7 (17h30 - 19h00)
        </div>
    </div>
    <div style="display:flex; align-items:center;">{right_logo_html}</div>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)

# ================= 1. ĐIỂM DANH BUỔI TẬP =================
if menu == "📋 Điểm danh buổi tập":
    thu_vn = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ Nhật"}

    c1, c2 = st.columns(2)
    with c1:
        ngay_tap = st.date_input("📅 Chọn ngày điểm danh:", datetime.date.today(), key="chon_ngay_tap")
        thu_hien_tai = thu_vn[ngay_tap.weekday()]

    if "ngay_truoc_do" not in st.session_state:
        st.session_state["ngay_truoc_do"] = ngay_tap

    with c2:
        if thu_hien_tai == "Chủ Nhật":
            st.selectbox("⏰ Ca học tương ứng:", ["🛑 Chủ Nhật - CLB Nghỉ tập (Không có ca học)"], disabled=True)
            ca_hoc_chon = "Chủ Nhật (Nghỉ)"
        elif thu_hien_tai in ["Thứ 2", "Thứ 4", "Thứ 6"]:
            ca_hoc_chon = st.selectbox("⏰ Ca học tương ứng:",
                                       ["Thứ 2 - 4 - 6 (16h45 - 18h15)", "Thứ 3 - 5 - 7 (17h30 - 19h00)"])
        else:
            ca_hoc_chon = st.selectbox("⏰ Ca học tương ứng:",
                                       ["Thứ 3 - 5 - 7 (17h30 - 19h00)", "Thứ 2 - 4 - 6 (16h45 - 18h15)"])

    if st.session_state["ngay_truoc_do"] != ngay_tap:
        st.session_state["ngay_truoc_do"] = ngay_tap
        st.rerun()

    st.write("")

    # KIỂM TRA NGÀY CHỦ NHẬT -> KHÓA ĐIỂM DANH HOÀN TOÀN
    if thu_hien_tai == "Chủ Nhật":
        st.markdown("""
        <div style="background-color: #ffebee; border-left: 6px solid #c62828; padding: 30px; border-radius: 12px; text-align: center; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <h2 style="color: #c62828; margin: 0;">🛑 HÔM NAY LÀ CHỦ NHẬT - KHÔNG CÓ CA HỌC NÀO</h2>
            <p style="color: #555; font-size: 16px; margin-top: 12px;">Hệ thống đã tự động khóa chức năng điểm danh. Chúc các em võ sinh và HLV có ngày nghỉ cuối tuần trọn vẹn!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if "2 - 4 - 6" in ca_hoc_chon:
            df_hs = load_students(FILE_HS_246, DANH_SACH_GOC_246)
            ten_ca_luu = "Thứ 2 - 4 - 6 (16h45 - 18h15)"
        else:
            df_hs = load_students(FILE_HS_357, [{"STT": 1, "Họ và tên": "Chưa có danh sách"}])
            ten_ca_luu = "Thứ 3 - 5 - 7 (17h30 - 19h00)"

        if df_hs.empty or (len(df_hs) == 1 and df_hs.iloc[0]["Họ và tên"] == "Chưa có danh sách"):
            st.warning(
                f"⚠️ Ca học **{ca_hoc_chon}** hiện chưa có võ sinh nào. Vui lòng vào mục **'➕ Quản lý danh sách võ sinh'** ở menu bên trái để thêm học sinh vào ca này!")
        else:
            df_check = df_hs.copy()
            if "Có mặt" not in df_check.columns:
                df_check["Có mặt"] = True
            if "Ghi chú" not in df_check.columns:
                df_check["Ghi chú"] = ""

            b1, b2, _ = st.columns([1.6, 1.6, 4.8])
            with b1:
                if st.button("✅ Có mặt tất cả", use_container_width=True):
                    st.session_state["chon_tat_ca"] = True
            with b2:
                if st.button("⚪ Bỏ chọn tất cả", use_container_width=True):
                    st.session_state["chon_tat_ca"] = False

            if "chon_tat_ca" in st.session_state:
                df_check["Có mặt"] = st.session_state["chon_tat_ca"]

            edited_df = st.data_editor(
                df_check[["STT", "Họ và tên", "Có mặt", "Ghi chú"]],
                column_config={
                    "STT": st.column_config.NumberColumn("STT", disabled=True, width="small"),
                    "Họ và tên": st.column_config.TextColumn("Họ và tên võ sinh", disabled=True, width="large"),
                    "Có mặt": st.column_config.CheckboxColumn("Có mặt", default=True),
                    "Ghi chú": st.column_config.TextColumn("Ghi chú (Xin phép / Đi trễ)", width="large"),
                },
                disabled=["STT", "Họ và tên"],
                hide_index=True,
                use_container_width=True,
                height=435
            )

            tong_so = len(edited_df)
            so_co_mat = int(edited_df["Có mặt"].sum())
            so_vang = tong_so - so_co_mat

            k1, k2, k3 = st.columns(3)
            k1.metric("👥 Tổng số võ sinh", f"{tong_so} em")
            k2.metric("🟢 Có mặt", f"{so_co_mat} em")
            k3.metric("🔴 Vắng mặt", f"{so_vang} em")

            if st.button("💾 LƯU ĐIỂM DANH BUỔI TẬP", type="primary", use_container_width=True):
                new_rows = []
                for _, r in edited_df.iterrows():
                    new_rows.append({
                        "Ngày": ngay_tap.strftime("%d/%m/%Y"),
                        "Thứ": thu_hien_tai,
                        "Ca học": ten_ca_luu,
                        "STT": r["STT"],
                        "Họ và tên": r["Họ và tên"],
                        "Trạng thái": "Có mặt" if r["Có mặt"] else "Vắng",
                        "Ghi chú": r["Ghi chú"]
                    })
                df_save = pd.concat([df_ls, pd.DataFrame(new_rows)], ignore_index=True)
                df_save.drop_duplicates(subset=["Ngày", "Ca học", "Họ và tên"], keep="last", inplace=True)
                df_save.to_csv(FILE_LS, index=False, encoding="utf-8-sig")
                st.success(f"🎉 Đã lưu điểm danh ca **{ten_ca_luu}** ngày {ngay_tap.strftime('%d/%m/%Y')} thành công!")

# ================= 2. LỊCH SỬ & XUẤT EXCEL =================
elif menu == "📊 Lịch sử & Xuất Excel":
    st.subheader("📊 Lịch sử điểm danh toàn CLB")
    if df_ls.empty:
        st.info("Chưa có dữ liệu điểm danh nào được lưu.")
    else:
        st.dataframe(df_ls, use_container_width=True, hide_index=True)

        # Chuyển đổi DataFrame thành file Excel (.xlsx) trong bộ nhớ đệm
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_ls.to_excel(writer, index=False, sheet_name='Lich_Su_Diem_Danh')

            # --- ĐOẠN CODE TỰ ĐỘNG CHỈNH CỘT VỪA KHÍT NỘI DUNG ---
            workbook = writer.book
            worksheet = writer.sheets['Lich_Su_Diem_Danh']
            for col in worksheet.columns:
                max_len = 0
                col_letter = col[0].column_letter  # Lấy tên cột (A, B, C,...)
                for cell in col:
                    if cell.value is not None:
                        max_len = max(max_len, len(str(cell.value)))
                # Đặt chiều rộng bằng độ dài ký tự lớn nhất cộng thêm khoảng trống
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
        # -----------------------------------------------------

        excel_data = output.getvalue()

        st.download_button(
            label="📥 Tải file báo cáo Excel (.xlsx)",
            data=excel_data,
            file_name=f"Diem_Danh_Vovinam_AnLac3_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

# ================= 3. QUẢN LÝ DANH SÁCH VÕ SINH =================
elif menu == "➕ Quản lý danh sách võ sinh":
    st.subheader("📋 Quản lý & Chỉnh sửa danh sách võ sinh theo ca")

    chon_ca_ql = st.selectbox("Chọn ca học cần chỉnh sửa danh sách:",
                              ["Thứ 2 - 4 - 6 (16h45 - 18h15)", "Thứ 3 - 5 - 7 (17h30 - 19h00)"])

    file_chon = FILE_HS_246 if "2 - 4 - 6" in chon_ca_ql else FILE_HS_357
    default_data = DANH_SACH_GOC_246 if "2 - 4 - 6" in chon_ca_ql else [
        {"STT": 1, "Họ và tên": "Nhập tên võ sinh vào đây..."}]
    df_hien_tai = load_students(file_chon, default_data)

    st.info(
        "💡 **Hướng dẫn:** Bạn có thể chỉnh sửa trực tiếp tên võ sinh trên bảng bên dưới, thêm dòng mới bằng dấu `+` ở cuối bảng, hoặc xóa dòng tùy ý. Sau đó nhớ bấm nút **Lưu thay đổi** ở phía dưới!")

    edited_ds_hs = st.data_editor(
        df_hien_tai,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "STT": st.column_config.NumberColumn("STT", width="small"),
            "Họ và tên": st.column_config.TextColumn("Họ và tên võ sinh", width="large")
        }
    )

    if st.button("💾 LƯU THAY ĐỔI DANH SÁCH", type="primary", use_container_width=True):
        if not edited_ds_hs.empty:
            edited_ds_hs = edited_ds_hs.dropna(subset=["Họ và tên"])
            edited_ds_hs = edited_ds_hs[edited_ds_hs["Họ và tên"].astype(str).str.strip() != ""]
            edited_ds_hs["STT"] = range(1, len(edited_ds_hs) + 1)

        edited_ds_hs.to_csv(file_chon, index=False, encoding="utf-8-sig")
        st.success(f"🎉 Đã cập nhật thành công danh sách võ sinh cho ca **{chon_ca_ql}**!")
        st.rerun()