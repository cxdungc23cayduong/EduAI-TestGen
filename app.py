import io
import google.generativeai as genai
import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CẤU HÌNH GIAO DIỆN TRANG WEB ---
st.set_page_config(
    page_title="EduAI-TestGen - Hệ Thống Sinh Đề Tổng Hợp",
    page_icon="🤖",
    layout="wide",
)

st.subheader("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG")
st.title("🤖 EduAI-TestGen: Hệ Thống Sinh Đề Kiểm Tra & Trộn Đề")
st.markdown(
    "Ứng dụng hỗ trợ giáo viên Tin học xây dựng ma trận, tạo đề kiểm tra tổng hợp "
    "và tự động hoán vị mã đề bám sát Chương trình GDPT 2018 (Sách Kết nối tri thức)."
)
st.divider()

# --- 2. DỮ LIỆU CHUẨN SÁCH GIÁO KHOA "KẾT NỐI TRI THỨC" TIN HỌC THPT ---
CURRICULUM_DATA = {
    "Lớp 10": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Thông tin và xử lí thông tin",
            "Bài 2: Vai trò của thiết bị thông minh và tin học đối với xã hội",
            "Bài 3: Một số kiểu dữ liệu và dữ liệu văn bản",
            "Bài 4: Hệ nhị phân và dữ liệu số nguyên",
            "Bài 5: Dữ liệu lôgic",
            "Bài 6: Dữ liệu âm thanh và hình ảnh",
            "Bài 7: Thực hành sử dụng thiết bị số thông dụng"
        ],
        "Chủ đề 2: Mạng máy tính và Internet": [
            "Bài 8: Mạng máy tính trong cuộc sống hiện đại",
            "Bài 9: An toàn trên không gian mạng",
            "Bài 10: Thực hành khai thác tài nguyên trên Internet"
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Bài 11: Ứng xử trên môi trường số. Nghĩa vụ tôn trọng bản quyền"
        ],
        "Chủ đề 4: Ứng dụng tin học": [
            "Bài 12: Phần mềm thiết kế đồ hoạ",
            "Bài 13: Bổ sung các đối tượng đồ hoạ",
            "Bài 14: Làm việc với đối tượng đường và văn bản",
            "Bài 15: Hoàn thiện hình ảnh đồ hoạ"
        ],
        "Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính": [
            "Bài 16: Ngôn ngữ lập trình bậc cao và Python",
            "Bài 17: Biến và lệnh gán",
            "Bài 18: Các lệnh vào ra đơn giản",
            "Bài 19: Câu lệnh rẽ nhánh if",
            "Bài 20: Câu lệnh lặp for",
            "Bài 21: Câu lệnh lặp while",
            "Bài 22: Kiểu dữ liệu danh sách",
            "Bài 23: Một số lệnh làm việc với dữ liệu danh sách",
            "Bài 24: Xâu kí tự",
            "Bài 25: Một số lệnh làm việc với xâu kí tự",
            "Bài 26: Hàm trong Python",
            "Bài 27: Tham số của hàm",
            "Bài 28: Phạm vi của biến",
            "Bài 29: Nhận biết lỗi chương trình",
            "Bài 30: Kiểm thử và gỡ lỗi chương trình",
            "Bài 31: Thực hành viết chương trình đơn giản",
            "Bài 32: Ôn tập lập trình Python"
        ],
        "Chủ đề 6: Hướng nghiệp với tin học": [
            "Bài 33: Nghề thiết kế đồ hoạ máy tính",
            "Bài 34: Nghề phát triển phần mềm"
        ]
    },
    "Lớp 11 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Hệ điều hành",
            "Bài 2: Thực hành sử dụng hệ điều hành",
            "Bài 3: Phần mềm nguồn mở và phần mềm chạy trên Internet",
            "Bài 4: Bên trong máy tính",
            "Bài 5: Kết nối máy tính với các thiết bị số"
        ],
        "Chủ đề 2: Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin": [
            "Bài 6: Lưu trữ và chia sẻ tệp tin trên Internet",
            "Bài 7: Thực hành tìm kiếm thông tin trên Internet",
            "Bài 8: Thực hành nâng cao sử dụng thư điện tử và mạng xã hội"
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Bài 9: Giao tiếp an toàn trên Internet"
        ],
        "Chủ đề 4: Giới thiệu các hệ cơ sở dữ liệu": [
            "Bài 10: Lưu trữ dữ liệu và khai thác thông tin phục vụ quản lí",
            "Bài 11: Cơ sở dữ liệu",
            "Bài 12: Hệ quản trị cơ sở dữ liệu và hệ cơ sở dữ liệu",
            "Bài 13: Cơ sở dữ liệu quan hệ",
            "Bài 14: SQL - Ngôn ngữ truy vấn có cấu trúc",
            "Bài 15: Bảo mật và an toàn hệ cơ sở dữ liệu"
        ],
        "Chủ đề 5: Hướng nghiệp với tin học": [
            "Bài 16: Công việc quản trị cơ sở dữ liệu"
        ],
        "Chủ đề 6: Thực hành tạo và khai thác cơ sở dữ liệu": [
            "Bài 17: Quản trị cơ sở dữ liệu trên máy tính",
            "Bài 18: Thực hành xác định cấu trúc bảng và các trường khoá",
            "Bài 19: Thực hành tạo lập cơ sở dữ liệu và các bảng",
            "Bài 20: Thực hành tạo lập các bảng có khoá ngoài",
            "Bài 21: Thực hành cập nhật và truy xuất dữ liệu các bảng",
            "Bài 22: Thực hành cập nhật bảng dữ liệu có tham chiếu",
            "Bài 23: Thực hành truy xuất dữ liệu qua liên kết các bảng",
            "Bài 24: Thực hành sao lưu dữ liệu"
        ],
        "Chủ đề 7: Phần mềm chỉnh sửa ảnh và làm video": [
            "Bài 25: Phần mềm chỉnh sửa ảnh",
            "Bài 26: Công cụ tinh chỉnh màu sắc và công cụ chọn",
            "Bài 27: Công cụ vẽ và một số ứng dụng",
            "Bài 28: Tạo ảnh động",
            "Bài 29: Khám phá phần mềm làm phim",
            "Bài 30: Biên tập phim",
            "Bài 31: Thực hành tạo phim hoạt hình"
        ]
    },
    "Lớp 12 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Làm quen với Trí tuệ nhân tạo",
            "Trí tuệ nhân tạo trong khoa học và đời sống"
        ],
        "Chủ đề 2: Mạng máy tính và Internet": [
            "Một số thiết bị mạng thông dụng",
            "Giao thức mạng",
            "Thực hành chia sẻ tài nguyên trên mạng"
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Giao tiếp và ứng xử trong không gian mạng"
        ],
        "Chủ đề 4: Giải quyết vấn đề với sự trợ giúp của máy tính": [
            "HTML và cấu trúc trang web",
            "Định dạng văn bản",
            "Tạo danh sách, bảng",
            "Tạo liên kết",
            "Chèn tệp tin đa phương tiện và khung nội tuyến vào trang web",
            "Tạo biểu mẫu",
            "Khái niệm, vai trò của CSS",
            "Định dạng văn bản bằng CSS",
            "Tạo màu cho chữ và nền",
            "Định dạng khung",
            "Các mức ưu tiên của bộ chọn",
            "Thực hành tổng hợp thiết kế trang web"
        ],
        "Chủ đề 5: Hướng nghiệp với tin học": [
            "Dịch vụ sửa chữa và bảo trì máy tính",
            "Nhóm nghề quản trị thuộc ngành Công nghệ thông tin",
            "Hội thảo hướng nghiệp"
        ],
        "Chủ đề 6: Máy tính và xã hội tri thức (Định hướng ứng dụng)": [
            "Thực hành kết nối các thiết bị số"
        ],
        "Chủ đề 7: Ứng dụng tin học (Định hướng ứng dụng)": [
            "Chuẩn bị xây dựng trang web",
            "Xây dựng phần đầu trang web",
            "Xây dựng phần thân và chân trang web",
            "Liên kết và thanh điều hướng",
            "Biểu mẫu trên trang web",
            "Thực hành tổng hợp"
        ]
    }
}

# --- 3. THANH BÊN (SIDEBAR): CẤU HÌNH API & MA TRẬN ĐA BÀI HỌC ---
st.sidebar.markdown("### 👨‍🏫 GIÁO VIÊN: CAO XUÂN ĐÚNG")
st.sidebar.header("⚙️ Cấu hình hệ thống & AI")

api_key_input = st.sidebar.text_input(
    "Nhập Google Gemini API Key của thầy/cô",
    type="password",
    help="Dán mã API Key lấy từ Google AI Studio vào đây",
)

st.sidebar.divider()
st.sidebar.header("📚 Xây dựng ma trận đề kiểm tra")

# Chọn khối lớp
selected_grade = st.sidebar.selectbox("Chọn khối lớp", list(CURRICULUM_DATA.keys()))

# Tạo danh sách tất cả các bài học
all_lessons_in_grade = []
for topic, lessons in CURRICULUM_DATA[selected_grade].items():
    for lesson in lessons:
        all_lessons_in_grade.append(f"{topic} | {lesson}")

selected_lessons = st.sidebar.multiselect(
    "Chọn các bài học đưa vào đề thi",
    all_lessons_in_grade,
    help="Có thể chọn 1 bài hoặc nhiều bài để tạo đề tổng hợp."
)

# Cấu hình trộn mã đề
st.sidebar.divider()
st.sidebar.header("🔀 Cấu hình Trộn đề")
num_versions = st.sidebar.number_input("Số lượng mã đề cần tạo", min_value=1, max_value=10, value=1)
st.sidebar.caption("Hệ thống sẽ tự động hoán vị câu hỏi và phương án A, B, C, D để tạo ra nhiều mã đề.")

# --- TÍCH HỢP AI SINH MA TRẬN VÀ BẢNG EXCEL (TỐI ƯU HÓA HIỆU NĂNG) ---
st.sidebar.divider()
st.sidebar.header("📊 Bảng Ma Trận Đề Kiểm Tra")

col_ai_btn, col_reset = st.sidebar.columns([3, 1])
with col_ai_btn:
    ai_auto_matrix_btn = st.button("✨ AI gợi ý ma trận")
with col_reset:
    if st.button("🔄 Đặt lại"):
        st.session_state.matrix_df_state = None
        st.rerun()

# Khởi tạo state lưu trữ ma trận nếu chưa có
if "matrix_df_state" not in st.session_state:
    st.session_state.matrix_df_state = None

# Xử lý khi bấm nút "AI gợi ý ma trận"
# Xử lý khi bấm nút gợi ý ma trận chuẩn (Thuật toán siêu tốc 0.01s chuẩn GDPT 2018)
if ai_auto_matrix_btn:
    if not selected_lessons:
        st.sidebar.warning("⚠️ Vui lòng chọn ít nhất một bài học ở trên!")
    else:
        num_lessons = len(selected_lessons)
        # Mục tiêu đề 20 câu: 8 NB (40%), 6 TH (30%), 4 VD (20%), 2 VDC (10%)
        # Chia đều và rải đều cho các bài đã chọn
        ai_data = []
        for idx, item in enumerate(selected_lessons):
            topic_name, lesson_name = item.split(" | ")
            
            # Phân bổ thông minh bám sát tỉ lệ khảo thí
            nb = max(1, round(8 / num_lessons))
            th = max(1, round(6 / num_lessons))
            vd = 1 if (idx % 2 == 0 or num_lessons <= 4) else 0
            vdc = 1 if (idx == num_lessons - 1) else 0
            
            ai_data.append({
                "Chọn": True,
                "Chủ đề": topic_name,
                "Bài học": lesson_name,
                "Nhận biết": nb,
                "Thông hiểu": th,
                "Vận dụng": vd,
                "Vận dụng cao": vdc
            })
            
        st.session_state.matrix_df_state = pd.DataFrame(ai_data)
        st.sidebar.success("✨ Đã thiết lập ma trận chuẩn tức thì! Thầy có thể chỉnh sửa lại các ô bên dưới.")
    if not api_key_input:
        st.sidebar.error("⚠️ Vui lòng nhập API Key ở trên trước!")
    elif not selected_lessons:
        st.sidebar.warning("⚠️ Vui lòng chọn ít nhất một bài học ở trên!")
    else:
        with st.spinner("🤖 AI đang phân tích và tính toán ma trận phù hợp..."):
            genai.configure(api_key=api_key_input)
            model = genai.GenerativeModel("gemini-3.8-flash")
            
            # Sử dụng ngoặc đơn () nối chuỗi an toàn tuyệt đối
            prompt_matrix_gen = (
                "Bạn là chuyên gia khảo thí môn Tin học THPT. Dựa trên các bài học sau:\n"
                f"{selected_lessons}\n"
                "Hãy thiết lập ma trận đề kiểm tra tổng hợp bám sát GDPT 2018 (sách Kết nối tri thức).\n"
                "Tổng số câu hỏi khoảng 20 câu.\n"
                "Tỉ lệ nhận thức mục tiêu: ~40% Nhận biết, ~30% Thông hiểu, ~20% Vận dụng, ~10% Vận dụng cao.\n"
                "YÊU CẦU: Trả về kết quả CHỈ gồm các dòng dữ liệu, phân tách bằng dấu gạch đứng (|):\n"
                "Tên bài học | Số câu Nhận biết | Số câu Thông hiểu | Số câu Vận dụng | Số câu Vận dụng cao\n"
                "Không viết thêm lời chào hay giải thích gì khác."
            )
            
            try:
                response = model.generate_content(prompt_matrix_gen)
                lines = response.text.strip().split("\n")
                ai_data = []
                for item in selected_lessons:
                    topic_name, lesson_name = item.split(" | ")
                    nb, th, vd, vdc = 1, 1, 0, 0
                    for line in lines:
                        if lesson_name in line or lesson_name.split(":")[0] in line:
                            parts = [p.strip() for p in line.split("|")]
                            if len(parts) >= 5:
                                try:
                                    nb = int(parts[1])
                                    th = int(parts[2])
                                    vd = int(parts[3])
                                    vdc = int(parts[4])
                                except:
                                    pass
                    ai_data.append({
                        "Chọn": True,
                        "Chủ đề": topic_name,
                        "Bài học": lesson_name,
                        "Nhận biết": nb,
                        "Thông hiểu": th,
                        "Vận dụng": vd,
                        "Vận dụng cao": vdc
                    })
                st.session_state.matrix_df_state = pd.DataFrame(ai_data)
                st.sidebar.success("✨ AI đã thiết lập xong ma trận gợi ý!")
            except Exception as e:
                st.sidebar.error(f"Lỗi AI: {e}")

# Tối ưu hóa cache khởi tạo bảng mặc định
@st.cache_data
def get_default_matrix(lessons):
    data = []
    for item in lessons:
        topic_name, lesson_name = item.split(" | ")
        data.append({
            "Chọn": True,
            "Chủ đề": topic_name,
            "Bài học": lesson_name,
            "Nhận biết": 1,
            "Thông hiểu": 1,
            "Vận dụng": 0,
            "Vận dụng cao": 0
        })
    return pd.DataFrame(data)

if st.session_state.matrix_df_state is None and selected_lessons:
    st.session_state.matrix_df_state = get_default_matrix(selected_lessons)

matrix_config = []
total_questions = 0

# Hiển thị bảng tính tương tác trực tiếp (Đã tối ưu hóa chống giật lag)
if selected_lessons and st.session_state.matrix_df_state is not None:
    st.sidebar.caption("💡 Thầy/cô có thể click đúp chuột vào ô số bên dưới để sửa:")
    
    edited_df = st.sidebar.data_editor(
        st.session_state.matrix_df_state,
        hide_index=True,
        column_config={
            "Chọn": st.column_config.CheckboxColumn("Chọn", width="small"),
            "Chủ đề": st.column_config.TextColumn("Chủ đề", disabled=True),
            "Bài học": st.column_config.TextColumn("Bài học", disabled=True),
            "Nhận biết": st.column_config.NumberColumn("NB", min_value=0, max_value=20, step=1, width="small"),
            "Thông hiểu": st.column_config.NumberColumn("TH", min_value=0, max_value=20, step=1, width="small"),
            "Vận dụng": st.column_config.NumberColumn("VD", min_value=0, max_value=20, step=1, width="small"),
            "Vận dụng cao": st.column_config.NumberColumn("VDC", min_value=0, max_value=20, step=1, width="small"),
        },
        key="matrix_editor_ai",
        use_container_width=True
    )
    st.session_state.matrix_df_state = edited_df

    # Xử lý tính toán tổng số câu hỏi bằng Pandas (Chạy siêu nhanh)
    if not edited_df.empty:
        df_selected = edited_df[edited_df["Chọn"] == True].copy()
        cols_to_int = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
        df_selected[cols_to_int] = df_selected[cols_to_int].fillna(0).astype(int)
        df_selected["Tổng số câu"] = df_selected[cols_to_int].sum(axis=1)
        total_questions = df_selected["Tổng số câu"].sum()
        
        for _, row in df_selected.iterrows():
            if row["Tổng số câu"] > 0:
                matrix_config.append({
                    "topic": row["Chủ đề"],
                    "lesson": row["Bài học"],
                    "nb": row["Nhận biết"], "th": row["Thông hiểu"], 
                    "vd": row["Vận dụng"], "vdc": row["Vận dụng cao"]
                })

    st.sidebar.success(f"**📊 Tổng số câu hỏi: {total_questions} câu**")

    # TẠO FILE EXCEL VÀ NÚT TẢI VỀ
    if not df_selected.empty:
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df_export = df_selected.drop(columns=["Chọn"]).reset_index(drop=True)
            df_export.index += 1
            df_export.index.name = "STT"
            
            df_export.to_excel(writer, sheet_name="MaTranDeThi", startrow=5)
            ws = writer.sheets["MaTranDeThi"]
            
            ws["A1"] = "TRƯỜNG THCS VÀ THPT CÂY DƯƠNG"
            ws["A2"] = f"MA TRẬN ĐỀ KIỂM TRA ĐỊNH KỲ MÔN TIN HỌC {selected_grade.upper()}"
            ws["A3"] = "GIÁO VIÊN BIÊN SOẠN: CAO XUÂN ĐÚNG"
            ws["A4"] = f"Thời gian làm bài: 45 phút | Tổng số câu: {total_questions} câu"
            
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

        excel_buffer.seek(0)
        
        st.sidebar.download_button(
            label="📊 Tải Ma trận (Excel chuẩn)",
            data=excel_buffer,
            file_name=f"Ma_Tran_De_Thi_TinHoc_{selected_grade.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# --- 4. KHU VỰC CHÍNH: GỌI GEMINI AI SINH ĐỀ ---
st.subheader(f"📋 Nội dung đề kiểm tra ({num_versions} Mã đề)")

if "generated_test" not in st.session_state:
    st.session_state.generated_test = ""

if st.button("🚀 Bắt đầu sinh đề kiểm tra", type="primary"):
    if not api_key_input:
        st.error("⚠️ Thầy/cô vui lòng nhập Google Gemini API Key ở thanh bên trái!")
    elif not matrix_config:
        st.warning("⚠️ Thầy/cô vui lòng chọn ít nhất một bài học để đưa vào đề thi!")
    else:
        try:
            with st.spinner("🤖 Gemini AI đang phân tích ma trận và thực hiện hoán vị trộn đề..."):
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel("gemini-3.8-flash")

                matrix_str = ""
                for config in matrix_config:
                    matrix_str += f"- Chủ đề: {config['topic']} | Bài học: {config['lesson']}\n"
                    matrix_str += f"  + Nhận biết: {config['nb']} câu | Thông hiểu: {config['th']} câu | Vận dụng: {config['vd']} câu | Vận dụng cao: {config['vdc']} câu.\n"

                # Sử dụng ngoặc đơn () nối chuỗi an toàn tuyệt đối
                prompt = (
                    "Bạn là một chuyên gia khảo thí và giáo viên Tin học THPT xuất sắc theo Chương trình GDPT 2018 (sách Kết nối tri thức).\n"
                    f"Hãy biên soạn một đề kiểm tra định kỳ môn Tin học cho {selected_grade}.\n\n"
                    "YÊU CẦU MA TRẬN BẮT BUỘC (TUÂN THỦ TUYỆT ĐỐI SỐ LƯỢNG NÀY):\n"
                    f"{matrix_str}\n"
                    "CHỈ DẪN BIÊN SOẠN VÀ TRỘN ĐỀ:\n"
                    f"1. Số lượng mã đề yêu cầu: {num_versions} mã đề. Nếu > 1 mã đề: Hãy lấy Đề gốc (Mã 101) sau đó tự động HOÁN VỊ (đảo vị trí các câu hỏi và đảo các phương án A,B,C,D) để tạo ra các mã đề tiếp theo (Ví dụ: Mã 102, 103...). Cung cấp đầy đủ nội dung toàn văn của từng mã đề.\n"
                    "2. Câu hỏi Trắc nghiệm: Phải có 4 phương án A, B, C, D. Chỉ có duy nhất 1 đáp án đúng. Tuyệt đối KHÔNG lạm dụng phương án 'Tất cả các đáp án trên'.\n"
                    "3. BẮT BUỘC: Phần nội dung đề thi của mỗi mã đề phải được bắt đầu bằng tiêu đề chuẩn xác: '### MÃ ĐỀ <số>' (Ví dụ: ### MÃ ĐỀ 101).\n"
                    "4. TUYỆT ĐỐI KHÔNG ghi chú, hiển thị tên chủ đề hay tên bài học vào trong phần câu hỏi của đề thi dành cho học sinh.\n"
                    "5. BẮT BUỘC: Phần Đáp án phải được đặt ở vị trí cuối cùng của toàn bộ văn bản và bắt đầu bằng tiêu đề chuẩn xác: '### ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM'.\n"
                    "6. Trong phần Đáp án, hãy lập Bảng đáp án trắc nghiệm tổng hợp so sánh cho tất cả các mã đề.\n\n"
                    "Trình bày kết quả chuyên nghiệp bằng định dạng Markdown."
                )

                # Gọi API với chế độ STREAM (Trực tiếp)
                response = model.generate_content(prompt, stream=True)

                def stream_parser():
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                full_text = st.write_stream(stream_parser)
                st.session_state.generated_test = full_text

                st.success(f"🎉 Gemini AI đã sinh và trộn thành công {num_versions} mã đề kiểm tra!")

        except Exception as e:
            st.error(f"❌ Lỗi kết nối với Gemini AI: {e}")

# --- 5. TẠO FILE WORD CHUẨN FORM GIÁO DỤC (TỰ ĐỘNG NGẮT TRANG) ---
if st.session_state.generated_test:
    st.markdown("---")
    
    doc = Document()
    
    # Thiết lập Font chữ mặc định
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    def add_exam_header(docx_obj, ma_de=""):
        header_p = docx_obj.add_paragraph()
        header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run_truong = header_p.add_run("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG\n")
        run_truong.bold = True
        run_truong.font.size = Pt(13)

        run_de = header_p.add_run(f"ĐỀ KIỂM TRA ĐỊNH KỲ - MÔN TIN HỌC {selected_grade.upper()}\n")
        run_de.bold = True
        run_de.font.size = Pt(14)

        if ma_de:
            run_ma = header_p.add_run(f"{ma_de}\n")
            run_ma.bold = True
            run_ma.font.size = Pt(13)

        run_tg = header_p.add_run("Thời gian làm bài: 45 phút (Không kể thời gian phát đề)\n")
        run_tg.italic = True
        run_tg.font.size = Pt(12)

        docx_obj.add_paragraph(
            "Họ và tên thí sinh: ................................................................. Lớp: .....................")
        docx_obj.add_paragraph(
            "Số báo danh: ..........................................................................................................")
        docx_obj.add_paragraph("_" * 60).alignment = WD_ALIGN_PARAGRAPH.CENTER
        docx_obj.add_paragraph()

    first_page = True
    for line in st.session_state.generated_test.split("\n"):
        line = line.strip()
        if not line:
            doc.add_paragraph()
            continue

        if "MÃ ĐỀ" in line.upper() and line.startswith("#"):
            if not first_page:
                doc.add_page_break()
            first_page = False

            ma_de_text = line.replace("#", "").strip()
            add_exam_header(doc, ma_de_text)
            continue

        if "ĐÁP ÁN" in line.upper() and line.startswith("#"):
            if not first_page:
                doc.add_page_break()
            first_page = False

            p = doc.add_heading(level=1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line.replace("#", "").strip())
            run.font.name = 'Times New Roman'
            continue

        if line.startswith("# "):
            p = doc.add_heading(level=1)
            run = p.add_run(line.replace("# ", ""))
            run.font.name = 'Times New Roman'
        elif line.startswith("## "):
            p = doc.add_heading(level=2)
            run = p.add_run(line.replace("## ", ""))
            run.font.name = 'Times New Roman'
        elif line.startswith("### "):
            p = doc.add_heading(level=3)
            run = p.add_run(line.replace("### ", ""))
            run.font.name = 'Times New Roman'
        else:
            p = doc.add_paragraph()
            parts = line.split("**")
            for i, part in enumerate(parts):
                run = p.add_run(part)
                run.font.name = 'Times New Roman'
                if i % 2 != 0:
                    run.bold = True

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="📥 Tải BỘ ĐỀ (Word) bản in chuẩn (Có tự động ngắt trang)",
        data=buffer,
        file_name=f"Bo_De_Kiem_Tra_Tron_Ma_{selected_grade.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
